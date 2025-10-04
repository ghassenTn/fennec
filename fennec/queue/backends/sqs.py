"""
AWS SQS Queue Backend

Implements message queue using AWS SQS.
"""

import json
from typing import Any, Callable, Optional


class SQSBackend:
    """AWS SQS-based message queue backend."""
    
    def __init__(
        self,
        url: Optional[str] = None,
        region: str = "us-east-1",
        **kwargs
    ):
        """
        Initialize SQS backend.
        
        Args:
            url: Queue URL (optional, can be constructed from queue name)
            region: AWS region
            **kwargs: Additional options (aws_access_key_id, aws_secret_access_key)
        """
        self.url = url
        self.region = region
        self.client = None
        self.options = kwargs
    
    async def connect(self):
        """Connect to AWS SQS."""
        try:
            import aioboto3
        except ImportError:
            raise ImportError(
                "aioboto3 package is required for SQS backend. "
                "Install it with: pip install aioboto3"
            )
        
        session = aioboto3.Session()
        self.client = await session.client(
            'sqs',
            region_name=self.region,
            **self.options
        ).__aenter__()
    
    async def disconnect(self):
        """Disconnect from AWS SQS."""
        if self.client:
            await self.client.__aexit__(None, None, None)
    
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
            delay: Delay in seconds (max 900 for SQS)
        """
        # Get queue URL
        queue_url = await self._get_queue_url(queue_name)
        
        # Serialize message
        body = json.dumps(message)
        
        # Send message
        params = {
            'QueueUrl': queue_url,
            'MessageBody': body
        }
        
        if delay:
            params['DelaySeconds'] = min(delay, 900)  # SQS max delay
        
        await self.client.send_message(**params)
    
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
            prefetch_count: Number of messages to receive
        """
        # Get queue URL
        queue_url = await self._get_queue_url(queue_name)
        
        while True:
            # Receive messages
            response = await self.client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=prefetch_count,
                WaitTimeSeconds=20  # Long polling
            )
            
            messages = response.get('Messages', [])
            
            for msg in messages:
                # Parse message
                data = json.loads(msg['Body'])
                
                # Process message
                await callback(data)
                
                # Delete message
                await self.client.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=msg['ReceiptHandle']
                )
    
    async def get_queue_size(self, queue_name: str) -> int:
        """Get queue size."""
        queue_url = await self._get_queue_url(queue_name)
        
        response = await self.client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['ApproximateNumberOfMessages']
        )
        
        return int(response['Attributes']['ApproximateNumberOfMessages'])
    
    async def purge_queue(self, queue_name: str):
        """Purge queue."""
        queue_url = await self._get_queue_url(queue_name)
        await self.client.purge_queue(QueueUrl=queue_url)
    
    async def _get_queue_url(self, queue_name: str) -> str:
        """Get queue URL from name."""
        if self.url:
            return self.url
        
        response = await self.client.get_queue_url(QueueName=queue_name)
        return response['QueueUrl']
