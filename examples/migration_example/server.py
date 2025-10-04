"""
Fennec Database Migration Example

Demonstrates database migration management with version control.
"""

import asyncpg
from fennec import Application, Request, Response
from fennec.migrations import MigrationManager
from fennec.migrations.cli import MigrationCLI


# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'fennec_demo',
    'user': 'postgres',
    'password': 'postgres'
}


app = Application()
db_pool = None
migration_manager = None


@app.on_startup
async def startup():
    """Initialize database connection and migrations."""
    global db_pool, migration_manager
    
    # Create connection pool
    db_pool = await asyncpg.create_pool(**DB_CONFIG)
    
    # Initialize migration manager
    async with db_pool.acquire() as conn:
        migration_manager = MigrationManager(
            connection=conn,
            migrations_dir="migrations"
        )
        await migration_manager.init()
    
    print("✓ Database connected")
    print("✓ Migration manager initialized")


@app.on_shutdown
async def shutdown():
    """Close database connection."""
    if db_pool:
        await db_pool.close()
    print("✓ Database connection closed")


# Migration API endpoints
@app.post("/migrations/create")
async def create_migration(request: Request):
    """Create a new migration."""
    data = await request.json()
    description = data.get('description')
    migration_type = data.get('type', 'python')
    
    if not description:
        return Response({"error": "Description required"}, status=400)
    
    async with db_pool.acquire() as conn:
        manager = MigrationManager(conn, migrations_dir="migrations")
        filepath = await manager.create(description, migration_type)
    
    return Response({
        "message": "Migration created",
        "filepath": filepath
    })


@app.post("/migrations/migrate")
async def run_migrations(request: Request):
    """Apply pending migrations."""
    data = await request.json()
    target = data.get('target')
    
    async with db_pool.acquire() as conn:
        manager = MigrationManager(conn, migrations_dir="migrations")
        count = await manager.migrate(target)
    
    return Response({
        "message": f"Applied {count} migration(s)",
        "count": count
    })


@app.post("/migrations/rollback")
async def rollback_migrations(request: Request):
    """Rollback migrations."""
    data = await request.json()
    steps = data.get('steps', 1)
    
    async with db_pool.acquire() as conn:
        manager = MigrationManager(conn, migrations_dir="migrations")
        count = await manager.rollback(steps)
    
    return Response({
        "message": f"Rolled back {count} migration(s)",
        "count": count
    })


@app.get("/migrations/status")
async def migration_status(request: Request):
    """Get migration status."""
    async with db_pool.acquire() as conn:
        manager = MigrationManager(conn, migrations_dir="migrations")
        status = await manager.status()
    
    return Response(status)


# Example: Query users table (created by migration)
@app.get("/users")
async def get_users(request: Request):
    """Get all users."""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM users ORDER BY id")
        users = [dict(row) for row in rows]
    
    return Response({"users": users})


@app.post("/users")
async def create_user(request: Request):
    """Create a new user."""
    data = await request.json()
    
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO users (username, email) VALUES ($1, $2) RETURNING *",
            data['username'],
            data['email']
        )
    
    return Response({"user": dict(row)}, status=201)


if __name__ == "__main__":
    import sys
    
    # Check if running CLI commands
    if len(sys.argv) > 1 and sys.argv[1] == "migrate":
        # Run migration CLI
        import asyncio
        
        async def run_cli():
            conn = await asyncpg.connect(**DB_CONFIG)
            manager = MigrationManager(conn, migrations_dir="migrations")
            cli = MigrationCLI(manager)
            cli.run(sys.argv[2:])
            await conn.close()
        
        asyncio.run(run_cli())
    else:
        # Run web server
        print("🚀 Starting Fennec Migration Example")
        print("📝 Endpoints:")
        print("   POST /migrations/create  - Create migration")
        print("   POST /migrations/migrate - Apply migrations")
        print("   POST /migrations/rollback - Rollback migrations")
        print("   GET  /migrations/status  - Migration status")
        print("   GET  /users              - List users")
        print("   POST /users              - Create user")
        print("\n💡 CLI Usage:")
        print("   python server.py migrate create 'description'")
        print("   python server.py migrate migrate")
        print("   python server.py migrate rollback")
        print("   python server.py migrate status")
        
        app.run(host="0.0.0.0", port=8000)
