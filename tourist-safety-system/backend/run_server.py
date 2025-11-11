#!/usr/bin/env python3
"""
Simple launcher for Tourist Safety System
"""
import os
import sys

# Set environment variables for production
os.environ['FLASK_CONFIG'] = 'production'
os.environ['SECRET_KEY'] = 'TouristSafety2025SecureKey'
# Default to MongoDB backend if not explicitly set
os.environ.setdefault('DB_BACKEND', 'mongo')
os.environ.setdefault('MONGO_DB_NAME', 'tourist_safety')
os.environ.setdefault('MONGO_URI', 'mongodb://127.0.0.1:27017')

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Import and run the Flask app
if __name__ == "__main__":
    try:
        from app import app
        print("🚀 Starting Tourist Safety System...")
        print("📍 Server will be available at: http://127.0.0.1:5000")
        print("🔒 Environment: production")
        print("🌐 Language support: Multi-language enabled")
        print("💾 Database: MongoDB")
        print("\n✨ System Features:")
        print("   • Tourist Registration & Digital ID")
        print("   • Real-time Location Tracking")
        print("   • Emergency SOS System") 
        print("   • Admin Dashboard")
        print("   • Multi-language Support")
        print("   • Geofencing & Safety Zones")
        print("\n⚡ Press Ctrl+C to stop the server")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=5000, debug=False)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)