"""
Redis cache implementation for Regex Intelligence Exchange.
"""

import json
import logging
from typing import Any, Optional
from utils.logging import log_manager

class RedisCache:
    """Redis-based cache implementation."""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self.client = None
        self.redis_module = None
        
        # Try to import Redis, but make it optional
        try:
            import redis
            self.redis_module = redis
            self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            # Test connection
            self.client.ping()
            log_manager.info("Redis cache connected successfully")
        except ImportError:
            log_manager.warning("Redis not available, using in-memory cache")
        except Exception as e:
            log_manager.error(f"Failed to connect to Redis: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available and connected."""
        return self.client is not None and self.redis_module is not None
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self.is_available():
            return None
        
        try:
            # Use getattr to avoid type checking issues
            get_method = getattr(self.client, 'get', None)
            if get_method:
                value = get_method(key)
                if value:
                    # Ensure value is a string before parsing
                    if not isinstance(value, str):
                        value = str(value)
                    return json.loads(value)
        except Exception as e:
            log_manager.error(f"Error getting cache key {key}: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache."""
        if not self.is_available():
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            # Use getattr to avoid type checking issues
            setex_method = getattr(self.client, 'setex', None)
            if setex_method:
                setex_method(key, ttl, serialized_value)
                return True
        except Exception as e:
            log_manager.error(f"Error setting cache key {key}: {e}")
            return False
        return False
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        if not self.is_available():
            return False
        
        try:
            # Use getattr to avoid type checking issues
            delete_method = getattr(self.client, 'delete', None)
            if delete_method:
                delete_method(key)
                return True
        except Exception as e:
            log_manager.error(f"Error deleting cache key {key}: {e}")
            return False
        return False
    
    def clear(self) -> bool:
        """Clear all cache."""
        if not self.is_available():
            return False
        
        try:
            # Use getattr to avoid type checking issues
            flushdb_method = getattr(self.client, 'flushdb', None)
            if flushdb_method:
                flushdb_method()
                return True
        except Exception as e:
            log_manager.error(f"Error clearing cache: {e}")
            return False
        return False
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        if not self.is_available():
            return {}
        
        try:
            # Use getattr to avoid type checking issues
            info_method = getattr(self.client, 'info', None)
            if info_method:
                info = info_method()
                # Handle potential async response
                if info:
                    # Convert to dict if needed
                    if hasattr(info, '__dict__'):
                        info_dict = info.__dict__
                    elif isinstance(info, dict):
                        info_dict = info
                    else:
                        info_dict = {}
                    
                    return {
                        'redis_version': str(info_dict.get('redis_version', 'unknown')) if isinstance(info_dict, dict) else 'unknown',
                        'connected_clients': int(info_dict.get('connected_clients', 0)) if isinstance(info_dict, dict) else 0,
                        'used_memory': str(info_dict.get('used_memory_human', 'unknown')) if isinstance(info_dict, dict) else 'unknown',
                        'total_commands_processed': int(info_dict.get('total_commands_processed', 0)) if isinstance(info_dict, dict) else 0,
                        'keyspace_hits': int(info_dict.get('keyspace_hits', 0)) if isinstance(info_dict, dict) else 0,
                        'keyspace_misses': int(info_dict.get('keyspace_misses', 0)) if isinstance(info_dict, dict) else 0
                    }
        except Exception as e:
            log_manager.error(f"Error getting cache stats: {e}")
            return {}
        return {}

# Global Redis cache instance
redis_cache = RedisCache()

def get_redis_cache() -> RedisCache:
    """Get the global Redis cache instance."""
    return redis_cache