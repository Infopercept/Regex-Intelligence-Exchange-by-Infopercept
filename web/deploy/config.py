"""
Deployment configuration for Regex Intelligence Exchange.
"""

import os
from typing import Dict, Any

class DeploymentConfig:
    """Configuration for deployment environments."""
    
    def __init__(self):
        self.environments = {
            'development': {
                'debug': True,
                'host': '127.0.0.1',
                'port': 5000,
                'api_port': 5001,
                'log_level': 'DEBUG',
                'require_https': False,
                'redis_host': 'localhost',
                'redis_port': 6379,
                'redis_db': 0
            },
            'staging': {
                'debug': False,
                'host': '0.0.0.0',
                'port': 8080,
                'api_port': 8081,
                'log_level': 'INFO',
                'require_https': True,
                'redis_host': 'localhost',
                'redis_port': 6379,
                'redis_db': 1
            },
            'production': {
                'debug': False,
                'host': '0.0.0.0',
                'port': 80,
                'api_port': 81,
                'log_level': 'WARNING',
                'require_https': True,
                'redis_host': 'localhost',
                'redis_port': 6379,
                'redis_db': 2
            }
        }
    
    def get_config(self, environment: str = 'development') -> Dict[str, Any]:
        """Get configuration for specified environment."""
        return self.environments.get(environment, self.environments['development'])
    
    def load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {
            'debug': os.getenv('DEBUG', 'False').lower() == 'true',
            'host': os.getenv('HOST', '127.0.0.1'),
            'port': int(os.getenv('PORT', 5000)),
            'api_port': int(os.getenv('API_PORT', 5001)),
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'require_https': os.getenv('REQUIRE_HTTPS', 'False').lower() == 'true',
            'redis_host': os.getenv('REDIS_HOST', 'localhost'),
            'redis_port': int(os.getenv('REDIS_PORT', 6379)),
            'redis_db': int(os.getenv('REDIS_DB', 0))
        }
        return config

# Global deployment config
deploy_config = DeploymentConfig()