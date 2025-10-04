"""
Fennec Caching Module

Provides Redis-based caching with decorators and multiple caching strategies.
"""

from .redis import RedisCache
from .decorators import cache
from .strategies import CacheAside, WriteThrough

__all__ = ['RedisCache', 'cache', 'CacheAside', 'WriteThrough']
