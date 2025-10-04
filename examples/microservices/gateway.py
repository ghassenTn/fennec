"""
API Gateway - Microservice Example

Routes requests to appropriate microservices and aggregates responses.
"""

from fennec import Application, Router, JSONResponse, HTTPException, Request
import httpx
from typing import Optional


# Service URLs
USER_SERVICE_URL = "http://localhost:8001"
ORDER_SERVICE_URL = "http://localhost:8002"


# Create application
app = Application(title="API Gateway", version="1.0.0")
router = Router(prefix="/api")


# HTTP client for service communication
async def call_service(url: str, method: str = "GET", json_data: dict = None):
    """Call a microservice"""
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=json_data)
            elif method == "PUT":
                response = await client.put(url, json=json_data)
            elif method == "DELETE":
                response = await client.delete(url)
            else:
                raise HTTPException(400, f"Unsupported method: {method}")
            
            if response.status_code >= 400:
                raise HTTPException(response.status_code, response.json().get("message", "Service error"))
            
            return response.json()
        
        except httpx.ConnectError:
            raise HTTPException(503, "Service unavailable")


# User endpoints (proxy to user service)
@router.get("/users")
async def get_users():
    """Get all users"""
    data = await call_service(f"{USER_SERVICE_URL}/api/users")
    return JSONResponse(data=data)


@router.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user by ID"""
    data = await call_service(f"{USER_SERVICE_URL}/api/users/{user_id}")
    return JSONResponse(data=data)


@router.post("/users")
async def create_user(request: Request):
    """Create new user"""
    body = await request.json()
    data = await call_service(f"{USER_SERVICE_URL}/api/users", method="POST", json_data=body)
    return JSONResponse(data=data, status_code=201)


# Order endpoints (proxy to order service)
@router.get("/orders")
async def get_orders(user_id: Optional[int] = None, status: Optional[str] = None):
    """Get all orders"""
    url = f"{ORDER_SERVICE_URL}/api/orders"
    params = []
    if user_id:
        params.append(f"user_id={user_id}")
    if status:
        params.append(f"status={status}")
    
    if params:
        url += "?" + "&".join(params)
    
    data = await call_service(url)
    return JSONResponse(data=data)


@router.get("/orders/{order_id}")
async def get_order(order_id: int):
    """Get order by ID"""
    data = await call_service(f"{ORDER_SERVICE_URL}/api/orders/{order_id}")
    return JSONResponse(data=data)


@router.post("/orders")
async def create_order(request: Request):
    """Create new order"""
    body = await request.json()
    data = await call_service(f"{ORDER_SERVICE_URL}/api/orders", method="POST", json_data=body)
    return JSONResponse(data=data, status_code=201)


# Aggregated endpoints (combine data from multiple services)
@router.get("/users/{user_id}/profile")
async def get_user_profile(user_id: int):
    """Get user profile with their orders"""
    # Get user data
    user_data = await call_service(f"{USER_SERVICE_URL}/api/users/{user_id}")
    
    # Get user's orders
    orders_data = await call_service(f"{ORDER_SERVICE_URL}/api/orders/user/{user_id}")
    
    # Combine data
    profile = {
        "user": user_data.get("data"),
        "orders": orders_data.get("data"),
        "total_orders": len(orders_data.get("data", []))
    }
    
    return JSONResponse(data=profile)


@router.get("/dashboard")
async def get_dashboard():
    """Get dashboard with aggregated statistics"""
    # Get data from both services
    users_data = await call_service(f"{USER_SERVICE_URL}/api/users")
    orders_data = await call_service(f"{ORDER_SERVICE_URL}/api/orders")
    
    users = users_data.get("data", [])
    orders = orders_data.get("data", [])
    
    # Calculate statistics
    dashboard = {
        "total_users": len(users),
        "total_orders": len(orders),
        "pending_orders": len([o for o in orders if o.get("status") == "pending"]),
        "completed_orders": len([o for o in orders if o.get("status") == "completed"]),
        "total_revenue": sum(o.get("total", 0) for o in orders if o.get("status") == "completed")
    }
    
    return JSONResponse(data=dashboard)


@router.get("/health")
async def health_check():
    """Health check for all services"""
    services = {}
    
    # Check user service
    try:
        user_health = await call_service(f"{USER_SERVICE_URL}/api/users/health")
        services["user_service"] = user_health.get("data", {})
    except:
        services["user_service"] = {"status": "unhealthy"}
    
    # Check order service
    try:
        order_health = await call_service(f"{ORDER_SERVICE_URL}/api/orders/health")
        services["order_service"] = order_health.get("data", {})
    except:
        services["order_service"] = {"status": "unhealthy"}
    
    # Overall status
    all_healthy = all(s.get("status") == "healthy" for s in services.values())
    
    return JSONResponse(data={
        "gateway": "healthy",
        "services": services,
        "overall_status": "healthy" if all_healthy else "degraded"
    })


app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    print("🦊 API Gateway")
    print("=" * 50)
    print("Running on http://localhost:8000")
    print("\nRouting to:")
    print(f"  - User Service: {USER_SERVICE_URL}")
    print(f"  - Order Service: {ORDER_SERVICE_URL}")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
