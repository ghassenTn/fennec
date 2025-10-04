# Fennec Framework 🦊 - Complete Example Guide

## Overview

This example demonstrates **ALL features** of Fennec Framework in one complete application.

## Features Demonstrated

### ✅ Core Features
- Routing with path parameters (`/users/{id}`)
- Query parameters
- Request body parsing
- JSON responses
- Exception handling

### ✅ Validation
- Type-hint based validation
- Custom validators
- Field constraints (min/max length)
- Automatic error messages

### ✅ Security
- JWT authentication
- Role-based authorization
- Protected routes with `@requires_auth`
- CORS middleware
- Rate limiting

### ✅ Advanced
- Dependency injection with `Depends()`
- Background tasks (email sending)
- Custom middleware (logging)
- Custom exception handlers
- OpenAPI/Swagger documentation

## Running the Example

### 1. Install Dependencies

```bash
pip install fennec-framework uvicorn
```

### 2. Run the Application

```bash
python main.py
```

Or with PYTHONPATH:
```bash
PYTHONPATH=$PWD python main.py
```

### 3. Open Your Browser

Visit: http://localhost:8001/docs

## API Endpoints

### Public Endpoints

#### GET /
Welcome message with API information

```bash
curl http://localhost:8001/
```

#### GET /health
Health check endpoint

```bash
curl http://localhost:8001/health
```

#### GET /users
List all users

```bash
curl http://localhost:8001/users
```

#### GET /users/{id}
Get user by ID

```bash
curl http://localhost:8001/users/1
```

#### POST /users
Create new user (with background task - sends welcome email)

```bash
curl -X POST http://localhost:8001/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
  }'
```

#### PUT /users/{id}
Update user

```bash
curl -X PUT http://localhost:8001/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Updated",
    "email": "john@example.com",
    "age": 31
  }'
```

#### DELETE /users/{id}
Delete user

```bash
curl -X DELETE http://localhost:8001/users/1
```

### Authentication Endpoints

#### POST /auth/login
Login and get JWT token

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@fennec.dev",
    "password": "admin123"
  }'
```

Response:
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "name": "Admin User",
      "email": "admin@fennec.dev",
      "role": "admin"
    }
  },
  "message": "Login successful"
}
```

#### GET /auth/me (Protected)
Get current user info

```bash
curl http://localhost:8001/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Admin Endpoints (Protected)

#### GET /admin/users (Admin Only)
List all users (admin only)

```bash
curl http://localhost:8001/admin/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### DELETE /admin/users/{id} (Admin Only)
Delete user (admin only)

```bash
curl -X DELETE http://localhost:8001/admin/users/2 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Testing with Swagger UI

### 1. Open Swagger UI
Visit: http://localhost:8001/docs

### 2. Login
1. Find **POST /auth/login**
2. Click "Try it out"
3. Use credentials:
   ```json
   {
     "email": "admin@fennec.dev",
     "password": "admin123"
   }
   ```
4. Click "Execute"
5. Copy the `access_token` from response

### 3. Authorize
1. Click the **"Authorize"** button (🔒 icon at top)
2. Paste your token
3. Click "Authorize"
4. Click "Close"

### 4. Test Protected Endpoints
Now you can test all protected endpoints:
- GET /auth/me
- GET /admin/users
- DELETE /admin/users/{id}

## Code Walkthrough

### 1. Application Setup

```python
from fennec import Application, Router, JSONResponse

app = Application(
    title="Fennec Framework Demo API 🦊",
    version="1.0.0",
    docs_enabled=True
)
```

### 2. Middleware

```python
# CORS
app.middleware_manager.add(
    CORSMiddleware(allow_origins=["*"])
)

# Rate Limiting
app.middleware_manager.add(
    RateLimitMiddleware(max_requests=100, window_seconds=60)
)

# Custom Logging
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"🦊 [{request.method}] {request.path}")
    response = await call_next(request)
    return response
```

### 3. Validation Models

```python
from fennec.validation import BaseModel, Field

class User(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: str
    age: int
    
    def validate_age(self, value):
        if value < 0 or value > 150:
            raise ValueError("Age must be between 0 and 150")
        return value
```

### 4. Dependency Injection

```python
from fennec.dependencies import Depends

def get_db():
    return users_db

@router.get("/users")
async def list_users(db=Depends(get_db)):
    return JSONResponse(data={"users": list(db.values())})
```

### 5. Authentication

```python
from fennec.security import JWTHandler, requires_auth

jwt_handler = JWTHandler(secret_key="your-secret-key")

@router.get("/protected")
@requires_auth
async def protected_route(request):
    user = get_current_user(request)
    return JSONResponse(data={"user": user})
```

### 6. Background Tasks

```python
from fennec.background import BackgroundTasks

background_tasks = BackgroundTasks()
background_tasks.add_task(send_welcome_email, email, name)

import asyncio
asyncio.create_task(background_tasks.execute_all())
```

### 7. Exception Handling

```python
from fennec.exceptions import NotFoundException

@app.exception_handler(ValueError)
async def handle_value_error(request, exc):
    return JSONResponse(
        message=str(exc),
        status="error",
        status_code=400
    )
```

## Features Breakdown

### Routing
- ✅ Path parameters: `/users/{id}`
- ✅ Query parameters: `/search?q=term`
- ✅ Multiple HTTP methods: GET, POST, PUT, DELETE
- ✅ Route prefixes: `/auth`, `/admin`

### Validation
- ✅ Automatic type validation
- ✅ Field constraints (min/max length)
- ✅ Custom validators
- ✅ Clear error messages

### Security
- ✅ JWT authentication
- ✅ Token-based auth
- ✅ Role-based access control
- ✅ Protected routes
- ✅ CORS support
- ✅ Rate limiting

### Middleware
- ✅ CORS middleware
- ✅ Rate limiting middleware
- ✅ Custom logging middleware
- ✅ Request/response modification

### Dependency Injection
- ✅ Database dependencies
- ✅ User authentication
- ✅ Easy testing with mocks

### Background Tasks
- ✅ Async task execution
- ✅ Non-blocking operations
- ✅ Email sending example

### Documentation
- ✅ Auto-generated Swagger UI
- ✅ OpenAPI 3.0 specification
- ✅ Interactive testing
- ✅ Request/response examples

## Production Considerations

### Security
⚠️ This example uses simplified security for demonstration:

1. **Passwords**: Use bcrypt for hashing
   ```python
   import bcrypt
   hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
   ```

2. **Secret Keys**: Use environment variables
   ```python
   import os
   secret_key = os.getenv("SECRET_KEY")
   ```

3. **HTTPS**: Deploy behind reverse proxy with TLS

4. **Rate Limiting**: Adjust limits for production

5. **CORS**: Specify exact origins, not "*"

### Database
Replace in-memory dict with real database:
```python
from fennec.db import DatabaseConnection

def get_db():
    db = DatabaseConnection("postgresql://...")
    return db
```

### Logging
Use structured logging:
```python
import logging
logger = logging.getLogger(__name__)
logger.info(f"Request: {request.method} {request.path}")
```

## Next Steps

1. **Customize**: Modify the example for your needs
2. **Add Features**: Add more endpoints and models
3. **Database**: Integrate with PostgreSQL/MySQL
4. **Deploy**: Deploy to production with proper security
5. **Monitor**: Add monitoring and logging

## Learn More

- [Fennec Documentation](README.md)
- [Security Guide](SECURITY_IMPROVEMENTS.md)
- [Production Readiness](PRODUCTION_READINESS.md)
- [API Documentation Guide](OPENAPI_GUIDE.md)

---

<div align="center">
  <strong>🦊 Fennec Framework 🦊</strong><br>
  Small, Swift, and Adaptable<br><br>
  Built with ❤️ in Tunisia 🇹🇳
</div>
