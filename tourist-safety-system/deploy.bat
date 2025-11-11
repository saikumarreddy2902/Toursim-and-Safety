@echo off
REM Windows deployment script for Tourist Safety System
REM Usage: deploy.bat [local|docker]

set DEPLOYMENT_TYPE=%1
if "%DEPLOYMENT_TYPE%"=="" set DEPLOYMENT_TYPE=local

echo 🚀 Starting Tourist Safety System Deployment
echo Deployment type: %DEPLOYMENT_TYPE%

if "%DEPLOYMENT_TYPE%"=="local" (
    echo 📦 Installing dependencies...
    cd backend
    pip install -r requirements.txt
    
    echo 🗄️ Setting up database...
    python -c "from app import init_db; init_db()"
    
    echo 🌟 Starting local server...
    python app.py
    
) else if "%DEPLOYMENT_TYPE%"=="docker" (
    echo 🐳 Building Docker container...
    
    REM Build image
    docker build -t tourist-safety-system .
    
    REM Stop existing container
    docker stop tourist-safety-system 2>nul
    docker rm tourist-safety-system 2>nul
    
    REM Run new container
    docker run -d --name tourist-safety-system -p 5000:5000 -v "%cd%\data:/app/data" -e FLASK_ENV=production tourist-safety-system
    
    echo ✅ Docker container started!
    echo 🌐 Access at: http://localhost:5000
    
) else (
    echo ❌ Unknown deployment type: %DEPLOYMENT_TYPE%
    echo Usage: deploy.bat [local^|docker]
    exit /b 1
)

echo 🎉 Deployment complete!