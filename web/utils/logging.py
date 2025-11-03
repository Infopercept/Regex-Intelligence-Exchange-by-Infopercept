"""
Enhanced logging utilities for Regex Intelligence Exchange.
"""

import os
import logging
import logging.handlers
from typing import Dict, Any, Optional
from datetime import datetime
from flask import Flask, request, g
import structlog
import json

class StructuredLogger:
    """Structured logging with JSON output and context."""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.logger = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize structured logging with Flask app."""
        self.app = app
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            # cache_logger_on_first_use=True,
        )
        
        # Create logger
        self.logger = structlog.get_logger("regex_exchange")
        
        # Set up file handlers
        self._setup_file_handlers(app)
        
        # Add request context
        @app.before_request
        def add_request_context():
            g.request_id = self._generate_request_id()
            g.start_time = datetime.utcnow()
        
        @app.after_request
        def log_request(response):
            if hasattr(g, 'start_time'):
                duration = (datetime.utcnow() - g.start_time).total_seconds()
                self.log_request_info(request, response.status_code, duration)
            return response
    
    def _setup_file_handlers(self, app: Flask):
        """Set up file logging handlers."""
        log_dir = os.path.join(app.root_path, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Main application log
        app_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        app_handler.setLevel(logging.INFO)
        
        # Security events log
        security_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'security.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        security_handler.setLevel(logging.WARNING)
        
        # API usage log
        api_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'api.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        api_handler.setLevel(logging.INFO)
        
        # Error log
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'error.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        error_handler.setLevel(logging.ERROR)
        
        # Add handlers to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(app_handler)
        root_logger.addHandler(security_handler)
        root_logger.addHandler(api_handler)
        root_logger.addHandler(error_handler)
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _get_request_context(self) -> Dict[str, Any]:
        """Get request context for logging."""
        context = {}
        
        if request:
            context.update({
                'request_id': getattr(g, 'request_id', None),
                'method': request.method,
                'url': request.url,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'referrer': request.referrer,
                'content_type': request.content_type,
                'content_length': request.content_length
            })
        
        return context
    
    def log_request_info(self, req, status_code: int, duration: float = None):
        """Log request information."""
        context = {
            'request_id': getattr(g, 'request_id', None),
            'method': req.method,
            'url': req.url,
            'status_code': status_code,
            'remote_addr': req.remote_addr,
            'user_agent': req.headers.get('User-Agent', ''),
            'duration': duration
        }
        
        if status_code >= 400:
            self.logger.warning("HTTP request completed with error", **context)
        else:
            self.logger.info("HTTP request completed", **context)
    
    def log_api_call(self, endpoint: str, method: str, **kwargs):
        """Log API call."""
        context = self._get_request_context()
        context.update({
            'endpoint': endpoint,
            'method': method,
            'event_type': 'api_call',
            **kwargs
        })
        
        self.logger.info("API call", **context)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event."""
        context = self._get_request_context()
        context.update({
            'event_type': event_type,
            'security_event': True,
            'details': details
        })
        
        self.logger.warning("Security event", **context)
    
    def log_pattern_access(self, vendor: str, product: str, user_agent: str = None):
        """Log pattern access."""
        context = self._get_request_context()
        context.update({
            'event_type': 'pattern_access',
            'vendor': vendor,
            'product': product,
            'user_agent': user_agent or context.get('user_agent')
        })
        
        self.logger.info("Pattern accessed", **context)
    
    def log_search_query(self, query: str, category: str = None, vendor: str = None):
        """Log search query."""
        context = self._get_request_context()
        context.update({
            'event_type': 'search_query',
            'query': query[:100],  # Limit query length in logs
            'category': category,
            'vendor': vendor
        })
        
        self.logger.info("Search performed", **context)
    
    def log_performance_metric(self, operation: str, duration: float, **kwargs):
        """Log performance metrics."""
        context = self._get_request_context()
        context.update({
            'event_type': 'performance_metric',
            'operation': operation,
            'duration': duration,
            **kwargs
        })
        
        if duration > 1.0:  # Log slow operations
            self.logger.warning("Slow operation detected", **context)
        else:
            self.logger.info("Performance metric", **context)
    
    # Database and cache logging methods removed for simplicity
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log error with context."""
        log_context = self._get_request_context()
        if context:
            log_context.update(context)
        
        log_context.update({
            'event_type': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error)
        })
        
        self.logger.error("Application error", **log_context, exc_info=True)
    
    def log_user_action(self, action: str, details: Dict[str, Any] = None):
        """Log user actions."""
        context = self._get_request_context()
        context.update({
            'event_type': 'user_action',
            'action': action,
            'details': details or {}
        })
        
        self.logger.info("User action", **context)

class MetricsCollector:
    """Collect and log application metrics."""
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_by_status': {},
            'response_times': [],
            'api_calls': 0,
            'pattern_accesses': 0,
            'search_queries': 0,
            'errors': 0
        }
    
    def record_request(self, status_code: int, duration: float):
        """Record request metrics."""
        self.metrics['requests_total'] += 1
        
        if status_code not in self.metrics['requests_by_status']:
            self.metrics['requests_by_status'][status_code] = 0
        self.metrics['requests_by_status'][status_code] += 1
        
        self.metrics['response_times'].append(duration)
        
        # Keep only last 1000 response times
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
    
    def record_api_call(self):
        """Record API call."""
        self.metrics['api_calls'] += 1
    
    def record_pattern_access(self):
        """Record pattern access."""
        self.metrics['pattern_accesses'] += 1
    
    def record_search_query(self):
        """Record search query."""
        self.metrics['search_queries'] += 1
    
    def record_error(self):
        """Record error."""
        self.metrics['errors'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        avg_response_time = (
            sum(self.metrics['response_times']) / len(self.metrics['response_times'])
            if self.metrics['response_times'] else 0
        )
        
        return {
            **self.metrics,
            'avg_response_time': avg_response_time,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            'requests_total': 0,
            'requests_by_status': {},
            'response_times': [],
            'api_calls': 0,
            'pattern_accesses': 0,
            'search_queries': 0,
            'errors': 0
        }

# Global instances
log_manager = StructuredLogger()
metrics_collector = MetricsCollector()