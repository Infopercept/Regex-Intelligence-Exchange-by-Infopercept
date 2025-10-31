"""
Redis cache implementation for Regex Intelligence Exchange.
"""

import json
import logging
from typing import Any, Optional
from utils.logging import log_manager

# Try to import Redis, but make it optional
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    log_manager.warning("Redis not available, using in-memory cache")

class RedisCache:
    """Redis-based cache implementation."""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self.client = None
        
        if REDIS_AVAILABLE:
            try:
                self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
                # Test connection
                self.client.ping()
                log_manager.info("Redis cache connected successfully")
            except Exception as e:
                log_manager.error(f"Failed to connect to Redis: {e}")
                self.client = None
        else:
            log_manager.info("Redis not available, using in-memory cache")
    
    def is_available(self) -> bool:
        """Check if Redis is available and connected."""
        return self.client is not None
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self.is_available():
            return None
        
        try:
            value = self.client.get(key)
            if value:
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
            self.client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            log_manager.error(f"Error setting cache key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        if not self.is_available():
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            log_manager.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache."""
        if not self.is_available():
            return False
        
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            log_manager.error(f"Error clearing cache: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        if not self.is_available():
            return {}
        
        try:
            info = self.client.info()
            return {
                'redis_version': info.get('redis_version', 'unknown'),
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory_human', 'unknown'),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
        except Exception as e:
            log_manager.error(f"Error getting cache stats: {e}")
            return {}

# Global Redis cache instance
redis_cache = RedisCache()

def get_redis_cache() -> RedisCache:
    """Get the global Redis cache instance."""
    return redis_cache