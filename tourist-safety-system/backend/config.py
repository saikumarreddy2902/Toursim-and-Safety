"""
Production configuration for Tourist Safety System
"""
import os
from datetime import timedelta
from typing import Dict, Type

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, use os.environ directly
    pass


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Database (Mongo-only)
    DATABASE_PATH = os.environ.get('DATABASE_URL') or 'mongodb://127.0.0.1:27017/tourist_safety'
    
    # API Keys
    GOOGLE_TRANSLATE_API_KEY = os.environ.get('GOOGLE_TRANSLATE_API_KEY') or 'AIzaSyCh7GaUtDEiux3CM9FRq93YD9jqDy1I3FM'
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    # Admin Configuration
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')  # Change in production
    
    # Session Configuration
    SESSION_COOKIE_SECURE = False  # Set to True only in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # CORS
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5000']


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Override with environment variables if available
    SECRET_KEY = os.environ.get('SECRET_KEY') or Config.SECRET_KEY
    
    # Security headers
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year
    
    # Database connection pooling
    DATABASE_POOL_SIZE = 20
    DATABASE_POOL_TIMEOUT = 30
    DATABASE_POOL_RECYCLE = 3600
    
    @classmethod
    def validate_production_config(cls):  # type: ignore
        """Validate production configuration when explicitly using production mode"""
        if not os.environ.get('SECRET_KEY'):
            raise ValueError("SECRET_KEY environment variable must be set in production")


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    DATABASE_PATH = 'mongodb://127.0.0.1:27017/tourist_safety_test'


# Configuration mapping
config: Dict[str, Type[Config]] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}