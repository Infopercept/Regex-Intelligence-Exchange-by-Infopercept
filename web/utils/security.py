"""
Security utilities for Regex Intelligence Exchange.
"""

import re
from functools import wraps
from flask import request, jsonify, current_app
from werkzeug.exceptions import Forbidden

class SecurityManager:
    """Manages security for the web interface."""
    
    def __init__(self):
        # Define safe patterns for input validation
        self.safe_pattern = re.compile(r'^[a-zA-Z0-9\-_\.]+$')
        self.safe_text_pattern = re.compile(r'^[a-zA-Z0-9\-_\.\/\s\(\)\[\]\{\}\<\>\:\;\,\!\?\@\#\$\%\^\&\*\+\=\~]+$')
    
    def sanitize_input(self, input_string):
        """Sanitize user input to prevent injection attacks."""
        if not input_string:
            return input_string
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', str(input_string))
        return sanitized.strip()
    
    def validate_id(self, id_string):
        """Validate ID strings to ensure they're safe."""
        if not id_string:
            return False
        return bool(self.safe_pattern.match(str(id_string)))
    
    def validate_search_query(self, query):
        """Validate search queries to ensure they're safe."""
        if not query:
            return True
        return bool(self.safe_text_pattern.match(str(query)))
    
    def rate_limit(self, max_requests=100, window_seconds=3600):
        """Decorator to implement rate limiting."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # This is a simplified rate limiter
                # In production, you would use Redis or similar
                client_ip = request.remote_addr
                # Implementation would go here
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def require_https(self, f):
        """Decorator to require HTTPS connections."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_secure and current_app.config.get('REQUIRE_HTTPS', False):
                return jsonify({'error': 'HTTPS required'}), 403
            return f(*args, **kwargs)
        return decorated_function

# Global security manager
security_manager = SecurityManager()

def sanitize_user_input(f):
    """Decorator to sanitize user input."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Sanitize query parameters
        sanitized_args = {}
        for key, value in request.args.items():
            sanitized_args[key] = security_manager.sanitize_input(value)
        
        # Add sanitized args to request context if needed
        return f(*args, **kwargs)
    return decorated_function

def validate_pattern_id(f):
    """Decorator to validate pattern IDs in URL parameters."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Validate vendor_id and product_id
        vendor_id = kwargs.get('vendor_id')
        product_id = kwargs.get('product_id')
        
        if vendor_id and not security_manager.validate_id(vendor_id):
            return jsonify({'error': 'Invalid vendor ID'}), 400
        
        if product_id and not security_manager.validate_id(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        
        return f(*args, **kwargs)
    return decorated_function

def validate_search_input(f):
    """Decorator to validate search input."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Validate search query
        query = request.args.get('q', '')
        if query and not security_manager.validate_search_query(query):
            return jsonify({'error': 'Invalid search query'}), 400
        
        # Validate category and vendor filters
        category = request.args.get('category', '')
        vendor = request.args.get('vendor', '')
        
        if category and not security_manager.validate_id(category):
            return jsonify({'error': 'Invalid category'}), 400
        
        if vendor and not security_manager.validate_id(vendor):
            return jsonify({'error': 'Invalid vendor'}), 400
        
        return f(*args, **kwargs)
    return decorated_function

def require_https(f):
    """Decorator to require HTTPS connections."""
    return security_manager.require_https(f)