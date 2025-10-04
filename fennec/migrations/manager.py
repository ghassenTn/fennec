"""
Migration Manager

Manages database migrations with version tracking and rollback support.
"""

import os
import importlib.util
from typing import List, Optional, Any
from datetime import datetime
import asyncio


class MigrationManager:
    """Manages database migrations."""
    
    def __init__(
        self,
        connection,
        migrations_dir: str = "migrations",
        table_name: str = "schema_migrations"
    ):
        """
        Initialize migration manager.
        
        Args:
            connection: Database connection
            migrations_dir: Directory containing migration files
            table_name: Table name for tracking migrations
        """
        self.connection = connection
        self.migrations_dir = migrations_dir
        self.table_name = table_name
        self._migrations = []
    
    async def init(self):
        """Initialize migrations table."""
        await self._create_migrations_table()
    
    async def _create_migrations_table(self):
        """Create migrations tracking table if it doesn't exist."""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            version VARCHAR(255) PRIMARY KEY,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            execution_time_ms INTEGER
        )
        """
        await self.connection.execute(create_table_sql)
    
    async def _get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions."""
        query = f"SELECT version FROM {self.table_name} ORDER BY version"
        result = await self.connection.fetch(query)
        return [row['version'] for row in result]
    
    async def _mark_migration_applied(
        self,
        version: str,
        description: str,
        execution_time_ms: int
    ):
        """Mark migration as applied."""
        query = f"""
        INSERT INTO {self.table_name} (version, description, execution_time_ms)
        VALUES ($1, $2, $3)
        """
        await self.connection.execute(query, version, description, execution_time_ms)
    
    async def _mark_migration_reverted(self, version: str):
        """Mark migration as reverted."""
        query = f"DELETE FROM {self.table_name} WHERE version = $1"
        await self.connection.execute(query, version)
    
    def _load_migrations(self) -> List[Any]:
        """Load migration files from directory."""
        if not os.path.exists(self.migrations_dir):
            return []
        
        migrations = []
        
        for filename in sorted(os.listdir(self.migrations_dir)):
            if not filename.endswith('.py') or filename.startswith('__'):
                continue
            
            filepath = os.path.join(self.migrations_dir, filename)
            
            # Load module
            spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get migration instance
            if hasattr(module, 'migration'):
                migrations.append(module.migration)
        
        return migrations
    
    async def create(self, description: str, migration_type: str = "python") -> str:
        """
        Create a new migration file.
        
        Args:
            description: Migration description
            migration_type: Type of migration ('python' or 'sql')
            
        Returns:
            Path to created migration file
        """
        # Create migrations directory if it doesn't exist
        os.makedirs(self.migrations_dir, exist_ok=True)
        
        # Generate version (timestamp)
        version = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Create filename
        safe_description = description.lower().replace(' ', '_')
        filename = f"{version}_{safe_description}.py"
        filepath = os.path.join(self.migrations_dir, filename)
        
        # Generate template
        if migration_type == "sql":
            template = self._generate_sql_template(version, description)
        else:
            template = self._generate_python_template(version, description)
        
        # Write file
        with open(filepath, 'w') as f:
            f.write(template)
        
        return filepath
    
    def _generate_python_template(self, version: str, description: str) -> str:
        """Generate Python migration template."""
        return f'''"""
Migration: {description}
Version: {version}
"""

from fennec.migrations import PythonMigration


class Migration{version}(PythonMigration):
    """
    {description}
    """
    
    def __init__(self):
        super().__init__(
            version="{version}",
            description="{description}"
        )
    
    async def up(self, connection):
        """Apply migration."""
        # TODO: Implement upgrade logic
        pass
    
    async def down(self, connection):
        """Revert migration."""
        # TODO: Implement downgrade logic
        pass


# Migration instance
migration = Migration{version}()
'''
    
    def _generate_sql_template(self, version: str, description: str) -> str:
        """Generate SQL migration template."""
        return f'''"""
Migration: {description}
Version: {version}
"""

from fennec.migrations import SQLMigration


# Define your SQL statements
UP_SQL = """
-- TODO: Add upgrade SQL
"""

DOWN_SQL = """
-- TODO: Add downgrade SQL
"""


# Migration instance
migration = SQLMigration(
    version="{version}",
    description="{description}",
    up_sql=UP_SQL,
    down_sql=DOWN_SQL
)
'''
    
    async def migrate(self, target: Optional[str] = None) -> int:
        """
        Apply pending migrations.
        
        Args:
            target: Target version (applies all if None)
            
        Returns:
            Number of migrations applied
        """
        await self.init()
        
        # Load migrations
        migrations = self._load_migrations()
        applied = await self._get_applied_migrations()
        
        # Filter pending migrations
        pending = [m for m in migrations if m.version not in applied]
        
        if target:
            pending = [m for m in pending if m.version <= target]
        
        if not pending:
            print("No pending migrations")
            return 0
        
        # Apply migrations
        count = 0
        for migration in pending:
            try:
                print(f"Applying migration {migration.version}: {migration.description}")
                
                start_time = datetime.now()
                
                # Begin transaction
                async with self.connection.transaction():
                    await migration.up(self.connection)
                    
                    execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    await self._mark_migration_applied(
                        migration.version,
                        migration.description,
                        execution_time
                    )
                
                print(f"✓ Applied {migration.version} ({execution_time}ms)")
                count += 1
                
            except Exception as e:
                print(f"✗ Failed to apply {migration.version}: {e}")
                print("Rolling back...")
                raise
        
        return count
    
    async def rollback(self, steps: int = 1) -> int:
        """
        Rollback migrations.
        
        Args:
            steps: Number of migrations to rollback
            
        Returns:
            Number of migrations rolled back
        """
        await self.init()
        
        # Load migrations
        migrations = self._load_migrations()
        applied = await self._get_applied_migrations()
        
        if not applied:
            print("No migrations to rollback")
            return 0
        
        # Get migrations to rollback
        to_rollback = applied[-steps:]
        migration_map = {m.version: m for m in migrations}
        
        count = 0
        for version in reversed(to_rollback):
            migration = migration_map.get(version)
            
            if not migration:
                print(f"Warning: Migration {version} not found in files")
                continue
            
            try:
                print(f"Rolling back {migration.version}: {migration.description}")
                
                # Begin transaction
                async with self.connection.transaction():
                    await migration.down(self.connection)
                    await self._mark_migration_reverted(migration.version)
                
                print(f"✓ Rolled back {migration.version}")
                count += 1
                
            except Exception as e:
                print(f"✗ Failed to rollback {migration.version}: {e}")
                raise
        
        return count
    
    async def status(self) -> dict:
        """
        Get migration status.
        
        Returns:
            Dictionary with migration status
        """
        await self.init()
        
        migrations = self._load_migrations()
        applied = await self._get_applied_migrations()
        
        pending = [m for m in migrations if m.version not in applied]
        applied_migrations = [m for m in migrations if m.version in applied]
        
        return {
            'total': len(migrations),
            'applied': len(applied_migrations),
            'pending': len(pending),
            'applied_list': [
                {
                    'version': m.version,
                    'description': m.description
                }
                for m in applied_migrations
            ],
            'pending_list': [
                {
                    'version': m.version,
                    'description': m.description
                }
                for m in pending
            ]
        }
