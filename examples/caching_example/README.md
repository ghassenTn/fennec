# Fennec Caching Example

This example demonstrates Redis caching capabilities in Fennec Framework.

## Features

- **@cache Decorator**: Automatic function result caching
- **Cache-Aside Pattern**: Lazy loading with cache fallback
- **Write-Through Pattern**: Synchronous cache and database updates
- **Cache Statistics**: Hit/miss tracking and performance metrics
- **Manual Cache Control**: Clear, invalidate, and health checks

## Prerequisites

Redis must be running. Start it with Docker:

```bash
docker run -d -p 6379:6379 redis
```

Or install locally:

```bash
# macOS
brew install redis
redis-server

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
```

## Installation

Install required dependencies:

```bash
pip install redis hiredis
```

## Running the Example

```bash
python server.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### 1. Cached User Lookup (@cache decorator)

```bash
# First request (cache miss - slow)
curl http://localhost:8000/users/1

# Second request (cache hit - fast)
curl http://localhost:8000/users/1
```

Response:
```json
{
  "user": {"id": 1, "name": "Alice", "email": "alice@example.com"},
  "cached": true,
  "duration_ms": 2.5
}
```

### 2. Cache-Aside Pattern

```bash
curl http://localhost:8000/users-aside/2
```

### 3. Write-Through Pattern

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"id": 4, "name": "David", "email": "david@example.com"}'
```

### 4. Cache Statistics

```bash
curl http://localhost:8000/cache/stats
```

Response:
```json
{
  "hits": 15,
  "misses": 3,
  "sets": 3,
  "deletes": 0,
  "total_requests": 18,
  "hit_rate": 83.33
}
```

### 5. Clear Cache

```bash
curl -X POST http://localhost:8000/cache/clear
```

### 6. Cache Health Check

```bash
curl http://localhost:8000/cache/health
```

### 7. Performance Benchmark

```bash
curl http://localhost:8000/benchmark
```

Response:
```json
{
  "uncached_ms": 1002.5,
  "cache_miss_ms": 1003.1,
  "cache_hit_ms": 2.3,
  "speedup": 435.87
}
```

## Caching Strategies

### Cache-Aside (Lazy Loading)

Best for read-heavy workloads:

```python
from fennec.cache import CacheAside, RedisCache

cache = RedisCache()
cache_aside = CacheAside(cache, ttl=300)

async def get_data(key):
    return await cache_aside.get(
        key,
        loader=lambda: fetch_from_database(key)
    )
```

### Write-Through

Best for write consistency:

```python
from fennec.cache import WriteThrough, RedisCache

cache = RedisCache()
write_through = WriteThrough(cache, ttl=300)

async def save_data(key, value):
    await write_through.set(
        key,
        value,
        writer=lambda v: save_to_database(v)
    )
```

### @cache Decorator

Simplest approach for function caching:

```python
from fennec.cache import cache, RedisCache

redis = RedisCache()

@cache(ttl=600, backend=redis)
async def expensive_operation(param):
    # Expensive computation
    return result
```

## Performance Tips

1. **Set appropriate TTL**: Balance freshness vs performance
2. **Use key prefixes**: Organize cache namespaces
3. **Monitor hit rates**: Aim for >80% hit rate
4. **Cache warming**: Pre-populate frequently accessed data
5. **Invalidation strategy**: Clear stale data proactively

## Cache Key Design

Good key design is crucial:

```python
# ✅ Good: Specific, hierarchical
user:123:profile
product:456:details
session:abc123

# ❌ Bad: Generic, collision-prone
user
data
cache
```

## Monitoring

Track cache performance:

```python
stats = await redis_cache.get_stats()
print(f"Hit rate: {stats['hit_rate']}%")
print(f"Total requests: {stats['total_requests']}")
```

## Common Patterns

### Cache Invalidation

```python
# Invalidate specific key
await redis_cache.delete("user:123")

# Invalidate pattern
await redis_cache.clear("user:*")
```

### Conditional Caching

```python
@cache(ttl=300)
async def get_user(user_id: int):
    user = await db.get_user(user_id)
    # Don't cache if user is None
    if user is None:
        raise ValueError("User not found")
    return user
```

### Cache Warming

```python
async def warm_cache():
    """Pre-populate cache with frequently accessed data."""
    popular_users = [1, 2, 3, 4, 5]
    for user_id in popular_users:
        user = await db.get_user(user_id)
        await redis_cache.set(f"user:{user_id}", user, ttl=3600)
```

## Troubleshooting

### Connection Issues

```bash
# Test Redis connection
redis-cli ping
# Should return: PONG
```

### Memory Issues

```bash
# Check Redis memory usage
redis-cli info memory

# Set max memory policy
redis-cli config set maxmemory-policy allkeys-lru
```

### Performance Issues

- Check network latency to Redis
- Use connection pooling (enabled by default)
- Consider Redis Cluster for scale
- Monitor slow queries with `SLOWLOG`

## Next Steps

- Explore cache invalidation strategies
- Implement cache warming on startup
- Add cache metrics to monitoring dashboard
- Try different eviction policies
- Scale with Redis Cluster
