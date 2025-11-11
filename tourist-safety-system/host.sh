#!/bin/bash

# TOURIST SAFETY SYSTEM - UNIFIED HOST (Linux/Mac)
# All-in-one hosting solution

clear

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                 TOURIST SAFETY SYSTEM                        ║"
echo "║                   🚀 UNIFIED HOST MANAGER                    ║"
echo "║                                                              ║"
echo "║  🔒 SOS Alerts with Authentication                           ║"
echo "║  📊 Admin-Only Post-Incident Reports                        ║"
echo "║  🗺️ Real-time GPS & Geofencing                               ║"
echo "║  🤖 AI Monitoring & Analysis                                 ║"
echo "║  🌐 Multi-language Support                                   ║"
echo "║  🔗 Blockchain Security                                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python is not installed"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "✅ Python is installed"
echo "🚀 Starting Unified Host Manager..."
echo

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    echo "❌ backend/app.py not found. Please run from project root directory"
    exit 1
fi

# Try to run the Python unified host manager
$PYTHON_CMD host.py

# If Python host manager fails, show manual options
if [ $? -ne 0 ]; then
    echo
    echo "⚠️ Python host manager failed. Showing manual options..."
    echo
    
    echo "📱 Manual Setup Options:"
    echo
    echo "1. Quick Local Start:"
    echo "   cd backend && $PYTHON_CMD app.py"
    echo
    echo "2. Docker Start:"
    echo "   docker-compose up -d"
    echo
    echo "3. Install Dependencies:"
    echo "   $PYTHON_CMD -m pip install -r backend/requirements.txt"
    echo
    
    read -p "Try manual local setup? (y/n): " choice
    if [[ $choice =~ ^[Yy]$ ]]; then
        echo
        echo "🚀 Starting manual local server..."
        cd backend
        $PYTHON_CMD -m pip install -r requirements.txt
        $PYTHON_CMD app.py
    fi
fi

echo
echo "📞 Need Help?"
echo "📖 Read DEPLOYMENT_README.md for detailed instructions"
echo "🔍 Check logs/app.log for troubleshooting"
echo "🌐 Visit http://localhost:5000/health for system status"