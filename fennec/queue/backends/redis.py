"""
Redis Queue Backend

Implements message queue using Redis lists.
"""

import json
import asyncio
from typing import Any, Callable, Optional


class RedisBackend:
    """Redis-based message queue backend."""
    
    def __init__(self, url: str = "redis://localhost:6379", **kwargs):
        """
        Initialize Redis backend.
        
        Args:
            url: Redis connection URL
            **kwargs: Additional options
        """
        self.url = url
        self.client = None
        self.options = kwargs
    
    async def connect(self):
        """Connect to Redis."""
        try:
            import redis.asyncio as aioredis
        except ImportError:
            raise ImportError(
                "redis package is required for Redis backend. "
                "Install it with: pip install redis"
            )
        
        self.client = await aioredis.from_url(self.url)
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
    
    async def publish(
        self,
        queue_name: str,
        message: Any,
        delay: Optional[int] = None
    ):
        """
        Publish message to queue.
        
        Args:
            queue_name: Queue name
            message: Message to publish
            delay: Delay in seconds (not supported in basic Redis)
        """
        serialized = json.dumps(message)
        
        if delay:
            # Use sorted set for delayed messages
            score = asyncio.get_event_loop().time() + delay
            await self.client.zadd(f"{queue_name}:delayed", {serialized: score})
        else:
            await self.client.rpush(queue_name, serialized)
    
    async def consume(
        self,
        queue_name: str,
        callback: Callable,
        prefetch_count: int = 1
    ):
        """
        Consume messages from queue.
        
        Args:
            queue_name: Queue name
            callback: Callback function
            prefetch_count: Number of messages to prefetch
        """
        while True:
            # Check for delayed messages
            await self._process_delayed_messages(queue_name)
            
            # Blocking pop from queue
            result = await self.client.blpop(queue_name, timeout=1)
            
            if result:
                _, message_data = result
                message = json.loads(message_data)
                await callback(message)
    
    async def _process_delayed_messages(self, queue_name: str):
        """Process delayed messages that are ready."""
        current_time = asyncio.get_event_loop().time()
        
        # Get messages ready to be processed
        messages = await self.client.zrangebyscore(
            f"{queue_name}:delayed",
            0,
            current_time
        )
        
        for message_data in messages:
            # Move to main queue
            await self.client.rpush(queue_name, message_data)
            await self.client.zrem(f"{queue_name}:delayed", message_data)
    
    async def get_queue_size(self, queue_name: str) -> int:
        """Get queue size."""
        return await self.client.llen(queue_name)
    
    async def purge_queue(self, queue_name: str):
        """Purge queue."""
        await self.client.delete(queue_name)
        await self.client.delete(f"{queue_name}:delayed")
