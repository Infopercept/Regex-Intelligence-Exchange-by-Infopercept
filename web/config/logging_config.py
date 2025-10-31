"""
Logging configuration for Regex Intelligence Exchange.
"""

import logging
import logging.config
import os

def setup_logging(log_level='INFO', log_file='app.log'):
    """Set up logging configuration."""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Full path to log file
    log_file_path = os.path.join(log_dir, log_file)
    
    # Logging configuration
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            }
        },
        'handlers': {
            'default': {
                'level': log_level,
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': log_level,
                'formatter': 'detailed',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_file_path,
                'maxBytes': 10*1024*1024,  # 10MB
                'backupCount': 5,
            },
            'error_file': {
                'level': 'ERROR',
                'formatter': 'detailed',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'error.log'),
                'maxBytes': 10*1024*1024,  # 10MB
                'backupCount': 5,
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['default', 'file', 'error_file'],
                'level': log_level,
                'propagate': False
            },
            'regex_exchange': {
                'handlers': ['default', 'file', 'error_file'],
                'level': log_level,
                'propagate': False
            },
            'werkzeug': {
                'handlers': ['default', 'file'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)

def get_logger(name='regex_exchange'):
    """Get a logger instance."""
    return logging.getLogger(name)

# Set up logging when module is imported
setup_logging()