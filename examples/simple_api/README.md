# Simple API Example

مثال بسيط يوضح كيفية استخدام Lightweight Framework لبناء REST API.

## Features

- ✅ CRUD operations للـ users
- ✅ Validation باستخدام BaseModel
- ✅ Dependency injection
- ✅ Middleware (CORS, Rate Limiting, Logging)
- ✅ Custom exception handlers
- ✅ Auto-generated API documentation

## Running

```bash
# Install dependencies
pip install uvicorn

# Run the application
python examples/simple_api/main.py
```

## API Endpoints

### GET /
Welcome message

### GET /users
List all users

### GET /users/{id}
Get user by ID

### POST /users
Create new user

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
```

### PUT /users/{id}
Update user

**Request Body:**
```json
{
  "name": "John Updated",
  "email": "john.updated@example.com",
  "age": 31
}
```

### DELETE /users/{id}
Delete user

## API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation.

## Testing

```python
import asyncio
from fennec.testing import TestClient
from main import app

async def test_api():
    client = TestClient(app)
    
    # Test root endpoint
    response = await client.get("/")
    print(response.json())
    
    # Create user
    response = await client.post("/users", json_data={
        "name": "Test User",
        "email": "test@example.com",
        "age": 25
    })
    print(response.json())
    
    # List users
    response = await client.get("/users")
    print(response.json())

asyncio.run(test_api())
```
