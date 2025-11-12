"""
Redis cache implementation for the application
Provides caching for face embeddings and frequently accessed data
"""
import json
import pickle
from typing import Any, Optional, List
from datetime import timedelta
from functools import wraps
import redis
from loguru import logger

from backend_src.app.config import settings


class RedisCache:
    """Redis cache client with helper methods"""
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                decode_responses=False,  # We'll handle encoding ourselves
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Redis connected: {settings.redis_host}:{settings.redis_port}")
            self._enabled = True
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self._enabled = False
            self.redis_client = None
    
    def is_enabled(self) -> bool:
        """Check if Redis is available"""
        return self._enabled
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None
    
    def set(
        self, 
        key: str, 
        value: Any, 
        expire_seconds: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional expiration"""
        if not self._enabled:
            return False
        
        try:
            serialized = pickle.dumps(value)
            if expire_seconds:
                return self.redis_client.setex(key, expire_seconds, serialized)
            else:
                return self.redis_client.set(key, serialized)
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self._enabled:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self._enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for '{pattern}': {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self._enabled:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key '{key}': {e}")
            return False
    
    def get_many(self, keys: List[str]) -> List[Optional[Any]]:
        """Get multiple values from cache"""
        if not self._enabled:
            return [None] * len(keys)
        
        try:
            values = self.redis_client.mget(keys)
            return [pickle.loads(v) if v else None for v in values]
        except Exception as e:
            logger.error(f"Cache get_many error: {e}")
            return [None] * len(keys)
    
    def set_many(
        self, 
        mapping: dict, 
        expire_seconds: Optional[int] = None
    ) -> bool:
        """Set multiple values in cache"""
        if not self._enabled:
            return False
        
        try:
            pipe = self.redis_client.pipeline()
            for key, value in mapping.items():
                serialized = pickle.dumps(value)
                if expire_seconds:
                    pipe.setex(key, expire_seconds, serialized)
                else:
                    pipe.set(key, serialized)
            pipe.execute()
            return True
        except Exception as e:
            logger.error(f"Cache set_many error: {e}")
            return False
    
    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter"""
        if not self._enabled:
            return None
        
        try:
            return self.redis_client.incr(key, amount)
        except Exception as e:
            logger.error(f"Cache incr error for key '{key}': {e}")
            return None
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on existing key"""
        if not self._enabled:
            return False
        
        try:
            return bool(self.redis_client.expire(key, seconds))
        except Exception as e:
            logger.error(f"Cache expire error for key '{key}': {e}")
            return False


# Global cache instance
cache = RedisCache()


# Cache key prefixes
FACE_EMBEDDING_PREFIX = "face_embedding:"
EMPLOYEE_PREFIX = "employee:"
ATTENDANCE_PREFIX = "attendance:"
STATS_PREFIX = "stats:"


def get_face_embedding_key(employee_id: int) -> str:
    """Generate cache key for face embedding"""
    return f"{FACE_EMBEDDING_PREFIX}{employee_id}"


def get_employee_key(employee_id: int) -> str:
    """Generate cache key for employee data"""
    return f"{EMPLOYEE_PREFIX}{employee_id}"


def get_attendance_list_key(date: str = "today") -> str:
    """Generate cache key for attendance list"""
    return f"{ATTENDANCE_PREFIX}list:{date}"


def get_stats_key(stat_type: str, date: str = "today") -> str:
    """Generate cache key for statistics"""
    return f"{STATS_PREFIX}{stat_type}:{date}"


def cache_result(
    key_prefix: str,
    expire_seconds: int = 300,
    key_builder=None
):
    """
    Decorator to cache function results
    
    Args:
        key_prefix: Prefix for cache key
        expire_seconds: Cache expiration in seconds (default 5 minutes)
        key_builder: Optional function to build cache key from args/kwargs
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = f"{key_prefix}{key_builder(*args, **kwargs)}"
            else:
                # Default: use first arg as key
                cache_key = f"{key_prefix}{args[0] if args else 'default'}"
            
            # Try to get from cache
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, expire_seconds)
                logger.debug(f"Cache set: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Decorator to invalidate cache after function execution
    
    Args:
        pattern: Pattern to match cache keys for deletion
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            deleted = cache.delete_pattern(pattern)
            if deleted:
                logger.debug(f"Cache invalidated: {pattern} ({deleted} keys)")
            return result
        
        return wrapper
    return decorator
