#!/usr/bin/env python3
"""
🌟 TOURIST SAFETY SYSTEM - AUTO LAUNCHER 🌟
═══════════════════════════════════════════════════════════════
Automatically detects and launches the best hosting solution
for your platform and environment.
═══════════════════════════════════════════════════════════════
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def print_banner():
    """Display startup banner"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    TOURIST SAFETY SYSTEM                         ║
║                  🚀 AUTO LAUNCHER 🚀                           ║
║                                                                  ║
║  Automatically launching the best hosting solution...           ║
╚══════════════════════════════════════════════════════════════════╝
""")

def main():
    """Main launcher function"""
    print_banner()
    
    # Check if we're in the right directory
    if not Path('backend/app.py').exists():
        print("❌ Error: backend/app.py not found!")
        print("Please run this script from the tourist-safety-system directory")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Try to launch unified_host.py (best option)
    if Path('unified_host.py').exists():
        print("🎯 Launching Unified Host Manager (Python)...")
        try:
            subprocess.run([sys.executable, 'unified_host.py'])
            sys.exit(0)
        except Exception as e:
            print(f"⚠️ Failed to launch Python host: {e}")
    
    # Fall back to platform-specific scripts
    system = platform.system().lower()
    
    if system == "windows":
        # Try Windows batch file
        batch_files = ['UNIFIED_HOST.bat', 'host.bat']
        for batch_file in batch_files:
            if Path(batch_file).exists():
                print(f"🎯 Launching Windows Host ({batch_file})...")
                try:
                    subprocess.run([batch_file], shell=True)
                    sys.exit(0)
                except Exception as e:
                    print(f"⚠️ Failed to launch {batch_file}: {e}")
    
    elif system in ["linux", "darwin"]:  # Linux or macOS
        # Try shell script
        shell_files = ['UNIFIED_HOST.sh', 'host.sh']
        for shell_file in shell_files:
            shell_path = Path(shell_file)
            if shell_path.exists():
                print(f"🎯 Launching Shell Host ({shell_file})...")
                try:
                    # Make executable
                    os.chmod(shell_path, 0o755)
                    subprocess.run([f'./{shell_file}'])
                    sys.exit(0)
                except Exception as e:
                    print(f"⚠️ Failed to launch {shell_file}: {e}")
    
    # Last resort: direct Flask launch
    print("🚀 Last resort: Launching Flask directly...")
    try:
        os.chdir('backend')
        
        # Quick dependency install
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      capture_output=True)
        
        print("🌐 Starting server at http://localhost:5000")
        print("⚠️ Press Ctrl+C to stop")
        subprocess.run([sys.executable, 'app.py'])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("\nTry running manually:")
        print("  cd backend")
        print("  pip install -r requirements.txt")
        print("  python app.py")
        input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        input("Press Enter to exit...")