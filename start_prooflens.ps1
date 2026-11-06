# ProofLens One-Click Launcher for PowerShell
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "       ProofLens — Investigation Workspace" -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

$root = $PSScriptRoot

Write-Host "Starting FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

Start-Sleep -Seconds 2

Write-Host "Starting React/Vite Frontend on http://127.0.0.1:5173 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev -- --host 127.0.0.1 --port 5173"

Start-Sleep -Seconds 2

Write-Host "Opening ProofLens in default web browser..." -ForegroundColor Yellow
Start-Process "http://127.0.0.1:5173/"

Write-Host ""
Write-Host "Both servers are running! To stop, close the two terminal windows." -ForegroundColor Cyan

