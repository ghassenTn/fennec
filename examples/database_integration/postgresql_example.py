"""
PostgreSQL Integration Example

Demonstrates how to integrate PostgreSQL with Fennec using asyncpg.
"""

from fennec import Application, Router, JSONResponse, HTTPException, Depends
from fennec.db import DatabaseConnection, Repository
from typing import List, Optional
import asyncpg


class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection using asyncpg"""
    
    def __init__(self, connection_string: str):
        super().__init__(connection_string)
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create connection pool"""
        self.pool = await asyncpg.create_pool(self.connection_string)
        print("✓ Connected to PostgreSQL")
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            print("✓ Disconnected from PostgreSQL")
    
    async def execute(self, query: str, *args):
        """Execute query and return results"""
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
    
    async def execute_one(self, query: str, *args):
        """Execute query and return single result"""
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)
    
    async def execute_many(self, query: str, args_list: List[tuple]):
        """Execute query with multiple parameter sets"""
        async with self.pool.acquire() as connection:
            await connection.executemany(query, args_list)


class UserRepository(Repository):
    """Repository for user operations"""
    
    def __init__(self, db: PostgreSQLConnection):
        self.db = db
    
    async def create_table(self):
        """Create users table"""
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        await self.db.execute(query)
    
    async def get_all(self) -> List[dict]:
        """Get all users"""
        query = "SELECT * FROM users ORDER BY id"
        rows = await self.db.execute(query)
        return [dict(row) for row in rows]
    
    async def get(self, id: int) -> Optional[dict]:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = $1"
        row = await self.db.execute_one(query, id)
        return dict(row) if row else None
    
    async def create(self, name: str, email: str, age: int) -> dict:
        """Create new user"""
        query = """
        INSERT INTO users (name, email, age)
        VALUES ($1, $2, $3)
        RETURNING *
        """
        row = await self.db.execute_one(query, name, email, age)
        return dict(row)
    
    async def update(self, id: int, name: Optional[str] = None, 
                    email: Optional[str] = None, age: Optional[int] = None) -> Optional[dict]:
        """Update user"""
        # Build dynamic update query
        updates = []
        params = []
        param_count = 1
        
        if name is not None:
            updates.append(f"name = ${param_count}")
            params.append(name)
            param_count += 1
        
        if email is not None:
            updates.append(f"email = ${param_count}")
            params.append(email)
            param_count += 1
        
        if age is not None:
            updates.append(f"age = ${param_count}")
            params.append(age)
            param_count += 1
        
        if not updates:
            return await self.get(id)
        
        params.append(id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ${param_count} RETURNING *"
        
        row = await self.db.execute_one(query, *params)
        return dict(row) if row else None
    
    async def delete(self, id: int) -> bool:
        """Delete user"""
        query = "DELETE FROM users WHERE id = $1 RETURNING id"
        row = await self.db.execute_one(query, id)
        return row is not None
    
    async def find_by_email(self, email: str) -> Optional[dict]:
        """Find user by email"""
        query = "SELECT * FROM users WHERE email = $1"
        row = await self.db.execute_one(query, email)
        return dict(row) if row else None
    
    async def search(self, query_text: str) -> List[dict]:
        """Search users by name or email"""
        query = """
        SELECT * FROM users 
        WHERE name ILIKE $1 OR email ILIKE $1
        ORDER BY id
        """
        rows = await self.db.execute(query, f"%{query_text}%")
        return [dict(row) for row in rows]


# Database connection
db = PostgreSQLConnection(
    "postgresql://postgres:password@localhost:5432/fennec_db"
)

# Repository
user_repo = UserRepository(db)


# Dependency injection
def get_user_repo():
    return user_repo


# Create application
app = Application(title="PostgreSQL Example")
router = Router(prefix="/api/users")


@app.middleware("http")
async def db_middleware(request, call_next):
    """Ensure database is connected"""
    if not db.pool:
        await db.connect()
        await user_repo.create_table()
    
    response = await call_next(request)
    return response


@router.get("/")
async def get_users(repo: UserRepository = Depends(get_user_repo)):
    """Get all users"""
    users = await repo.get_all()
    return JSONResponse(data=users)


@router.get("/{user_id}")
async def get_user(user_id: int, repo: UserRepository = Depends(get_user_repo)):
    """Get user by ID"""
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(404, f"User {user_id} not found")
    return JSONResponse(data=user)


@router.post("/")
async def create_user(name: str, email: str, age: int, 
                     repo: UserRepository = Depends(get_user_repo)):
    """Create new user"""
    # Check if email exists
    existing = await repo.find_by_email(email)
    if existing:
        raise HTTPException(400, f"Email {email} already exists")
    
    user = await repo.create(name, email, age)
    return JSONResponse(data=user, status_code=201)


@router.put("/{user_id}")
async def update_user(user_id: int, name: Optional[str] = None,
                     email: Optional[str] = None, age: Optional[int] = None,
                     repo: UserRepository = Depends(get_user_repo)):
    """Update user"""
    user = await repo.update(user_id, name, email, age)
    if not user:
        raise HTTPException(404, f"User {user_id} not found")
    return JSONResponse(data=user)


@router.delete("/{user_id}")
async def delete_user(user_id: int, repo: UserRepository = Depends(get_user_repo)):
    """Delete user"""
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(404, f"User {user_id} not found")
    return JSONResponse(data={"message": "User deleted"})


@router.get("/search/{query}")
async def search_users(query: str, repo: UserRepository = Depends(get_user_repo)):
    """Search users"""
    users = await repo.search(query)
    return JSONResponse(data=users)


app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    print("🦊 Fennec + PostgreSQL Example")
    print("=" * 50)
    print("Make sure PostgreSQL is running:")
    print("  docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres")
    print("\nOr update connection string in code")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
