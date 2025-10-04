# OpenAPI Documentation Guide

## How to Document Your API

The framework automatically generates OpenAPI/Swagger documentation from your code. Here's how to make the most of it:

## Basic Route Documentation

### Using Docstrings

```python
@router.get("/users/{id}")
async def get_user(id: int):
    """
    Get user by ID
    Returns a single user by their ID
    """
    return JSONResponse(data={"id": id})
```

This will generate:
- **Summary**: "Get User" (from function name)
- **Description**: Full docstring text
- **Path Parameter**: `id` (integer, required)

## Documenting Request Bodies

For POST/PUT/PATCH endpoints, document the request body in the docstring:

```python
@router.post("/users")
async def create_user(request):
    """
    Create new user
    Creates a new user with validation
    
    Request Body:
        name (str): User's full name (2-50 characters)
        email (str): User's email address
        age (int): User's age (0-150)
    """
    data = await request.json()
    # ... process data
```

### Request Body Format

Use this format in your docstring:

```
Request Body:
    field_name (type): Description
    another_field (type): Description
```

Supported types:
- `str` → string
- `int` → integer
- `float` → number
- `bool` → boolean
- `list` → array
- `dict` → object

### Example

```python
@router.post("/products")
async def create_product(request):
    """
    Create a new product
    
    Request Body:
        name (str): Product name
        price (float): Product price in USD
        quantity (int): Available quantity
        in_stock (bool): Whether product is in stock
        tags (list): Product tags
    """
    data = await request.json()
    return JSONResponse(data=data, status_code=201)
```

This generates a complete OpenAPI schema with:
- Field names
- Types
- Descriptions
- Examples (auto-generated for common fields like name, email, age)

## Path Parameters

Path parameters are automatically detected from function signatures:

```python
@router.get("/users/{id}/posts/{post_id}")
async def get_user_post(id: int, post_id: int):
    """Get a specific post from a user"""
    return JSONResponse(data={"user_id": id, "post_id": post_id})
```

## Query Parameters

Query parameters are detected from the request object:

```python
@router.get("/search")
async def search(request):
    """
    Search for items
    
    Query Parameters:
        q (str): Search query
        limit (int): Maximum results
    """
    query = request.query_params.get("q", "")
    limit = int(request.query_params.get("limit", 10))
    return JSONResponse(data={"query": query, "limit": limit})
```

## Response Documentation

You can document responses in the docstring:

```python
@router.get("/users/{id}")
async def get_user(id: int):
    """
    Get user by ID
    
    Returns:
        User object with id, name, email, and age
        
    Raises:
        404: User not found
    """
    # ... implementation
```

## Using BaseModel for Better Documentation

For even better documentation, use BaseModel:

```python
from fennec.validation import BaseModel, Field

class User(BaseModel):
    """User model"""
    name: str = Field(min_length=2, max_length=50)
    email: str
    age: int

@router.post("/users")
async def create_user(request):
    """
    Create new user
    
    Request Body:
        name (str): User's full name (2-50 characters)
        email (str): User's email address
        age (int): User's age
    """
    data = await request.json()
    user = User(**data)  # Validates automatically
    return JSONResponse(data=user.dict(), status_code=201)
```

## Viewing Documentation

Once your API is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Tips

1. **Be Descriptive**: Write clear docstrings
2. **Document Request Bodies**: Always document POST/PUT/PATCH bodies
3. **Use Type Hints**: They help generate accurate schemas
4. **Add Examples**: Common field names get auto-examples (name, email, age, etc.)
5. **Test Your Docs**: Visit /docs to see how it looks

## Example: Complete Endpoint Documentation

```python
@router.post("/api/v1/users")
async def create_user(request, db=Depends(get_db)):
    """
    Create a new user account
    
    This endpoint creates a new user with the provided information.
    The user data is validated before being stored in the database.
    
    Request Body:
        name (str): User's full name (2-50 characters)
        email (str): User's email address (must be unique)
        age (int): User's age (must be between 0 and 150)
        password (str): User's password (min 8 characters)
    
    Returns:
        Created user object with generated ID
        
    Raises:
        400: Invalid input data
        409: Email already exists
    """
    data = await request.json()
    
    # Validate
    user = User(**data)
    
    # Check if email exists
    if db.email_exists(user.email):
        raise ConflictException("Email already exists")
    
    # Create user
    user_id = db.create_user(user.dict())
    
    return JSONResponse(
        data={"id": user_id, **user.dict()},
        message="User created successfully",
        status_code=201
    )
```

This will generate complete, professional API documentation automatically!
