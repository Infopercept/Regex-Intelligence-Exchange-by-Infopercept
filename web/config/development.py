"""
Development configuration settings.
"""

import os

class DevelopmentConfig:
    """Development configuration class."""
    
    # Flask settings
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # Database settings (if applicable)
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///dev.db'
    
    # API settings
    API_TITLE = "Regex Intelligence Exchange API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    
    # Pattern database settings
    PATTERNS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'patterns')
    
    # Logging settings
    LOG_LEVEL = 'DEBUG'
    
    # Security settings
    WTF_CSRF_ENABLED = True