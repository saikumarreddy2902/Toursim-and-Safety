#!/usr/bin/env python3
"""
🌟 TOURIST SAFETY SYSTEM - UNIFIED HOST MANAGER 🌟
═══════════════════════════════════════════════════════════════
ALL-IN-ONE HOSTING SOLUTION
✅ Local Development  ✅ Docker Deployment  ✅ Production Server
✅ Health Monitoring  ✅ System Management  ✅ Auto Setup
═══════════════════════════════════════════════════════════════
"""

import os
import sys
import subprocess
import time
import platform
import webbrowser
import signal
import threading
import socket
import json
from pathlib import Path
from datetime import datetime

class Colors:
    """Enhanced terminal colors for better user experience"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    # Emojis for better visual appeal
    SUCCESS = '✅'
    ERROR = '❌'
    WARNING = '⚠️'
    INFO = 'ℹ️'
    ROCKET = '🚀'
    DOCKER = '🐳'
    SERVER = '🌐'
    DATABASE = '🗄️'
    SECURITY = '🔒'
    MONITOR = '📊'

class UnifiedHostManager:
    """All-in-one hosting solution for Tourist Safety System"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.backend_path = self.project_root / 'backend'
        self.data_path = self.project_root / 'data'
        self.running_processes = []
        
    def print_colored(self, text: str, color: str = Colors.WHITE) -> None:
        """Print colored text to terminal"""
        print(f"{color}{text}{Colors.END}")
    
    def print_header(self, title: str, emoji: str = "🌟") -> None:
        """Print a beautiful formatted header"""
        width = 70
        border = "═" * width
        
        print(f"\n{Colors.CYAN}{border}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{emoji} {title.upper()} {emoji}{Colors.END}")
        print(f"{Colors.CYAN}{border}{Colors.END}\n")
    
    def print_logo(self) -> None:
        """Display the system logo"""
        logo = f"""
{Colors.BOLD}{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════╗
║                    TOURIST SAFETY SYSTEM                         ║
║                  🚀 UNIFIED HOST MANAGER 🚀                     ║
║                                                                  ║
║  {Colors.GREEN}✅ SOS Alerts with Authentication{Colors.CYAN}                      ║
║  {Colors.GREEN}✅ Admin-Only Post-Incident Reports{Colors.CYAN}                   ║
║  {Colors.GREEN}✅ Real-time GPS & Geofencing{Colors.CYAN}                         ║
║  {Colors.GREEN}✅ AI Monitoring & Analysis{Colors.CYAN}                           ║
║  {Colors.GREEN}✅ Multi-language Support{Colors.CYAN}                             ║
║  {Colors.GREEN}✅ Blockchain Security{Colors.CYAN}                                ║
║  {Colors.GREEN}✅ Docker & Production Ready{Colors.CYAN}                          ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.END}"""
        print(logo)
    
    def check_system_requirements(self) -> bool:
        """Comprehensive system requirements check"""
        self.print_header("System Requirements Check", "🔍")
        
        all_good = True
        
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 7):
            self.print_colored(f"{Colors.SUCCESS} Python {python_version.major}.{python_version.minor}.{python_version.micro} - Compatible", Colors.GREEN)
        else:
            self.print_colored(f"{Colors.ERROR} Python {python_version.major}.{python_version.minor} - Need 3.7+", Colors.RED)
            all_good = False
        
        # Check project structure
        required_files = [
            'backend/app.py',
            'backend/requirements.txt',
            'frontend/templates/index.html'
        ]
        
        for file_path in required_files:
            if (self.project_root / file_path).exists():
                self.print_colored(f"{Colors.SUCCESS} {file_path} - Found", Colors.GREEN)
            else:
                self.print_colored(f"{Colors.ERROR} {file_path} - Missing", Colors.RED)
                all_good = False
        
        # Check optional tools
        self.check_docker()
        self.check_git()
        
        return all_good
    
    def check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split()[2].rstrip(',')
                self.print_colored(f"{Colors.SUCCESS} Docker {version} - Available", Colors.GREEN)
                return True
        except FileNotFoundError:
            pass
        
        self.print_colored(f"{Colors.WARNING} Docker - Not installed (optional for Docker deployment)", Colors.YELLOW)
        return False
    
    def check_git(self) -> bool:
        """Check if Git is available"""
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split()[2]
                self.print_colored(f"{Colors.SUCCESS} Git {version} - Available", Colors.GREEN)
                return True
        except FileNotFoundError:
            pass
        
        self.print_colored(f"{Colors.WARNING} Git - Not installed (optional for version control)", Colors.YELLOW)
        return False
    
    def install_dependencies(self) -> bool:
        """Install all required dependencies"""
        self.print_header("Installing Dependencies", "📦")
        
        try:
            requirements_file = self.backend_path / 'requirements.txt'
            if not requirements_file.exists():
                self.print_colored(f"{Colors.ERROR} requirements.txt not found", Colors.RED)
                return False
            
            self.print_colored(f"{Colors.INFO} Installing Python packages...", Colors.CYAN)
            
            # Install main requirements
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_colored(f"{Colors.SUCCESS} Core dependencies installed", Colors.GREEN)
            else:
                self.print_colored(f"{Colors.ERROR} Failed to install dependencies: {result.stderr}", Colors.RED)
                return False
            
            # Install production packages
            production_packages = ['gunicorn', 'waitress', 'psutil']
            for package in production_packages:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.print_colored(f"{Colors.SUCCESS} {package} installed", Colors.GREEN)
                else:
                    self.print_colored(f"{Colors.WARNING} {package} installation failed (optional)", Colors.YELLOW)
            
            return True
            
        except Exception as e:
            self.print_colored(f"{Colors.ERROR} Installation failed: {e}", Colors.RED)
            return False
    
    def setup_database(self) -> bool:
        """Initialize the database"""
        self.print_header("Database Setup", "🗄️")
        
        try:
            # Create data directory
            self.data_path.mkdir(exist_ok=True)
            self.print_colored(f"{Colors.SUCCESS} Data directory created", Colors.GREEN)
            
            # Add backend to Python path
            sys.path.insert(0, str(self.backend_path))
            
            # Import and initialize database
            from app import init_db
            init_db()
            
            self.print_colored(f"{Colors.SUCCESS} Database initialized successfully", Colors.GREEN)
            return True
            
        except Exception as e:
            self.print_colored(f"{Colors.ERROR} Database setup failed: {e}", Colors.RED)
            self.print_colored(f"{Colors.INFO} You may need to run this from the project directory", Colors.CYAN)
            return False
    
    def start_local_server(self) -> None:
        """Start Flask development server"""
        self.print_header("Starting Local Development Server", "🚀")
        
        try:
            # Ensure we're using absolute paths
            backend_path = self.backend_path.resolve()
            app_path = backend_path / 'app.py'
            
            if not backend_path.exists():
                raise FileNotFoundError(f"Backend directory not found: {backend_path}")
            
            if not app_path.exists():
                raise FileNotFoundError(f"Flask app not found: {app_path}")
            
            self.print_colored(f"{Colors.INFO} Backend directory: {backend_path}", Colors.CYAN)
            self.print_colored(f"{Colors.INFO} Starting Flask server...", Colors.CYAN)
            self.print_colored(f"{Colors.INFO} Server will be available at:", Colors.CYAN)
            self.print_colored(f"   🏠 Home: http://localhost:5000", Colors.WHITE)
            self.print_colored(f"   👨‍💼 Admin: http://localhost:5000/admin", Colors.WHITE)
            self.print_colored(f"   🔍 Health: http://localhost:5000/health", Colors.WHITE)
            self.print_colored(f"\n{Colors.WARNING} Press Ctrl+C to stop the server{Colors.END}", Colors.YELLOW)
            
            # Start server using absolute path
            subprocess.run([sys.executable, str(app_path)], cwd=str(backend_path))
            
        except KeyboardInterrupt:
            self.print_colored(f"\n{Colors.INFO} Server stopped by user", Colors.CYAN)
        except Exception as e:
            self.print_colored(f"{Colors.ERROR} Server failed to start: {e}", Colors.RED)
            input("Press Enter to continue...")
    
    def start_docker_deployment(self) -> bool:
        """Deploy using Docker"""
        self.print_header("Docker Deployment", "🐳")
        
        if not self.check_docker():
            self.print_colored(f"{Colors.ERROR} Docker is required for this deployment method", Colors.RED)
            return False
        
        try:
            # Build Docker image
            self.print_colored(f"{Colors.INFO} Building Docker image...", Colors.CYAN)
            result = subprocess.run(['docker', 'build', '-t', 'tourist-safety-system', '.'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_colored(f"{Colors.SUCCESS} Docker image built successfully", Colors.GREEN)
            else:
                self.print_colored(f"{Colors.ERROR} Docker build failed: {result.stderr}", Colors.RED)
                return False
            
            # Stop existing container
            self.print_colored(f"{Colors.INFO} Stopping existing container (if any)...", Colors.CYAN)
            subprocess.run(['docker', 'stop', 'tourist-safety-system'], capture_output=True)
            subprocess.run(['docker', 'rm', 'tourist-safety-system'], capture_output=True)
            
            # Start new container
            self.print_colored(f"{Colors.INFO} Starting Docker container...", Colors.CYAN)
            result = subprocess.run([
                'docker', 'run', '-d', '--name', 'tourist-safety-system',
                '-p', '5000:5000', '-v', f"{self.data_path}:/app/data",
                '-e', 'FLASK_ENV=production', 'tourist-safety-system'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_colored(f"{Colors.SUCCESS} Docker container started successfully!", Colors.GREEN)
                self.print_colored(f"📱 Access your application at: http://localhost:5000", Colors.WHITE)
                self.print_colored(f"🐳 Container name: tourist-safety-system", Colors.WHITE)
                self.print_docker_commands()
                return True
            else:
                self.print_colored(f"{Colors.ERROR} Failed to start container: {result.stderr}", Colors.RED)
                return False
                
        except Exception as e:
            self.print_colored(f"{Colors.ERROR} Docker deployment failed: {e}", Colors.RED)
            return False
    
    def print_docker_commands(self) -> None:
        """Print useful Docker management commands"""
        self.print_colored(f"\n📋 Docker Management Commands:", Colors.CYAN)
        commands = [
            ("Stop container", "docker stop tourist-safety-system"),
            ("Start container", "docker start tourist-safety-system"),
            ("View logs", "docker logs tourist-safety-system"),
            ("Remove container", "docker rm -f tourist-safety-system"),
            ("Container status", "docker ps"),
        ]
        
        for desc, cmd in commands:
            self.print_colored(f"   {desc}: {cmd}", Colors.WHITE)
    
    def start_production_server(self) -> None:
        """Start production server with Waitress"""
        self.print_header("Production Server", "🏭")
        
        try:
            os.chdir(self.backend_path)
            
            # Install waitress if not available
            try:
                import waitress
            except ImportError:
                self.print_colored(f"{Colors.INFO} Installing production server (Waitress)...", Colors.CYAN)
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'waitress'], check=True)
                self.print_colored(f"{Colors.SUCCESS} Waitress installed", Colors.GREEN)
            
            self.print_colored(f"{Colors.INFO} Starting production server...", Colors.CYAN)
            self.print_colored(f"🌐 Production server: http://0.0.0.0:5000", Colors.WHITE)
            self.print_colored(f"🔒 Configure HTTPS and domain for production use", Colors.YELLOW)
            
            # Start production server
            from waitress import serve
            from app import app
            serve(app, host='0.0.0.0', port=5000)
            
        except KeyboardInterrupt:
            self.print_colored(f"\n{Colors.INFO} Production server stopped", Colors.CYAN)
        except Exception as e:
            self.print_colored(f"{Colors.ERROR} Production server failed: {e}", Colors.RED)
        finally:
            os.chdir(self.project_root)
    
    def check_server_health(self) -> None:
        """Check if server is running and healthy"""
        self.print_header("Health Check", "📊")
        
        try:
            import requests
            response = requests.get('http://localhost:5000/health', timeout=5)
            
            if response.status_code == 200:
                self.print_colored(f"{Colors.SUCCESS} Server is healthy! Response: {response.status_code}", Colors.GREEN)
                try:
                    health_data = response.json()
                    self.print_colored(f"📊 Health Details:", Colors.CYAN)
                    for key, value in health_data.items():
                        self.print_colored(f"   {key}: {value}", Colors.WHITE)
                except:
                    self.print_colored(f"📝 Response: {response.text}", Colors.WHITE)
            else:
                self.print_colored(f"{Colors.WARNING} Server responded with status: {response.status_code}", Colors.YELLOW)
                
        except ImportError:
            self.print_colored(f"{Colors.INFO} Installing requests for health check...", Colors.CYAN)
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'])
            self.check_server_health()
            
        except Exception as e:
            self.print_colored(f"{Colors.ERROR} Health check failed: {e}", Colors.RED)
            self.print_colored(f"{Colors.INFO} Server may not be running. Try starting it first.", Colors.CYAN)
    
    def open_browser(self) -> None:
        """Open application in browser"""
        self.print_header("Opening Browser", "🌐")
        
        urls = [
            ("🏠 Home Page", "http://localhost:5000"),
            ("👨‍💼 Admin Dashboard", "http://localhost:5000/admin"),
            ("🔍 Health Check", "http://localhost:5000/health"),
        ]
        
        for name, url in urls:
            try:
                webbrowser.open(url)
                self.print_colored(f"{Colors.SUCCESS} Opened {name}", Colors.GREEN)
                time.sleep(1)  # Delay between opening tabs
            except Exception as e:
                self.print_colored(f"{Colors.ERROR} Failed to open {name}: {e}", Colors.RED)
    
    def system_status(self) -> None:
        """Comprehensive system status check"""
        self.print_header("System Status Overview", "📊")
        
        # System info
        self.print_colored(f"🖥️  Operating System: {platform.system()} {platform.release()}", Colors.WHITE)
        self.print_colored(f"🐍 Python Version: {sys.version.split()[0]}", Colors.WHITE)
        self.print_colored(f"📁 Project Path: {self.project_root}", Colors.WHITE)
        
        # Check services
        self.print_colored(f"\n📋 Service Status:", Colors.CYAN)
        
        # Check if server is running
        try:
            import requests
            response = requests.get('http://localhost:5000/health', timeout=2)
            self.print_colored(f"{Colors.SUCCESS} Local Server: Running (Port 5000)", Colors.GREEN)
        except:
            self.print_colored(f"{Colors.ERROR} Local Server: Not Running", Colors.RED)
        
        # Check Docker container
        try:
            result = subprocess.run(['docker', 'ps', '--filter', 'name=tourist-safety-system', '--format', '{{.Status}}'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                self.print_colored(f"{Colors.SUCCESS} Docker Container: Running", Colors.GREEN)
            else:
                self.print_colored(f"{Colors.WARNING} Docker Container: Not Running", Colors.YELLOW)
        except:
            self.print_colored(f"{Colors.WARNING} Docker: Not Available", Colors.YELLOW)
        
        # Check database
        if (self.data_path / 'tourist_safety.db').exists():
            self.print_colored(f"{Colors.SUCCESS} Database: Initialized", Colors.GREEN)
        else:
            self.print_colored(f"{Colors.WARNING} Database: Not Found", Colors.YELLOW)
    
    def full_setup(self) -> bool:
        """Complete system setup"""
        self.print_header("Full System Setup", "🔧")
        
        steps = [
            ("Checking Requirements", self.check_system_requirements),
            ("Installing Dependencies", self.install_dependencies),
            ("Setting up Database", self.setup_database),
        ]
        
        for step_name, step_func in steps:
            self.print_colored(f"{Colors.INFO} {step_name}...", Colors.CYAN)
            if not step_func():
                self.print_colored(f"{Colors.ERROR} {step_name} failed", Colors.RED)
                return False
            self.print_colored(f"{Colors.SUCCESS} {step_name} completed", Colors.GREEN)
            print()
        
        self.print_colored(f"🎉 {Colors.BOLD}FULL SETUP COMPLETE!{Colors.END}", Colors.GREEN)
        self.print_colored(f"Your Tourist Safety System is ready to run!", Colors.WHITE)
        return True
    
    def show_help(self) -> None:
        """Display comprehensive help"""
        self.print_header("Help & Documentation", "❓")
        
        help_sections = [
            ("🎯 RECOMMENDED WORKFLOW", [
                "For Development:",
                "  1. Choose 'Full System Setup' (option 8) - one time only",
                "  2. Choose 'Quick Start' (option 1) - to run the server",
                "",
                "For Production:",
                "  1. Choose 'Full System Setup' (option 8) - one time only",
                "  2. Choose 'Docker Deployment' (option 2) or 'Production Server' (option 3)",
                "",
                "For Testing:",
                "  • 'System Status' (option 4) - check everything is working",
                "  • 'Health Check' (option 9) - test server health",
                "  • 'Open Browser' (option 7) - view the application"
            ]),
            
            ("🔧 TROUBLESHOOTING", [
                "If something doesn't work:",
                "  1. Run 'System Status' to diagnose issues",
                "  2. Run 'Install Dependencies' if packages are missing",
                "  3. Run 'Setup Database' if database issues",
                "  4. Check the terminal output for error messages"
            ]),
            
            ("🌐 ACCESS URLS", [
                "• Home: http://localhost:5000",
                "• Admin: http://localhost:5000/admin",
                "• Health: http://localhost:5000/health"
            ]),
            
            ("📚 FEATURES", [
                "• SOS Alerts with User Authentication",
                "• Admin-Only Post-Incident Reports",
                "• Real-time GPS Tracking & Geofencing",
                "• AI Monitoring & Threat Analysis",
                "• Multi-language Support",
                "• Blockchain Security Logging",
                "• Docker & Production Deployment"
            ])
        ]
        
        for title, items in help_sections:
            self.print_colored(f"\n{title}:", Colors.CYAN)
            for item in items:
                if item.strip():
                    self.print_colored(f"  {item}", Colors.WHITE)
                else:
                    print()
    
    def main_menu(self) -> None:
        """Display and handle the main menu"""
        while True:
            self.print_logo()
            
            menu_options = [
                ("🚀 Quick Start (Local Development)", "Start Flask development server"),
                ("🐳 Docker Deployment", "Deploy using Docker containers"),
                ("🏭 Production Server", "Start production server with Waitress"),
                ("📊 System Status", "Check overall system health"),
                ("📦 Install Dependencies", "Install all required packages"),
                ("🗄️  Setup Database", "Initialize database tables"),
                ("🌐 Open in Browser", "Open application in web browser"),
                ("🔧 Full System Setup", "Complete setup (recommended for first run)"),
                ("📋 Health Check", "Test server health endpoint"),
                ("❓ Help & Documentation", "Show detailed help"),
                ("🚪 Quit", "Exit the host manager")
            ]
            
            self.print_colored("╔══════════════════════════════════════════════════════════════════╗", Colors.CYAN)
            self.print_colored("║                        🌐 HOSTING OPTIONS                        ║", Colors.CYAN)
            self.print_colored("╚══════════════════════════════════════════════════════════════════╝", Colors.CYAN)
            print()
            
            for i, (option, description) in enumerate(menu_options, 1):
                if i <= 9:
                    self.print_colored(f"  {i}. {option}", Colors.WHITE)
                elif i == 10:
                    self.print_colored(f" {i}. {option}", Colors.WHITE)
                else:
                    self.print_colored(f"  Q. {option}", Colors.YELLOW)
            
            print("\n" + "═" * 70)
            
            try:
                choice = input(f"\n{Colors.BOLD}Enter your choice (1-10, Q): {Colors.END}").strip().lower()
                
                if choice == '1':
                    self.start_local_server()
                elif choice == '2':
                    self.start_docker_deployment()
                elif choice == '3':
                    self.start_production_server()
                elif choice == '4':
                    self.system_status()
                elif choice == '5':
                    self.install_dependencies()
                elif choice == '6':
                    self.setup_database()
                elif choice == '7':
                    self.open_browser()
                elif choice == '8':
                    self.full_setup()
                elif choice == '9':
                    self.check_server_health()
                elif choice == '10':
                    self.show_help()
                elif choice in ['q', 'quit']:
                    break
                else:
                    self.print_colored(f"{Colors.ERROR} Invalid choice. Please enter 1-10 or Q.", Colors.RED)
                
                if choice != 'q' and choice != 'quit':
                    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
                    
            except KeyboardInterrupt:
                self.print_colored(f"\n\n{Colors.INFO} Goodbye! 👋", Colors.CYAN)
                break
            except Exception as e:
                self.print_colored(f"{Colors.ERROR} An error occurred: {e}", Colors.RED)
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

if __name__ == "__main__":
    try:
        manager = UnifiedHostManager()
        manager.main_menu()
    except KeyboardInterrupt:
        print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Fatal error: {e}{Colors.END}")
        sys.exit(1)