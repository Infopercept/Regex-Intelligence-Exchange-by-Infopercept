"""
Enhanced error handling for Regex Intelligence Exchange.
"""

import logging
import traceback
from typing import Dict, Any, Tuple
from flask import Flask, request, jsonify, render_template
from werkzeug.exceptions import HTTPException

# Simplified error handling - no database or cache dependencies

logger = logging.getLogger(__name__)

def register_error_handlers(app: Flask):
    """Register comprehensive error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad request errors."""
        logger.warning(f"Bad request: {error.description}", extra={
            'url': request.url,
            'method': request.method,
            'ip': request.remote_addr
        })
        
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Bad Request',
                'message': error.description or 'Invalid request parameters',
                'status_code': 400
            }), 400
        
        return render_template('errors/400.html', error=error), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle unauthorized errors."""
        logger.warning(f"Unauthorized access: {error.description}", extra={
            'url': request.url,
            'method': request.method,
            'ip': request.remote_addr
        })
        
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Unauthorized',
                'message': error.description or 'Authentication required',
                'status_code': 401
            }), 401
        
        return render_template('errors/401.html', error=error), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle forbidden errors."""
        logger.warning(f"Forbidden access: {error.description}", extra={
            'url': request.url,
            'method': request.method,
            'ip': request.remote_addr
        })
        
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Forbidden',
                'message': error.description or 'Access denied',
                'status_code': 403
            }), 403
        
        return render_template('errors/403.html', error=error), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle not found errors."""
        logger.info(f"Resource not found: {request.url}", extra={
            'url': request.url,
            'method': request.method,
            'ip': request.remote_addr
        })
        
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested resource was not found',
                'status_code': 404
            }), 404
        
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle rate limit errors."""
        logger.warning(f"Rate limit exceeded: {error.description}", extra={
            'url': request.url,
            'method': request.method,
            'ip': request.remote_addr
        })
        
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Rate Limit Exceeded',
                'message': 'Too many requests. Please try again later.',
                'status_code': 429,
                'retry_after': getattr(error, 'retry_after', 60)
            }), 429
        
        return render_template('errors/429.html', error=error), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle internal server errors."""
        logger.error(f"Internal server error: {str(error)}", extra={
            'url': request.url,
            'method': request.method,
            'ip': request.remote_addr,
            'traceback': traceback.format_exc()
        })
        
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred',
                'status_code': 500
            }), 500
        
        return render_template('errors/500.html'), 500
    
    # Database and cache error handlers removed for simplicity
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle unexpected errors."""
        logger.error(f"Unexpected error: {str(error)}", extra={
            'url': request.url,
            'method': request.method,
            'ip': request.remote_addr,
            'error_type': type(error).__name__,
            'traceback': traceback.format_exc()
        })
        
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Unexpected Error',
                'message': 'An unexpected error occurred',
                'status_code': 500
            }), 500
        
        return render_template('errors/500.html'), 500

class ErrorLogger:
    """Enhanced error logging with structured logging."""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize error logger with Flask app."""
        self.app = app
        
        # Configure structured logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add request context to logs
        @app.before_request
        def log_request_info():
            logger.info('Request started', extra={
                'url': request.url,
                'method': request.method,
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')
            })
        
        @app.after_request
        def log_response_info(response):
            logger.info('Request completed', extra={
                'url': request.url,
                'method': request.method,
                'status_code': response.status_code,
                'ip': request.remote_addr
            })
            return response
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events with structured data."""
        logger.warning(f"Security event: {event_type}", extra={
            'event_type': event_type,
            'details': details,
            'url': request.url if request else None,
            'method': request.method if request else None,
            'ip': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent', '') if request else None
        })
    
    def log_performance_issue(self, operation: str, duration: float, threshold: float = 1.0):
        """Log performance issues."""
        if duration > threshold:
            logger.warning(f"Performance issue: {operation}", extra={
                'operation': operation,
                'duration': duration,
                'threshold': threshold,
                'url': request.url if request else None
            })
    
    def log_api_usage(self, endpoint: str, method: str, response_time: float, status_code: int):
        """Log API usage statistics."""
        logger.info(f"API usage: {method} {endpoint}", extra={
            'endpoint': endpoint,
            'method': method,
            'response_time': response_time,
            'status_code': status_code,
            'ip': request.remote_addr if request else None
        })

# Global error logger instance
error_logger = ErrorLogger()