"""
Redis Cache Implementation

Provides Redis client wrapper with connection pooling, TTL support,
and cache statistics tracking.
"""

import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
import asyncio


class RedisCache:
    """Redis cache client with connection pooling and statistics."""
    
    def __init__(
        self,
        url: str = "redis://localhost:6379",
        max_connections: int = 10,
        decode_responses: bool = False,
        prefix: str = "fennec:"
    ):
        """
        Initialize Redis cache client.
        
        Args:
            url: Redis connection URL
            max_connections: Maximum number of connections in pool
            decode_responses: Whether to decode responses as strings
            prefix: Key prefix for namespacing
        """
        self.url = url
        self.max_connections = max_connections
        self.decode_responses = decode_responses
        self.prefix = prefix
        self._client = None
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    async def connect(self):
        """Establish Redis connection with connection pooling."""
        try:
            import redis.asyncio as aioredis
        except ImportError:
            raise ImportError(
                "redis package is required for caching. "
                "Install it with: pip install redis hiredis"
            )
        
        self._client = await aioredis.from_url(
            self.url,
            max_connections=self.max_connections,
            decode_responses=self.decode_responses
        )
    
    async def disconnect(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
    
    def _make_key(self, key: str) -> str:
        """Create namespaced key."""
        return f"{self.prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self._client:
            await self.connect()
        
        namespaced_key = self._make_key(key)
        value = await self._client.get(namespaced_key)
        
        if value is None:
            self._stats['misses'] += 1
            return None
        
        self._stats['hits'] += 1
        
        # Try to unpickle, fallback to raw value
        try:
            return pickle.loads(value)
        except (pickle.PickleError, TypeError):
            return value
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """
        Set value in cache with optional TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds or timedelta
            
        Returns:
            True if successful
        """
        if not self._client:
            await self.connect()
        
        namespaced_key = self._make_key(key)
        
        # Serialize value
        try:
            serialized = pickle.dumps(value)
        except (pickle.PickleError, TypeError):
            serialized = str(value)
        
        # Convert timedelta to seconds
        if isinstance(ttl, timedelta):
            ttl = int(ttl.total_seconds())
        
        if ttl:
            await self._client.setex(namespaced_key, ttl, serialized)
        else:
            await self._client.set(namespaced_key, serialized)
        
        self._stats['sets'] += 1
        return True
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted
        """
        if not self._client:
            await self.connect()
        
        namespaced_key = self._make_key(key)
        result = await self._client.delete(namespaced_key)
        
        if result:
            self._stats['deletes'] += 1
        
        return bool(result)
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists
        """
        if not self._client:
            await self.connect()
        
        namespaced_key = self._make_key(key)
        return bool(await self._client.exists(namespaced_key))
    
    async def clear(self, pattern: str = "*") -> int:
        """
        Clear cache keys matching pattern.
        
        Args:
            pattern: Key pattern (default: all keys with prefix)
            
        Returns:
            Number of keys deleted
        """
        if not self._client:
            await self.connect()
        
        full_pattern = self._make_key(pattern)
        keys = []
        
        async for key in self._client.scan_iter(match=full_pattern):
            keys.append(key)
        
        if keys:
            return await self._client.delete(*keys)
        
        return 0
    
    async def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with hit/miss statistics
        """
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (
            self._stats['hits'] / total_requests * 100
            if total_requests > 0
            else 0
        )
        
        return {
            **self._stats,
            'total_requests': total_requests,
            'hit_rate': round(hit_rate, 2)
        }
    
    async def reset_stats(self):
        """Reset cache statistics."""
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    async def ping(self) -> bool:
        """
        Check Redis connection health.
        
        Returns:
            True if connection is healthy
        """
        if not self._client:
            await self.connect()
        
        try:
            return await self._client.ping()
        except Exception:
            return False
