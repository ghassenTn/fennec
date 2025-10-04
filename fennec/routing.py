"""
Router implementation - URL routing and handler mapping
"""

from typing import List, Callable, Optional, Dict, Any
from dataclasses import dataclass
import re


@dataclass
class Route:
    """
    يمثل route definition
    """
    path: str
    handler: Callable
    methods: List[str]
    name: Optional[str] = None
    pattern: Optional[re.Pattern] = None
    param_names: Optional[List[str]] = None


@dataclass
class RouteMatch:
    """
    يمثل نتيجة route matching
    """
    handler: Callable
    path_params: Dict[str, Any]


class Router:
    """
    يدير routes وmapping بين paths وhandlers
    يدعم path parameters مثل /user/{id}
    """
    
    def __init__(self, prefix: str = ""):
        self.prefix = prefix.rstrip("/")
        self.routes: List[Route] = []
    
    def add_route(
        self, 
        path: str, 
        handler: Callable, 
        methods: List[str],
        name: Optional[str] = None
    ):
        """
        إضافة route جديد
        يدعم path parameters مثل /user/{id}
        """
        # Add prefix to path
        full_path = self.prefix + path
        
        # Convert path parameters to regex pattern
        # Example: /user/{id} -> /user/(?P<id>[^/]+)
        pattern_str = full_path
        param_names = []
        
        # Find all {param} patterns
        param_pattern = re.compile(r'\{([^}]+)\}')
        for match in param_pattern.finditer(full_path):
            param_name = match.group(1)
            param_names.append(param_name)
            # Replace {param} with regex group
            pattern_str = pattern_str.replace(
                f"{{{param_name}}}", 
                f"(?P<{param_name}>[^/]+)"
            )
        
        # Compile regex pattern
        pattern = re.compile(f"^{pattern_str}$")
        
        route = Route(
            path=full_path,
            handler=handler,
            methods=[m.upper() for m in methods],
            name=name,
            pattern=pattern,
            param_names=param_names
        )
        
        self.routes.append(route)
    
    async def match(self, path: str, method: str) -> Optional[RouteMatch]:
        """
        إيجاد handler مناسب للـ path والـ method
        يستخرج path parameters من الـ URL
        """
        method = method.upper()
        
        for route in self.routes:
            # Check if method matches
            if method not in route.methods:
                continue
            
            # Check if path matches
            match = route.pattern.match(path)
            if match:
                # Extract path parameters
                path_params = match.groupdict()
                
                # Convert numeric parameters to int if possible
                for key, value in path_params.items():
                    if value.isdigit():
                        path_params[key] = int(value)
                
                return RouteMatch(
                    handler=route.handler,
                    path_params=path_params
                )
        
        return None
    
    def get(self, path: str, name: Optional[str] = None):
        """
        Decorator لـ GET requests
        """
        def decorator(handler: Callable):
            self.add_route(path, handler, ["GET"], name)
            return handler
        return decorator
    
    def post(self, path: str, name: Optional[str] = None):
        """
        Decorator لـ POST requests
        """
        def decorator(handler: Callable):
            self.add_route(path, handler, ["POST"], name)
            return handler
        return decorator
    
    def put(self, path: str, name: Optional[str] = None):
        """
        Decorator لـ PUT requests
        """
        def decorator(handler: Callable):
            self.add_route(path, handler, ["PUT"], name)
            return handler
        return decorator
    
    def delete(self, path: str, name: Optional[str] = None):
        """
        Decorator لـ DELETE requests
        """
        def decorator(handler: Callable):
            self.add_route(path, handler, ["DELETE"], name)
            return handler
        return decorator
    
    def patch(self, path: str, name: Optional[str] = None):
        """
        Decorator لـ PATCH requests
        """
        def decorator(handler: Callable):
            self.add_route(path, handler, ["PATCH"], name)
            return handler
        return decorator
