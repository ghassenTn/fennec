"""
Database abstraction layer
"""

from fennec.db.repository import Repository
from fennec.db.connection import DatabaseConnection

__all__ = ["Repository", "DatabaseConnection"]
