"""
Simple CRUD API Example with Fennec Framework 🦊

A minimal example demonstrating Create, Read, Update, Delete operations
for a simple Todo application.

Run: python server.py
Then visit: http://localhost:8000/docs
"""

from fennec import Application, Router, JSONResponse
from fennec.validation import BaseModel, Field
from fennec.security import CORSMiddleware
from typing import Optional

# ============================================================================
# DATA MODELS
# ============================================================================

class Todo(BaseModel):
    """Todo item model"""
    id: Optional[int] = Field(default=None, required=False)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default="", required=False)
    completed: bool = Field(default=False, required=False)


# ============================================================================
# IN-MEMORY DATABASE
# ============================================================================

todos_db = {}
next_id = 1


# ============================================================================
# APPLICATION SETUP
# ============================================================================

app = Application(
    title="Todo API",
    version="1.0.0",
    docs_enabled=True
)

# Add CORS middleware
app.middleware_manager.add(
    CORSMiddleware(
        allow_origins=["*"],
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type"]
    )
)

router = Router()


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

@router.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Todo API! 🦊",
        "docs": "/docs",
        "endpoints": {
            "list_todos": "GET /todos",
            "get_todo": "GET /todos/{id}",
            "create_todo": "POST /todos",
            "update_todo": "PUT /todos/{id}",
            "delete_todo": "DELETE /todos/{id}"
        }
    }


@router.get("/todos")
async def list_todos():
    """
    📋 List all todos
    
    Returns all todo items in the database.
    """
    return {
        "todos": list(todos_db.values()),
        "total": len(todos_db)
    }


@router.get("/todos/{id}")
async def get_todo(id: int):
    """
    🔍 Get a specific todo by ID
    
    Args:
        id: Todo ID
    
    Returns:
        Todo item
    """
    if id not in todos_db:
        return JSONResponse(
            data=None,
            message=f"Todo with ID {id} not found",
            status="error",
            status_code=404
        )
    
    return {
        "todo": todos_db[id]
    }


@router.post("/todos")
async def create_todo(request):
    """
    ➕ Create a new todo
    
    Request Body:
        title (str): Todo title (required)
        description (str): Todo description (optional)
        completed (bool): Completion status (optional, default: false)
    
    Returns:
        Created todo item
    """
    global next_id
    
    # Get request data
    data = await request.json()
    
    # Validate with model
    try:
        todo = Todo(**data)
    except Exception as e:
        return JSONResponse(
            data=None,
            message=f"Validation error: {str(e)}",
            status="error",
            status_code=400
        )
    
    # Add to database
    todo_dict = todo.dict()
    todo_dict["id"] = next_id
    todos_db[next_id] = todo_dict
    next_id += 1
    
    return JSONResponse(
        data={"todo": todo_dict},
        message="Todo created successfully",
        status_code=201
    )


@router.put("/todos/{id}")
async def update_todo(request, id: int):
    """
    ✏️ Update an existing todo
    
    Args:
        id: Todo ID
    
    Request Body:
        title (str): Todo title
        description (str): Todo description
        completed (bool): Completion status
    
    Returns:
        Updated todo item
    """
    if id not in todos_db:
        return JSONResponse(
            data=None,
            message=f"Todo with ID {id} not found",
            status="error",
            status_code=404
        )
    
    # Get request data
    data = await request.json()
    
    # Validate with model
    try:
        todo = Todo(**data)
    except Exception as e:
        return JSONResponse(
            data=None,
            message=f"Validation error: {str(e)}",
            status="error",
            status_code=400
        )
    
    # Update database
    todo_dict = todo.dict()
    todo_dict["id"] = id
    todos_db[id] = todo_dict
    
    return {
        "todo": todo_dict,
        "message": "Todo updated successfully"
    }


@router.delete("/todos/{id}")
async def delete_todo(id: int):
    """
    🗑️ Delete a todo
    
    Args:
        id: Todo ID
    
    Returns:
        Success message
    """
    if id not in todos_db:
        return JSONResponse(
            data=None,
            message=f"Todo with ID {id} not found",
            status="error",
            status_code=404
        )
    
    deleted_todo = todos_db[id]
    del todos_db[id]
    
    return {
        "message": "Todo deleted successfully",
        "deleted_todo": deleted_todo
    }


# ============================================================================
# REGISTER ROUTES
# ============================================================================

app.include_router(router)


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🦊 Fennec Framework - Simple CRUD Example")
    print("=" * 60)
    print("\n📚 Features:")
    print("  ✓ Create todos (POST /todos)")
    print("  ✓ Read todos (GET /todos, GET /todos/{id})")
    print("  ✓ Update todos (PUT /todos/{id})")
    print("  ✓ Delete todos (DELETE /todos/{id})")
    print("\n🌐 Server Info:")
    print("  URL: http://localhost:8000")
    print("  Docs: http://localhost:8000/docs")
    print("\n💡 Quick Test:")
    print("  1. Visit http://localhost:8000/docs")
    print("  2. Try POST /todos to create a todo")
    print("  3. Try GET /todos to list all todos")
    print("=" * 60)
    print("\nPress CTRL+C to stop\n")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
