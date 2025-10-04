"""
Rate limiting middleware
"""

from typing import Dict, Callable
from fennec.middleware import Middleware
from fennec.request import Request, Response, JSONResponse
import time


class RateLimitMiddleware(Middleware):
    """
    Rate limiting middleware
    يحد من عدد الـ requests لكل IP في فترة زمنية محددة
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Args:
            max_requests: الحد الأقصى للـ requests
            window_seconds: الفترة الزمنية بالثواني
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}

    def _get_client_ip(self, request: Request) -> str:
        """
        استخراج IP address من الـ request
        """
        # Check X-Forwarded-For header first (for proxies)
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Fallback to direct connection
        client = request.scope.get("client")
        if client:
            return client[0]

        return "unknown"

    def _clean_old_requests(self, client_ip: str, current_time: float):
        """
        حذف الـ requests القديمة خارج الـ window
        """
        if client_ip in self.requests:
            cutoff_time = current_time - self.window_seconds
            self.requests[client_ip] = [
                req_time
                for req_time in self.requests[client_ip]
                if req_time > cutoff_time
            ]

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        تنفيذ rate limiting
        """
        client_ip = self._get_client_ip(request)
        current_time = time.time()

        # Clean old requests
        self._clean_old_requests(client_ip, current_time)

        # Initialize if new client
        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Check rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                message=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds} seconds",
                status="error",
                status_code=429,
            )

        # Add current request
        self.requests[client_ip].append(current_time)

        # Continue to next middleware/handler
        response = await call_next(request)

        # Convert dict responses to JSONResponse
        if isinstance(response, dict):
            response = JSONResponse(data=response)

        # Add rate limit headers
        remaining = self.max_requests - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(
            int(current_time + self.window_seconds)
        )

        return response
