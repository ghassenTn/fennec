"""
Caching Strategies

Implements cache-aside and write-through caching patterns.
"""

from typing import Any, Callable, Optional, Union
from datetime import timedelta


class CacheAside:
    """
    Cache-Aside (Lazy Loading) Strategy
    
    Application checks cache first, loads from source on miss,
    then updates cache.
    """
    
    def __init__(self, cache_backend, ttl: Optional[Union[int, timedelta]] = 300):
        """
        Initialize cache-aside strategy.
        
        Args:
            cache_backend: Cache backend instance
            ttl: Default time to live
        """
        self.cache = cache_backend
        self.ttl = ttl
    
    async def get(
        self,
        key: str,
        loader: Callable,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> Any:
        """
        Get value using cache-aside pattern.
        
        Args:
            key: Cache key
            loader: Function to load data on cache miss
            ttl: Time to live (uses default if not specified)
            
        Returns:
            Cached or loaded value
        """
        # Try cache first
        value = await self.cache.get(key)
        
        if value is not None:
            return value
        
        # Cache miss - load from source
        value = await loader()
        
        # Update cache
        cache_ttl = ttl if ttl is not None else self.ttl
        await self.cache.set(key, value, ttl=cache_ttl)
        
        return value
    
    async def invalidate(self, key: str):
        """
        Invalidate cache entry.
        
        Args:
            key: Cache key to invalidate
        """
        await self.cache.delete(key)


class WriteThrough:
    """
    Write-Through Strategy
    
    Application writes to cache and source simultaneously.
    Cache is always consistent with source.
    """
    
    def __init__(self, cache_backend, ttl: Optional[Union[int, timedelta]] = 300):
        """
        Initialize write-through strategy.
        
        Args:
            cache_backend: Cache backend instance
            ttl: Default time to live
        """
        self.cache = cache_backend
        self.ttl = ttl
    
    async def get(self, key: str, loader: Optional[Callable] = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            loader: Optional loader function for cache miss
            
        Returns:
            Cached value or None
        """
        value = await self.cache.get(key)
        
        if value is None and loader:
            value = await loader()
            await self.cache.set(key, value, ttl=self.ttl)
        
        return value
    
    async def set(
        self,
        key: str,
        value: Any,
        writer: Callable,
        ttl: Optional[Union[int, timedelta]] = None
    ):
        """
        Write value to both cache and source.
        
        Args:
            key: Cache key
            value: Value to write
            writer: Function to write to source
            ttl: Time to live (uses default if not specified)
        """
        # Write to source first
        await writer(value)
        
        # Then update cache
        cache_ttl = ttl if ttl is not None else self.ttl
        await self.cache.set(key, value, ttl=cache_ttl)
    
    async def delete(self, key: str, deleter: Callable):
        """
        Delete from both cache and source.
        
        Args:
            key: Cache key
            deleter: Function to delete from source
        """
        # Delete from source first
        await deleter()
        
        # Then invalidate cache
        await self.cache.delete(key)


class WriteBehind:
    """
    Write-Behind (Write-Back) Strategy
    
    Application writes to cache immediately, source updated asynchronously.
    Provides better write performance but eventual consistency.
    """
    
    def __init__(
        self,
        cache_backend,
        ttl: Optional[Union[int, timedelta]] = 300,
        flush_interval: int = 60
    ):
        """
        Initialize write-behind strategy.
        
        Args:
            cache_backend: Cache backend instance
            ttl: Default time to live
            flush_interval: Interval to flush to source (seconds)
        """
        self.cache = cache_backend
        self.ttl = ttl
        self.flush_interval = flush_interval
        self._dirty_keys = set()
    
    async def get(self, key: str, loader: Optional[Callable] = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            loader: Optional loader function for cache miss
            
        Returns:
            Cached value or None
        """
        value = await self.cache.get(key)
        
        if value is None and loader:
            value = await loader()
            await self.cache.set(key, value, ttl=self.ttl)
        
        return value
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None
    ):
        """
        Write value to cache immediately.
        
        Args:
            key: Cache key
            value: Value to write
            ttl: Time to live (uses default if not specified)
        """
        cache_ttl = ttl if ttl is not None else self.ttl
        await self.cache.set(key, value, ttl=cache_ttl)
        
        # Mark as dirty for later flush
        self._dirty_keys.add(key)
    
    async def flush(self, writer: Callable):
        """
        Flush dirty keys to source.
        
        Args:
            writer: Function to write batch to source
        """
        if not self._dirty_keys:
            return
        
        # Get all dirty values
        dirty_data = {}
        for key in self._dirty_keys:
            value = await self.cache.get(key)
            if value is not None:
                dirty_data[key] = value
        
        # Write to source
        if dirty_data:
            await writer(dirty_data)
        
        # Clear dirty keys
        self._dirty_keys.clear()
