"""Flask backend for the automated grading demo."""
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import uuid
from difflib import SequenceMatcher
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from fpdf import FPDF

load_dotenv()

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "submissions.db"
TESTCASE_DIR = BASE_DIR / "testcases"

JUDGE0 = os.getenv("JUDGE0_BASE_URL", "https://ce.judge0.com")
JUDGE0_KEY = os.getenv("JUDGE0_API_KEY", "")
ADMIN_KEY = os.getenv("ADMIN_KEY", "admin123")
USE_LOCAL_PYTHON = os.getenv("USE_LOCAL_PYTHON", "true").lower() == "true"
LOCAL_TIMEOUT_SECONDS = float(os.getenv("LOCAL_TIMEOUT_SECONDS", "5"))
MAX_CODE_LENGTH = int(os.getenv("MAX_CODE_LENGTH", "100000"))
MAX_PLAGIARISM_COMPARISONS = int(os.getenv("MAX_PLAGIARISM_COMPARISONS", "200"))

app = Flask(__name__)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_db():
    if not DB_PATH.exists():
        from init_db import init

        init()


def safe_assignment_id(value):
    value = str(value or "").strip()
    if re.fullmatch(r"[A-Za-z0-9_-]+", value):
        return value
    return None


def parse_json_field(value):
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if not stripped.startswith(("[", "{")):
        return value
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return value


def similarity(a, b):
    return SequenceMatcher(None, a or "", b or "").ratio()


def pdf_text(value):
    return str(value or "").encode("latin-1", errors="replace").decode("latin-1")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/submit", methods=["POST"])
def submit():
    ensure_db()
    data = request.get_json(silent=True) or {}
    required = ["assignment_id", "student_name", "student_email", "code"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"missing {field}"}), 400

    assignment_id = safe_assignment_id(data.get("assignment_id"))
    if not assignment_id:
        return jsonify({"error": "assignment_id may contain only letters, numbers, underscores, and hyphens"}), 400

    sid = str(uuid.uuid4())
    name = str(data.get("student_name", "")).strip()
    email = str(data.get("student_email", "")).strip()
    language = str(data.get("language", "python")).strip().lower()
    code = str(data.get("code", ""))

    if len(code) > MAX_CODE_LENGTH:
        return jsonify({"error": f"code is too large; max {MAX_CODE_LENGTH} characters"}), 400

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO submissions (id, assignment_id, student_name, student_email, language, code)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (sid, assignment_id, name, email, language, code),
        )

    results, score = run_tests(code, language, assignment_id)
    plagiarism = quick_plagiarism_check(sid, assignment_id, code)
    feedback = generate_feedback(name, assignment_id, code, results, score)

    with get_conn() as conn:
        conn.execute(
            """
            UPDATE submissions
            SET results = ?, score = ?, plagiarism = ?, feedback = ?, status = ?
            WHERE id = ?
            """,
            (json.dumps(results), score, json.dumps(plagiarism), feedback, "graded", sid),
        )

    return jsonify(
        {
            "success": True,
            "submission_id": sid,
            "score": score,
            "results": results,
            "plagiarism": plagiarism,
            "feedback": feedback,
        }
    )


@app.route("/api/submissions", methods=["GET"])
def list_submissions():
    ensure_db()
    if request.args.get("adminKey", "") != ADMIN_KEY:
        return jsonify({"error": "unauthorized (provide adminKey query param)"}), 401

    try:
        limit = min(max(int(request.args.get("limit", 200)), 1), 1000)
    except ValueError:
        limit = 200

    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM submissions ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = [dict(row) for row in cur.fetchall()]

    for row in rows:
        row["results"] = parse_json_field(row.get("results"))
        row["plagiarism"] = parse_json_field(row.get("plagiarism"))

    return jsonify({"submissions": rows})


@app.route("/api/submission/<sid>", methods=["GET"])
def get_submission(sid):
    ensure_db()
    if request.args.get("adminKey", "") != ADMIN_KEY:
        return jsonify({"error": "unauthorized (provide adminKey query param)"}), 401

    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM submissions WHERE id = ?", (sid,))
        row = cur.fetchone()

    if not row:
        return jsonify({"error": "not found"}), 404

    submission = dict(row)
    submission["results"] = parse_json_field(submission.get("results"))
    submission["plagiarism"] = parse_json_field(submission.get("plagiarism"))
    return jsonify({"submission": submission})


def run_tests(code, language, assignment_id):
    assignment_id = safe_assignment_id(assignment_id)
    if not assignment_id:
        return [], 0

    testcase_path = TESTCASE_DIR / f"{assignment_id}.json"
    if not testcase_path.exists():
        return [], 0

    try:
        testcases = json.loads(testcase_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [], 0

    results = []
    passed = 0
    for testcase in testcases:
        stdin = str(testcase.get("input", ""))
        expected = str(testcase.get("expected", "")).strip()
        output, stderr = run_code(code, language, stdin)
        ok = output.strip() == expected
        passed += int(ok)
        results.append(
            {
                "input": stdin,
                "expected": expected,
                "output": output,
                "ok": ok,
                "stderr": stderr,
            }
        )

    score = int((passed / len(testcases)) * 100) if testcases else 0
    return results, score


def run_code(source_code, language, stdin):
    if USE_LOCAL_PYTHON and language in {"python", "python3"}:
        return run_python_locally(source_code, stdin)
    return call_judge0(source_code, language, stdin)


def run_python_locally(source_code, stdin):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as temp_file:
        temp_file.write(source_code)
        temp_path = temp_file.name

    try:
        proc = subprocess.run(
            [sys.executable, temp_path],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=LOCAL_TIMEOUT_SECONDS,
        )
        return proc.stdout or "", proc.stderr or ""
    except subprocess.TimeoutExpired:
        return "", f"Execution timed out after {LOCAL_TIMEOUT_SECONDS:g} seconds"
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


def call_judge0(source_code, language, stdin):
    mapping = {"python": 71, "python3": 71, "c": 50, "cpp": 54, "java": 62, "javascript": 63}
    language_id = mapping.get(language, 71)
    payload = {"source_code": source_code, "language_id": language_id, "stdin": stdin}
    headers = {"X-Auth-Token": JUDGE0_KEY} if JUDGE0_KEY else {}

    try:
        resp = requests.post(f"{JUDGE0.rstrip('/')}/submissions/?wait=true", json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("stdout") or "", data.get("stderr") or data.get("compile_output") or ""
    except Exception as exc:
        return "", str(exc)


def quick_plagiarism_check(submission_id, assignment_id, code):
    with get_conn() as conn:
        cur = conn.execute(
            """
            SELECT id, student_name, code
            FROM submissions
            WHERE assignment_id = ? AND id != ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (assignment_id, submission_id, MAX_PLAGIARISM_COMPARISONS),
        )
        rows = cur.fetchall()

    matches = []
    for row in rows:
        score = similarity(code, row["code"])
        if score > 0.25:
            matches.append({"id": row["id"], "student_name": row["student_name"], "similarity": round(score, 3)})
    return matches


def generate_feedback(student_name, assignment_id, code, results, score):
    passed = sum(1 for result in results if result.get("ok"))
    total = len(results)
    failed = total - passed

    code_lower = code.lower()
    has_loops = any(token in code_lower for token in ["for", "while"])
    has_conditions = any(token in code_lower for token in ["if", "elif", "else"])
    has_functions = "def " in code_lower
    lines_count = len(code.splitlines())

    feedback = []
    if score == 100:
        feedback.append(f"Perfect score, {student_name}! Excellent work.")
    elif score >= 80:
        feedback.append(f"Great job, {student_name}! You scored {score}%.")
    elif score >= 60:
        feedback.append(f"Good effort, {student_name}. Score: {score}%.")
    else:
        feedback.append(f"Keep trying, {student_name}! Score: {score}%.")

    if failed:
        failed_tests = [result for result in results if not result.get("ok")]
        empty_outputs = sum(1 for result in failed_tests if not result.get("output", "").strip())
        error_outputs = sum(1 for result in failed_tests if result.get("stderr", "").strip())
        if error_outputs:
            feedback.append("Fix the runtime errors first.")
        elif empty_outputs:
            feedback.append("Some test cases produce no output; check your print statements.")
        else:
            feedback.append(f"Review the {failed} failed test case(s) for logic errors.")

    if not has_functions and lines_count > 20:
        feedback.append("Consider breaking your code into functions.")
    elif not has_loops and "loop" in assignment_id.lower():
        feedback.append("This assignment might benefit from using loops.")
    elif not has_conditions and any(word in assignment_id.lower() for word in ["condition", "if", "decision"]):
        feedback.append("Consider using conditional statements.")

    assignment_lower = assignment_id.lower()
    if "beginner" in assignment_lower or "intro" in assignment_lower:
        feedback.append("Great start with programming!")
    elif "advanced" in assignment_lower or "challenge" in assignment_lower:
        feedback.append("Tackling advanced problems; keep it up!")
    else:
        feedback.append("Keep practicing and you will improve.")

    return " ".join(feedback)


@app.route("/api/report/<sid>", methods=["GET"])
def report(sid):
    ensure_db()
    if request.args.get("adminKey", "") != ADMIN_KEY:
        return jsonify({"error": "unauthorized (provide adminKey)"}), 401

    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM submissions WHERE id = ?", (sid,))
        row = cur.fetchone()

    if not row:
        return jsonify({"error": "not found"}), 404

    pdf_path = BASE_DIR / f"report_{sid}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Automated Grading Report", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, pdf_text(f"Student: {row['student_name']} ({row['student_email']})"))
    pdf.multi_cell(0, 8, pdf_text(f"Assignment: {row['assignment_id']}"))
    pdf.multi_cell(0, 8, pdf_text(f"Score: {row['score']}"))
    pdf.ln(4)
    pdf.multi_cell(0, 8, "Feedback:")
    pdf.multi_cell(0, 8, pdf_text(row["feedback"]))
    pdf.ln(4)
    pdf.multi_cell(0, 8, "Plagiarism matches:")
    pdf.multi_cell(0, 8, pdf_text(row["plagiarism"]))
    pdf.output(str(pdf_path))
    return send_file(str(pdf_path), as_attachment=True)


if __name__ == "__main__":
    ensure_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
