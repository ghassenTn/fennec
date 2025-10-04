"""
Dependency injection system
"""

from typing import Callable, Dict, Any
import inspect
from contextlib import asynccontextmanager


class DependencyInjector:
    """
    يدير dependency injection
    يحل dependencies تلقائياً من function signatures
    """
    
    def __init__(self):
        self.dependencies: Dict[str, Callable] = {}
        self.overrides: Dict[str, Callable] = {}
    
    def register(self, name: str, factory: Callable):
        """
        تسجيل dependency
        
        Args:
            name: اسم الـ dependency
            factory: function تنشئ الـ dependency
        """
        self.dependencies[name] = factory
    
    def override(self, name: str, factory: Callable):
        """
        Override dependency (مفيد للـ testing)
        
        Args:
            name: اسم الـ dependency
            factory: function بديلة
        """
        self.overrides[name] = factory
    
    async def resolve(self, func: Callable) -> Dict[str, Any]:
        """
        Resolve dependencies لـ function من signature
        
        Args:
            func: الـ function المراد حل dependencies لها
        
        Returns:
            Dictionary من resolved dependencies
        """
        sig = inspect.signature(func)
        resolved = {}
        
        for param_name, param in sig.parameters.items():
            # Skip self, request, and other non-dependency parameters
            if param_name in ('self', 'request'):
                continue
            
            # Check if parameter has a default value that's a DependencyMarker
            if param.default != inspect.Parameter.empty:
                if isinstance(param.default, DependencyMarker):
                    # Resolve the dependency
                    dependency_func = param.default.dependency
                    
                    # Check for override
                    if param_name in self.overrides:
                        dependency_func = self.overrides[param_name]
                    
                    # Call the dependency function
                    if inspect.iscoroutinefunction(dependency_func):
                        value = await dependency_func()
                    elif inspect.isgeneratorfunction(dependency_func):
                        # Handle generator (for resource management)
                        gen = dependency_func()
                        value = next(gen)
                    elif inspect.isasyncgenfunction(dependency_func):
                        # Handle async generator
                        gen = dependency_func()
                        value = await gen.__anext__()
                    else:
                        value = dependency_func()
                    
                    resolved[param_name] = value
        
        return resolved
    
    async def inject(self, func: Callable, **kwargs) -> Any:
        """
        Execute function مع dependency injection
        
        Args:
            func: الـ function المراد تنفيذها
            **kwargs: arguments إضافية
        
        Returns:
            نتيجة تنفيذ الـ function
        """
        # Resolve dependencies
        dependencies = await self.resolve(func)
        
        # Merge with provided kwargs
        all_kwargs = {**dependencies, **kwargs}
        
        # Filter kwargs to only include parameters that the function accepts
        sig = inspect.signature(func)
        filtered_kwargs = {}
        for param_name in sig.parameters.keys():
            if param_name in all_kwargs:
                filtered_kwargs[param_name] = all_kwargs[param_name]
        
        # Execute function
        if inspect.iscoroutinefunction(func):
            return await func(**filtered_kwargs)
        else:
            return func(**filtered_kwargs)


class DependencyMarker:
    """
    Marker لـ dependency injection
    """
    
    def __init__(self, dependency: Callable):
        self.dependency = dependency


def Depends(dependency: Callable):
    """
    Marker function لـ dependency injection
    
    Usage:
        def get_db():
            return Database()
        
        @router.get("/users")
        async def get_users(db = Depends(get_db)):
            return db.query("SELECT * FROM users")
    """
    return DependencyMarker(dependency)
