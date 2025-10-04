"""
Middleware system
"""

from typing import Callable, List
from fennec.request import Request, Response


class Middleware:
    """
    Base class لجميع middleware
    """
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        تنفيذ middleware logic
        
        Args:
            request: HTTP request
            call_next: الـ function التالي في الـ chain
        
        Returns:
            Response object
        """
        # Pre-processing (قبل تنفيذ الـ handler)
        # يمكن تعديل الـ request هنا
        
        # Call next middleware or handler
        response = await call_next(request)
        
        # Post-processing (بعد تنفيذ الـ handler)
        # يمكن تعديل الـ response هنا
        
        return response


class MiddlewareManager:
    """
    يدير middleware chain
    ينفذ middleware بالترتيب المسجل
    """
    
    def __init__(self):
        self.middleware_stack: List[Middleware] = []
    
    def add(self, middleware: Middleware):
        """
        إضافة middleware للـ stack
        """
        self.middleware_stack.append(middleware)
    
    async def execute(self, request: Request, handler: Callable) -> Response:
        """
        تنفيذ middleware chain
        
        Args:
            request: HTTP request
            handler: الـ route handler النهائي
        
        Returns:
            Response object
        """
        # Build the chain from the end
        async def build_chain(index: int):
            if index >= len(self.middleware_stack):
                # No more middleware, call the handler
                return await handler(request)
            
            # Get current middleware
            middleware = self.middleware_stack[index]
            
            # Create call_next function for this middleware
            async def call_next(req: Request):
                return await build_chain(index + 1)
            
            # Execute middleware
            return await middleware(request, call_next)
        
        # Start the chain
        return await build_chain(0)
