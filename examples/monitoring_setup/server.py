"""
Fennec Monitoring Example

Demonstrates Prometheus metrics, distributed tracing, and structured logging.
"""

import asyncio
import time
from fennec import Application, Request, Response
from fennec.monitoring import PrometheusMetrics, RequestTracer, StructuredLogger
from fennec.monitoring.metrics import MetricsMiddleware
from fennec.monitoring.tracing import TracingMiddleware
from fennec.monitoring.logging import LoggingMiddleware
from fennec.monitoring.health import HealthCheck


# Initialize app
app = Application()

# Initialize monitoring components
metrics = PrometheusMetrics(app_name="demo_app")
tracer = RequestTracer(service_name="demo_app")
logger = StructuredLogger(name="demo_app")
health = HealthCheck(service_name="demo_app")

# Add middleware
app.add_middleware(MetricsMiddleware(metrics))
app.add_middleware(TracingMiddleware(tracer))
app.add_middleware(LoggingMiddleware(logger))


# Health checks
async def check_database():
    """Simulate database health check."""
    await asyncio.sleep(0.01)
    return True


async def check_cache():
    """Simulate cache health check."""
    await asyncio.sleep(0.01)
    return True


health.add_check("database", check_database)
health.add_check("cache", check_cache)


# Monitoring endpoints
@app.get("/metrics")
async def get_metrics(request: Request):
    """Prometheus metrics endpoint."""
    metrics_data = metrics.generate_metrics()
    return Response(
        metrics_data,
        content_type=metrics.get_content_type()
    )


@app.get("/health")
async def health_check(request: Request):
    """Detailed health check."""
    result = await health.run_checks()
    status = 200 if result['status'] == 'healthy' else 503
    return Response(result, status=status)


@app.get("/health/live")
async def liveness_probe(request: Request):
    """Kubernetes liveness probe."""
    result = await health.liveness()
    return Response(result)


@app.get("/health/ready")
async def readiness_probe(request: Request):
    """Kubernetes readiness probe."""
    result = await health.readiness()
    status = 200 if result['status'] == 'healthy' else 503
    return Response(result, status=status)


# Example endpoints
@app.get("/")
async def index(request: Request):
    """Index endpoint."""
    logger.info("Index page accessed")
    return Response({"message": "Monitoring Demo", "version": "1.0.0"})


@app.get("/users/{user_id}")
async def get_user(request: Request):
    """Get user with tracing."""
    user_id = request.path_params['user_id']
    
    # Start a span for database query
    span_id = tracer.start_span(
        "database.query",
        attributes={'query': 'SELECT * FROM users', 'user_id': user_id}
    )
    
    # Simulate database query
    await asyncio.sleep(0.1)
    metrics.record_db_query("SELECT", 0.1)
    
    tracer.end_span(span_id)
    
    logger.info("User fetched", user_id=user_id)
    
    return Response({
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com"
    })


@app.post("/users")
async def create_user(request: Request):
    """Create user with metrics."""
    data = await request.json()
    
    # Record cache miss
    metrics.record_cache_miss()
    
    # Simulate database insert
    span_id = tracer.start_span("database.insert")
    await asyncio.sleep(0.05)
    metrics.record_db_query("INSERT", 0.05)
    tracer.end_span(span_id)
    
    logger.info("User created", username=data.get('username'))
    
    return Response({"message": "User created", "data": data}, status=201)


@app.get("/slow")
async def slow_endpoint(request: Request):
    """Slow endpoint for testing."""
    logger.warning("Slow endpoint called")
    await asyncio.sleep(2)
    return Response({"message": "This was slow"})


@app.get("/error")
async def error_endpoint(request: Request):
    """Error endpoint for testing."""
    logger.error("Intentional error triggered")
    raise ValueError("This is a test error")


@app.get("/cache-test")
async def cache_test(request: Request):
    """Test cache metrics."""
    # Simulate cache operations
    for _ in range(10):
        metrics.record_cache_hit()
    
    for _ in range(3):
        metrics.record_cache_miss()
    
    return Response({"message": "Cache metrics recorded"})


@app.get("/websocket-test")
async def websocket_test(request: Request):
    """Test WebSocket metrics."""
    # Simulate WebSocket activity
    metrics.record_websocket_connection(1)
    
    for _ in range(5):
        metrics.record_websocket_message("sent")
        metrics.record_websocket_message("received")
    
    metrics.record_websocket_connection(-1)
    
    return Response({"message": "WebSocket metrics recorded"})


if __name__ == "__main__":
    print("🚀 Starting Fennec Monitoring Example")
    print("📊 Endpoints:")
    print("   GET  /metrics          - Prometheus metrics")
    print("   GET  /health           - Detailed health check")
    print("   GET  /health/live      - Liveness probe")
    print("   GET  /health/ready     - Readiness probe")
    print("   GET  /                 - Index")
    print("   GET  /users/{id}       - Get user (with tracing)")
    print("   POST /users            - Create user")
    print("   GET  /slow             - Slow endpoint")
    print("   GET  /error            - Error endpoint")
    print("   GET  /cache-test       - Cache metrics test")
    print("   GET  /websocket-test   - WebSocket metrics test")
    print("\n📈 View metrics at: http://localhost:8000/metrics")
    print("💚 View health at: http://localhost:8000/health")
    
    app.run(host="0.0.0.0", port=8000)
