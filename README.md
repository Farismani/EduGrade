# Automated Grading & Feedback - Hackathon MVP

## Project overview
This repository contains an automated grading demo with:
- `backend/`: Flask API, local SQLite database, code execution, plagiarism scoring, and feedback generation.
- `frontend/`: Streamlit app for submitting code and viewing results.
- `requirements.txt`: Python dependencies.

## Backend structure
- `backend/server.py`: Flask backend that accepts submissions, runs test cases, stores results, and generates feedback.
- `backend/init_db.py`: Initializes the SQLite database and creates `assignments` and `submissions` tables.
- `backend/testcases/assignment1.json`: Example assignment test cases.

## Frontend structure
- `frontend/streamlit_app.py`: Streamlit UI for students and instructors.
  - Uses `API_URL` environment variable to connect to the backend (default `http://localhost:5000`).

## Requirements
- Python 3.11+
- `pip install -r requirements.txt`

## Local setup
1. Create and activate a virtual environment:
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Initialize the database (optional; backend auto-initializes if missing):
   ```powershell
   python backend/init_db.py
   ```

## Environment variables
Set these before running the app if you want to override defaults.
- `JUDGE0_BASE_URL`: Judge0 API base URL (default: `https://ce.judge0.com`)
- `JUDGE0_API_KEY`: Optional Judge0 API key
- `ADMIN_KEY`: Admin key for protected endpoints (default: `admin123`)
- `USE_LOCAL_PYTHON`: `true`/`false` to run Python submissions locally instead of Judge0 (default: `true`)
- `LOCAL_TIMEOUT_SECONDS`: Timeout for local Python execution in seconds (default: `5`)
- `PORT`: Backend port (default: `5000`)
- `API_URL`: Frontend backend URL for `frontend/streamlit_app.py` (default: `http://localhost:5000`)

## Run the app
1. Start the backend:
   ```powershell
   python backend/server.py
   ```
2. Start the frontend:
   ```powershell
   streamlit run frontend/streamlit_app.py
   ```

## Free deployment option (not GitHub Pages)
A free deployment option is Render.com, which supports Python web services and can host both the Flask backend and the Streamlit frontend.

### Render deployment using `render.yaml`
A `render.yaml` file is included in this repository to deploy both services with Render.
- Backend service: `auto-grader-backend`
- Frontend service: `auto-grader-frontend`

After connecting your GitHub repo to Render, the services will build and deploy automatically.

### Manual Render deployment
#### Backend on Render
1. Create a new Web Service in Render.
2. Connect your GitHub repository.
3. Use the repository root.
4. Set the build command to:
   ```bash
   pip install -r requirements.txt
   ```
5. Set the start command to:
   ```bash
   python backend/server.py
   ```
6. Add these environment variables:
   - `ADMIN_KEY=admin123` (or choose your own secret)
   - `USE_LOCAL_PYTHON=false`
   - `PORT=5000`
   - `JUDGE0_BASE_URL=https://ce.judge0.com` (optional)
   - `JUDGE0_API_KEY=` (optional)

#### Frontend on Render
1. Create a second Web Service in Render.
2. Connect the same repository.
3. Use the repository root.
4. Set the build command to:
   ```bash
   pip install -r requirements.txt
   ```
5. Set the start command to:
   ```bash
   streamlit run frontend/streamlit_app.py --server.port 3000 --server.enableCORS false
   ```
6. Add this environment variable:
   - `API_URL=https://auto-grader-backend.onrender.com`

> If the backend URL differs, update `API_URL` to the actual Render backend service URL.

### Alternative split deployment
- Frontend: Streamlit Community Cloud
- Backend: Render (or Railway free tier)
- Set `API_URL` in the frontend service to the deployed backend URL.

## Using the demo
- Submit a code solution from the Streamlit UI.
- Use `assignment1` as the assignment ID to run the example test cases in `backend/testcases/assignment1.json`.
- After submission, the backend returns:
  - `score`
  - `results` for each test case
  - `plagiarism` matches from recent submissions
  - `feedback`

## Test case format
Add JSON files under `backend/testcases` named by assignment ID, for example:
```json
[
  {"input": "2 3", "expected": "5"},
  {"input": "10 20", "expected": "30"}
]
```

## Notes
- This is a prototype demo. Running untrusted code in production requires a secure sandbox.
- Judge0 is used for non-Python languages and may have rate limits.
- The plagiarism check is a simple similarity heuristic; use a dedicated plagiarism tool for real grading.

## Helpful endpoints
- `GET /api/health`
- `POST /api/submit`
- `GET /api/submissions?adminKey=<key>`
- `GET /api/submission/<id>?adminKey=<key>`
- `GET /api/report/<id>?adminKey=<key>`

deployed link: https://auto-grader-frontend.onrender.com/