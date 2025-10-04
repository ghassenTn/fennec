"""
Queue Manager

Manages message queues with backend abstraction.
"""

import asyncio
import json
from typing import Any, Callable, Dict, Optional
from functools import wraps


class QueueManager:
    """Message queue manager with backend abstraction."""
    
    def __init__(
        self,
        backend: str = "redis",
        connection_url: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize queue manager.
        
        Args:
            backend: Backend type ('redis', 'rabbitmq', 'sqs')
            connection_url: Connection URL for backend
            **kwargs: Additional backend-specific options
        """
        self.backend_type = backend
        self.connection_url = connection_url
        self.backend = None
        self.tasks = {}
        self.options = kwargs
    
    async def connect(self):
        """Connect to queue backend."""
        if self.backend_type == "redis":
            from .backends.redis import RedisBackend
            self.backend = RedisBackend(self.connection_url, **self.options)
        elif self.backend_type == "rabbitmq":
            from .backends.rabbitmq import RabbitMQBackend
            self.backend = RabbitMQBackend(self.connection_url, **self.options)
        elif self.backend_type == "sqs":
            from .backends.sqs import SQSBackend
            self.backend = SQSBackend(self.connection_url, **self.options)
        else:
            raise ValueError(f"Unknown backend: {self.backend_type}")
        
        await self.backend.connect()
    
    async def disconnect(self):
        """Disconnect from queue backend."""
        if self.backend:
            await self.backend.disconnect()
    
    def task(
        self,
        queue_name: str = "default",
        max_retries: int = 3,
        retry_delay: int = 60
    ):
        """
        Decorator to register a task.
        
        Args:
            queue_name: Queue name
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries in seconds
            
        Example:
            @queue.task(queue_name="emails")
            async def send_email(to: str, subject: str):
                # Send email
                pass
        """
        def decorator(func: Callable):
            task_name = func.__name__
            
            self.tasks[task_name] = {
                'func': func,
                'queue_name': queue_name,
                'max_retries': max_retries,
                'retry_delay': retry_delay
            }
            
            @wraps(func)
            async def wrapper(*args, **kwargs):
                """Enqueue task for async execution."""
                if not self.backend:
                    await self.connect()
                
                message = {
                    'task': task_name,
                    'args': args,
                    'kwargs': kwargs,
                    'retries': 0
                }
                
                await self.backend.publish(queue_name, message)
                return f"Task {task_name} enqueued"
            
            # Add direct execution method
            wrapper.run = func
            
            return wrapper
        
        return decorator
    
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
            delay: Delay in seconds (for scheduled messages)
        """
        if not self.backend:
            await self.connect()
        
        await self.backend.publish(queue_name, message, delay=delay)
    
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
            callback: Callback function for messages
            prefetch_count: Number of messages to prefetch
        """
        if not self.backend:
            await self.connect()
        
        await self.backend.consume(queue_name, callback, prefetch_count)
    
    async def get_queue_size(self, queue_name: str) -> int:
        """
        Get queue size.
        
        Args:
            queue_name: Queue name
            
        Returns:
            Number of messages in queue
        """
        if not self.backend:
            await self.connect()
        
        return await self.backend.get_queue_size(queue_name)
    
    async def purge_queue(self, queue_name: str):
        """
        Purge all messages from queue.
        
        Args:
            queue_name: Queue name
        """
        if not self.backend:
            await self.connect()
        
        await self.backend.purge_queue(queue_name)
    
    def get_task(self, task_name: str) -> Optional[Dict]:
        """
        Get registered task.
        
        Args:
            task_name: Task name
            
        Returns:
            Task configuration or None
        """
        return self.tasks.get(task_name)
