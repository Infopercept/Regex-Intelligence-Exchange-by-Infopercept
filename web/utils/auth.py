"""
Authentication utilities for Regex Intelligence Exchange.
"""

import hashlib
import secrets
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app

class AuthenticationManager:
    """Manages authentication for the web interface."""
    
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or secrets.token_hex(32)
    
    def hash_password(self, password):
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_token(self, user_id, expiration_hours=24):
        """Generate a JWT token for a user."""
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expiration_hours),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token):
        """Verify a JWT token and return the payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def require_auth(self, f):
        """Decorator to require authentication for API endpoints."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'Missing authorization token'}), 401
            
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = self.verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Add user info to request context
            request.current_user = payload
            
            return f(*args, **kwargs)
        return decorated_function

# Global authentication manager
auth_manager = AuthenticationManager()

def require_api_auth(f):
    """Decorator to require authentication for API endpoints."""
    return auth_manager.require_auth(f)

def generate_api_key():
    """Generate a new API key."""
    return secrets.token_urlsafe(32)

def hash_api_key(api_key):
    """Hash an API key for secure storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()

def verify_api_key(provided_key, stored_hash):
    """Verify an API key against its stored hash."""
    return hash_api_key(provided_key) == stored_hash