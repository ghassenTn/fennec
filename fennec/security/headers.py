"""
Security headers middleware
"""

from fennec.middleware import Middleware
from fennec.request import Request
from typing import Callable, Dict


class SecurityHeadersMiddleware(Middleware):
    """
    Add security headers to all responses
    """

    def __init__(
        self,
        x_content_type_options: str = "nosniff",
        x_frame_options: str = "DENY",
        x_xss_protection: str = "1; mode=block",
        referrer_policy: str = "strict-origin-when-cross-origin",
        content_security_policy: str = "default-src 'self'",
        strict_transport_security: str = "max-age=31536000; includeSubDomains",
        custom_headers: Dict[str, str] = None
    ):
        """
        Initialize security headers middleware

        Args:
            x_content_type_options: X-Content-Type-Options header value
            x_frame_options: X-Frame-Options header value
            x_xss_protection: X-XSS-Protection header value
            referrer_policy: Referrer-Policy header value
            content_security_policy: Content-Security-Policy header value
            strict_transport_security: Strict-Transport-Security header value
            custom_headers: Additional custom headers
        """
        self.headers = {
            "X-Content-Type-Options": x_content_type_options,
            "X-Frame-Options": x_frame_options,
            "X-XSS-Protection": x_xss_protection,
            "Referrer-Policy": referrer_policy,
            "Content-Security-Policy": content_security_policy,
            "Strict-Transport-Security": strict_transport_security,
        }

        if custom_headers:
            self.headers.update(custom_headers)

    async def __call__(self, request: Request, call_next: Callable):
        """
        Add security headers to response

        Args:
            request: Request object
            call_next: Next middleware/handler

        Returns:
            Response with security headers
        """
        response = await call_next(request)

        # Convert dict responses to Response objects
        if isinstance(response, dict):
            from fennec.request import JSONResponse
            response = JSONResponse(data=response)

        # Add security headers
        for header, value in self.headers.items():
            # Relax CSP for documentation endpoints
            if header == "Content-Security-Policy" and request.path in ["/docs", "/graphql/graphiql"]:
                # Allow CDN resources for Swagger UI and GraphiQL
                relaxed_csp = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
                    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
                    "img-src 'self' data: https:; "
                    "font-src 'self' data:;"
                )
                response.headers[header] = relaxed_csp
            else:
                response.headers[header] = value

        return response


class RequestSizeLimitMiddleware(Middleware):
    """
    Limit request body size to prevent memory exhaustion
    """

    def __init__(self, max_size: int = 10 * 1024 * 1024):
        """
        Initialize request size limit middleware

        Args:
            max_size: Maximum request size in bytes (default: 10MB)
        """
        self.max_size = max_size

    async def __call__(self, request: Request, call_next: Callable):
        """
        Check request size before processing

        Args:
            request: Request object
            call_next: Next middleware/handler

        Returns:
            Response or raises exception if too large
        """
        from fennec.exceptions import HTTPException

        content_length = request.headers.get("content-length")

        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    raise HTTPException(
                        413,
                        f"Request too large. Maximum size: {self.max_size} bytes"
                    )
            except ValueError:
                pass

        return await call_next(request)
