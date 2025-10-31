"""
Security utilities for Regex Intelligence Exchange.
"""

import re
import hashlib
import secrets
import time
from functools import wraps
from flask import request, jsonify, current_app, session
from werkzeug.exceptions import Forbidden

class SecurityManager:
    """Manages security for the web interface."""
    
    def __init__(self):
        # Define safe patterns for input validation
        self.safe_pattern = re.compile(r'^[a-zA-Z0-9\-_\.]+$')
        self.safe_text_pattern = re.compile(r'^[a-zA-Z0-9\-_\.\/\s\(\)\[\]\{\}\<\>\:\;\,\!\?\@\#\$\%\^\&\*\+\=\~]+$')
        
        # Rate limiting storage (in production, use Redis)
        self.rate_limits = {}
    
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
    
    def generate_csrf_token(self):
        """Generate a CSRF token."""
        return secrets.token_hex(16)
    
    def validate_csrf_token(self, token):
        """Validate a CSRF token."""
        if 'csrf_token' not in session:
            return False
        return secrets.compare_digest(session['csrf_token'], token)
    
    def rate_limit(self, max_requests=100, window_seconds=3600):
        """Decorator to implement rate limiting."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Get client IP
                client_ip = request.remote_addr
                
                # Create a unique key for this endpoint and IP
                key = f"{client_ip}:{request.endpoint}"
                
                current_time = time.time()
                
                # Initialize rate limit data for this key if it doesn't exist
                if key not in self.rate_limits:
                    self.rate_limits[key] = {
                        'count': 0,
                        'first_request_time': current_time
                    }
                
                # Reset count if window has expired
                if current_time - self.rate_limits[key]['first_request_time'] > window_seconds:
                    self.rate_limits[key] = {
                        'count': 0,
                        'first_request_time': current_time
                    }
                
                # Increment request count
                self.rate_limits[key]['count'] += 1
                
                # Check if limit exceeded
                if self.rate_limits[key]['count'] > max_requests:
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                
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
    
    def sanitize_json_input(self, data):
        """Sanitize JSON input data."""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                sanitized_key = self.sanitize_input(key)
                sanitized_value = self.sanitize_json_input(value)
                sanitized[sanitized_key] = sanitized_value
            return sanitized
        elif isinstance(data, list):
            return [self.sanitize_json_input(item) for item in data]
        elif isinstance(data, str):
            return self.sanitize_input(data)
        else:
            return data
    
    def hash_password(self, password):
        """Hash a password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{hashed}:{salt}"
    
    def verify_password(self, password, hashed_password):
        """Verify a password against a hashed password."""
        if ':' not in hashed_password:
            return False
        
        hashed, salt = hashed_password.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hashed
    
    def validate_api_key(self, api_key):
        """Validate an API key (placeholder implementation)."""
        # In a real implementation, you would check against a database of valid API keys
        # For now, we'll just check if it's a valid hex string
        try:
            bytes.fromhex(api_key)
            return len(api_key) == 32  # 16 bytes = 32 hex characters
        except ValueError:
            return False

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

def require_api_key(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        if not security_manager.validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=100, window_seconds=3600):
    """Decorator to implement rate limiting."""
    return security_manager.rate_limit(max_requests, window_seconds)