"""
Fennec Framework 🦊
A lightweight, fast, and agile Python backend framework

Named after the Fennec fox - small, swift, and adaptable.
Perfect for building modern REST APIs with minimal overhead.

Example:
    from framework import Application, Router, JSONResponse
    
    app = Application(title="My API", version="1.0.0")
    router = Router()
    
    @router.get("/hello/{name}")
    async def hello(name: str):
        return JSONResponse(data={"message": f"Hello, {name}!"})
    
    app.include_router(router)
"""

__version__ = "0.2.0"
__author__ = "Fennec Team"
__framework_name__ = "Fennec"

from fennec.app import Application
from fennec.routing import Router
from fennec.request import Request, Response, JSONResponse
from fennec.exceptions import (
    HTTPException,
    NotFoundException,
    ValidationException,
    UnauthorizedException,
)
from fennec.validation import BaseModel, Field
from fennec.dependencies import Depends
from fennec.middleware import Middleware
from fennec.background import BackgroundTasks
from fennec.websocket import (
    WebSocket,
    WebSocketRouter,
    WebSocketManager,
    WebSocketException,
)
from fennec.graphql import (
    GraphQLEngine,
    GraphQLContext,
    GraphQLError,
    query,
    mutation,
    subscription,
)

__all__ = [
    "Application",
    "Router",
    "Request",
    "Response",
    "JSONResponse",
    "HTTPException",
    "NotFoundException",
    "ValidationException",
    "UnauthorizedException",
    "BaseModel",
    "Field",
    "Depends",
    "Middleware",
    "BackgroundTasks",
    "WebSocket",
    "WebSocketRouter",
    "WebSocketManager",
    "WebSocketException",
    "GraphQLEngine",
    "GraphQLContext",
    "GraphQLError",
    "query",
    "mutation",
    "subscription",
]
