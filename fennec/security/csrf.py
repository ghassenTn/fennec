"""
CSRF (Cross-Site Request Forgery) protection middleware
"""

from fennec.middleware import Middleware
from fennec.request import Request
from fennec.exceptions import HTTPException
from typing import Callable, List
import secrets
import hmac
import hashlib
import time


class CSRFMiddleware(Middleware):
    """
    CSRF protection middleware
    """

    def __init__(
        self,
        secret_key: str,
        token_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        safe_methods: List[str] = None,
        token_expiry: int = 3600
    ):
        """
        Initialize CSRF middleware

        Args:
            secret_key: Secret key for token generation
            token_name: Form field name for CSRF token
            header_name: HTTP header name for CSRF token
            safe_methods: HTTP methods that don't require CSRF protection
            token_expiry: Token expiration time in seconds (default: 1 hour)
        """
        self.secret_key = secret_key
        self.token_name = token_name
        self.header_name = header_name
        self.safe_methods = safe_methods or ["GET", "HEAD", "OPTIONS", "TRACE"]
        self.token_expiry = token_expiry

    def generate_token(self, session_id: str = None) -> str:
        """
        Generate CSRF token

        Args:
            session_id: Optional session identifier

        Returns:
            CSRF token string
        """
        # Generate random token
        random_part = secrets.token_urlsafe(32)
        timestamp = str(int(time.time()))
        session_part = session_id or ""

        # Create message to sign
        message = f"{random_part}:{timestamp}:{session_part}"

        # Create signature
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        # Combine into token
        token = f"{random_part}.{timestamp}.{signature}"
        return token

    def validate_token(self, token: str, session_id: str = None) -> bool:
        """
        Validate CSRF token

        Args:
            token: CSRF token to validate
            session_id: Optional session identifier

        Returns:
            True if valid, False otherwise
        """
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return False

            random_part, timestamp, signature = parts

            # Check expiration
            token_time = int(timestamp)
            if time.time() - token_time > self.token_expiry:
                return False

            # Recreate message
            session_part = session_id or ""
            message = f"{random_part}:{timestamp}:{session_part}"

            # Verify signature
            expected_signature = hmac.new(
                self.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        except Exception:
            return False

    async def __call__(self, request: Request, call_next: Callable):
        """
        Validate CSRF token for unsafe methods

        Args:
            request: Request object
            call_next: Next middleware/handler

        Returns:
            Response or raises exception if CSRF validation fails
        """
        # Skip CSRF check for safe methods
        if request.method in self.safe_methods:
            return await call_next(request)

        # Get token from header or form data
        token = request.headers.get(self.header_name.lower())

        if not token and hasattr(request, 'form'):
            form_data = await request.form()
            token = form_data.get(self.token_name)

        if not token:
            raise HTTPException(403, "CSRF token missing")

        # Get session ID if available
        session_id = getattr(request, 'session_id', None)

        # Validate token
        if not self.validate_token(token, session_id):
            raise HTTPException(403, "CSRF token invalid or expired")

        return await call_next(request)
