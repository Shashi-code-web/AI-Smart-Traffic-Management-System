@echo off
cd /d %~dp0..\backend
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
if not exist .venv\installed.flag pip install -r requirements.txt && echo installed> .venv\installed.flag
uvicorn app.main:app --host 127.0.0.1 --port 8000
