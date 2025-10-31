"""
Logging utilities for Regex Intelligence Exchange.
"""

import logging
from datetime import datetime
from config.logging_config import get_logger

class LogManager:
    """Manages logging for the web interface."""
    
    def __init__(self, log_level=logging.INFO, log_file=None):
        self.logger = get_logger()
        self.logger.setLevel(log_level)
    
    def debug(self, message):
        """Log a debug message."""
        self.logger.debug(message)
    
    def info(self, message):
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message):
        """Log an error message."""
        self.logger.error(message)
    
    def critical(self, message):
        """Log a critical message."""
        self.logger.critical(message)
    
    def log_request(self, request, response_status):
        """Log HTTP request information."""
        self.info(f"{request.method} {request.path} - {response_status}")
    
    def log_pattern_access(self, vendor_id, product_id, user_agent=None):
        """Log pattern access for analytics."""
        message = f"Pattern accessed: {vendor_id}/{product_id}"
        if user_agent:
            message += f" - User-Agent: {user_agent}"
        self.info(message)
    
    def log_search_query(self, query, category=None, vendor=None):
        """Log search queries for analytics."""
        message = f"Search query: '{query}'"
        if category:
            message += f" - Category: {category}"
        if vendor:
            message += f" - Vendor: {vendor}"
        self.info(message)
    
    def log_api_call(self, endpoint, method, user_id=None):
        """Log API calls for monitoring."""
        message = f"API call: {method} {endpoint}"
        if user_id:
            message += f" - User: {user_id}"
        self.info(message)

# Global log manager
log_manager = LogManager()

def log_request_info(request, response_status):
    """Log request information."""
    log_manager.log_request(request, response_status)

def log_pattern_access(vendor_id, product_id, user_agent=None):
    """Log pattern access."""
    log_manager.log_pattern_access(vendor_id, product_id, user_agent)

def log_search_query(query, category=None, vendor=None):
    """Log search query."""
    log_manager.log_search_query(query, category, vendor)

def log_api_call(endpoint, method, user_id=None):
    """Log API call."""
    log_manager.log_api_call(endpoint, method, user_id)