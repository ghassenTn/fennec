"""
Exception classes
"""

from typing import Dict, Optional


class HTTPException(Exception):
    """
    Base exception لجميع HTTP exceptions
    """
    
    def __init__(self, status_code: int, message: str, details: Optional[Dict] = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(HTTPException):
    """
    404 Not Found exception
    """
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(404, message)


class ValidationException(HTTPException):
    """
    422 Validation Error exception
    """
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict] = None):
        super().__init__(422, message, details)


class UnauthorizedException(HTTPException):
    """
    401 Unauthorized exception
    """
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(401, message)
