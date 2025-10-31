"""
Staging configuration settings.
"""

import os

class StagingConfig:
    """Staging configuration class."""
    
    # Flask settings
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'staging-secret-key-change-in-production'
    
    # Database settings (if applicable)
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///staging.db'
    
    # API settings
    API_TITLE = "Regex Intelligence Exchange API - Staging"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    
    # Pattern database settings
    PATTERNS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'patterns')
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    # Security settings
    WTF_CSRF_ENABLED = True
    REQUIRE_HTTPS = os.environ.get('REQUIRE_HTTPS', 'True').lower() == 'true'
    
    # Redis settings
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(os.environ.get('REDIS_PORT') or 6379)
    REDIS_DB = int(os.environ.get('REDIS_DB') or 1)
    
    # Performance settings
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT') or 300)
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 16 * 1024 * 1024)  # 16MB