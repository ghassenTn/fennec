"""
Fennec Admin Dashboard Example

Demonstrates the admin dashboard with real-time monitoring.
"""

import asyncio
import time
from fennec import Application, Request, Response
from fennec.admin import AdminDashboard


# Initialize app
app = Application()

# Initialize admin dashboard
admin = AdminDashboard(
    app,
    auth_required=False,  # Disable auth for demo
    prefix="/admin"
)


# Middleware to track metrics
@app.middleware
async def metrics_middleware(request: Request, handler):
    """Track request metrics."""
    start_time = time.time()
    
    try:
        response = await handler(request)
        duration = time.time() - start_time
        
        # Record request
        admin.metrics.record_request(
            method=request.method,
            endpoint=request.path,
            status=response.status,
            duration=duration
        )
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        
        # Record error
        admin.metrics.record_request(
            method=request.method,
            endpoint=request.path,
            status=500,
            duration=duration
        )
        admin.metrics.record_error(type(e).__name__)
        
        raise


# Example endpoints
@app.get("/")
async def index(request: Request):
    """Index endpoint."""
    return Response({
        "message": "Admin Dashboard Demo",
        "admin_url": "/admin"
    })


@app.get("/users/{user_id}")
async def get_user(request: Request):
    """Get user."""
    user_id = request.path_params['user_id']
    await asyncio.sleep(0.1)  # Simulate work
    
    return Response({
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com"
    })


@app.post("/users")
async def create_user(request: Request):
    """Create user."""
    data = await request.json()
    await asyncio.sleep(0.05)
    
    return Response({
        "message": "User created",
        "data": data
    }, status=201)


@app.get("/slow")
async def slow_endpoint(request: Request):
    """Slow endpoint for testing."""
    await asyncio.sleep(2)
    return Response({"message": "This was slow"})


@app.get("/error")
async def error_endpoint(request: Request):
    """Error endpoint for testing."""
    raise ValueError("This is a test error")


if __name__ == "__main__":
    print("🚀 Starting Fennec Admin Dashboard Example")
    print("📊 Admin Dashboard: http://localhost:8000/admin")
    print("📝 Test Endpoints:")
    print("   GET  /                - Index")
    print("   GET  /users/{id}      - Get user")
    print("   POST /users           - Create user")
    print("   GET  /slow            - Slow endpoint")
    print("   GET  /error           - Error endpoint")
    print("\n💡 Generate some traffic to see metrics in the dashboard!")
    
    app.run(host="0.0.0.0", port=8000)
