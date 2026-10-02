@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
echo.
echo FitBuddy is starting at http://127.0.0.1:8000
echo Press Ctrl+C to stop the server.
python -m uvicorn app.main:app --reload
pause
