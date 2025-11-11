@echo off
setlocal enabledelayedexpansion
cls

:: ============================================================================
::                      TOURIST SAFETY SYSTEM
::                      UNIFIED HOST MANAGER
::                  🌟 ALL-IN-ONE SOLUTION 🌟
:: ============================================================================

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                    TOURIST SAFETY SYSTEM                         ║
echo ║                  🚀 UNIFIED HOST MANAGER 🚀                     ║
echo ║                                                                  ║
echo ║  For the BEST experience, use: python unified_host.py           ║
echo ║  This script provides basic functionality only                   ║
echo ║                                                                  ║
echo ║  ✅ SOS Alerts with Authentication                               ║
echo ║  ✅ Admin-Only Post-Incident Reports                            ║
echo ║  ✅ Real-time GPS ^& Geofencing                                   ║
echo ║  ✅ AI Monitoring ^& Analysis                                     ║
echo ║  ✅ Multi-language Support                                       ║
echo ║  ✅ Blockchain Security                                           ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: Check if unified host exists and recommend it
if exist "unified_host.py" (
    echo 🌟 RECOMMENDED: Use the full-featured Python host manager
    echo    Command: python unified_host.py
    echo.
    set /p use_python="Would you like to launch the Python host manager now? (Y/N): "
    if /i "!use_python!"=="y" (
        python unified_host.py
        exit /b 0
    )
    echo.
    echo Continuing with basic Windows script...
    echo.
)

:: Check if we're in the right directory
if not exist "backend\app.py" (
    echo ❌ Error: backend\app.py not found!
    echo Please run this script from the tourist-safety-system directory
    echo.
    pause
    exit /b 1
)

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python is installed
echo ✅ Project structure verified
echo.

:menu
echo ════════════════════════════════════════════════════════════════
echo                      🌐 BASIC HOSTING OPTIONS
echo ════════════════════════════════════════════════════════════════
echo.
echo  1. 🚀 Quick Start (Local Server)
echo  2. 📦 Install Dependencies
echo  3. 🗄️  Setup Database
echo  4. 🌐 Open Browser
echo  5. 📊 Basic Status Check
echo  U. 🌟 Launch Unified Host Manager (RECOMMENDED)
echo  Q. 🚪 Quit
echo.
echo ════════════════════════════════════════════════════════════════
echo.

set /p choice="Enter your choice: "

if /i "%choice%"=="1" goto quick_start
if /i "%choice%"=="2" goto install_deps
if /i "%choice%"=="3" goto setup_db
if /i "%choice%"=="4" goto open_browser
if /i "%choice%"=="5" goto status_check
if /i "%choice%"=="u" goto unified_host
if /i "%choice%"=="q" goto quit

echo ❌ Invalid choice.
pause
goto menu

:quick_start
echo.
echo 🚀 Starting Local Development Server...
cd backend
pip install -r requirements.txt >nul 2>&1
python app.py
cd ..
pause
goto menu

:install_deps
echo.
echo 📦 Installing Dependencies...
cd backend
pip install -r requirements.txt
cd ..
echo ✅ Dependencies installed
pause
goto menu

:setup_db
echo.
echo 🗄️ Setting up Database...
cd backend
python -c "from app import init_db; init_db()"
cd ..
echo ✅ Database setup complete
pause
goto menu

:open_browser
echo.
echo 🌐 Opening Browser...
start http://localhost:5000
start http://localhost:5000/admin
echo ✅ Browser opened
pause
goto menu

:status_check
echo.
echo 📊 Basic Status Check...
echo ✅ Python Version:
python --version
echo.
if exist "backend\app.py" (echo ✅ Backend found) else (echo ❌ Backend missing)
if exist "data\tourist_safety.db" (echo ✅ Database found) else (echo ❌ Database not found)
pause
goto menu

:unified_host
echo.
echo 🌟 Launching Unified Host Manager...
python unified_host.py
goto menu

:quit
echo.
echo 👋 Goodbye!
echo.
echo 📱 If your server is running, access it at: http://localhost:5000
echo 🛑 Press Ctrl+C to stop the server if it's running
echo.
pause
exit /b 0