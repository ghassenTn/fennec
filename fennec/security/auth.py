"""
Authentication system
"""

from typing import Callable, Optional, Dict, Any, Set
from fennec.request import Request
from fennec.exceptions import UnauthorizedException
import base64
import hmac
import hashlib
import json
import time


class JWTHandler:
    """
    Simple JWT token handler
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def encode(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """
        إنشاء JWT token

        Args:
            payload: البيانات المراد تشفيرها
            expires_in: مدة صلاحية الـ token بالثواني

        Returns:
            JWT token string
        """
        # Add expiration
        payload["exp"] = int(time.time()) + expires_in

        # Encode header
        header = {"alg": self.algorithm, "typ": "JWT"}
        header_encoded = self._base64_encode(json.dumps(header))

        # Encode payload
        payload_encoded = self._base64_encode(json.dumps(payload))

        # Create signature
        message = f"{header_encoded}.{payload_encoded}"
        signature = self._sign(message)

        return f"{message}.{signature}"

    def decode(self, token: str) -> Dict[str, Any]:
        """
        فك تشفير JWT token

        Args:
            token: JWT token string

        Returns:
            Payload dictionary

        Raises:
            UnauthorizedException: إذا كان الـ token غير صالح
        """
        try:
            parts = token.split(".")
            if len(parts) != 3:
                raise UnauthorizedException("Invalid token format")

            header_encoded, payload_encoded, signature = parts

            # Verify signature
            message = f"{header_encoded}.{payload_encoded}"
            expected_signature = self._sign(message)

            if not hmac.compare_digest(signature, expected_signature):
                raise UnauthorizedException("Invalid token signature")

            # Decode payload
            payload = json.loads(self._base64_decode(payload_encoded))

            # Check expiration
            if "exp" in payload:
                if payload["exp"] < time.time():
                    raise UnauthorizedException("Token expired")

            return payload

        except Exception as e:
            if isinstance(e, UnauthorizedException):
                raise
            raise UnauthorizedException("Invalid token")

    def _base64_encode(self, data: str) -> str:
        """Base64 URL-safe encoding"""
        return (
            base64.urlsafe_b64encode(data.encode()).decode().rstrip("=")
        )

    def _base64_decode(self, data: str) -> str:
        """Base64 URL-safe decoding"""
        # Add padding if needed
        padding = 4 - (len(data) % 4)
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data.encode()).decode()

    def _sign(self, message: str) -> str:
        """Create HMAC signature"""
        signature = hmac.new(
            self.secret_key.encode(), message.encode(), hashlib.sha256
        ).digest()
        return base64.urlsafe_b64encode(signature).decode().rstrip("=")


def requires_auth(func: Callable) -> Callable:
    """
    Decorator للتحقق من authentication

    Usage:
        @router.get("/protected")
        @requires_auth
        async def protected_route(request: Request):
            return {"message": "Authenticated"}
    """

    async def wrapper(request: Request, *args, **kwargs):
        # Check for Authorization header
        auth_header = request.headers.get("authorization", "")

        if not auth_header:
            raise UnauthorizedException("Missing authorization header")

        # Extract token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise UnauthorizedException("Invalid authorization header format")

        token = parts[1]

        # Store token in request for handler to use
        request.auth_token = token

        # Call original function
        return await func(request, *args, **kwargs)

    return wrapper


def get_current_user(request: Request, jwt_handler: JWTHandler) -> Dict[str, Any]:
    """
    استخراج معلومات المستخدم من الـ token

    Usage with dependency injection:
        def get_user(request: Request):
            jwt = JWTHandler(secret_key="your-secret")
            return get_current_user(request, jwt)

        @router.get("/me")
        async def me(user = Depends(get_user)):
            return {"user": user}
    """
    if not hasattr(request, "auth_token"):
        raise UnauthorizedException("Not authenticated")

    payload = jwt_handler.decode(request.auth_token)
    return payload



class ForbiddenException(Exception):
    """
    403 Forbidden exception
    """

    def __init__(self, message: str = "Forbidden"):
        self.status_code = 403
        self.message = message
        super().__init__(self.message)


def requires_role(*roles: str):
    """
    Decorator للتحقق من role-based authorization

    Usage:
        @router.get("/admin")
        @requires_role("admin", "superuser")
        async def admin_route(request: Request):
            return {"message": "Admin access"}
    """

    def decorator(func: Callable) -> Callable:
        async def wrapper(request: Request, *args, **kwargs):
            # Check if user is authenticated
            if not hasattr(request, "auth_token"):
                raise UnauthorizedException("Not authenticated")

            # Get user info (assumes JWT payload has 'role' field)
            # In production, you'd want to decode the token properly
            user_role = getattr(request, "user_role", None)

            if not user_role or user_role not in roles:
                raise ForbiddenException(
                    f"Required role: {', '.join(roles)}"
                )

            # Call original function
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


def has_permission(permission: str):
    """
    Decorator للتحقق من permission-based authorization

    Usage:
        @router.delete("/users/{id}")
        @has_permission("users:delete")
        async def delete_user(request: Request, id: int):
            return {"message": "User deleted"}
    """

    def decorator(func: Callable) -> Callable:
        async def wrapper(request: Request, *args, **kwargs):
            # Check if user is authenticated
            if not hasattr(request, "auth_token"):
                raise UnauthorizedException("Not authenticated")

            # Get user permissions (assumes JWT payload has 'permissions' field)
            user_permissions = getattr(request, "user_permissions", [])

            if permission not in user_permissions:
                raise ForbiddenException(
                    f"Required permission: {permission}"
                )

            # Call original function
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


class EnhancedJWTHandler(JWTHandler):
    """
    Enhanced JWT handler with refresh tokens and blacklist
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        super().__init__(secret_key, algorithm)
        self.blacklist: Set[str] = set()  # In production: use Redis or database

    def create_access_token(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """
        Create access token (short-lived)

        Args:
            payload: Token payload
            expires_in: Expiration time in seconds (default: 1 hour)

        Returns:
            Access token string
        """
        payload["type"] = "access"
        return self.encode(payload, expires_in)

    def create_refresh_token(self, payload: Dict[str, Any], expires_in: int = 604800) -> str:
        """
        Create refresh token (long-lived)

        Args:
            payload: Token payload
            expires_in: Expiration time in seconds (default: 7 days)

        Returns:
            Refresh token string
        """
        payload["type"] = "refresh"
        return self.encode(payload, expires_in)

    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Create new access token from refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token

        Raises:
            UnauthorizedException: If refresh token is invalid or revoked
        """
        # Check if token is revoked
        if self.is_revoked(refresh_token):
            raise UnauthorizedException("Token has been revoked")

        # Decode refresh token
        payload = self.decode(refresh_token)

        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type")

        # Create new access token with same payload (minus exp and type)
        new_payload = {k: v for k, v in payload.items() if k not in ["exp", "type"]}
        return self.create_access_token(new_payload)

    def revoke_token(self, token: str) -> None:
        """
        Add token to blacklist

        Args:
            token: Token to revoke
        """
        self.blacklist.add(token)

    def is_revoked(self, token: str) -> bool:
        """
        Check if token is revoked

        Args:
            token: Token to check

        Returns:
            True if revoked, False otherwise
        """
        return token in self.blacklist

    def decode(self, token: str) -> Dict[str, Any]:
        """
        Decode token with revocation check

        Args:
            token: JWT token

        Returns:
            Token payload

        Raises:
            UnauthorizedException: If token is invalid or revoked
        """
        # Check if token is revoked
        if self.is_revoked(token):
            raise UnauthorizedException("Token has been revoked")

        # Decode using parent method
        return super().decode(token)
