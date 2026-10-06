#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -d "backend/.venv" ]; then
  python3 -m venv backend/.venv
fi

source backend/.venv/bin/activate
python -m pip install -r backend/requirements.txt

if [ ! -d "frontend/node_modules" ]; then
  (cd frontend && npm install)
fi

echo "Starting offline traffic backend on http://127.0.0.1:8000"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

cleanup() {
  kill "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting dashboard on http://127.0.0.1:5173"
cd frontend
npm run dev -- --host 127.0.0.1
