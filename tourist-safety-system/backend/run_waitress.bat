@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Determine script directory and ensure we run from backend folder
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

REM Provide friendly banner
echo ==============================================
echo  Starting Tourist Safety System (Waitress)
echo  Working dir: %CD%
echo ==============================================

REM Accept HOST and PORT as optional args if provided
if not "%~1"=="" set "HOST=%~1"
if not "%~2"=="" set "PORT=%~2"

REM Defaults (bind to localhost by default; port 5000)
if "%HOST%"=="" set "HOST=127.0.0.1"
if "%PORT%"=="" set "PORT=5000"

REM Ensure MongoDB environment variables are set for backend to use Mongo
if "%DB_BACKEND%"=="" set "DB_BACKEND=mongo"
if "%MONGO_URI%"=="" set "MONGO_URI=mongodb://127.0.0.1:27017"
if "%MONGO_DB_NAME%"=="" set "MONGO_DB_NAME=tourist_safety"
echo Using database: DB_BACKEND=%DB_BACKEND% MONGO_URI=%MONGO_URI% MONGO_DB_NAME=%MONGO_DB_NAME%

REM Ensure venv exists using python, fallback to py launcher
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment in: %CD%\venv
    where python >nul 2>&1
    if %ERRORLEVEL%==0 (
        python -m venv venv
    ) else (
        py -3 -m venv venv
    )
)

REM Upgrade pip and install deps using python -m pip for reliability
echo Ensuring dependencies are installed...
call .\venv\Scripts\python.exe -m pip install --disable-pip-version-check --upgrade pip >nul 2>&1
if exist requirements.txt (
    call .\venv\Scripts\python.exe -m pip install --disable-pip-version-check -r requirements.txt
    if errorlevel 1 (
        echo.
        echo WARNING: Some dependencies failed to install. Trying to continue...
        echo.
    )
)

REM Validate wsgi entry exists
if not exist "wsgi.py" (
    echo ERROR: wsgi.py not found in %CD%
    echo Please make sure you are in the backend directory.
    popd
    endlocal & exit /b 1
)

REM Launch Waitress
set "PYTHONUNBUFFERED=1"
set "PYTHONPATH=%SCRIPT_DIR%"
echo Launching Waitress at http://%HOST%:%PORT%
call .\venv\Scripts\python.exe -m waitress --listen=%HOST%:%PORT% wsgi:app
set "EXITCODE=%ERRORLEVEL%"

REM Fallback to Flask dev server if Waitress failed to start
if not "%EXITCODE%"=="0" (
    echo.
    echo ⚠️  Waitress failed with exit code %EXITCODE%. Falling back to Flask dev server...
    echo (For production, please fix Waitress or check logs above.)
    call .\venv\Scripts\python.exe app.py
    set "EXITCODE=%ERRORLEVEL%"
)

popd
endlocal & exit /b %EXITCODE%
