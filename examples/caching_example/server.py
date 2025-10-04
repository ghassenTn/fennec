"""
Fennec Caching Example

Demonstrates Redis caching with decorators and strategies.
"""

import asyncio
import time
from fennec import Application, Request, Response
from fennec.cache import RedisCache, cache, CacheAside, WriteThrough


# Initialize app and cache
app = Application()
redis_cache = RedisCache(url="redis://localhost:6379", prefix="demo:")


# Simulated database
fake_db = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
    3: {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
}


# Example 1: Using @cache decorator
@cache(ttl=60, backend=redis_cache)
async def get_user_from_db(user_id: int):
    """Simulate expensive database query."""
    print(f"[DB Query] Fetching user {user_id} from database...")
    await asyncio.sleep(1)  # Simulate slow query
    return fake_db.get(user_id)


@app.get("/users/{user_id}")
async def get_user(request: Request):
    """Get user with caching."""
    user_id = int(request.path_params['user_id'])
    
    start = time.time()
    user = await get_user_from_db(user_id)
    duration = time.time() - start
    
    if not user:
        return Response({"error": "User not found"}, status=404)
    
    return Response({
        "user": user,
        "cached": duration < 0.1,  # If fast, it was cached
        "duration_ms": round(duration * 1000, 2)
    })


# Example 2: Cache-Aside Strategy
cache_aside = CacheAside(redis_cache, ttl=120)


async def load_user_from_db(user_id: int):
    """Load user from database."""
    print(f"[Cache-Aside] Loading user {user_id} from database...")
    await asyncio.sleep(1)
    return fake_db.get(user_id)


@app.get("/users-aside/{user_id}")
async def get_user_cache_aside(request: Request):
    """Get user using cache-aside pattern."""
    user_id = int(request.path_params['user_id'])
    
    start = time.time()
    user = await cache_aside.get(
        f"user:{user_id}",
        lambda: load_user_from_db(user_id)
    )
    duration = time.time() - start
    
    if not user:
        return Response({"error": "User not found"}, status=404)
    
    return Response({
        "user": user,
        "strategy": "cache-aside",
        "cached": duration < 0.1,
        "duration_ms": round(duration * 1000, 2)
    })


# Example 3: Write-Through Strategy
write_through = WriteThrough(redis_cache, ttl=120)


async def save_user_to_db(user_data: dict):
    """Save user to database."""
    print(f"[Write-Through] Saving user to database...")
    await asyncio.sleep(0.5)
    fake_db[user_data['id']] = user_data


@app.post("/users")
async def create_user(request: Request):
    """Create user using write-through pattern."""
    data = await request.json()
    user_id = data.get('id')
    
    if not user_id:
        return Response({"error": "User ID required"}, status=400)
    
    start = time.time()
    await write_through.set(
        f"user:{user_id}",
        data,
        lambda value: save_user_to_db(value)
    )
    duration = time.time() - start
    
    return Response({
        "message": "User created",
        "user": data,
        "strategy": "write-through",
        "duration_ms": round(duration * 1000, 2)
    })


# Example 4: Manual cache operations
@app.get("/cache/stats")
async def cache_stats(request: Request):
    """Get cache statistics."""
    stats = await redis_cache.get_stats()
    return Response(stats)


@app.post("/cache/clear")
async def clear_cache(request: Request):
    """Clear all cache entries."""
    count = await redis_cache.clear()
    await redis_cache.reset_stats()
    return Response({
        "message": "Cache cleared",
        "keys_deleted": count
    })


@app.get("/cache/health")
async def cache_health(request: Request):
    """Check cache health."""
    is_healthy = await redis_cache.ping()
    return Response({
        "status": "healthy" if is_healthy else "unhealthy",
        "backend": "redis"
    })


# Example 5: Performance comparison
@app.get("/benchmark")
async def benchmark(request: Request):
    """Compare cached vs uncached performance."""
    user_id = 1
    
    # Uncached request
    start = time.time()
    await load_user_from_db(user_id)
    uncached_time = time.time() - start
    
    # First cached request (cache miss)
    await redis_cache.delete(f"user:{user_id}")
    start = time.time()
    await cache_aside.get(
        f"user:{user_id}",
        lambda: load_user_from_db(user_id)
    )
    first_cached_time = time.time() - start
    
    # Second cached request (cache hit)
    start = time.time()
    await cache_aside.get(
        f"user:{user_id}",
        lambda: load_user_from_db(user_id)
    )
    second_cached_time = time.time() - start
    
    return Response({
        "uncached_ms": round(uncached_time * 1000, 2),
        "cache_miss_ms": round(first_cached_time * 1000, 2),
        "cache_hit_ms": round(second_cached_time * 1000, 2),
        "speedup": round(uncached_time / second_cached_time, 2)
    })


if __name__ == "__main__":
    print("🚀 Starting Fennec Caching Example")
    print("📝 Endpoints:")
    print("   GET  /users/{user_id}       - Cached user lookup (@cache decorator)")
    print("   GET  /users-aside/{user_id} - Cache-aside pattern")
    print("   POST /users                 - Write-through pattern")
    print("   GET  /cache/stats           - Cache statistics")
    print("   POST /cache/clear           - Clear cache")
    print("   GET  /cache/health          - Cache health check")
    print("   GET  /benchmark             - Performance comparison")
    print("\n⚠️  Make sure Redis is running: docker run -d -p 6379:6379 redis")
    
    app.run(host="0.0.0.0", port=8000)
