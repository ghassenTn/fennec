# Fennec Message Queue Example

Demonstrates asynchronous task processing with message queues.

## Features

- **Multiple Backends**: Redis, RabbitMQ, AWS SQS
- **Task Decorators**: Simple @task decorator for async functions
- **Retry Logic**: Automatic retry with exponential backoff
- **Worker Processes**: Concurrent message processing
- **Pub/Sub Pattern**: Publish and subscribe to queues
- **Delayed Messages**: Schedule tasks for future execution

## Installation

### Redis Backend
```bash
pip install redis
docker run -d -p 6379:6379 redis
```

### RabbitMQ Backend
```bash
pip install aio-pika
docker run -d -p 5672:5672 rabbitmq
```

### AWS SQS Backend
```bash
pip install aioboto3
# Configure AWS credentials
```

## Running the Example

### 1. Start the Web Server

```bash
python server.py
```

### 2. Start Worker Processes

In another terminal:

```bash
python server.py worker
```

## Usage

### Queue Email Task

```bash
curl -X POST http://localhost:8000/emails/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "user@example.com",
    "subject": "Hello",
    "body": "This is a test email"
  }'
```

### Queue Notification

```bash
curl -X POST http://localhost:8000/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "message": "You have a new message"
  }'
```

### Generate Report

```bash
curl -X POST http://localhost:8000/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "monthly",
    "user_id": 456
  }'
```

### Check Queue Status

```bash
curl http://localhost:8000/queues/status
```

Response:
```json
{
  "emails": {"size": 3, "status": "active"},
  "notifications": {"size": 0, "status": "idle"},
  "reports": {"size": 1, "status": "active"},
  "processing": {"size": 0, "status": "idle"}
}
```

### Purge Queue

```bash
curl -X POST http://localhost:8000/queues/emails/purge
```

## Task Definition

Define tasks with the @task decorator:

```python
from fennec.queue import QueueManager

queue = QueueManager(backend="redis")

@queue.task(queue_name="emails", max_retries=3)
async def send_email(to: str, subject: str, body: str):
    # Send email logic
    await email_service.send(to, subject, body)
    return {"status": "sent"}
```

## Worker Configuration

Configure workers for specific queues:

```python
from fennec.queue import Worker

worker = Worker(
    queue_manager=queue,
    queue_names=["emails", "notifications"],
    concurrency=4  # 4 concurrent workers
)

await worker.start()
```

## Backend Configuration

### Redis

```python
queue = QueueManager(
    backend="redis",
    connection_url="redis://localhost:6379"
)
```

### RabbitMQ

```python
queue = QueueManager(
    backend="rabbitmq",
    connection_url="amqp://guest:guest@localhost/"
)
```

### AWS SQS

```python
queue = QueueManager(
    backend="sqs",
    region="us-east-1",
    aws_access_key_id="YOUR_KEY",
    aws_secret_access_key="YOUR_SECRET"
)
```

## Retry Logic

Tasks automatically retry on failure:

```python
@queue.task(
    queue_name="emails",
    max_retries=3,      # Retry up to 3 times
    retry_delay=60      # Wait 60s between retries
)
async def send_email(to: str):
    # If this fails, it will retry with exponential backoff
    pass
```

Retry delays:
- 1st retry: 60s
- 2nd retry: 120s
- 3rd retry: 180s

## Delayed Messages

Schedule tasks for future execution:

```python
# Publish with delay
await queue.publish(
    "emails",
    {"to": "user@example.com", "subject": "Reminder"},
    delay=3600  # Execute in 1 hour
)
```

## Patterns

### Work Queue

Multiple workers process tasks from a single queue:

```python
# Worker 1
worker1 = Worker(queue, queue_names=["tasks"], concurrency=2)

# Worker 2
worker2 = Worker(queue, queue_names=["tasks"], concurrency=2)
```

### Topic-based Routing

Use different queues for different task types:

```python
@queue.task(queue_name="high_priority")
async def urgent_task():
    pass

@queue.task(queue_name="low_priority")
async def background_task():
    pass
```

## Monitoring

Track queue metrics:

```python
# Get queue size
size = await queue.get_queue_size("emails")

# Purge queue
await queue.purge_queue("emails")
```

## Production Tips

1. **Multiple Workers**: Run multiple worker processes for throughput
2. **Queue Separation**: Use separate queues for different priorities
3. **Dead Letter Queues**: Handle failed messages
4. **Monitoring**: Track queue depth and processing time
5. **Graceful Shutdown**: Handle SIGTERM for clean worker shutdown

## Troubleshooting

### Tasks not processing

- Check worker is running
- Verify queue backend is accessible
- Check worker logs for errors

### High queue depth

- Increase worker concurrency
- Add more worker processes
- Optimize task execution time

### Connection errors

- Verify backend is running
- Check connection URL
- Review firewall rules
