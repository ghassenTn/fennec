"""
Test OpenAPI generation
"""

import sys
sys.path.insert(0, ".")

from fennec import Application, Router, JSONResponse
from fennec.dependencies import Depends
from fennec.openapi import OpenAPIGenerator
import json


# Create app
app = Application(title="Test API", version="1.0.0", docs_enabled=False)
router = Router()


def get_db():
    return {}


@router.post("/users")
async def create_user(request, db=Depends(get_db)):
    """
    Create new user
    Creates a new user with validation
    
    Request Body:
        name (str): User's full name (2-50 characters)
        email (str): User's email address
        age (int): User's age (0-150)
    """
    data = await request.json()
    return JSONResponse(data=data, status_code=201)


@router.get("/users/{id}")
async def get_user(id: int, db=Depends(get_db)):
    """
    Get user by ID
    Returns a single user by their ID
    """
    return JSONResponse(data={"id": id})


app.include_router(router)

# Generate OpenAPI spec
generator = OpenAPIGenerator(app)
spec = generator.generate_spec()

# Print the spec
print("OpenAPI Specification:")
print("=" * 50)
print(json.dumps(spec, indent=2))

# Check if POST /users has requestBody
if "/users" in spec["paths"]:
    post_spec = spec["paths"]["/users"].get("post", {})
    if "requestBody" in post_spec:
        print("\n✓ POST /users has requestBody")
        print("\nRequest Body Schema:")
        print(json.dumps(post_spec["requestBody"], indent=2))
    else:
        print("\n✗ POST /users missing requestBody")

# Check if GET /users/{id} has path parameter
if "/users/{id}" in spec["paths"]:
    get_spec = spec["paths"]["/users/{id}"].get("get", {})
    if "parameters" in get_spec and len(get_spec["parameters"]) > 0:
        print("\n✓ GET /users/{id} has path parameter")
        print("\nPath Parameters:")
        print(json.dumps(get_spec["parameters"], indent=2))
    else:
        print("\n✗ GET /users/{id} missing path parameter")
