#!/usr/bin/env python3
"""
TOURIST SAFETY SYSTEM - UNIFIED HOST MANAGER
🌟 ALL-IN-ONE HOSTING SOLUTION 🌟
Local • Docker • Production • Cloud • Monitoring • Management
"""

import os
import sys
import subprocess
import time
import json
import platform
import webbrowser
import signal
import threading
import socket
from pathlib import Path
from datetime import datetime

# Enhanced Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    END = '\033[0m'
    
    # Background colors
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'

def print_colored(text, color=Colors.WHITE):
    """Print colored text to terminal"""
    print(f"{color}{text}{Colors.END}")

def print_header(title, color=Colors.CYAN):
    """Print a formatted header"""
    print("\n" + "="*60)
    print_colored(f"🚀 {title}", color)
    print("="*60)

def check_requirements():
    """Check if Python and basic requirements are available"""
    print_header("System Requirements Check", Colors.BLUE)
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 7):
        print_colored(f"✅ Python {python_version.major}.{python_version.minor} - OK", Colors.GREEN)
    else:
        print_colored(f"❌ Python {python_version.major}.{python_version.minor} - Need 3.7+", Colors.RED)
        return False
    
    # Check if we're in the right directory
    if not Path('backend/app.py').exists():
        print_colored("❌ backend/app.py not found. Run from project root directory", Colors.RED)
        return False
    
    print_colored("✅ Project structure - OK", Colors.GREEN)
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Dependencies", Colors.YELLOW)
    
    requirements_file = Path('backend/requirements.txt')
    if not requirements_file.exists():
        print_colored("❌ requirements.txt not found", Colors.RED)
        return False
    
    try:
        print_colored("📦 Installing Python packages...", Colors.CYAN)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'], 
                      check=True, capture_output=True)
        print_colored("✅ Dependencies installed successfully", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Failed to install dependencies: {e}", Colors.RED)
        return False

def setup_database():
    """Initialize the database"""
    print_header("Database Setup", Colors.PURPLE)
    
    try:
        # Create data directory if it doesn't exist
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        # Initialize database by importing and calling init_db
        sys.path.insert(0, str(Path('backend').absolute()))
        
        print_colored("🗄️ Initializing database...", Colors.CYAN)
        from app import init_db
        init_db()
        print_colored("✅ Database initialized successfully", Colors.GREEN)
        return True
    except Exception as e:
        print_colored(f"❌ Database setup failed: {e}", Colors.RED)
        return False

def start_local_server():
    """Start the Flask development server"""
    print_header("Starting Local Development Server", Colors.GREEN)
    
    try:
        # Change to backend directory
        backend_path = Path('backend').absolute()
        app_path = backend_path / 'app.py'
        
        print_colored("🌟 Starting Flask server...", Colors.CYAN)
        print_colored("📱 Application will be available at:", Colors.YELLOW)
        print_colored("   🏠 Home: http://localhost:5000", Colors.WHITE)
        print_colored("   👨‍💼 Admin: http://localhost:5000/admin", Colors.WHITE)
        print_colored("   🔍 Health: http://localhost:5000/health", Colors.WHITE)
        print_colored("\n⚠️  Press Ctrl+C to stop the server", Colors.YELLOW)
        
        # Start the server
        subprocess.run([sys.executable, str(app_path)], cwd=str(backend_path))
        
    except KeyboardInterrupt:
        print_colored("\n🛑 Server stopped by user", Colors.YELLOW)
    except Exception as e:
        print_colored(f"❌ Failed to start server: {e}", Colors.RED)

def check_docker():
    """Check if Docker is available"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def start_docker_deployment():
    """Deploy using Docker"""
    print_header("Docker Deployment", Colors.BLUE)
    
    if not check_docker():
        print_colored("❌ Docker not found. Please install Docker Desktop", Colors.RED)
        print_colored("   Download from: https://www.docker.com/products/docker-desktop", Colors.CYAN)
        return False
    
    print_colored("✅ Docker is available", Colors.GREEN)
    
    try:
        # Build Docker image
        print_colored("🐳 Building Docker image...", Colors.CYAN)
        subprocess.run(['docker', 'build', '-t', 'tourist-safety-system', '.'], check=True)
        
        # Stop existing container if running
        print_colored("🛑 Stopping existing container...", Colors.YELLOW)
        subprocess.run(['docker', 'stop', 'tourist-safety-system'], 
                      capture_output=True, check=False)
        subprocess.run(['docker', 'rm', 'tourist-safety-system'], 
                      capture_output=True, check=False)
        
        # Start new container
        print_colored("🚀 Starting Docker container...", Colors.CYAN)
        data_volume = f"{Path.cwd().absolute()}/data:/app/data"
        
        subprocess.run([
            'docker', 'run', '-d',
            '--name', 'tourist-safety-system',
            '-p', '5000:5000',
            '-v', data_volume,
            '-e', 'FLASK_ENV=production',
            'tourist-safety-system'
        ], check=True)
        
        print_colored("✅ Docker container started successfully!", Colors.GREEN)
        print_colored("📱 Access at: http://localhost:5000", Colors.CYAN)
        print_colored("🐳 Container name: tourist-safety-system", Colors.WHITE)
        
        # Show Docker management commands
        print_colored("\n📋 Docker Management Commands:", Colors.YELLOW)
        print_colored("   Stop:    docker stop tourist-safety-system", Colors.WHITE)
        print_colored("   Restart: docker start tourist-safety-system", Colors.WHITE)
        print_colored("   Logs:    docker logs tourist-safety-system", Colors.WHITE)
        print_colored("   Remove:  docker rm -f tourist-safety-system", Colors.WHITE)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Docker deployment failed: {e}", Colors.RED)
        return False

def check_heroku():
    """Check if Heroku CLI is available"""
    try:
        result = subprocess.run(['heroku', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def deploy_to_heroku():
    """Deploy to Heroku"""
    print_header("Heroku Deployment", Colors.PURPLE)
    
    if not check_heroku():
        print_colored("❌ Heroku CLI not found", Colors.RED)
        print_colored("   Install from: https://devcenter.heroku.com/articles/heroku-cli", Colors.CYAN)
        return False
    
    print_colored("✅ Heroku CLI is available", Colors.GREEN)
    
    try:
        # Login to Heroku
        print_colored("🔑 Logging into Heroku...", Colors.CYAN)
        subprocess.run(['heroku', 'login'], check=True)
        
        # Create app name
        import random
        app_name = f"tourist-safety-{random.randint(1000, 9999)}"
        
        # Create Heroku app
        print_colored(f"🏗️ Creating Heroku app: {app_name}", Colors.CYAN)
        subprocess.run(['heroku', 'create', app_name], check=True)
        
        # Set environment variables
        print_colored("⚙️ Setting environment variables...", Colors.CYAN)
        subprocess.run(['heroku', 'config:set', 'FLASK_ENV=production'], check=True)
        
        # Generate secret key
        import secrets
        secret_key = secrets.token_hex(32)
        subprocess.run(['heroku', 'config:set', f'SECRET_KEY={secret_key}'], check=True)
        
        # Deploy
        print_colored("🚀 Deploying to Heroku...", Colors.CYAN)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', f'Deploy to Heroku - {time.strftime("%Y-%m-%d %H:%M")}'], 
                      check=False)  # Don't fail if nothing to commit
        subprocess.run(['git', 'push', 'heroku', 'main'], check=True)
        
        print_colored("✅ Deployed successfully to Heroku!", Colors.GREEN)
        print_colored(f"🌐 App URL: https://{app_name}.herokuapp.com", Colors.CYAN)
        
        # Open in browser
        webbrowser.open(f"https://{app_name}.herokuapp.com")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Heroku deployment failed: {e}", Colors.RED)
        return False

def production_server():
    """Start production server with Gunicorn"""
    print_header("Production Server Setup", Colors.RED)
    
    try:
        # Install gunicorn if not available
        print_colored("📦 Installing Gunicorn...", Colors.CYAN)
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'gunicorn'], check=True)
        
        # Start Gunicorn server
        print_colored("🏭 Starting production server with Gunicorn...", Colors.CYAN)
        backend_path = Path('backend').absolute()
        
        print_colored("📱 Production server will be available at:", Colors.YELLOW)
        print_colored("   🌐 http://0.0.0.0:5000", Colors.WHITE)
        print_colored("   🔒 Configure HTTPS and domain for production", Colors.YELLOW)
        
        subprocess.run([
            'gunicorn',
            '--bind', '0.0.0.0:5000',
            '--workers', '4',
            '--timeout', '120',
            '--keep-alive', '2',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            'wsgi:app'
        ], cwd=str(backend_path))
        
    except KeyboardInterrupt:
        print_colored("\n🛑 Production server stopped", Colors.YELLOW)
    except Exception as e:
        print_colored(f"❌ Production server failed: {e}", Colors.RED)

def show_status():
    """Show system status and URLs"""
    print_header("System Status", Colors.GREEN)
    
    # Check if local server is running
    try:
        import requests
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print_colored("✅ Local server is running", Colors.GREEN)
            print_colored(f"   Status: {health_data.get('status', 'unknown')}", Colors.WHITE)
            print_colored(f"   Environment: {health_data.get('environment', 'unknown')}", Colors.WHITE)
        else:
            print_colored("⚠️ Local server responding but unhealthy", Colors.YELLOW)
    except:
        print_colored("❌ Local server not running", Colors.RED)
    
    # Check Docker container
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=tourist-safety-system', '--format', 'table {{.Names}}\\t{{.Status}}'], 
                              capture_output=True, text=True, timeout=10)
        if 'tourist-safety-system' in result.stdout and 'Up' in result.stdout:
            print_colored("✅ Docker container is running", Colors.GREEN)
        else:
            print_colored("❌ Docker container not running", Colors.RED)
    except:
        print_colored("⚠️ Docker not available", Colors.YELLOW)
    
    # Show available URLs
    print_colored("\n🌐 Available URLs:", Colors.CYAN)
    print_colored("   🏠 Home: http://localhost:5000", Colors.WHITE)
    print_colored("   👨‍💼 Admin: http://localhost:5000/admin", Colors.WHITE)
    print_colored("   🔍 Health: http://localhost:5000/health", Colors.WHITE)
    print_colored("   📊 Reports: http://localhost:5000/admin (admin only)", Colors.WHITE)

def show_help():
    """Show help information"""
    print_header("Tourist Safety System - Host Manager", Colors.CYAN)
    print_colored("All-in-one hosting solution for the Tourist Safety System\n", Colors.WHITE)
    
    print_colored("📋 Available Commands:", Colors.YELLOW)
    print_colored("   1  - Quick Start (Local Development)", Colors.WHITE)
    print_colored("   2  - Docker Deployment", Colors.WHITE)
    print_colored("   3  - Heroku Cloud Deployment", Colors.WHITE)
    print_colored("   4  - Production Server (Gunicorn)", Colors.WHITE)
    print_colored("   5  - System Status", Colors.WHITE)
    print_colored("   6  - Install Dependencies Only", Colors.WHITE)
    print_colored("   7  - Database Setup Only", Colors.WHITE)
    print_colored("   8  - Open in Browser", Colors.WHITE)
    print_colored("   h  - Show this help", Colors.WHITE)
    print_colored("   q  - Quit", Colors.WHITE)
    
    print_colored("\n🎯 Recommended:", Colors.GREEN)
    print_colored("   • Development: Use option 1 (Quick Start)", Colors.WHITE)
    print_colored("   • Production: Use option 2 (Docker) or 4 (Gunicorn)", Colors.WHITE)
    print_colored("   • Cloud: Use option 3 (Heroku)", Colors.WHITE)

def open_browser():
    """Open the application in browser"""
    print_header("Opening Browser", Colors.CYAN)
    
    urls = [
        ("🏠 Home Page", "http://localhost:5000"),
        ("👨‍💼 Admin Dashboard", "http://localhost:5000/admin"),
        ("🔍 Health Check", "http://localhost:5000/health")
    ]
    
    for name, url in urls:
        try:
            webbrowser.open(url)
            print_colored(f"✅ Opened {name}: {url}", Colors.GREEN)
            time.sleep(1)  # Small delay between opening tabs
        except Exception as e:
            print_colored(f"❌ Failed to open {name}: {e}", Colors.RED)

def main():
    """Main application loop"""
    # Clear screen
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    print_colored("""
╔══════════════════════════════════════════════════════════════╗
║                 TOURIST SAFETY SYSTEM                        ║
║                   🚀 UNIFIED HOST MANAGER                    ║
║                                                              ║
║  🔒 SOS Alerts with Authentication                           ║
║  📊 Admin-Only Post-Incident Reports                        ║
║  🗺️ Real-time GPS & Geofencing                               ║
║  🤖 AI Monitoring & Analysis                                 ║
║  🌐 Multi-language Support                                   ║
║  🔗 Blockchain Security                                       ║
╚══════════════════════════════════════════════════════════════╝
    """, Colors.CYAN)
    
    # Check basic requirements
    if not check_requirements():
        print_colored("\n❌ Requirements check failed. Please fix the issues above.", Colors.RED)
        return 1
    
    while True:
        show_help()
        
        choice = input(f"\n{Colors.BOLD}Enter your choice: {Colors.END}").strip().lower()
        
        if choice == '1':
            if install_dependencies() and setup_database():
                start_local_server()
        elif choice == '2':
            if install_dependencies() and setup_database():
                start_docker_deployment()
        elif choice == '3':
            if install_dependencies() and setup_database():
                deploy_to_heroku()
        elif choice == '4':
            if install_dependencies() and setup_database():
                production_server()
        elif choice == '5':
            show_status()
        elif choice == '6':
            install_dependencies()
        elif choice == '7':
            setup_database()
        elif choice == '8':
            open_browser()
        elif choice == 'h':
            continue  # Show help again
        elif choice == 'q':
            print_colored("\n👋 Goodbye! Thanks for using Tourist Safety System!", Colors.GREEN)
            break
        else:
            print_colored(f"\n❌ Invalid choice: {choice}", Colors.RED)
        
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_colored("\n\n👋 Goodbye!", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        print_colored(f"\n❌ Unexpected error: {e}", Colors.RED)
        sys.exit(1)