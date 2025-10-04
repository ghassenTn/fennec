"""
Application core - Main application class
"""

from typing import Dict, Type, Callable, Any, List
from fennec.middleware import MiddlewareManager, Middleware
from fennec.routing import Router
from fennec.dependencies import DependencyInjector
from fennec.request import Request, Response, JSONResponse
from fennec.openapi import OpenAPIGenerator
import json


class Application:
    """
    المكون الرئيسي للـ framework
    يدير lifecycle الـ application ويوفر ASGI interface
    """
    
    def __init__(
        self, title: str = "API", version: str = "1.0.0", docs_enabled: bool = True
    ):
        self.title = title
        self.version = version
        self.router = Router()
        self.middleware_manager = MiddlewareManager()
        self.dependency_injector = DependencyInjector()
        self.exception_handlers: Dict[Type[Exception], Callable] = {}
        self._routers: List[Router] = []
        self._websocket_routers: List = []
        self._graphql_engines: Dict[str, Any] = {}
        self.docs_enabled = docs_enabled

        # Add documentation routes if enabled
        if self.docs_enabled:
            self._setup_docs_routes()
    
    def include_router(self, router: Router, prefix: str = ""):
        """
        إضافة router للـ application
        يسمح بتنظيم routes في modules منفصلة
        
        Args:
            router: Router instance
            prefix: URL prefix للـ routes (مثل /api/v1)
        """
        # Update router prefix
        if prefix:
            router.prefix = prefix.rstrip("/") + router.prefix
        
        # Add router to list
        self._routers.append(router)
        
        # Merge routes into main router
        self.router.routes.extend(router.routes)

    def include_websocket_router(self, ws_router, prefix: str = ""):
        """
        Add WebSocket router to application

        Args:
            ws_router: WebSocketRouter instance
            prefix: URL prefix for WebSocket routes
        """
        # Update router prefix
        if prefix:
            ws_router.prefix = prefix.rstrip("/") + ws_router.prefix

        # Add to WebSocket routers list
        self._websocket_routers.append(ws_router)

    def add_graphql(self, path: str, engine, graphiql: bool = True):
        """
        Add GraphQL endpoint to application

        Args:
            path: GraphQL endpoint path
            engine: GraphQLEngine instance
            graphiql: Enable GraphiQL interface
        """
        from fennec.graphql import GraphQLContext

        # Store engine
        self._graphql_engines[path] = engine

        # Add GraphQL endpoint
        async def graphql_handler(request: Request):
            # Get query from request
            if request.method == "GET":
                query = request.query_params.get("query", "")
                variables_str = request.query_params.get("variables", "{}")
                try:
                    variables = json.loads(variables_str)
                except:
                    variables = {}
            else:
                body = await request.json()
                query = body.get("query", "")
                variables = body.get("variables", {})
                operation_name = body.get("operationName")

            # Create context
            context = GraphQLContext(request=request)

            # Execute query
            result = await engine.execute(query, variables, context)

            return JSONResponse(data=result)

        self.router.add_route(path, graphql_handler, ["GET", "POST"])

        # Add GraphiQL interface
        if graphiql:
            graphiql_path = path.rstrip("/") + "/graphiql"

            async def graphiql_handler(request: Request):
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>GraphiQL</title>
                    <link rel="stylesheet" href="https://unpkg.com/graphiql/graphiql.min.css" />
                </head>
                <body style="margin: 0;">
                    <div id="graphiql" style="height: 100vh;"></div>
                    <script crossorigin src="https://unpkg.com/react/umd/react.production.min.js"></script>
                    <script crossorigin src="https://unpkg.com/react-dom/umd/react-dom.production.min.js"></script>
                    <script crossorigin src="https://unpkg.com/graphiql/graphiql.min.js"></script>
                    <script>
                        const fetcher = GraphiQL.createFetcher({{
                            url: '{graphql_path}',
                        }});
                        ReactDOM.render(
                            React.createElement(GraphiQL, {{ fetcher: fetcher }}),
                            document.getElementById('graphiql'),
                        );
                    </script>
                </body>
                </html>
                """.format(graphql_path=path)

                return Response(html, status_code=200, headers={"content-type": "text/html"})

            self.router.add_route(graphiql_path, graphiql_handler, ["GET"])
    
    def middleware(self, middleware_type: str = "http"):
        """
        Decorator لإضافة middleware
        
        Usage:
            @app.middleware("http")
            async def my_middleware(request, call_next):
                # Pre-processing
                response = await call_next(request)
                # Post-processing
                return response
        """
        def decorator(func: Callable):
            # Create a middleware instance from the function
            class FunctionMiddleware(Middleware):
                async def __call__(self, request, call_next):
                    return await func(request, call_next)
            
            # Add to middleware stack
            self.middleware_manager.add(FunctionMiddleware())
            return func
        
        return decorator
    
    def exception_handler(self, exc_class: Type[Exception]):
        """
        Decorator لإضافة exception handler
        
        Usage:
            @app.exception_handler(ValueError)
            async def handle_value_error(request, exc):
                return JSONResponse(
                    message=str(exc),
                    status="error",
                    status_code=400
                )
        """
        def decorator(func: Callable):
            self.exception_handlers[exc_class] = func
            return func
        
        return decorator
    
    async def __call__(self, scope: Dict, receive, send):
        """
        ASGI interface
        يستقبل requests ويعالجها
        
        Args:
            scope: ASGI scope dictionary
            receive: ASGI receive callable
            send: ASGI send callable
        """
        if scope["type"] == "http":
            await self.handle_http(scope, receive, send)
        elif scope["type"] == "websocket":
            await self.handle_websocket(scope, receive, send)
        elif scope["type"] == "lifespan":
            await self.handle_lifespan(scope, receive, send)
    
    async def handle_lifespan(self, scope: Dict, receive, send):
        """
        Handle ASGI lifespan events
        """
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return
    
    async def handle_http(self, scope: Dict, receive, send):
        """
        Handle HTTP requests
        """
        # Create Request object
        request = Request(scope, receive)
        
        try:
            # Find matching route
            route_match = await self.router.match(request.path, request.method)
            
            if route_match is None:
                # No route found - 404
                response = JSONResponse(
                    message="Not Found",
                    status="error",
                    status_code=404
                )
            else:
                # Set path parameters
                request.path_params = route_match.path_params
                
                # Create handler wrapper that injects dependencies
                async def handler_with_dependencies(req: Request):
                    # Inject dependencies
                    return await self.dependency_injector.inject(
                        route_match.handler,
                        request=req,
                        **req.path_params
                    )
                
                # Execute middleware chain
                response = await self.middleware_manager.execute(
                    request,
                    handler_with_dependencies
                )
        
        except Exception as exc:
            # Handle exceptions
            response = await self.handle_exception(request, exc)
        
        # Convert dict responses to JSONResponse
        if isinstance(response, dict):
            response = JSONResponse(data=response)
        
        # Send response
        await response(send)
        
        # Execute background tasks if any
        # Note: In a real implementation, you'd want to pass BackgroundTasks
        # to handlers via dependency injection

    
    def _setup_docs_routes(self):
        """
        إعداد documentation routes
        """

        async def openapi_json(request: Request):
            """Get OpenAPI specification"""
            generator = OpenAPIGenerator(self)
            spec = generator.generate_spec()
            return Response(
                json.dumps(spec), status_code=200, headers={"content-type": "application/json"}
            )

        async def swagger_ui(request: Request):
            """Swagger UI documentation page"""
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>{title} - API Documentation</title>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
            </head>
            <body>
                <div id="swagger-ui"></div>
                <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
                <script>
                    SwaggerUIBundle({{
                        url: '/openapi.json',
                        dom_id: '#swagger-ui',
                    }});
                </script>
            </body>
            </html>
            """.format(
                title=self.title
            )
            return Response(html, status_code=200, headers={"content-type": "text/html"})

        # Add routes
        self.router.add_route("/openapi.json", openapi_json, ["GET"])
        self.router.add_route("/docs", swagger_ui, ["GET"])

    async def handle_websocket(self, scope: Dict, receive, send):
        """
        Handle WebSocket connections
        """
        from fennec.websocket import WebSocket

        path = scope["path"]

        # Find matching WebSocket route
        route_match = None
        for ws_router in self._websocket_routers:
            route_match = await ws_router.match(path)
            if route_match:
                break

        if route_match is None:
            # No route found - reject connection
            await send({
                "type": "websocket.close",
                "code": 1000,
                "reason": "Not Found"
            })
            return

        # Create WebSocket instance
        websocket = WebSocket(scope, receive, send)

        try:
            # Call handler with path parameters
            if route_match.path_params:
                await route_match.handler(websocket, **route_match.path_params)
            else:
                await route_match.handler(websocket)
        except Exception as exc:
            # Handle WebSocket errors
            try:
                await websocket.close(code=1011, reason="Internal Error")
            except:
                pass

    async def handle_exception(self, request: Request, exc: Exception) -> Response:
        """
        Handle exceptions وإرجاع response مناسب
        """
        # Check for custom exception handler
        for exc_class, handler in self.exception_handlers.items():
            if isinstance(exc, exc_class):
                return await handler(request, exc)
        
        # Default exception handling
        from fennec.exceptions import HTTPException
        
        if isinstance(exc, HTTPException):
            return JSONResponse(
                message=exc.message,
                data=exc.details,
                status="error",
                status_code=exc.status_code
            )
        
        # Log the error for debugging
        import traceback
        print(f"❌ Unhandled exception in {request.method} {request.path}:")
        print(f"   Error: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        
        # Generic error
        return JSONResponse(
            message="Internal Server Error",
            status="error",
            status_code=500
        )
