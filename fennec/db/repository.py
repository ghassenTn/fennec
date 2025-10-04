"""
Repository pattern implementation
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Repository(ABC):
    """
    Base repository interface
    """
    
    @abstractmethod
    async def get(self, id: Any):
        """الحصول على entity بواسطة ID"""
        pass
    
    @abstractmethod
    async def list(self, filters: Optional[Dict] = None, limit: int = 100, offset: int = 0):
        """الحصول على list من entities"""
        pass
    
    @abstractmethod
    async def create(self, data: Dict):
        """إنشاء entity جديد"""
        pass
    
    @abstractmethod
    async def update(self, id: Any, data: Dict):
        """تحديث entity"""
        pass
    
    @abstractmethod
    async def delete(self, id: Any):
        """حذف entity"""
        pass
