"""
Order Service - Microservice Example

Handles order management operations.
"""

from fennec import Application, Router, JSONResponse, HTTPException
from typing import List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Order:
    id: int
    user_id: int
    product: str
    quantity: int
    total: float
    status: str = "pending"
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


# In-memory database
orders_db: List[Order] = [
    Order(id=1, user_id=1, product="Laptop", quantity=1, total=999.99, status="completed"),
    Order(id=2, user_id=2, product="Mouse", quantity=2, total=49.98, status="shipped"),
    Order(id=3, user_id=1, product="Keyboard", quantity=1, total=79.99, status="pending"),
]
next_id = 4


# Create application
app = Application(title="Order Service", version="1.0.0")
router = Router(prefix="/api/orders")


@router.get("/")
async def get_orders(user_id: Optional[int] = None, status: Optional[str] = None):
    """Get all orders with optional filters"""
    filtered_orders = orders_db
    
    if user_id is not None:
        filtered_orders = [o for o in filtered_orders if o.user_id == user_id]
    
    if status:
        filtered_orders = [o for o in filtered_orders if o.status == status]
    
    return JSONResponse(data=[asdict(o) for o in filtered_orders])


@router.get("/{order_id}")
async def get_order(order_id: int):
    """Get order by ID"""
    for order in orders_db:
        if order.id == order_id:
            return JSONResponse(data=asdict(order))
    
    raise HTTPException(404, f"Order {order_id} not found")


@router.post("/")
async def create_order(user_id: int, product: str, quantity: int, total: float):
    """Create new order"""
    global next_id
    
    new_order = Order(
        id=next_id,
        user_id=user_id,
        product=product,
        quantity=quantity,
        total=total,
        status="pending"
    )
    
    orders_db.append(new_order)
    next_id += 1
    
    return JSONResponse(data=asdict(new_order), status_code=201)


@router.put("/{order_id}/status")
async def update_order_status(order_id: int, status: str):
    """Update order status"""
    valid_statuses = ["pending", "processing", "shipped", "completed", "cancelled"]
    
    if status not in valid_statuses:
        raise HTTPException(400, f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    for order in orders_db:
        if order.id == order_id:
            order.status = status
            return JSONResponse(data=asdict(order))
    
    raise HTTPException(404, f"Order {order_id} not found")


@router.delete("/{order_id}")
async def cancel_order(order_id: int):
    """Cancel order"""
    for order in orders_db:
        if order.id == order_id:
            if order.status in ["shipped", "completed"]:
                raise HTTPException(400, "Cannot cancel shipped or completed orders")
            
            order.status = "cancelled"
            return JSONResponse(data=asdict(order))
    
    raise HTTPException(404, f"Order {order_id} not found")


@router.get("/user/{user_id}")
async def get_user_orders(user_id: int):
    """Get all orders for a specific user"""
    user_orders = [o for o in orders_db if o.user_id == user_id]
    return JSONResponse(data=[asdict(o) for o in user_orders])


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(data={
        "service": "order-service",
        "status": "healthy",
        "orders_count": len(orders_db)
    })


app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    print("🦊 Order Service")
    print("Running on http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
