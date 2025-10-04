# Database Integration Examples 🦊

Examples demonstrating how to integrate databases with Fennec Framework using the Repository pattern.

## Examples

1. **PostgreSQL** - Relational database using asyncpg
2. **MongoDB** - Document database using motor

## Project Structure

```
database_integration/
├── postgresql_example.py    # PostgreSQL integration
├── mongodb_example.py        # MongoDB integration
└── README.md                 # This file
```

## PostgreSQL Example

### Installation

```bash
pip install fennec uvicorn asyncpg
```

### Setup PostgreSQL

Using Docker:
```bash
docker run -d \
  --name postgres \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=fennec_db \
  postgres:latest
```

Or update the connection string in `postgresql_example.py`:
```python
db = PostgreSQLConnection(
    "postgresql://username:password@localhost:5432/database_name"
)
```

### Running

```bash
python postgresql_example.py
```

### Features

- ✅ Connection pooling with asyncpg
- ✅ Repository pattern
- ✅ CRUD operations
- ✅ Search functionality
- ✅ Parameterized queries (SQL injection safe)
- ✅ Dependency injection
- ✅ Automatic table creation

### API Endpoints

```bash
# Get all users
curl http://localhost:8000/api/users

# Get user by ID
curl http://localhost:8000/api/users/1

# Create user
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "age": 30}'

# Update user
curl -X PUT http://localhost:8000/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "John Smith", "age": 31}'

# Delete user
curl -X DELETE http://localhost:8000/api/users/1

# Search users
curl http://localhost:8000/api/users/search/john
```

## MongoDB Example

### Installation

```bash
pip install fennec uvicorn motor
```

### Setup MongoDB

Using Docker:
```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  mongo:latest
```

Or update the connection string in `mongodb_example.py`:
```python
db = MongoDBConnection(
    "mongodb://username:password@localhost:27017",
    database_name="fennec_db"
)
```

### Running

```bash
python mongodb_example.py
```

### Features

- ✅ Async MongoDB driver (motor)
- ✅ Repository pattern
- ✅ CRUD operations
- ✅ Text search with regex
- ✅ Range queries
- ✅ Indexes for performance
- ✅ ObjectId handling
- ✅ Dependency injection

### API Endpoints

```bash
# Get all users
curl http://localhost:8000/api/users

# Count users
curl http://localhost:8000/api/users/count

# Get user by ID
curl http://localhost:8000/api/users/507f1f77bcf86cd799439011

# Create user
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "email": "jane@example.com", "age": 28}'

# Update user
curl -X PUT http://localhost:8000/api/users/507f1f77bcf86cd799439011 \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Smith"}'

# Delete user
curl -X DELETE http://localhost:8000/api/users/507f1f77bcf86cd799439011

# Search users
curl http://localhost:8000/api/users/search/jane

# Find by age range
curl http://localhost:8000/api/users/age/25/35
```

## Repository Pattern

Both examples use the Repository pattern to abstract database operations:

```python
class UserRepository(Repository):
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    async def get_all(self) -> List[dict]:
        """Get all users"""
        pass
    
    async def get(self, id) -> Optional[dict]:
        """Get user by ID"""
        pass
    
    async def create(self, **kwargs) -> dict:
        """Create new user"""
        pass
    
    async def update(self, id, **kwargs) -> Optional[dict]:
        """Update user"""
        pass
    
    async def delete(self, id) -> bool:
        """Delete user"""
        pass
```

## Dependency Injection

Use Fennec's dependency injection to provide repositories to handlers:

```python
def get_user_repo():
    return user_repo

@router.get("/")
async def get_users(repo: UserRepository = Depends(get_user_repo)):
    users = await repo.get_all()
    return JSONResponse(data=users)
```

## Connection Management

### PostgreSQL Connection Pooling

```python
class PostgreSQLConnection(DatabaseConnection):
    async def connect(self):
        self.pool = await asyncpg.create_pool(self.connection_string)
    
    async def execute(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
```

### MongoDB Connection

```python
class MongoDBConnection(DatabaseConnection):
    async def connect(self):
        self.client = AsyncIOMotorClient(self.connection_string)
        self.db = self.client[self.database_name]
```

## Best Practices

### 1. Use Parameterized Queries (PostgreSQL)

```python
# Good - Safe from SQL injection
query = "SELECT * FROM users WHERE email = $1"
await db.execute(query, email)

# Bad - Vulnerable to SQL injection
query = f"SELECT * FROM users WHERE email = '{email}'"
await db.execute(query)
```

### 2. Handle ObjectId (MongoDB)

```python
from bson import ObjectId

# Convert string to ObjectId
user = await collection.find_one({"_id": ObjectId(user_id)})

# Convert ObjectId to string for JSON
user["id"] = str(user["_id"])
del user["_id"]
```

### 3. Create Indexes

```python
# PostgreSQL
await db.execute("CREATE INDEX idx_email ON users(email)")

# MongoDB
await collection.create_index("email", unique=True)
```

### 4. Use Transactions (PostgreSQL)

```python
async with db.pool.acquire() as connection:
    async with connection.transaction():
        await connection.execute("INSERT INTO users ...")
        await connection.execute("INSERT INTO profiles ...")
```

### 5. Connection Pooling

```python
# Configure pool size
pool = await asyncpg.create_pool(
    connection_string,
    min_size=10,
    max_size=20
)
```

## Error Handling

### PostgreSQL

```python
try:
    await repo.create(name, email, age)
except asyncpg.UniqueViolationError:
    raise HTTPException(400, "Email already exists")
except asyncpg.PostgresError as e:
    raise HTTPException(500, f"Database error: {str(e)}")
```

### MongoDB

```python
from pymongo.errors import DuplicateKeyError

try:
    await repo.create(name, email, age)
except DuplicateKeyError:
    raise HTTPException(400, "Email already exists")
```

## Testing

### Unit Tests

```python
import pytest
from fennec.testing import TestClient

@pytest.mark.asyncio
async def test_create_user():
    # Setup test database
    db = PostgreSQLConnection("postgresql://localhost/test_db")
    await db.connect()
    
    # Create user
    repo = UserRepository(db)
    user = await repo.create("Test", "test@example.com", 25)
    
    assert user["name"] == "Test"
    assert user["email"] == "test@example.com"
    
    # Cleanup
    await db.disconnect()
```

### Integration Tests

```python
def test_api_create_user():
    client = TestClient(app)
    response = client.post("/api/users", json={
        "name": "Test User",
        "email": "test@example.com",
        "age": 25
    })
    assert response.status_code == 201
    assert response.json()["data"]["name"] == "Test User"
```

## Performance Optimization

### 1. Connection Pooling

```python
# PostgreSQL - Configure pool
pool = await asyncpg.create_pool(
    connection_string,
    min_size=10,
    max_size=20,
    command_timeout=60
)
```

### 2. Indexes

```python
# PostgreSQL
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_name ON users(name);

# MongoDB
await collection.create_index([("email", 1)])
await collection.create_index([("name", "text")])
```

### 3. Query Optimization

```python
# Select only needed fields
query = "SELECT id, name, email FROM users"  # Good
query = "SELECT * FROM users"  # Avoid if possible

# MongoDB projection
users = await collection.find({}, {"name": 1, "email": 1})
```

### 4. Batch Operations

```python
# PostgreSQL
await db.execute_many(
    "INSERT INTO users (name, email) VALUES ($1, $2)",
    [("User1", "user1@example.com"), ("User2", "user2@example.com")]
)

# MongoDB
await collection.insert_many([
    {"name": "User1", "email": "user1@example.com"},
    {"name": "User2", "email": "user2@example.com"}
])
```

## Production Considerations

1. **Environment Variables**: Store connection strings in environment variables
   ```python
   import os
   connection_string = os.getenv("DATABASE_URL")
   ```

2. **Connection Limits**: Configure appropriate pool sizes
3. **Timeouts**: Set query timeouts to prevent hanging
4. **Monitoring**: Log slow queries
5. **Backups**: Regular database backups
6. **Migrations**: Use migration tools (Alembic for PostgreSQL)
7. **Read Replicas**: Use read replicas for scaling reads
8. **Caching**: Cache frequently accessed data

## Migration Tools

### PostgreSQL - Alembic

```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Create users table"
alembic upgrade head
```

### MongoDB - No Schema Migrations

MongoDB is schemaless, but you can use migration scripts for data transformations.

## Learn More

- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [Motor Documentation](https://motor.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Fennec Documentation](https://github.com/your-repo/fennec)
