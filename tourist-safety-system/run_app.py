#!/usr/bin/env python3
"""
Simple runner for the Tourist Safety System
Ensures proper environment setup and keeps the app running
"""
import os
import sys
from pathlib import Path
import subprocess

# Get absolute paths
project_root = Path(__file__).parent.absolute()
backend_dir = project_root / 'backend'

def setup_environment():
    """Set up the environment variables"""
    os.environ['FLASK_ENV'] = 'development'
    os.environ['SECRET_KEY'] = 'dev-secret-change-me-in-production'
    os.environ['PYTHONPATH'] = str(backend_dir)

def run_flask_app():
    """Run the Flask app using subprocess for better control"""
    app_path = backend_dir / 'app.py'
    
    print(">>> Starting Tourist Safety System...")
    print(">>> Access at: http://127.0.0.1:5000")
    print(">>> Network access: http://192.168.0.26:5000")
    print(">>> Press Ctrl+C to stop")
    print(f">>> Running from: {app_path}")
    print("-" * 50)
    
    try:
        # Change to project root for proper relative paths
        os.chdir(project_root)
        
        # Run the Flask app
        subprocess.run([
            sys.executable, 
            str(app_path)
        ], check=True, cwd=str(project_root))
        
    except KeyboardInterrupt:
        print("\n>>> Tourist Safety System stopped")
    except subprocess.CalledProcessError as e:
        print(f"\n>>> ERROR: Error running Flask app: {e}")
        print("Try running manually with: python backend/app.py")
    except Exception as e:
        print(f"\n>>> ERROR: Unexpected error: {e}")

if __name__ == "__main__":
    setup_environment()
    run_flask_app()