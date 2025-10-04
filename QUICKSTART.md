# Quick Start Guide

## Installation

```bash
# Install the framework
pip install -e .

# Install uvicorn for running the server
pip install uvicorn
```

## Verify Installation

Run the test script to verify everything works:

```bash
python test_framework.py
```

You should see:
```
✓ All tests passed!
Framework is working correctly! 🎉
```

## Run the Example

### Option 1: Using PYTHONPATH

```bash
PYTHONPATH=$PWD python examples/simple_api/main.py
```

### Option 2: Using the run script

```bash
./run_example.sh
```

The server will start on http://localhost:8001

## Test the API

### Using curl

```bash
# Get root
curl http://localhost:8001/

# List users
curl http://localhost:8001/users

# Create user
curl -X POST http://localhost:8001/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "age": 30}'

# Get user by ID
curl http://localhost:8001/users/1

# Update user
curl -X PUT http://localhost:8001/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "John Updated", "email": "john@example.com", "age": 31}'

# Delete user
curl -X DELETE http://localhost:8001/users/1
```

### Using Python

```python
import requests

# Create user
response = requests.post(
    "http://localhost:8001/users",
    json={"name": "Jane Doe", "email": "jane@example.com", "age": 25}
)
print(response.json())

# List users
response = requests.get("http://localhost:8001/users")
print(response.json())
```

## View API Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8001/docs
- **OpenAPI JSON**: http://localhost:8001/openapi.json

## Create Your Own Project

```bash
# Create new project
python -m fennec.cli startproject myproject

# Navigate to project
cd myproject

# Run the project
PYTHONPATH=$PWD python -m app.main
```

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Check out [examples/simple_api/](examples/simple_api/) for a complete example
3. Explore the framework features:
   - Validation with BaseModel
   - Middleware system
   - Dependency injection
   - Authentication & Authorization
   - Rate limiting & CORS

## Troubleshooting

### ModuleNotFoundError: No module named 'framework'

Make sure you're running with PYTHONPATH set:
```bash
PYTHONPATH=$PWD python your_script.py
```

Or install the framework:
```bash
pip install -e .
```

### Port already in use

Change the port in the example:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use different port
```

### Import errors

Make sure you're in the project root directory and have installed the framework.

## Support

For issues and questions, please open an issue on GitHub.
