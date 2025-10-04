"""
Security features including authentication, authorization, CORS, and rate limiting
"""

from fennec.security.auth import (
    JWTHandler,
    EnhancedJWTHandler,
    requires_auth,
    requires_role,
    has_permission,
    get_current_user,
)
from fennec.security.cors import CORSMiddleware
from fennec.security.rate_limit import RateLimitMiddleware
from fennec.security.password import PasswordHasher
from fennec.security.headers import SecurityHeadersMiddleware, RequestSizeLimitMiddleware
from fennec.security.csrf import CSRFMiddleware
from fennec.security.sanitize import InputSanitizer

__all__ = [
    "JWTHandler",
    "EnhancedJWTHandler",
    "requires_auth",
    "requires_role",
    "has_permission",
    "get_current_user",
    "CORSMiddleware",
    "RateLimitMiddleware",
    "PasswordHasher",
    "SecurityHeadersMiddleware",
    "RequestSizeLimitMiddleware",
    "CSRFMiddleware",
    "InputSanitizer",
]
