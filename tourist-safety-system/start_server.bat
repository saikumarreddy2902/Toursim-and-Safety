@echo off
setlocal
echo Starting Tourist Safety Monitoring System (Waitress)...
echo.

REM Ensure we run from project root regardless of how script is started
pushd %~dp0

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://python.org and try again.
    pause
    exit /b 1
)

echo Python is installed ✓
echo.

REM Allow overriding HOST/PORT via environment variables; defaults are local-only
if "%HOST%"=="" set HOST=127.0.0.1
if "%PORT%"=="" set PORT=5000

echo Using HOST=%HOST% PORT=%PORT%
echo Starting server with Waitress...
echo Open your browser at: http://%HOST%:%PORT%
echo Press Ctrl+C in the upcoming window to stop the server.
echo.

REM Delegate to backend runner which handles venv and dependencies
pushd backend
setlocal
set "_HOST=%HOST%"
set "_PORT=%PORT%"
call run_waitress.bat %_HOST% %_PORT%
set "EXITCODE=%ERRORLEVEL%"
endlocal & set "EXITCODE=%EXITCODE%"
if not "%EXITCODE%"=="0" (
    echo Runner returned error (%EXITCODE%), attempting direct start...
    call .\venv\Scripts\python.exe -m waitress --listen=%HOST%:%PORT% wsgi:app
)
popd

popd
endlocal