# How to Test the OpenAPI Fix

## Quick Test

### 1. Run the OpenAPI Test Script

```bash
python test_openapi.py
```

Expected output:
```
✓ POST /users has requestBody

Request Body Schema:
{
  "required": true,
  "content": {
    "application/json": {
      "schema": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "User's full name (2-50 characters)",
            "example": "John Doe"
          },
          "email": {
            "type": "string",
            "description": "User's email address",
            "example": "john@example.com"
          },
          "age": {
            "type": "integer",
            "description": "User's age (0-150)",
            "example": 30
          }
        },
        "required": ["name", "email", "age"]
      }
    }
  }
}

✓ GET /users/{id} has path parameter
```

### 2. Run the Example Application

```bash
# Method 1: Using PYTHONPATH
PYTHONPATH=$PWD python examples/simple_api/main.py

# Method 2: Using the script
./run_example.sh
```

### 3. Open Swagger UI

Open your browser and visit:
```
http://localhost:8001/docs
```

### 4. Test POST /users Endpoint

In Swagger UI:

1. Click on **POST /users** to expand it
2. Click **"Try it out"**
3. You should now see a proper request body editor with:
   ```json
   {
     "name": "string",
     "email": "string",
     "age": 0
   }
   ```
4. Fill in the values:
   ```json
   {
     "name": "John Doe",
     "email": "john@example.com",
     "age": 30
   }
   ```
5. Click **"Execute"**
6. Check the response

### 5. Test PUT /users/{id} Endpoint

1. Click on **PUT /users/{id}** to expand it
2. Click **"Try it out"**
3. Enter an ID (e.g., 1)
4. You should see the request body editor with name, email, age fields
5. Fill in the values and execute

## What You Should See

### Before the Fix ❌

```
POST /users
Parameters:
  - db (string) [query]
```

### After the Fix ✅

```
POST /users

Request body (application/json):
{
  "name": "string",      // User's full name (2-50 characters)
  "email": "string",     // User's email address  
  "age": 0               // User's age (0-150)
}

Example Value:
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
```

## Testing with curl

### Create User

```bash
curl -X POST http://localhost:8001/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane@example.com",
    "age": 25
  }'
```

Expected response:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "age": 25
  },
  "message": "User created"
}
```

### Update User

```bash
curl -X PUT http://localhost:8001/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Updated",
    "email": "jane.updated@example.com",
    "age": 26
  }'
```

### Get User

```bash
curl http://localhost:8001/users/1
```

## Verify OpenAPI Spec

### Get OpenAPI JSON

```bash
curl http://localhost:8001/openapi.json | python -m json.tool
```

Look for the POST /users endpoint:
```json
{
  "paths": {
    "/users": {
      "post": {
        "summary": "Create User",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "name": {"type": "string", "example": "John Doe"},
                  "email": {"type": "string", "example": "john@example.com"},
                  "age": {"type": "integer", "example": 30}
                }
              }
            }
          }
        }
      }
    }
  }
}
```

## Common Issues

### Issue: Still seeing "db" parameter

**Solution**: Make sure you've restarted the server after the changes.

```bash
# Stop the server (CTRL+C)
# Start it again
PYTHONPATH=$PWD python examples/simple_api/main.py
```

### Issue: Request body not showing

**Solution**: Check that your endpoint has proper docstring:

```python
@router.post("/endpoint")
async def handler(request):
    """
    Endpoint description
    
    Request Body:
        field1 (str): Description
        field2 (int): Description
    """
    # ... implementation
```

### Issue: ModuleNotFoundError

**Solution**: Use PYTHONPATH:

```bash
PYTHONPATH=$PWD python examples/simple_api/main.py
```

## Success Criteria

✅ Swagger UI shows request body fields (name, email, age)
✅ Each field has proper type (string, integer)
✅ Each field has description
✅ Example values are shown
✅ Can test endpoints directly from Swagger UI
✅ OpenAPI JSON has proper requestBody schema

## Next Steps

Once verified:
1. Read [OPENAPI_GUIDE.md](OPENAPI_GUIDE.md) for documentation best practices
2. Document your own endpoints using the same format
3. Share the API documentation with your team
4. Generate client SDKs from the OpenAPI spec

---

**Status**: Ready to test
**Expected Time**: 5 minutes
**Difficulty**: Easy
