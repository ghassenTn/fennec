"""
RabbitMQ Queue Backend

Implements message queue using RabbitMQ.
"""

import json
import asyncio
from typing import Any, Callable, Optional


class RabbitMQBackend:
    """RabbitMQ-based message queue backend."""
    
    def __init__(self, url: str = "amqp://guest:guest@localhost/", **kwargs):
        """
        Initialize RabbitMQ backend.
        
        Args:
            url: RabbitMQ connection URL
            **kwargs: Additional options
        """
        self.url = url
        self.connection = None
        self.channel = None
        self.options = kwargs
    
    async def connect(self):
        """Connect to RabbitMQ."""
        try:
            import aio_pika
        except ImportError:
            raise ImportError(
                "aio-pika package is required for RabbitMQ backend. "
                "Install it with: pip install aio-pika"
            )
        
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)
    
    async def disconnect(self):
        """Disconnect from RabbitMQ."""
        if self.connection:
            await self.connection.close()
    
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
            delay: Delay in seconds
        """
        import aio_pika
        
        # Declare queue
        queue = await self.channel.declare_queue(queue_name, durable=True)
        
        # Serialize message
        body = json.dumps(message).encode()
        
        # Create message
        msg = aio_pika.Message(
            body=body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        
        if delay:
            # Use delayed exchange (requires rabbitmq_delayed_message_exchange plugin)
            msg.headers = {'x-delay': delay * 1000}  # milliseconds
        
        # Publish
        await self.channel.default_exchange.publish(
            msg,
            routing_key=queue_name
        )
    
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
        # Declare queue
        queue = await self.channel.declare_queue(queue_name, durable=True)
        
        # Set prefetch
        await self.channel.set_qos(prefetch_count=prefetch_count)
        
        async def process_message(message):
            async with message.process():
                data = json.loads(message.body.decode())
                await callback(data)
        
        # Start consuming
        await queue.consume(process_message)
        
        # Keep consuming
        await asyncio.Future()
    
    async def get_queue_size(self, queue_name: str) -> int:
        """Get queue size."""
        queue = await self.channel.declare_queue(queue_name, durable=True)
        return queue.declaration_result.message_count
    
    async def purge_queue(self, queue_name: str):
        """Purge queue."""
        queue = await self.channel.declare_queue(queue_name, durable=True)
        await queue.purge()
