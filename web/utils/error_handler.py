"""
Error handling utilities for Regex Intelligence Exchange.
"""

import traceback
import logging
from flask import jsonify, current_app, request
from werkzeug.exceptions import HTTPException

class ErrorHandler:
    """Centralized error handling for the web interface."""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger('regex_exchange')
    
    def handle_exception(self, e):
        """Handle exceptions and return appropriate responses."""
        # Log the exception
        self.logger.error(f"Exception occurred: {str(e)}")
        self.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Handle HTTP exceptions
        if isinstance(e, HTTPException):
            return jsonify({
                'error': e.description,
                'status_code': e.code
            }), e.code
        
        # Handle validation errors
        if hasattr(e, 'errors'):
            return jsonify({
                'error': 'Validation failed',
                'details': e.errors,
                'status_code': 400
            }), 400
        
        # Handle database errors
        if 'database' in str(e).lower() or 'sql' in str(e).lower():
            return jsonify({
                'error': 'Database error occurred',
                'status_code': 500
            }), 500
        
        # Handle general exceptions
        if current_app.config.get('DEBUG', False):
            # In debug mode, return full error details
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc(),
                'status_code': 500
            }), 500
        else:
            # In production, return generic error message
            return jsonify({
                'error': 'An internal server error occurred',
                'status_code': 500
            }), 500
    
    def handle_404(self, e):
        """Handle 404 errors."""
        self.logger.warning(f"404 error: {request.url}")
        return jsonify({
            'error': 'Resource not found',
            'status_code': 404
        }), 404
    
    def handle_500(self, e):
        """Handle 500 errors."""
        self.logger.error(f"500 error: {str(e)}")
        self.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Internal server error',
            'status_code': 500
        }), 500
    
    def log_api_error(self, endpoint, method, error, status_code):
        """Log API errors for monitoring."""
        self.logger.error(f"API Error: {method} {endpoint} - {status_code} - {str(error)}")
    
    def log_validation_error(self, endpoint, errors):
        """Log validation errors."""
        self.logger.warning(f"Validation Error on {endpoint}: {errors}")

def register_error_handlers(app):
    """Register error handlers with the Flask app."""
    error_handler = ErrorHandler()
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        return error_handler.handle_exception(e)
    
    @app.errorhandler(404)
    def handle_404(e):
        return error_handler.handle_404(e)
    
    @app.errorhandler(500)
    def handle_500(e):
        return error_handler.handle_500(e)

class ValidationError(Exception):
    """Custom validation error."""
    
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors or []

class PatternNotFoundError(Exception):
    """Custom error for when a pattern is not found."""
    
    def __init__(self, vendor_id, product_id):
        super().__init__(f"Pattern not found for vendor '{vendor_id}' and product '{product_id}'")
        self.vendor_id = vendor_id
        self.product_id = product_id

class SecurityError(Exception):
    """Custom error for security violations."""
    
    def __init__(self, message):
        super().__init__(message)

def validate_pattern_data(pattern_data):
    """Validate pattern data structure."""
    errors = []
    
    # Check required fields
    required_fields = ['vendor', 'vendor_id', 'product', 'product_id', 'category']
    for field in required_fields:
        if field not in pattern_data or not pattern_data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate pattern structure
    if 'all_versions' in pattern_data:
        if not isinstance(pattern_data['all_versions'], list):
            errors.append("all_versions must be a list")
        else:
            for i, pattern in enumerate(pattern_data['all_versions']):
                if not isinstance(pattern, dict):
                    errors.append(f"all_versions[{i}] must be a dictionary")
                elif 'pattern' not in pattern:
                    errors.append(f"all_versions[{i}] missing required 'pattern' field")
    
    if 'versions' in pattern_data:
        if not isinstance(pattern_data['versions'], dict):
            errors.append("versions must be a dictionary")
        else:
            for version, patterns in pattern_data['versions'].items():
                if not isinstance(patterns, list):
                    errors.append(f"versions['{version}'] must be a list")
                else:
                    for i, pattern in enumerate(patterns):
                        if not isinstance(pattern, dict):
                            errors.append(f"versions['{version}'][{i}] must be a dictionary")
                        elif 'pattern' not in pattern:
                            errors.append(f"versions['{version}'][{i}] missing required 'pattern' field")
    
    if errors:
        raise ValidationError("Pattern validation failed", errors)
    
    return True