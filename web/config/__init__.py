"""
Configuration package for the Regex Intelligence Exchange web interface.
"""

from .development import DevelopmentConfig
from .staging import StagingConfig
from .production import ProductionConfig

config = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig
}