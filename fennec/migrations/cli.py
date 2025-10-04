"""
Migration CLI Commands

Command-line interface for database migrations.
"""

import asyncio
import sys
from typing import Optional


class MigrationCLI:
    """CLI for database migrations."""
    
    def __init__(self, manager):
        """
        Initialize CLI.
        
        Args:
            manager: MigrationManager instance
        """
        self.manager = manager
    
    async def create(self, description: str, migration_type: str = "python"):
        """Create a new migration."""
        filepath = await self.manager.create(description, migration_type)
        print(f"✓ Created migration: {filepath}")
    
    async def migrate(self, target: Optional[str] = None):
        """Apply pending migrations."""
        count = await self.manager.migrate(target)
        if count > 0:
            print(f"\n✓ Applied {count} migration(s)")
        else:
            print("\n✓ No migrations to apply")
    
    async def rollback(self, steps: int = 1):
        """Rollback migrations."""
        count = await self.manager.rollback(steps)
        if count > 0:
            print(f"\n✓ Rolled back {count} migration(s)")
        else:
            print("\n✓ No migrations to rollback")
    
    async def status(self):
        """Show migration status."""
        status = await self.manager.status()
        
        print(f"\nMigration Status:")
        print(f"  Total: {status['total']}")
        print(f"  Applied: {status['applied']}")
        print(f"  Pending: {status['pending']}")
        
        if status['applied_list']:
            print(f"\nApplied Migrations:")
            for m in status['applied_list']:
                print(f"  ✓ {m['version']}: {m['description']}")
        
        if status['pending_list']:
            print(f"\nPending Migrations:")
            for m in status['pending_list']:
                print(f"  ○ {m['version']}: {m['description']}")
    
    def run(self, args: list):
        """
        Run CLI command.
        
        Args:
            args: Command-line arguments
        """
        if len(args) < 1:
            self._print_help()
            return
        
        command = args[0]
        
        if command == "create":
            if len(args) < 2:
                print("Error: Description required")
                print("Usage: migrate create <description> [--sql]")
                return
            
            description = args[1]
            migration_type = "sql" if "--sql" in args else "python"
            asyncio.run(self.create(description, migration_type))
        
        elif command == "migrate":
            target = args[1] if len(args) > 1 else None
            asyncio.run(self.migrate(target))
        
        elif command == "rollback":
            steps = int(args[1]) if len(args) > 1 else 1
            asyncio.run(self.rollback(steps))
        
        elif command == "status":
            asyncio.run(self.status())
        
        else:
            print(f"Unknown command: {command}")
            self._print_help()
    
    def _print_help(self):
        """Print help message."""
        print("""
Fennec Migration CLI

Usage:
  migrate create <description> [--sql]  Create a new migration
  migrate migrate [target]              Apply pending migrations
  migrate rollback [steps]              Rollback migrations (default: 1)
  migrate status                        Show migration status

Examples:
  migrate create "add users table"
  migrate create "add index" --sql
  migrate migrate
  migrate rollback
  migrate rollback 3
  migrate status
""")


def main():
    """Main entry point for CLI."""
    # This would be called from a script that sets up the database connection
    print("Use MigrationCLI with your database connection")
    print("See examples/migration_example/ for usage")


if __name__ == "__main__":
    main()
