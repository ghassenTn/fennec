"""
Cache Decorators

Provides @cache decorator for automatic function result caching.
"""

import functools
import hashlib
import json
from typing import Any, Callable, Optional, Union
from datetime import timedelta


def cache(
    ttl: Optional[Union[int, timedelta]] = 300,
    key_prefix: Optional[str] = None,
    backend: Optional[Any] = None
):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds or timedelta (default: 300s)
        key_prefix: Custom key prefix (default: function name)
        backend: Cache backend instance (default: global cache)
        
    Example:
        @cache(ttl=600)
        async def get_user(user_id: int):
            return await db.get_user(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache backend
            cache_backend = backend
            if cache_backend is None:
                # Try to get from global context
                from fennec.cache import RedisCache
                cache_backend = RedisCache()
            
            # Generate cache key
            prefix = key_prefix or func.__name__
            key_data = {
                'args': args,
                'kwargs': kwargs
            }
            key_hash = hashlib.md5(
                json.dumps(key_data, sort_keys=True, default=str).encode()
            ).hexdigest()
            cache_key = f"{prefix}:{key_hash}"
            
            # Try to get from cache
            cached_value = await cache_backend.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache_backend.set(cache_key, result, ttl=ttl)
            
            return result
        
        # Add cache control methods
        wrapper.cache_clear = lambda: _clear_cache(func, backend)
        wrapper.cache_info = lambda: _cache_info(func, backend)
        
        return wrapper
    
    return decorator


async def _clear_cache(func: Callable, backend: Any):
    """Clear all cached results for a function."""
    cache_backend = backend
    if cache_backend is None:
        from fennec.cache import RedisCache
        cache_backend = RedisCache()
    
    pattern = f"{func.__name__}:*"
    return await cache_backend.clear(pattern)


async def _cache_info(func: Callable, backend: Any):
    """Get cache statistics for a function."""
    cache_backend = backend
    if cache_backend is None:
        from fennec.cache import RedisCache
        cache_backend = RedisCache()
    
    return await cache_backend.get_stats()
