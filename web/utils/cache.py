"""
Caching utilities for Regex Intelligence Exchange.
"""

import functools
import time
import hashlib
import json
from typing import Any, Dict, Optional, Callable
from utils.logging import log_manager
from utils.redis_cache import redis_cache

class CacheManager:
    """Manages caching for the web interface."""
    
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl  # 5 minutes default
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
    
    def _generate_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate a cache key from function name and arguments."""
        # Create a hash of the function name and arguments
        key_data = {
            'function': func_name,
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        # Try Redis first
        if redis_cache.is_available():
            value = redis_cache.get(key)
            if value is not None:
                log_manager.debug(f"Redis cache hit for key: {key}")
                return value
        
        # Fall back to in-memory cache
        if key in self._cache:
            # Check if expired
            if time.time() - self._access_times[key] < self._cache[key]['ttl']:
                log_manager.debug(f"In-memory cache hit for key: {key}")
                return self._cache[key]['value']
            else:
                # Expired, remove from cache
                log_manager.debug(f"In-memory cache expired for key: {key}")
                del self._cache[key]
                del self._access_times[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache."""
        ttl = ttl or self.default_ttl
        
        # Set in Redis if available
        if redis_cache.is_available():
            redis_cache.set(key, value, ttl)
            log_manager.debug(f"Redis cache set for key: {key}")
        
        # Set in in-memory cache
        self._cache[key] = {
            'value': value,
            'ttl': ttl
        }
        self._access_times[key] = time.time()
        log_manager.debug(f"In-memory cache set for key: {key}")
    
    def delete(self, key: str) -> None:
        """Delete a value from cache."""
        # Delete from Redis if available
        if redis_cache.is_available():
            redis_cache.delete(key)
            log_manager.debug(f"Redis cache deleted for key: {key}")
        
        # Delete from in-memory cache
        if key in self._cache:
            del self._cache[key]
            del self._access_times[key]
            log_manager.debug(f"In-memory cache deleted for key: {key}")
    
    def clear(self) -> None:
        """Clear all cache."""
        # Clear Redis if available
        if redis_cache.is_available():
            redis_cache.clear()
            log_manager.debug("Redis cache cleared")
        
        # Clear in-memory cache
        self._cache.clear()
        self._access_times.clear()
        log_manager.info("In-memory cache cleared")
    
    def cache(self, ttl: Optional[int] = None) -> Callable:
        """Decorator to cache function results."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                key = self._generate_key(func.__name__, *args, **kwargs)
                
                # Try to get from cache
                cached_value = self.get(key)
                if cached_value is not None:
                    return cached_value
                
                # Call function and cache result
                result = func(*args, **kwargs)
                self.set(key, result, ttl)
                return result
            
            return wrapper
        return decorator
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            'in_memory': {
                'total_items': len(self._cache)
            }
        }
        
        # Add Redis stats if available
        if redis_cache.is_available():
            stats['redis'] = redis_cache.get_stats()
        
        current_time = time.time()
        active_items = 0
        expired_items = 0
        
        for key, access_time in self._access_times.items():
            if key in self._cache:
                ttl = self._cache[key]['ttl']
                if current_time - access_time < ttl:
                    active_items += 1
                else:
                    expired_items += 1
        
        stats['in_memory']['active_items'] = active_items
        stats['in_memory']['expired_items'] = expired_items
        stats['in_memory']['default_ttl'] = self.default_ttl
        
        return stats

# Global cache manager
cache_manager = CacheManager()

def get_cache() -> CacheManager:
    """Get the global cache manager."""
    return cache_manager

# Memory-based cache for pattern data
class PatternCache:
    """Specialized cache for pattern data."""
    
    def __init__(self):
        self._patterns: Dict[str, Any] = {}
        self._categories: Optional[list] = None
        self._vendors: Optional[list] = None
        self._stats: Optional[dict] = None
        self._last_updated: float = 0
        self.ttl = 300  # 5 minutes
    
    def is_expired(self) -> bool:
        """Check if cache is expired."""
        return time.time() - self._last_updated > self.ttl
    
    def update_patterns(self, patterns: Dict[str, Any]) -> None:
        """Update patterns cache."""
        self._patterns = patterns
        self._last_updated = time.time()
        log_manager.info(f"Pattern cache updated with {len(patterns)} items")
    
    def get_patterns(self) -> Dict[str, Any]:
        """Get patterns from cache."""
        if self.is_expired():
            return {}
        return self._patterns
    
    def update_categories(self, categories: list) -> None:
        """Update categories cache."""
        self._categories = categories
        self._last_updated = time.time()
        log_manager.info(f"Category cache updated with {len(categories)} items")
    
    def get_categories(self) -> Optional[list]:
        """Get categories from cache."""
        if self.is_expired():
            return None
        return self._categories
    
    def update_vendors(self, vendors: list) -> None:
        """Update vendors cache."""
        self._vendors = vendors
        self._last_updated = time.time()
        log_manager.info(f"Vendor cache updated with {len(vendors)} items")
    
    def get_vendors(self) -> Optional[list]:
        """Get vendors from cache."""
        if self.is_expired():
            return None
        return self._vendors
    
    def update_stats(self, stats: dict) -> None:
        """Update stats cache."""
        self._stats = stats
        self._last_updated = time.time()
        log_manager.info("Stats cache updated")
    
    def get_stats(self) -> Optional[dict]:
        """Get stats from cache."""
        if self.is_expired():
            return None
        return self._stats
    
    def clear(self) -> None:
        """Clear all pattern cache."""
        self._patterns = {}
        self._categories = None
        self._vendors = None
        self._stats = None
        self._last_updated = 0
        log_manager.info("Pattern cache cleared")

# Global pattern cache
pattern_cache = PatternCache()