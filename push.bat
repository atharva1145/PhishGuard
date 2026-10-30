@echo off
title PhishGuard Git Sync
echo ========================================================
echo        PhishGuard - Sync & Push to GitHub
echo ========================================================
echo.

set COMMIT_MSG=%*
if "%COMMIT_MSG%"=="" set /p COMMIT_MSG="Enter commit description: "
if "%COMMIT_MSG%"=="" set COMMIT_MSG="update: Improvements and feature updates"

echo [*] Staging all changes...
git add -A

echo [*] Committing: "%COMMIT_MSG%"
git commit -m "%COMMIT_MSG%"

echo [*] Pushing to origin main...
git push origin main

echo.
echo ========================================================
echo [OK] Changes pushed successfully to GitHub!
echo Repository: https://github.com/atharva1145/PhishGuard
echo ========================================================
echo.
pause
