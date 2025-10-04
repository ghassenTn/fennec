"""
CORS (Cross-Origin Resource Sharing) middleware
"""

from typing import List, Callable
from fennec.middleware import Middleware
from fennec.request import Request, Response


class CORSMiddleware(Middleware):
    """
    CORS middleware
    يتعامل مع CORS headers و preflight requests
    """

    def __init__(
        self,
        allow_origins: List[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        allow_credentials: bool = False,
        max_age: int = 600,
    ):
        """
        Args:
            allow_origins: قائمة الـ origins المسموح بها (["*"] للسماح للجميع)
            allow_methods: HTTP methods المسموح بها
            allow_headers: Headers المسموح بها
            allow_credentials: السماح بإرسال credentials
            max_age: مدة cache للـ preflight request
        """
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "OPTIONS",
        ]
        self.allow_headers = allow_headers or [
            "Content-Type",
            "Authorization",
        ]
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    def _is_origin_allowed(self, origin: str) -> bool:
        """
        التحقق من أن الـ origin مسموح به
        """
        if "*" in self.allow_origins:
            return True
        return origin in self.allow_origins

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        معالجة CORS
        """
        origin = request.headers.get("origin", "")

        # Handle preflight request
        if request.method == "OPTIONS":
            response = Response("", status_code=200)
        else:
            # Continue to next middleware/handler
            response = await call_next(request)
        
        # Convert dict responses to Response objects
        if isinstance(response, dict):
            from fennec.request import JSONResponse
            response = JSONResponse(data=response)

        # Add CORS headers if origin is allowed
        if origin and self._is_origin_allowed(origin):
            # Allow specific origin or *
            if "*" in self.allow_origins:
                response.headers["Access-Control-Allow-Origin"] = "*"
            else:
                response.headers["Access-Control-Allow-Origin"] = origin

            # Allow methods
            response.headers["Access-Control-Allow-Methods"] = ", ".join(
                self.allow_methods
            )

            # Allow headers
            response.headers["Access-Control-Allow-Headers"] = ", ".join(
                self.allow_headers
            )

            # Allow credentials
            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"

            # Max age for preflight cache
            response.headers["Access-Control-Max-Age"] = str(self.max_age)

        return response
