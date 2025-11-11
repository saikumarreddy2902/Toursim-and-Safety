#!/bin/bash

# ============================================================================
#                      TOURIST SAFETY SYSTEM
#                      UNIFIED HOST MANAGER
#                  🌟 ALL-IN-ONE SOLUTION 🌟
# ============================================================================

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

clear

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    TOURIST SAFETY SYSTEM                         ║"
echo "║                  🚀 UNIFIED HOST MANAGER 🚀                     ║"
echo "║                                                                  ║"
echo "║  For the BEST experience, use: python3 unified_host.py          ║"
echo "║  This script provides basic functionality only                   ║"
echo "║                                                                  ║"
echo "║  ✅ SOS Alerts with Authentication                               ║"
echo "║  ✅ Admin-Only Post-Incident Reports                            ║"
echo "║  ✅ Real-time GPS & Geofencing                                   ║"
echo "║  ✅ AI Monitoring & Analysis                                     ║"
echo "║  ✅ Multi-language Support                                       ║"
echo "║  ✅ Blockchain Security                                           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if unified host exists and recommend it
if [ -f "unified_host.py" ]; then
    echo -e "${YELLOW}🌟 RECOMMENDED: Use the full-featured Python host manager${NC}"
    echo -e "   Command: python3 unified_host.py"
    echo
    read -p "Would you like to launch the Python host manager now? (y/N): " use_python
    if [[ $use_python =~ ^[Yy]$ ]]; then
        python3 unified_host.py
        exit 0
    fi
    echo
    echo -e "${CYAN}Continuing with basic shell script...${NC}"
    echo
fi

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    echo -e "${RED}❌ Error: backend/app.py not found!${NC}"
    echo "Please run this script from the tourist-safety-system directory"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}❌ Python is not installed or not in PATH${NC}"
        echo "Please install Python 3.7+ from https://python.org"
        echo
        read -p "Press Enter to exit..."
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo -e "${GREEN}✅ Python is installed${NC}"
echo -e "${GREEN}✅ Project structure verified${NC}"
echo

show_menu() {
    echo "════════════════════════════════════════════════════════════════"
    echo "                      🌐 BASIC HOSTING OPTIONS"
    echo "════════════════════════════════════════════════════════════════"
    echo
    echo "  1. 🚀 Quick Start (Local Server)"
    echo "  2. 📦 Install Dependencies"
    echo "  3. 🗄️  Setup Database"
    echo "  4. 🌐 Open Browser"
    echo "  5. 📊 Basic Status Check"
    echo "  U. 🌟 Launch Unified Host Manager (RECOMMENDED)"
    echo "  Q. 🚪 Quit"
    echo
    echo "════════════════════════════════════════════════════════════════"
    echo
}

quick_start() {
    echo
    echo -e "${CYAN}🚀 Starting Local Development Server...${NC}"
    cd backend
    $PYTHON_CMD -m pip install -r requirements.txt > /dev/null 2>&1
    $PYTHON_CMD app.py
    cd ..
    read -p "Press Enter to continue..."
}

install_deps() {
    echo
    echo -e "${CYAN}📦 Installing Dependencies...${NC}"
    cd backend
    $PYTHON_CMD -m pip install -r requirements.txt
    cd ..
    echo -e "${GREEN}✅ Dependencies installed${NC}"
    read -p "Press Enter to continue..."
}

setup_db() {
    echo
    echo -e "${CYAN}🗄️ Setting up Database...${NC}"
    cd backend
    $PYTHON_CMD -c "from app import init_db; init_db()"
    cd ..
    echo -e "${GREEN}✅ Database setup complete${NC}"
    read -p "Press Enter to continue..."
}

open_browser() {
    echo
    echo -e "${CYAN}🌐 Opening Browser...${NC}"
    
    # Try different browsers based on OS
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:5000 > /dev/null 2>&1
        xdg-open http://localhost:5000/admin > /dev/null 2>&1
    elif command -v open &> /dev/null; then
        open http://localhost:5000 > /dev/null 2>&1
        open http://localhost:5000/admin > /dev/null 2>&1
    else
        echo "Please manually open: http://localhost:5000"
    fi
    
    echo -e "${GREEN}✅ Browser opened${NC}"
    read -p "Press Enter to continue..."
}

status_check() {
    echo
    echo -e "${CYAN}📊 Basic Status Check...${NC}"
    echo -e "${GREEN}✅ Python Version:${NC}"
    $PYTHON_CMD --version
    echo
    
    if [ -f "backend/app.py" ]; then
        echo -e "${GREEN}✅ Backend found${NC}"
    else
        echo -e "${RED}❌ Backend missing${NC}"
    fi
    
    if [ -f "data/tourist_safety.db" ]; then
        echo -e "${GREEN}✅ Database found${NC}"
    else
        echo -e "${RED}❌ Database not found${NC}"
    fi
    
    read -p "Press Enter to continue..."
}

unified_host() {
    echo
    echo -e "${CYAN}🌟 Launching Unified Host Manager...${NC}"
    $PYTHON_CMD unified_host.py
}

# Main menu loop
while true; do
    show_menu
    read -p "Enter your choice: " choice
    
    case $choice in
        1)
            quick_start
            ;;
        2)
            install_deps
            ;;
        3)
            setup_db
            ;;
        4)
            open_browser
            ;;
        5)
            status_check
            ;;
        [Uu])
            unified_host
            ;;
        [Qq])
            echo
            echo -e "${CYAN}👋 Goodbye!${NC}"
            echo
            echo -e "📱 If your server is running, access it at: ${WHITE}http://localhost:5000${NC}"
            echo -e "🛑 Press Ctrl+C to stop the server if it's running"
            echo
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Invalid choice.${NC}"
            read -p "Press Enter to continue..."
            ;;
    esac
done