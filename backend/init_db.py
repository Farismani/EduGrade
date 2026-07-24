# Initialize SQLite DB for Auto Grader
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "submissions.db"


def init():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS assignments (
        id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        language TEXT DEFAULT 'python',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS submissions (
        id TEXT PRIMARY KEY,
        assignment_id TEXT,
        student_name TEXT,
        student_email TEXT,
        language TEXT,
        code TEXT,
        results TEXT,
        score REAL DEFAULT 0,
        plagiarism TEXT,
        feedback TEXT,
        status TEXT DEFAULT 'submitted',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized at", DB_PATH)


if __name__ == '__main__':
    init()
