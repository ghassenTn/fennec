"""
Database connection management
"""

from typing import Any, Dict, Optional


class DatabaseConnection:
    """
    يدير database connection
    يوفر واجهة موحدة للتعامل مع قواعد البيانات
    """
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection: Optional[Any] = None
        self._is_connected = False
    
    async def connect(self):
        """
        فتح connection مع قاعدة البيانات
        يجب override هذه الـ method في subclasses
        """
        # This is a base implementation
        # Subclasses should implement actual connection logic
        self._is_connected = True
    
    async def disconnect(self):
        """
        إغلاق connection مع قاعدة البيانات
        """
        if self.connection:
            # Subclasses should implement actual disconnection logic
            self.connection = None
        self._is_connected = False
    
    async def execute(self, query: str, params: Optional[Dict] = None) -> Any:
        """
        تنفيذ query على قاعدة البيانات
        
        Args:
            query: SQL query أو command
            params: Parameters للـ query
        
        Returns:
            نتيجة الـ query
        """
        if not self._is_connected:
            await self.connect()
        
        # This is a base implementation
        # Subclasses should implement actual query execution
        raise NotImplementedError("Subclasses must implement execute method")
    
    async def __aenter__(self):
        """
        Context manager support
        """
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager cleanup
        """
        await self.disconnect()
