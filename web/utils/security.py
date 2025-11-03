"""
Enhanced security utilities for Regex Intelligence Exchange.
"""

import re
import hashlib
import secrets
import logging
from typing import Dict, Any, Optional, List
from functools import wraps
from flask import request, abort, current_app, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bcrypt
import jwt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecurityManager:
    """Enhanced security manager with comprehensive protection."""
    
    def __init__(self, app=None):
        self.app = app
        self.limiter = None
        self.failed_attempts = {}  # Simple in-memory storage
        self.blocked_ips = set()   # Simple in-memory storage
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security manager with Flask app."""
        self.app = app
        
        # Initialize rate limiter
        self.limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["1000 per hour", "100 per minute"]
        )
        
        # Set security headers
        @app.after_request
        def set_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self';"
            )
            return response
    
    def sanitize_input(self, input_text: str, max_length: int = 1000) -> str:
        """Sanitize user input to prevent XSS and injection attacks."""
        if not input_text:
            return ""
        
        # Limit length
        input_text = input_text[:max_length]
        
        # Remove potentially dangerous characters
        input_text = re.sub(r'[<>"\']', '', input_text)
        
        # Remove SQL injection patterns
        sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
            r'(--|#|/\*|\*/)',
            r'(\bOR\b.*=.*\bOR\b)',
            r'(\bAND\b.*=.*\bAND\b)'
        ]
        
        for pattern in sql_patterns:
            input_text = re.sub(pattern, '', input_text, flags=re.IGNORECASE)
        
        return input_text.strip()
    
    def validate_pattern_id(self, pattern_id: str) -> bool:
        """Validate pattern ID format."""
        if not pattern_id:
            return False
        
        # Allow only alphanumeric, hyphens, and underscores
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', pattern_id))
    
    def validate_search_query(self, query: str) -> bool:
        """Validate search query."""
        if not query:
            return True
        
        # Check length
        if len(query) > 500:
            return False
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
            r'eval\(',
            r'exec\(',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return False
        
        return True
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token."""
        return secrets.token_urlsafe(32)
    
    def validate_csrf_token(self, token: str) -> bool:
        """Validate CSRF token."""
        session_token = session.get('csrf_token')
        return session_token and secrets.compare_digest(session_token, token)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_api_key(self) -> str:
        """Generate API key."""
        return secrets.token_urlsafe(32)
    
    def create_jwt_token(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """Create JWT token."""
        payload['exp'] = datetime.utcnow() + timedelta(seconds=expires_in)
        payload['iat'] = datetime.utcnow()
        
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events."""
        logger.warning(f"Security Event: {event_type}", extra={
            'event_type': event_type,
            'details': details,
            'ip_address': get_remote_address(),
            'user_agent': request.headers.get('User-Agent', ''),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def check_rate_limit(self, identifier: str, limit: int, window: int) -> bool:
        """Check rate limit for identifier."""
        # Simple in-memory rate limiting
        # This is a simple in-memory implementation
        current_time = datetime.utcnow()
        
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        # Clean old attempts
        self.failed_attempts[identifier] = [
            attempt for attempt in self.failed_attempts[identifier]
            if (current_time - attempt).seconds < window
        ]
        
        # Check limit
        if len(self.failed_attempts[identifier]) >= limit:
            return False
        
        # Add current attempt
        self.failed_attempts[identifier].append(current_time)
        return True
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked."""
        return ip_address in self.blocked_ips
    
    def block_ip(self, ip_address: str, duration: int = 3600):
        """Block IP address."""
        self.blocked_ips.add(ip_address)
        self.log_security_event('ip_blocked', {
            'ip_address': ip_address,
            'duration': duration
        })

# Global security manager instance
security_manager = SecurityManager()

# Decorators for security validation
def validate_pattern_id(f):
    """Decorator to validate pattern ID parameters."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check vendor and product parameters
        vendor = kwargs.get('vendor') or request.view_args.get('vendor')
        product = kwargs.get('product') or request.view_args.get('product')
        
        if vendor and not security_manager.validate_pattern_id(vendor):
            security_manager.log_security_event('invalid_pattern_id', {
                'parameter': 'vendor',
                'value': vendor
            })
            abort(400, description="Invalid vendor ID format")
        
        if product and not security_manager.validate_pattern_id(product):
            security_manager.log_security_event('invalid_pattern_id', {
                'parameter': 'product',
                'value': product
            })
            abort(400, description="Invalid product ID format")
        
        return f(*args, **kwargs)
    return decorated_function

def validate_search_input(f):
    """Decorator to validate search input."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        query = request.args.get('q', '')
        
        if query and not security_manager.validate_search_query(query):
            security_manager.log_security_event('invalid_search_query', {
                'query': query[:100]  # Log only first 100 chars
            })
            abort(400, description="Invalid search query")
        
        return f(*args, **kwargs)
    return decorated_function

def require_api_key(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            security_manager.log_security_event('missing_api_key', {})
            abort(401, description="API key required")
        
        # Simple API key validation
        # For now, just check if it's a valid format
        if len(api_key) < 32:
            security_manager.log_security_event('invalid_api_key', {
                'api_key_length': len(api_key)
            })
            abort(401, description="Invalid API key")
        
        return f(*args, **kwargs)
    return decorated_function

def check_ip_whitelist(allowed_ips: List[str]):
    """Decorator to check IP whitelist."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = get_remote_address()
            
            if client_ip not in allowed_ips:
                security_manager.log_security_event('ip_not_whitelisted', {
                    'client_ip': client_ip,
                    'allowed_ips': allowed_ips
                })
                abort(403, description="Access denied")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator