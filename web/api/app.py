#!/usr/bin/env python3
"""
RESTful API for Regex Intelligence Exchange
"""

import os
import sys
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from utils.error_handler import register_error_handlers
from config import config

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def create_app(config_name='development'):
    """Application factory function."""
    
    app = Flask(__name__)
    
    # Load configuration
    if config_name in config:
        app.config.from_object(config[config_name])
    else:
        app.config.from_object(config['development'])
    
    # Enable CORS
    CORS(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Initialize API
    api = Api(
        app,
        title=app.config['API_TITLE'],
        version=app.config['API_VERSION'],
        description='RESTful API for Regex Intelligence Exchange',
        doc='/api/docs/'
    )
    
    # Register API namespaces
    from api.v1 import routes
    api.add_namespace(routes.api, path='/api/v1')
    
    return app

if __name__ == '__main__':
    # Get environment from command line or environment variable
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env)
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'] if 'HOST' in app.config else '0.0.0.0',
        port=app.config['API_PORT'] if 'API_PORT' in app.config else 5001
    )