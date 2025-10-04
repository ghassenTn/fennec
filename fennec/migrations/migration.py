"""
Migration Base Class

Defines the interface for database migrations.
"""

from abc import ABC, abstractmethod
from typing import Any


class Migration(ABC):
    """Base class for database migrations."""
    
    def __init__(self, version: str, description: str):
        """
        Initialize migration.
        
        Args:
            version: Migration version (timestamp)
            description: Migration description
        """
        self.version = version
        self.description = description
    
    @abstractmethod
    async def up(self, connection: Any):
        """
        Apply migration (upgrade).
        
        Args:
            connection: Database connection
        """
        pass
    
    @abstractmethod
    async def down(self, connection: Any):
        """
        Revert migration (downgrade).
        
        Args:
            connection: Database connection
        """
        pass
    
    def __repr__(self):
        return f"<Migration {self.version}: {self.description}>"


class SQLMigration(Migration):
    """SQL-based migration."""
    
    def __init__(self, version: str, description: str, up_sql: str, down_sql: str):
        """
        Initialize SQL migration.
        
        Args:
            version: Migration version
            description: Migration description
            up_sql: SQL for upgrade
            down_sql: SQL for downgrade
        """
        super().__init__(version, description)
        self.up_sql = up_sql
        self.down_sql = down_sql
    
    async def up(self, connection: Any):
        """Execute upgrade SQL."""
        await connection.execute(self.up_sql)
    
    async def down(self, connection: Any):
        """Execute downgrade SQL."""
        await connection.execute(self.down_sql)


class PythonMigration(Migration):
    """Python-based migration with custom logic."""
    
    def __init__(self, version: str, description: str):
        """
        Initialize Python migration.
        
        Args:
            version: Migration version
            description: Migration description
        """
        super().__init__(version, description)
    
    async def up(self, connection: Any):
        """Override this method with upgrade logic."""
        raise NotImplementedError("up() must be implemented")
    
    async def down(self, connection: Any):
        """Override this method with downgrade logic."""
        raise NotImplementedError("down() must be implemented")
