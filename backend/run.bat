@echo off
setlocal
cd /d %~dp0
echo Installing deps...
py -3 -m pip install -r requirements.txt
if errorlevel 1 goto :eof
echo Starting backend on http://localhost:8000
py -3 -m uvicorn app.main:app --reload --port 8000
