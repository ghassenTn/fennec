"""
Testing utilities
"""

from typing import Any, Dict, Optional
import json
import asyncio


class TestClient:
    """
    Client للاختبار بدون server حقيقي
    يسمح باختبار routes بدون تشغيل server
    """

    def __init__(self, app):
        self.app = app

    async def request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ):
        """
        إرسال request للـ application

        Args:
            method: HTTP method
            path: Request path
            json_data: JSON body
            headers: Request headers

        Returns:
            TestResponse object
        """
        # Build ASGI scope
        scope = {
            "type": "http",
            "method": method.upper(),
            "path": path,
            "query_string": b"",
            "headers": [],
        }

        # Add headers
        if headers:
            scope["headers"] = [
                (k.lower().encode(), v.encode()) for k, v in headers.items()
            ]

        # Add content-type for JSON
        if json_data:
            scope["headers"].append((b"content-type", b"application/json"))

        # Build receive callable
        body = json.dumps(json_data).encode() if json_data else b""
        body_sent = False

        async def receive():
            nonlocal body_sent
            if not body_sent:
                body_sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.request", "body": b"", "more_body": False}

        # Build send callable
        response_started = False
        response_body = b""
        response_status = 200
        response_headers = {}

        async def send(message):
            nonlocal response_started, response_body, response_status, response_headers

            if message["type"] == "http.response.start":
                response_started = True
                response_status = message["status"]
                response_headers = {
                    k.decode(): v.decode() for k, v in message.get("headers", [])
                }
            elif message["type"] == "http.response.body":
                response_body += message.get("body", b"")

        # Call application
        await self.app(scope, receive, send)

        # Return response
        return TestResponse(response_status, response_headers, response_body)

    async def get(self, path: str, headers: Optional[Dict] = None):
        """إرسال GET request"""
        return await self.request("GET", path, headers=headers)

    async def post(
        self, path: str, json_data: Optional[Dict] = None, headers: Optional[Dict] = None
    ):
        """إرسال POST request"""
        return await self.request("POST", path, json_data=json_data, headers=headers)

    async def put(
        self, path: str, json_data: Optional[Dict] = None, headers: Optional[Dict] = None
    ):
        """إرسال PUT request"""
        return await self.request("PUT", path, json_data=json_data, headers=headers)

    async def delete(self, path: str, headers: Optional[Dict] = None):
        """إرسال DELETE request"""
        return await self.request("DELETE", path, headers=headers)

    async def patch(
        self, path: str, json_data: Optional[Dict] = None, headers: Optional[Dict] = None
    ):
        """إرسال PATCH request"""
        return await self.request("PATCH", path, json_data=json_data, headers=headers)


class TestResponse:
    """
    Test response object
    """

    def __init__(self, status_code: int, headers: Dict[str, str], body: bytes):
        self.status_code = status_code
        self.headers = headers
        self._body = body

    @property
    def text(self) -> str:
        """Get response as text"""
        return self._body.decode()

    def json(self) -> Dict:
        """Get response as JSON"""
        return json.loads(self._body.decode())

    @property
    def content(self) -> bytes:
        """Get raw response body"""
        return self._body
