# Simple CRUD Example 🦊

A minimal Todo application demonstrating Create, Read, Update, Delete operations with Fennec Framework.

## Features

- ✅ **Create** todos with title and description
- 📋 **Read** all todos or get a specific todo by ID
- ✏️ **Update** todo details and completion status
- 🗑️ **Delete** todos
- 🎨 Beautiful web interface
- 📊 Real-time statistics
- 🔄 Auto-refresh on changes

## Project Structure

```
simple_crud/
├── server.py       # Backend API server
├── client.html     # Frontend web interface
└── README.md       # This file
```

## Quick Start

### 1. Start the Server

```bash
cd examples/simple_crud
python server.py
```

The server will start on `http://localhost:8000`

### 2. Open the Web Interface

Open `client.html` in your browser, or visit:
- Web UI: Open `client.html` in your browser
- API Docs: http://localhost:8000/docs
- API Root: http://localhost:8000

## API Endpoints

### List All Todos
```bash
GET /todos
```

**Response:**
```json
{
  "todos": [
    {
      "id": 1,
      "title": "Learn Fennec",
      "description": "Study the framework documentation",
      "completed": false
    }
  ],
  "total": 1
}
```

### Get Todo by ID
```bash
GET /todos/{id}
```

**Response:**
```json
{
  "todo": {
    "id": 1,
    "title": "Learn Fennec",
    "description": "Study the framework documentation",
    "completed": false
  }
}
```

### Create Todo
```bash
POST /todos
Content-Type: application/json

{
  "title": "Learn Fennec",
  "description": "Study the framework documentation",
  "completed": false
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Todo created successfully",
  "data": {
    "todo": {
      "id": 1,
      "title": "Learn Fennec",
      "description": "Study the framework documentation",
      "completed": false
    }
  }
}
```

### Update Todo
```bash
PUT /todos/{id}
Content-Type: application/json

{
  "title": "Learn Fennec Framework",
  "description": "Complete the tutorial",
  "completed": true
}
```

**Response:**
```json
{
  "todo": {
    "id": 1,
    "title": "Learn Fennec Framework",
    "description": "Complete the tutorial",
    "completed": true
  },
  "message": "Todo updated successfully"
}
```

### Delete Todo
```bash
DELETE /todos/{id}
```

**Response:**
```json
{
  "message": "Todo deleted successfully",
  "deleted_todo": {
    "id": 1,
    "title": "Learn Fennec",
    "description": "Study the framework documentation",
    "completed": false
  }
}
```

## Testing with cURL

### Create a todo
```bash
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread"}'
```

### List all todos
```bash
curl http://localhost:8000/todos
```

### Get a specific todo
```bash
curl http://localhost:8000/todos/1
```

### Update a todo
```bash
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread, cheese","completed":true}'
```

### Delete a todo
```bash
curl -X DELETE http://localhost:8000/todos/1
```

## Code Highlights

### Data Validation
```python
class Todo(BaseModel):
    """Todo item model"""
    id: Optional[int] = Field(default=None, required=False)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default="", required=False)
    completed: bool = Field(default=False, required=False)
```

### CRUD Operations
```python
# Create
@router.post("/todos")
async def create_todo(request):
    data = await request.json()
    todo = Todo(**data)
    # ... save to database

# Read
@router.get("/todos")
async def list_todos():
    return {"todos": list(todos_db.values())}

# Update
@router.put("/todos/{id}")
async def update_todo(request, id: int):
    data = await request.json()
    todo = Todo(**data)
    # ... update in database

# Delete
@router.delete("/todos/{id}")
async def delete_todo(id: int):
    del todos_db[id]
```

## Features Demonstrated

1. **Request Validation** - Using BaseModel for automatic validation
2. **Path Parameters** - Extracting ID from URL path
3. **Request Body** - Parsing JSON request bodies
4. **Error Handling** - Returning appropriate error responses
5. **CORS** - Enabling cross-origin requests
6. **OpenAPI Docs** - Auto-generated API documentation
7. **RESTful Design** - Following REST conventions

## Next Steps

- Add authentication (see `examples/oauth2_auth`)
- Add database persistence (see `examples/database_integration`)
- Add caching (see main.py for Redis caching example)
- Add WebSocket for real-time updates (see `examples/websocket_chat`)

## Built with ❤️ in Tunisia 🇹🇳

Using Fennec Framework - Small, Swift, and Adaptable
