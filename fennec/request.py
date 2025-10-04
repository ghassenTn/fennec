"""
Request and Response classes
"""

from typing import Any, Dict, Optional
import json
from urllib.parse import parse_qs


class Request:
    """
    يمثل HTTP request
    يوفر واجهة سهلة للوصول إلى بيانات الـ request
    """
    
    def __init__(self, scope: Dict, receive):
        self.scope = scope
        self.receive = receive
        self.path_params: Dict[str, Any] = {}
        self.query_params: Dict[str, Any] = {}
        self._body: Optional[bytes] = None
        self._json: Optional[Dict] = None
        
        # Parse query parameters from scope
        query_string = scope.get("query_string", b"").decode("utf-8")
        if query_string:
            parsed = parse_qs(query_string)
            # Convert lists to single values if only one item
            self.query_params = {
                k: v[0] if len(v) == 1 else v 
                for k, v in parsed.items()
            }
    
    async def body(self) -> bytes:
        """
        قراءة raw request body
        """
        if self._body is None:
            body_parts = []
            while True:
                message = await self.receive()
                if message["type"] == "http.request":
                    body_parts.append(message.get("body", b""))
                    if not message.get("more_body", False):
                        break
            self._body = b"".join(body_parts)
        return self._body
    
    async def json(self) -> Dict:
        """
        قراءة request body كـ JSON
        """
        if self._json is None:
            body = await self.body()
            if body:
                self._json = json.loads(body.decode("utf-8"))
            else:
                self._json = {}
        return self._json
    
    @property
    def headers(self) -> Dict[str, str]:
        """
        الحصول على request headers
        """
        return {
            key.decode("utf-8"): value.decode("utf-8")
            for key, value in self.scope.get("headers", [])
        }
    
    @property
    def method(self) -> str:
        """
        الحصول على HTTP method
        """
        return self.scope.get("method", "GET")
    
    @property
    def path(self) -> str:
        """
        الحصول على request path
        """
        return self.scope.get("path", "/")


class Response:
    """
    يمثل HTTP response
    """
    
    def __init__(
        self, 
        content: Any, 
        status_code: int = 200, 
        headers: Optional[Dict[str, str]] = None
    ):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}
    
    async def __call__(self, send):
        """
        إرسال response عبر ASGI
        """
        # Prepare headers
        headers_list = [
            (key.encode("utf-8"), value.encode("utf-8"))
            for key, value in self.headers.items()
        ]
        
        # Send response start
        await send({
            "type": "http.response.start",
            "status": self.status_code,
            "headers": headers_list,
        })
        
        # Prepare body
        if isinstance(self.content, str):
            body = self.content.encode("utf-8")
        elif isinstance(self.content, bytes):
            body = self.content
        elif isinstance(self.content, dict):
            body = json.dumps(self.content).encode("utf-8")
        else:
            body = str(self.content).encode("utf-8")
        
        # Send response body
        await send({
            "type": "http.response.body",
            "body": body,
        })


class JSONResponse(Response):
    """
    Response بصيغة JSON مع structured format
    يتبع الصيغة الموحدة: {"status": "success/error", "data": {...}, "message": ""}
    """
    
    def __init__(
        self, 
        data: Any = None, 
        message: str = "", 
        status: str = "success", 
        status_code: int = 200
    ):
        content = {
            "status": status,
            "data": data,
            "message": message
        }
        
        headers = {"content-type": "application/json"}
        super().__init__(content, status_code, headers)
