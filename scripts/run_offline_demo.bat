@echo off
setlocal
cd /d %~dp0..

if not exist backend\.venv python -m venv backend\.venv
call backend\.venv\Scripts\activate
python -m pip install -r backend\requirements.txt

if not exist frontend\node_modules (
  cd frontend
  call npm install
  cd ..
)

start "Traffic Backend" cmd /k "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"
start "Traffic Dashboard" cmd /k "cd /d %CD%\frontend && npm run dev -- --host 127.0.0.1"
echo.
echo Offline demo started.
echo Backend:  http://127.0.0.1:8000
echo Dashboard: http://127.0.0.1:5173
