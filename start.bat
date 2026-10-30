@echo off
title PhishGuard Launcher
echo ========================================================
echo        Starting PhishGuard AI Detection Platform
echo ========================================================
echo.
echo [1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "PhishGuard Backend" cmd /k "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

echo [2/2] Launching Vite Frontend on http://localhost:5173 ...
start "PhishGuard Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo [OK] Both services are starting in separate windows!
echo - Frontend Web UI:  http://localhost:5173
echo - Backend API Docs: http://127.0.0.1:8000/docs
echo ========================================================
echo.
pause
