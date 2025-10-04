"""
Queue Worker

Processes messages from queues with retry logic.
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime


logger = logging.getLogger(__name__)


class Worker:
    """Message queue worker."""
    
    def __init__(
        self,
        queue_manager,
        queue_names: list = None,
        concurrency: int = 1
    ):
        """
        Initialize worker.
        
        Args:
            queue_manager: QueueManager instance
            queue_names: List of queue names to process
            concurrency: Number of concurrent workers
        """
        self.queue_manager = queue_manager
        self.queue_names = queue_names or ["default"]
        self.concurrency = concurrency
        self.running = False
        self.tasks = []
    
    async def start(self):
        """Start worker processes."""
        self.running = True
        
        logger.info(f"Starting {self.concurrency} worker(s) for queues: {self.queue_names}")
        
        # Connect to backend
        await self.queue_manager.connect()
        
        # Start worker tasks
        for i in range(self.concurrency):
            for queue_name in self.queue_names:
                task = asyncio.create_task(
                    self._worker_loop(queue_name, i)
                )
                self.tasks.append(task)
        
        # Wait for all tasks
        await asyncio.gather(*self.tasks)
    
    async def stop(self):
        """Stop worker processes."""
        logger.info("Stopping workers...")
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for cancellation
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # Disconnect
        await self.queue_manager.disconnect()
        
        logger.info("Workers stopped")
    
    async def _worker_loop(self, queue_name: str, worker_id: int):
        """
        Worker loop for processing messages.
        
        Args:
            queue_name: Queue name to process
            worker_id: Worker ID
        """
        logger.info(f"Worker {worker_id} started for queue: {queue_name}")
        
        while self.running:
            try:
                await self.queue_manager.consume(
                    queue_name,
                    self._process_message,
                    prefetch_count=1
                )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(5)  # Wait before retry
    
    async def _process_message(self, message: Dict[str, Any]):
        """
        Process a message.
        
        Args:
            message: Message to process
        """
        task_name = message.get('task')
        args = message.get('args', [])
        kwargs = message.get('kwargs', {})
        retries = message.get('retries', 0)
        
        # Get task configuration
        task_config = self.queue_manager.get_task(task_name)
        
        if not task_config:
            logger.error(f"Unknown task: {task_name}")
            return
        
        task_func = task_config['func']
        max_retries = task_config['max_retries']
        retry_delay = task_config['retry_delay']
        
        try:
            logger.info(f"Processing task: {task_name}")
            start_time = datetime.now()
            
            # Execute task
            result = await task_func(*args, **kwargs)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Task {task_name} completed in {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Task {task_name} failed: {e}")
            
            # Retry logic
            if retries < max_retries:
                logger.info(f"Retrying task {task_name} (attempt {retries + 1}/{max_retries})")
                
                # Update retry count
                message['retries'] = retries + 1
                
                # Re-queue with delay
                await self.queue_manager.publish(
                    task_config['queue_name'],
                    message,
                    delay=retry_delay * (retries + 1)  # Exponential backoff
                )
            else:
                logger.error(f"Task {task_name} failed after {max_retries} retries")
                # TODO: Move to dead letter queue
