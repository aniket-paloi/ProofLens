@echo off
title ProofLens Workspace Launcher
echo =======================================================
echo          ProofLens - Investigation Workspace
echo =======================================================
echo.
echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "ProofLens Backend" cmd /k "cd /d %~dp0 && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

timeout /t 2 >nul

echo Starting Vite Frontend on http://127.0.0.1:5173 ...
start "ProofLens Frontend" cmd /k "cd /d %~dp0frontend && npm run dev -- --host 127.0.0.1 --port 5173"

timeout /t 2 >nul

echo Opening Browser...
start http://127.0.0.1:5173/

echo.
echo Both servers are running in separate terminal windows.
echo To stop, simply close the opened windows.
pause
