"""
Fennec Message Queue Example

Demonstrates async task processing with message queues.
"""

import asyncio
from fennec import Application, Request, Response
from fennec.queue import QueueManager


# Initialize app
app = Application()

# Initialize queue manager (using Redis backend)
queue = QueueManager(backend="redis", connection_url="redis://localhost:6379")


# Define tasks
@queue.task(queue_name="emails", max_retries=3)
async def send_email(to: str, subject: str, body: str):
    """Send email task."""
    print(f"📧 Sending email to {to}")
    print(f"   Subject: {subject}")
    print(f"   Body: {body}")
    
    # Simulate email sending
    await asyncio.sleep(2)
    
    print(f"✓ Email sent to {to}")
    return {"status": "sent", "to": to}


@queue.task(queue_name="notifications", max_retries=2)
async def send_notification(user_id: int, message: str):
    """Send notification task."""
    print(f"🔔 Sending notification to user {user_id}: {message}")
    
    # Simulate notification
    await asyncio.sleep(1)
    
    print(f"✓ Notification sent to user {user_id}")
    return {"status": "sent", "user_id": user_id}


@queue.task(queue_name="reports", max_retries=1)
async def generate_report(report_type: str, user_id: int):
    """Generate report task."""
    print(f"📊 Generating {report_type} report for user {user_id}")
    
    # Simulate report generation
    await asyncio.sleep(5)
    
    print(f"✓ Report generated: {report_type}")
    return {"status": "completed", "report_type": report_type}


@queue.task(queue_name="processing")
async def process_data(data: dict):
    """Process data task."""
    print(f"⚙️  Processing data: {data}")
    
    # Simulate processing
    await asyncio.sleep(3)
    
    print(f"✓ Data processed")
    return {"status": "processed", "data": data}


# API endpoints
@app.post("/emails/send")
async def enqueue_email(request: Request):
    """Enqueue email sending task."""
    data = await request.json()
    
    result = await send_email(
        to=data['to'],
        subject=data['subject'],
        body=data['body']
    )
    
    return Response({
        "message": "Email queued for sending",
        "result": result
    })


@app.post("/notifications/send")
async def enqueue_notification(request: Request):
    """Enqueue notification task."""
    data = await request.json()
    
    result = await send_notification(
        user_id=data['user_id'],
        message=data['message']
    )
    
    return Response({
        "message": "Notification queued",
        "result": result
    })


@app.post("/reports/generate")
async def enqueue_report(request: Request):
    """Enqueue report generation task."""
    data = await request.json()
    
    result = await generate_report(
        report_type=data['report_type'],
        user_id=data['user_id']
    )
    
    return Response({
        "message": "Report generation queued",
        "result": result
    })


@app.post("/data/process")
async def enqueue_processing(request: Request):
    """Enqueue data processing task."""
    data = await request.json()
    
    result = await process_data(data=data)
    
    return Response({
        "message": "Data processing queued",
        "result": result
    })


@app.get("/queues/status")
async def queue_status(request: Request):
    """Get queue status."""
    await queue.connect()
    
    queues = ["emails", "notifications", "reports", "processing"]
    status = {}
    
    for queue_name in queues:
        size = await queue.get_queue_size(queue_name)
        status[queue_name] = {
            "size": size,
            "status": "active" if size > 0 else "idle"
        }
    
    return Response(status)


@app.post("/queues/{queue_name}/purge")
async def purge_queue_endpoint(request: Request):
    """Purge a queue."""
    queue_name = request.path_params['queue_name']
    
    await queue.connect()
    await queue.purge_queue(queue_name)
    
    return Response({
        "message": f"Queue {queue_name} purged"
    })


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        # Run worker
        from fennec.queue import Worker
        
        print("🔧 Starting Fennec Queue Worker")
        print("📋 Processing queues: emails, notifications, reports, processing")
        
        worker = Worker(
            queue,
            queue_names=["emails", "notifications", "reports", "processing"],
            concurrency=2
        )
        
        try:
            asyncio.run(worker.start())
        except KeyboardInterrupt:
            print("\n⏹️  Stopping worker...")
            asyncio.run(worker.stop())
    else:
        # Run web server
        print("🚀 Starting Fennec Message Queue Example")
        print("📝 Endpoints:")
        print("   POST /emails/send         - Queue email")
        print("   POST /notifications/send  - Queue notification")
        print("   POST /reports/generate    - Queue report")
        print("   POST /data/process        - Queue data processing")
        print("   GET  /queues/status       - Queue status")
        print("   POST /queues/{name}/purge - Purge queue")
        print("\n💡 Start worker in another terminal:")
        print("   python server.py worker")
        print("\n⚠️  Make sure Redis is running:")
        print("   docker run -d -p 6379:6379 redis")
        
        app.run(host="0.0.0.0", port=8000)
