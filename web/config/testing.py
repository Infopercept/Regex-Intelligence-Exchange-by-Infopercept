"""
Testing configuration settings.
"""

import os

class TestingConfig:
    """Testing configuration class."""
    
    # Flask settings
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    
    # Database settings (if applicable)
    DATABASE_URL = 'sqlite:///:memory:'
    
    # API settings
    API_TITLE = "Regex Intelligence Exchange API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    
    # Pattern database settings
    PATTERNS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'patterns')
    
    # Logging settings
    LOG_LEVEL = 'DEBUG'
    
    # Security settings
    WTF_CSRF_ENABLED = False