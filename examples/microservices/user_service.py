"""
User Service - Microservice Example

Handles user management operations.
"""

from fennec import Application, Router, JSONResponse, HTTPException
from typing import List, Optional
from dataclasses import dataclass, asdict


@dataclass
class User:
    id: int
    name: str
    email: str
    role: str = "user"


# In-memory database
users_db: List[User] = [
    User(id=1, name="Alice Johnson", email="alice@example.com", role="admin"),
    User(id=2, name="Bob Smith", email="bob@example.com", role="user"),
    User(id=3, name="Charlie Brown", email="charlie@example.com", role="user"),
]
next_id = 4


# Create application
app = Application(title="User Service", version="1.0.0")
router = Router(prefix="/api/users")


@router.get("/")
async def get_users():
    """Get all users"""
    return JSONResponse(data=[asdict(u) for u in users_db])


@router.get("/{user_id}")
async def get_user(user_id: int):
    """Get user by ID"""
    for user in users_db:
        if user.id == user_id:
            return JSONResponse(data=asdict(user))
    
    raise HTTPException(404, f"User {user_id} not found")


@router.post("/")
async def create_user(name: str, email: str, role: str = "user"):
    """Create new user"""
    global next_id
    
    # Check if email exists
    for user in users_db:
        if user.email == email:
            raise HTTPException(400, f"Email {email} already exists")
    
    new_user = User(id=next_id, name=name, email=email, role=role)
    users_db.append(new_user)
    next_id += 1
    
    return JSONResponse(data=asdict(new_user), status_code=201)


@router.put("/{user_id}")
async def update_user(user_id: int, name: Optional[str] = None, email: Optional[str] = None):
    """Update user"""
    for user in users_db:
        if user.id == user_id:
            if name:
                user.name = name
            if email:
                user.email = email
            return JSONResponse(data=asdict(user))
    
    raise HTTPException(404, f"User {user_id} not found")


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    """Delete user"""
    global users_db
    
    for i, user in enumerate(users_db):
        if user.id == user_id:
            users_db.pop(i)
            return JSONResponse(data={"message": "User deleted"})
    
    raise HTTPException(404, f"User {user_id} not found")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(data={
        "service": "user-service",
        "status": "healthy",
        "users_count": len(users_db)
    })


app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    print("🦊 User Service")
    print("Running on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
