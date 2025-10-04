"""
Migration: add users index
Version: 20240104120100
"""

from fennec.migrations.migration import SQLMigration


# Define SQL statements
UP_SQL = """
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
"""

DOWN_SQL = """
DROP INDEX IF EXISTS idx_users_email;
DROP INDEX IF EXISTS idx_users_username;
"""


# Migration instance
migration = SQLMigration(
    version="20240104120100",
    description="add users index",
    up_sql=UP_SQL,
    down_sql=DOWN_SQL
)
