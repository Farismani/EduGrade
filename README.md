# Automated Grading & Feedback - Hackathon MVP

## What is included
- `backend/` : Flask backend with SQLite DB, Judge0 integration, plagiarism check, and feedback generation.
  - `server.py` : main API
  - `init_db.py` : initialize the local SQLite DB
  - `testcases/assignment1.json` : example testcases file
- `frontend/` : Streamlit frontend for students and instructors.
  - `streamlit_app.py` : Streamlit UI
- `requirements.txt` : Python packages to install

## Quick start (local)
1. Make sure Python 3.11+ is installed. If your old `venv` is broken, create a fresh local environment:
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```
   python -m pip install -r requirements.txt
   ```
3. Initialize the database (optional - server will auto-init if missing):
   ```
   python backend/init_db.py
   ```
4. (Optional) Set environment variables:
   - `JUDGE0_BASE_URL` (default: https://ce.judge0.com)
   - `JUDGE0_API_KEY` (if you have one)
   - `OPENAI_API_KEY` (for better AI feedback)
   - `ADMIN_KEY` (default `admin123`)
5. Run backend:
   ```
   python backend/server.py
   ```
6. Run frontend:
   ```
   streamlit run frontend/streamlit_app.py
   ```
7. Submit code from Streamlit UI (use assignment id `assignment1` to test example cases).

## Notes & Safety
- This is a hackathon MVP. For production, use a hardened sandbox for running untrusted code.
- Judge0 CE is used as a convenient sandbox; it is external and has usage limits.
- Plagiarism checks here are a simple similarity heuristic; for high-stakes use integrate MOSS/JPlag and manual review.

## What to edit
- Add testcases: place JSON files in `backend/testcases/<assignment_id>.json` with list of objects:
  ```
  [
    {"input":"2 3", "expected":"5"},
    {"input":"10 20", "expected":"30"}
  ]
  ```
- Improve mapping of languages to Judge0 language IDs in `backend/server.py`.

Good luck — use this for your hackathon demo!
