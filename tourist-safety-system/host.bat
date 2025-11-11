@echo off
cls
echo.
echo ========================================
echo  TOURIST SAFETY SYSTEM - UNIFIED HOST
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python is installed
echo 🚀 Starting Unified Host Manager...
echo.

REM Run the unified Python host manager
python host.py

REM If Python host manager fails, show manual options
if errorlevel 1 (
    echo.
    echo ⚠️ Python host manager failed. Trying manual setup...
    echo.
    goto manual
)

goto end

:manual
echo.
echo � Manual Setup Options:
echo.
echo 1. Quick Local Start:
echo    cd backend ^&^& python app.py
echo.
echo 2. Docker Start:
echo    docker-compose up -d
echo.
echo 3. Install Dependencies:
echo    pip install -r backend/requirements.txt
echo.
set /p choice=Try manual setup? (y/n): 
if /i "%choice%"=="y" (
    echo.
    echo 🚀 Starting manual local server...
    cd backend
    pip install -r requirements.txt
    python app.py
)

:end
echo.
echo 📞 Need Help?
echo 📖 Read DEPLOYMENT_README.md for detailed instructions
echo 🔍 Check logs/app.log for troubleshooting
echo 🌐 Visit http://localhost:5000/health for system status
echo.
pause