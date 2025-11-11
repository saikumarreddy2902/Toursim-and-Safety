@echo off
title Tourist Safety System
echo ========================================
echo    Tourist Safety System Launcher
echo ========================================
echo.

cd /d "%~dp0"
set FLASK_ENV=development
set SECRET_KEY=dev-secret-change-me-in-production

echo Starting Tourist Safety System...
echo Access at: http://127.0.0.1:5000
echo Press Ctrl+C to stop
echo.

python backend\app.py
pause