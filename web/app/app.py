#!/usr/bin/env python3
"""
Web interface for Regex Intelligence Exchange
"""

import os
import sys
from flask import Flask
from utils.error_handler import register_error_handlers
from config import config

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def create_app(config_name='development'):
    """Application factory function."""
    
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))
    
    # Load configuration
    if config_name in config:
        app.config.from_object(config[config_name])
    else:
        app.config.from_object(config['development'])
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app

if __name__ == '__main__':
    # Get environment from command line or environment variable
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env)
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'] if 'HOST' in app.config else '0.0.0.0',
        port=app.config['PORT'] if 'PORT' in app.config else 5000
    )