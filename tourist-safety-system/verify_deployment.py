#!/usr/bin/env python3
"""
Tourist Safety System - Hosting Verification Script
Checks if the system is ready for deployment and verifies all components
"""

import os
import sys
import requests
import subprocess
import time
from pathlib import Path

def print_header(title):
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def check_mark(condition, message):
    if condition:
        print(f"✅ {message}")
        return True
    else:
        print(f"❌ {message}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print_header("Checking Dependencies")
    
    required_packages = [
        'flask', 'werkzeug', 'requests', 'cryptography', 
        'python-dateutil', 'geopy'
    ]
    
    all_good = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            check_mark(True, f"{package} is installed")
        except ImportError:
            check_mark(False, f"{package} is missing")
            all_good = False
    
    return all_good

def check_project_structure():
    """Verify project structure is correct"""
    print_header("Checking Project Structure")
    
    required_files = [
        'backend/app.py',
        'backend/requirements.txt',
        'backend/wsgi.py',
        'frontend/templates/index.html',
        'frontend/templates/admin_dashboard.html',
        'Dockerfile',
        'docker-compose.yml',
        'Procfile',
        'DEPLOYMENT_README.md'
    ]
    
    all_good = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        check_mark(exists, f"{file_path} exists")
        if not exists:
            all_good = False
    
    return all_good

def check_environment_config():
    """Check environment configuration"""
    print_header("Checking Environment Configuration")
    
    # Check if .env.example exists
    env_example_exists = Path('.env.example').exists()
    check_mark(env_example_exists, ".env.example template exists")
    
    # Check for sensitive defaults
    app_py_path = Path('backend/app.py')
    if app_py_path.exists():
        try:
            content = app_py_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Try with different encoding
            content = app_py_path.read_text(encoding='latin-1')
        
        secure_config = True
        
        if 'debug=True' in content and 'FLASK_ENV' not in content:
            check_mark(False, "Debug mode should be configurable via environment")
            secure_config = False
        else:
            check_mark(True, "Debug mode is configurable")
        
        if 'host=\'0.0.0.0\'' in content or 'host="0.0.0.0"' in content:
            check_mark(True, "App configured to bind to all interfaces")
        else:
            check_mark(False, "App should bind to 0.0.0.0 for deployment")
            secure_config = False
    
    return env_example_exists and secure_config

def test_local_deployment():
    """Test local deployment"""
    print_header("Testing Local Deployment")
    
    # Start the Flask app in background
    print("🚀 Starting Flask server...")
    
    try:
        # Change to backend directory
        os.chdir('backend')
        
        # Start server process
        process = subprocess.Popen([
            sys.executable, 'app.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(5)
        
        # Test health endpoint
        try:
            response = requests.get('http://localhost:5000/health', timeout=10)
            health_check = response.status_code == 200
            check_mark(health_check, "Health endpoint responds correctly")
            
            if health_check:
                health_data = response.json()
                check_mark(health_data.get('status') == 'healthy', "System reports healthy status")
        except requests.exceptions.RequestException:
            check_mark(False, "Cannot connect to local server")
            health_check = False
        
        # Test main page
        try:
            response = requests.get('http://localhost:5000/', timeout=10)
            main_page = response.status_code == 200
            check_mark(main_page, "Main page loads successfully")
        except requests.exceptions.RequestException:
            check_mark(False, "Main page cannot be accessed")
            main_page = False
        
        # Test admin dashboard
        try:
            response = requests.get('http://localhost:5000/admin', timeout=10)
            admin_page = response.status_code == 200
            check_mark(admin_page, "Admin dashboard loads successfully")
        except requests.exceptions.RequestException:
            check_mark(False, "Admin dashboard cannot be accessed")
            admin_page = False
        
        # Stop the server
        process.terminate()
        process.wait(timeout=5)
        
        # Change back to original directory
        os.chdir('..')
        
        return health_check and main_page and admin_page
        
    except Exception as e:
        print(f"❌ Error during local testing: {e}")
        try:
            process.terminate()
            os.chdir('..')
        except:
            pass
        return False

def check_docker_setup():
    """Check Docker configuration"""
    print_header("Checking Docker Setup")
    
    # Check if Docker is installed
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        docker_installed = result.returncode == 0
        check_mark(docker_installed, f"Docker is installed: {result.stdout.strip()}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        docker_installed = False
        check_mark(False, "Docker is not installed or not in PATH")
    
    # Check Dockerfile
    dockerfile_exists = Path('Dockerfile').exists()
    check_mark(dockerfile_exists, "Dockerfile exists")
    
    # Check docker-compose.yml
    compose_exists = Path('docker-compose.yml').exists()
    check_mark(compose_exists, "docker-compose.yml exists")
    
    return docker_installed and dockerfile_exists and compose_exists

def generate_deployment_report():
    """Generate final deployment readiness report"""
    print_header("Deployment Readiness Report")
    
    # Run all checks
    deps_ok = check_dependencies()
    structure_ok = check_project_structure()
    config_ok = check_environment_config()
    local_test_ok = test_local_deployment()
    docker_ok = check_docker_setup()
    
    # Calculate overall score
    checks = [deps_ok, structure_ok, config_ok, local_test_ok, docker_ok]
    passed = sum(checks)
    total = len(checks)
    score = (passed / total) * 100
    
    print(f"\n🎯 Overall Readiness Score: {score:.1f}% ({passed}/{total} checks passed)")
    
    if score >= 90:
        print("🎉 EXCELLENT! Your project is ready for production deployment.")
        deployment_recommendation = "ready"
    elif score >= 70:
        print("👍 GOOD! Your project is mostly ready. Fix the failing checks.")
        deployment_recommendation = "mostly_ready"
    elif score >= 50:
        print("⚠️ NEEDS WORK! Several issues need to be addressed.")
        deployment_recommendation = "needs_work"
    else:
        print("🚨 NOT READY! Major issues need to be fixed first.")
        deployment_recommendation = "not_ready"
    
    # Deployment recommendations
    print("\n📋 Next Steps:")
    if deployment_recommendation == "ready":
        print("✅ You can deploy using any of these methods:")
        print("   • Local: ./deploy.bat local")
        print("   • Docker: docker-compose up -d")
        print("   • Heroku: git push heroku main")
        print("   • Cloud: Follow DEPLOYMENT_README.md")
    elif deployment_recommendation == "mostly_ready":
        print("🔧 Fix the failing checks, then you're ready to deploy!")
    else:
        print("🛠️ Address the issues above before deployment")
        print("💡 Run this script again after making fixes")
    
    return score >= 70

def main():
    print("🚀 Tourist Safety System - Deployment Verification")
    print("This script will verify your project is ready for hosting")
    
    # Check if we're in the right directory
    if not Path('backend/app.py').exists():
        print("❌ Please run this script from the tourist-safety-system root directory")
        sys.exit(1)
    
    # Run verification
    ready = generate_deployment_report()
    
    print("\n" + "="*60)
    if ready:
        print("🎉 CONGRATULATIONS! Your Tourist Safety System is ready for deployment!")
    else:
        print("🔧 Please fix the issues above and run the verification again.")
    print("="*60)
    
    return 0 if ready else 1

if __name__ == "__main__":
    sys.exit(main())