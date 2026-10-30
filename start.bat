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
echo [OK] PhishGuard is up and running!
echo - Unified Web Application: http://127.0.0.1:8000
echo - Vite Dev Hot-Reload:     http://localhost:5173
echo - Interactive API Docs:    http://127.0.0.1:8000/docs
echo ========================================================
echo.
pause
