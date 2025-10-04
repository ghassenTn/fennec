"""
Migration: create users table
Version: 20240104120000
"""

from fennec.migrations.migration import PythonMigration


class Migration20240104120000(PythonMigration):
    """
    Create users table
    """
    
    def __init__(self):
        super().__init__(
            version="20240104120000",
            description="create users table"
        )
    
    async def up(self, connection):
        """Apply migration."""
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    async def down(self, connection):
        """Revert migration."""
        await connection.execute("DROP TABLE IF EXISTS users")


# Migration instance
migration = Migration20240104120000()
