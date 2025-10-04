# How to Run the Framework

## ✅ Step 1: Verify Installation

```bash
python test_framework.py
```

Expected output:
```
Testing Lightweight Framework...
--------------------------------------------------

1. Testing GET /
   Status: 200
   ✓ Passed

2. Testing GET /users/123
   Status: 200
   ✓ Passed

3. Testing POST /users with validation
   Status: 201
   ✓ Passed

4. Testing validation error (name too short)
   Status: 500
   ✓ Passed (validation error caught)

5. Testing 404 Not Found
   Status: 404
   ✓ Passed

--------------------------------------------------
✓ All tests passed!

Framework is working correctly! 🎉
```

## ✅ Step 2: Run the Example Application

### Method 1: Using PYTHONPATH (Recommended)

```bash
PYTHONPATH=$PWD python examples/simple_api/main.py
```

### Method 2: Using the run script

```bash
chmod +x run_example.sh
./run_example.sh
```

Expected output:
```
Starting Simple API...
API Documentation: http://localhost:8001/docs
Press CTRL+C to stop
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

## ✅ Step 3: Test the API

### Open API Documentation

Open your browser and visit:
```
http://localhost:8001/docs
```

You'll see interactive Swagger UI documentation!

### Test with curl

```bash
# 1. Get welcome message
curl http://localhost:8001/

# 2. Create a user
curl -X POST http://localhost:8001/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "age": 30}'

# 3. List all users
curl http://localhost:8001/users

# 4. Get specific user
curl http://localhost:8001/users/1

# 5. Update user
curl -X PUT http://localhost:8001/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "John Updated", "email": "john.updated@example.com", "age": 31}'

# 6. Delete user
curl -X DELETE http://localhost:8001/users/1
```

### Test with Python

```python
import requests

# Create user
response = requests.post(
    "http://localhost:8001/users",
    json={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "age": 25
    }
)
print("Created:", response.json())

# List users
response = requests.get("http://localhost:8001/users")
print("Users:", response.json())

# Get user
response = requests.get("http://localhost:8001/users/1")
print("User 1:", response.json())
```

## ✅ Step 4: Create Your Own Project

```bash
# Create new project
python -m fennec.cli startproject myproject

# Navigate to project
cd myproject

# Run your project
PYTHONPATH=$PWD python -m app.main
```

Your new project will be available at http://localhost:8000

## 🎯 What You Can Do Now

### 1. Explore the Example
- Check `examples/simple_api/main.py` for complete code
- See how validation works
- See how middleware is used
- See how dependency injection works

### 2. Create Your Own Routes

```python
from fennec import Router, JSONResponse

router = Router()

@router.get("/hello/{name}")
async def hello(name: str):
    return JSONResponse(data={"message": f"Hello, {name}!"})
```

### 3. Add Validation

```python
from fennec.validation import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float
    quantity: int = Field(default=0)
    
    def validate_price(self, value):
        if value < 0:
            raise ValueError("Price must be positive")
        return value
```

### 4. Add Middleware

```python
from fennec.security import CORSMiddleware, RateLimitMiddleware

# Add CORS
app.middleware_manager.add(CORSMiddleware(allow_origins=["*"]))

# Add rate limiting
app.middleware_manager.add(RateLimitMiddleware(
    max_requests=100,
    window_seconds=60
))

# Custom middleware
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Request: {request.method} {request.path}")
    response = await call_next(request)
    return response
```

### 5. Add Authentication

```python
from fennec.security import JWTHandler, requires_auth

jwt = JWTHandler(secret_key="your-secret-key")

@router.post("/login")
async def login(request):
    data = await request.json()
    # Verify credentials...
    token = jwt.encode({"user_id": 1, "username": data["username"]})
    return JSONResponse(data={"token": token})

@router.get("/protected")
@requires_auth
async def protected_route(request):
    return JSONResponse(data={"message": "You are authenticated!"})
```

## 🐛 Troubleshooting

### Problem: ModuleNotFoundError: No module named 'framework'

**Solution**: Use PYTHONPATH
```bash
PYTHONPATH=$PWD python your_script.py
```

Or install the framework:
```bash
pip install -e .
```

### Problem: Port already in use

**Solution**: Change the port
```python
uvicorn.run(app, host="0.0.0.0", port=8002)  # Use different port
```

### Problem: Import errors

**Solution**: Make sure you're in the project root directory
```bash
cd /path/to/fastRest
PYTHONPATH=$PWD python examples/simple_api/main.py
```

## 📚 Next Steps

1. Read [README.md](README.md) for full documentation
2. Read [QUICKSTART.md](QUICKSTART.md) for quick reference
3. Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for project overview
4. Explore the code in `framework/` directory
5. Build your own API!

## 🎉 Success!

If you've made it this far, congratulations! You now have a working backend framework.

Happy coding! 🚀
