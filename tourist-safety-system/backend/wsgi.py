"""
WSGI entry point for Tourist Safety System
For production deployment with Gunicorn, uWSGI, or similar
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set environment
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DB_BACKEND', 'mongo')
os.environ.setdefault('MONGO_URI', 'mongodb://127.0.0.1:27017')
os.environ.setdefault('MONGO_DB_NAME', 'tourist_safety')

from app import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))