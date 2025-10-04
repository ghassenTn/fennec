# Fennec Database Migration Example

This example demonstrates database migration management with version control.

## Features

- **Create Migrations**: Generate timestamped migration files
- **Apply Migrations**: Run pending migrations in order
- **Rollback**: Revert migrations safely
- **Status Tracking**: View applied and pending migrations
- **SQL & Python**: Support both SQL and Python-based migrations
- **Automatic Rollback**: Failed migrations rollback automatically

## Prerequisites

PostgreSQL must be running:

```bash
# Using Docker
docker run -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=fennec_demo \
  postgres

# Or install locally
brew install postgresql  # macOS
sudo apt-get install postgresql  # Ubuntu
```

## Installation

```bash
pip install asyncpg
```

## Quick Start

### 1. Create Initial Migration

```bash
python server.py migrate create "create users table"
```

This creates `migrations/20240104120000_create_users_table.py`

### 2. Edit Migration

Edit the generated file:

```python
async def up(self, connection):
    """Apply migration."""
    await connection.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

async def down(self, connection):
    """Revert migration."""
    await connection.execute("DROP TABLE users")
```

### 3. Apply Migration

```bash
python server.py migrate migrate
```

### 4. Check Status

```bash
python server.py migrate status
```

## CLI Commands

```bash
# Create migrations
python server.py migrate create "description"
python server.py migrate create "add index" --sql

# Apply migrations
python server.py migrate migrate
python server.py migrate migrate 20240104120000  # to specific version

# Rollback migrations
python server.py migrate rollback
python server.py migrate rollback 3  # rollback 3 migrations

# Check status
python server.py migrate status
```

## API Endpoints

Start the server:

```bash
python server.py
```

### Create Migration

```bash
curl -X POST http://localhost:8000/migrations/create \
  -H "Content-Type: application/json" \
  -d '{"description": "add users table", "type": "python"}'
```

### Apply Migrations

```bash
curl -X POST http://localhost:8000/migrations/migrate \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Rollback

```bash
curl -X POST http://localhost:8000/migrations/rollback \
  -H "Content-Type: application/json" \
  -d '{"steps": 1}'
```

### Check Status

```bash
curl http://localhost:8000/migrations/status
```

## Migration Examples

See `migrations/` directory for examples.
