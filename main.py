"""
Fennec Framework 🦊 - Complete Example (v0.3.0)
================================================

This example demonstrates ALL features of Fennec Framework v0.3.0:

Core Features (v0.1.0):
- ✅ Routing with path parameters
- ✅ Request validation with BaseModel
- ✅ Dependency injection
- ✅ Middleware (CORS, Rate Limiting, Custom)
- ✅ Authentication & Authorization
- ✅ Background tasks
- ✅ Exception handling
- ✅ OpenAPI documentation
- ✅ Database abstraction

v0.2.0 Features:
- ✅ WebSocket support for real-time communication
- ✅ GraphQL API with queries and mutations
- ✅ Enhanced security (password hashing, security headers, CSRF, input sanitization)
- ✅ Environment-based configuration
- ✅ Token refresh and revocation

v0.3.0 Features (Production-Grade):
- ✅ Redis caching for performance
- ✅ Prometheus metrics and monitoring
- ✅ Distributed tracing with correlation IDs
- ✅ Structured JSON logging
- ✅ Health checks (liveness/readiness)
- ✅ Admin dashboard for real-time monitoring

Built with ❤️ in Tunisia 🇹🇳
"""

from fennec import (
    Application, Router, JSONResponse,
    WebSocket, WebSocketRouter, WebSocketManager,
    GraphQLEngine, query, mutation
)
from fennec.validation import BaseModel, Field
from fennec.dependencies import Depends
from fennec.security import (
    CORSMiddleware, RateLimitMiddleware,
    EnhancedJWTHandler, PasswordHasher,
    SecurityHeadersMiddleware, InputSanitizer,
    requires_auth
)
from fennec.background import BackgroundTasks
from fennec.exceptions import NotFoundException, ValidationException, UnauthorizedException
from fennec.config import Config

# v0.3.0 Imports
try:
    from fennec.cache import RedisCache, cache
    from fennec.monitoring import PrometheusMetrics, RequestTracer, StructuredLogger
    from fennec.monitoring.metrics import MetricsMiddleware
    from fennec.monitoring.tracing import TracingMiddleware
    from fennec.monitoring.logging import LoggingMiddleware
    from fennec.monitoring.health import HealthCheck
    ENABLE_V030_FEATURES = True
except ImportError:
    ENABLE_V030_FEATURES = False
    print("⚠️  v0.3.0 features not available. Install: pip install redis prometheus-client psutil")

from typing import Optional
import time
import uuid

# ============================================================================
# CONFIGURATION (v0.2.0 Feature)
# ============================================================================

# Load configuration from environment
Config.SECRET_KEY = "your-secret-key-change-in-production"
Config.DEBUG = True

# ============================================================================
# APPLICATION SETUP
# ============================================================================

# Create application with metadata
app = Application(
    title="Fennec Framework Demo API 🦊",
    version="0.3.0",
    docs_enabled=True  # Enable Swagger UI at /docs
)

# ============================================================================
# v0.3.0 FEATURES SETUP
# ============================================================================

if ENABLE_V030_FEATURES:
    # Initialize caching
    try:
        redis_cache = RedisCache(url="redis://localhost:6379", prefix="fennec_demo:")
        print("✓ Redis caching enabled")
    except Exception as e:
        redis_cache = None
        print(f"⚠️  Redis not available: {e}")
    
    # Initialize monitoring
    metrics = PrometheusMetrics(app_name="fennec_demo")
    tracer = RequestTracer(service_name="fennec_demo")
    logger = StructuredLogger(name="fennec_demo")
    health = HealthCheck(service_name="fennec_demo")
    
    # Add health checks
    async def check_redis():
        if redis_cache:
            return await redis_cache.ping()
        return True
    
    health.add_check("redis", check_redis)
    
    print("✓ Monitoring enabled (Prometheus, Tracing, Logging)")
    
    # Initialize admin dashboard
    try:
        from fennec.admin import AdminDashboard
        admin = AdminDashboard(
            app,
            auth_required=False,  # Disable for demo
            prefix="/admin"
        )
        print("✓ Admin dashboard enabled at /admin")
    except ImportError:
        print("⚠️  Admin dashboard not available (module not found)")
    except Exception as e:
        print(f"⚠️  Admin dashboard not available: {e}")

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# v0.3.0: Add monitoring middleware first
if ENABLE_V030_FEATURES:
    app.middleware_manager.add(MetricsMiddleware(metrics))
    app.middleware_manager.add(TracingMiddleware(tracer))
    app.middleware_manager.add(LoggingMiddleware(logger))

# 1. Security Headers (v0.2.0 Feature)
app.middleware_manager.add(SecurityHeadersMiddleware())

# 2. CORS - Allow cross-origin requests
app.middleware_manager.add(
    CORSMiddleware(
        allow_origins=["*"],  # In production: specify exact origins
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Content-Type", "Authorization"],
    )
)

# 3. Rate Limiting - Prevent abuse
app.middleware_manager.add(
    RateLimitMiddleware(
        max_requests=100,  # 100 requests
        window_seconds=60  # per minute
    )
)

# 4. Custom Logging Middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    if ENABLE_V030_FEATURES:
        logger.info(f"Request received", method=request.method, path=request.path)
    else:
        print(f"🦊 [{request.method}] {request.path}")
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    if ENABLE_V030_FEATURES:
        status = getattr(response, 'status', getattr(response, 'status_code', 200))
        logger.log_request(request.method, request.path, status, duration)
    else:
        status = getattr(response, 'status', getattr(response, 'status_code', 200))
        print(f"   ✓ {status} ({duration:.3f}s)")
    
    return response

# ============================================================================
# AUTHENTICATION SETUP (v0.2.0 Enhanced)
# ============================================================================

# Enhanced JWT Handler with token refresh and revocation
jwt_handler = EnhancedJWTHandler(
    secret_key=Config.SECRET_KEY,
    algorithm="HS256"
)

# Password hasher for secure password storage
password_hasher = PasswordHasher()

# ============================================================================
# WEBSOCKET SETUP (v0.2.0 Feature)
# ============================================================================

# WebSocket router and manager
ws_router = WebSocketRouter()
ws_manager = WebSocketManager()

# WebSocket: Echo endpoint
@ws_router.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket):
    """
    WebSocket Echo Endpoint
    
    Echoes back any message received.
    Great for testing WebSocket connections!
    """
    await websocket.accept()
    client_id = str(uuid.uuid4())
    await ws_manager.connect(websocket, client_id)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Fennec WebSocket Echo Server 🦊",
            "client_id": client_id
        })
        
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            # Echo it back
            await websocket.send_json({
                "type": "echo",
                "original": data,
                "timestamp": time.time()
            })
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    finally:
        await ws_manager.disconnect(client_id)


# WebSocket: Chat room endpoint
@ws_router.websocket("/ws/chat/{room}")
async def websocket_chat(websocket: WebSocket, room: str):
    """
    WebSocket Chat Room
    
    Join a chat room and send/receive messages in real-time.
    Multiple clients can connect to the same room.
    """
    await websocket.accept()
    client_id = str(uuid.uuid4())
    await ws_manager.connect(websocket, client_id)
    ws_manager.join_room(client_id, room)
    
    try:
        # Welcome message
        await websocket.send_json({
            "type": "system",
            "message": f"Welcome to room '{room}'! 🦊",
            "room": room,
            "client_id": client_id
        })
        
        # Notify others
        await ws_manager.broadcast_json(
            {
                "type": "user_joined",
                "message": f"User {client_id[:8]} joined the room",
                "room": room
            },
            room=room,
            exclude=client_id
        )
        
        while True:
            # Receive message
            message = await websocket.receive_text()
            
            # Broadcast to room
            await ws_manager.broadcast_json(
                {
                    "type": "message",
                    "from": client_id[:8],
                    "message": message,
                    "room": room,
                    "timestamp": time.time()
                },
                room=room
            )
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    finally:
        # Notify others
        await ws_manager.broadcast_json(
            {
                "type": "user_left",
                "message": f"User {client_id[:8]} left the room",
                "room": room
            },
            room=room,
            exclude=client_id
        )
        
        await ws_manager.disconnect(client_id)


# ============================================================================
# GRAPHQL SETUP (v0.2.0 Feature)
# ============================================================================

# GraphQL engine
gql_engine = GraphQLEngine()

# Define GraphQL schema
graphql_schema = """
type User {
    id: ID!
    name: String!
    email: String!
    age: Int!
    role: String!
}

type Query {
    users: [User!]!
    user(id: ID!): User
}

type Mutation {
    createUser(name: String!, email: String!, age: Int!): User!
}
"""

gql_engine.set_schema(graphql_schema)

# ============================================================================
# ROUTERS
# ============================================================================

# Main router
router = Router()

# Auth router (for login/register)
auth_router = Router(prefix="/auth")

# Admin router (protected routes)
admin_router = Router(prefix="/admin")

# ============================================================================
# GRAPHQL RESOLVERS (v0.2.0 Feature)
# ============================================================================

@query("users")
async def resolve_users(parent, info):
    """GraphQL: Get all users"""
    return [
        {k: v for k, v in user.items() if k != "password"}
        for user in users_db.values()
    ]

@query("user")
async def resolve_user(parent, info, id: str):
    """GraphQL: Get user by ID"""
    user_id = int(id)
    if user_id in users_db:
        user = users_db[user_id]
        return {k: v for k, v in user.items() if k != "password"}
    return None

@mutation("createUser")
async def resolve_create_user(parent, info, name: str, email: str, age: int):
    """GraphQL: Create new user"""
    global next_id
    
    # Sanitize input (v0.2.0 Feature)
    name = InputSanitizer.sanitize_html(name)
    email = InputSanitizer.validate_email(email)
    
    new_user = {
        "id": next_id,
        "name": name,
        "email": email,
        "age": age,
        "role": "user",
        "password": password_hasher.hash("default123")
    }
    
    users_db[next_id] = new_user
    next_id += 1
    
    return {k: v for k, v in new_user.items() if k != "password"}

# ============================================================================
# WEBSOCKET ROUTES (v0.2.0 Feature)
# ============================================================================

@ws_router.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket):
    """
    WebSocket Echo Server
    Echoes back any message received
    """
    await websocket.accept()
    client_id = str(uuid.uuid4())
    await ws_manager.connect(websocket, client_id)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Fennec WebSocket!",
            "client_id": client_id
        })
        
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({
                "type": "echo",
                "message": f"Echo: {data}",
                "timestamp": time.time()
            })
    except:
        pass
    finally:
        await ws_manager.disconnect(client_id)

@ws_router.websocket("/ws/broadcast")
async def websocket_broadcast(websocket: WebSocket):
    """
    WebSocket Broadcast Server
    Broadcasts messages to all connected clients
    """
    await websocket.accept()
    client_id = str(uuid.uuid4())
    await ws_manager.connect(websocket, client_id)
    
    try:
        # Notify others
        await ws_manager.broadcast_json(
            {"type": "user_joined", "client_id": client_id},
            exclude=client_id
        )
        
        while True:
            data = await websocket.receive_json()
            # Broadcast to all clients
            await ws_manager.broadcast_json({
                "type": "message",
                "from": client_id,
                "data": data
            })
    except:
        pass
    finally:
        await ws_manager.broadcast_json(
            {"type": "user_left", "client_id": client_id},
            exclude=client_id
        )
        await ws_manager.disconnect(client_id)


# ============================================================================
# DATA MODELS (with Validation)
# ============================================================================

class User(BaseModel):
    """User model with automatic validation"""
    
    id: Optional[int] = Field(default=None, required=False)
    name: str = Field(min_length=2, max_length=50)
    email: str
    age: int
    role: str = Field(default="user", required=False)
    
    def validate_age(self, value):
        """Custom validator: age must be between 0 and 150"""
        if value < 0 or value > 150:
            raise ValueError("Age must be between 0 and 150")
        return value
    
    def validate_email(self, value):
        """Custom validator: basic email format check"""
        if "@" not in value or "." not in value:
            raise ValueError("Invalid email format")
        return value.lower()


class LoginRequest(BaseModel):
    """Login request model"""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"


# ============================================================================
# IN-MEMORY DATABASE (Replace with real DB in production)
# ============================================================================

users_db = {
    1: {
        "id": 1,
        "name": "Admin User",
        "email": "admin@fennec.dev",
        "age": 30,
        "role": "admin",
        "password": password_hasher.hash("admin123")  # v0.2.0: Hashed passwords!
    }
}
next_id = 2


# ============================================================================
# DEPENDENCIES (Dependency Injection)
# ============================================================================

def get_db():
    """
    Database dependency
    In production: return actual database connection
    """
    return users_db


def get_current_user(request):
    """
    Get current authenticated user from JWT token
    """
    auth_header = request.headers.get("authorization", "")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedException("Missing or invalid authorization header")
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt_handler.decode(token)
        user_id = payload.get("user_id")
        
        if user_id not in users_db:
            raise UnauthorizedException("User not found")
        
        return users_db[user_id]
    except Exception:
        raise UnauthorizedException("Invalid or expired token")


def send_welcome_email(email: str, name: str):
    """
    Background task: Send welcome email
    (Simulated - in production: use real email service)
    """
    print(f"📧 Sending welcome email to {email}...")
    time.sleep(1)  # Simulate email sending
    print(f"✓ Welcome email sent to {name}!")


# ============================================================================
# PUBLIC ROUTES
# ============================================================================

@router.get("/")
async def root():
    """
    🏠 Root endpoint - Welcome message
    
    Returns information about the API and available endpoints.
    """
    return JSONResponse(
        data={
            "message": "Welcome to Fennec Framework Demo API! 🦊",
            "version": "1.0.0",
            "framework": "Fennec - Small, Swift, and Adaptable",
            "docs": "/docs",
            "endpoints": {
                "users": "/users",
                "auth": "/auth/login",
                "admin": "/admin (requires authentication)"
            },
            "made_in": "Tunisia 🇹🇳"
        },
        message="API is running"
    )


@router.get("/health")
async def health_check():
    """
    ❤️ Health check endpoint (v0.3.0 Enhanced)
    
    Returns the health status of the API with dependency checks.
    """
    if ENABLE_V030_FEATURES:
        result = await health.run_checks()
        status_code = 200 if result['status'] == 'healthy' else 503
        return JSONResponse(data=result, status_code=status_code)
    else:
        return JSONResponse(
            data={
                "status": "healthy",
                "timestamp": time.time(),
                "uptime": "running"
            }
        )


@router.get("/health/live")
async def liveness_probe():
    """
    🫀 Kubernetes liveness probe (v0.3.0)
    
    Checks if the service is running.
    """
    if ENABLE_V030_FEATURES:
        result = await health.liveness()
        return JSONResponse(data=result)
    else:
        return JSONResponse(data={"status": "alive"})


@router.get("/health/ready")
async def readiness_probe():
    """
    ✅ Kubernetes readiness probe (v0.3.0)
    
    Checks if the service is ready to accept traffic.
    """
    if ENABLE_V030_FEATURES:
        result = await health.readiness()
        status_code = 200 if result['status'] == 'healthy' else 503
        return JSONResponse(data=result, status_code=status_code)
    else:
        return JSONResponse(data={"status": "ready"})


@router.get("/users")
async def list_users(db=Depends(get_db)):
    """
    List all users (v0.3.0: With caching)
    Returns list of all users in the database
    """
    # v0.3.0: Try cache first
    if ENABLE_V030_FEATURES and redis_cache:
        cached_users = await redis_cache.get("all_users")
        if cached_users:
            return JSONResponse(
                data={"users": cached_users, "cached": True},
                message="Users retrieved from cache"
            )
    
    # Get from database
    users = list(db.values())
    
    # v0.3.0: Cache the result
    if ENABLE_V030_FEATURES and redis_cache:
        await redis_cache.set("all_users", users, ttl=60)
    
    return JSONResponse(data={"users": users, "cached": False}, message="Users retrieved")


@router.get("/users/{id}")
async def get_user(id: int, db=Depends(get_db)):
    """
    Get user by ID (v0.3.0: With caching)
    Returns a single user by their ID
    """
    # v0.3.0: Try cache first
    if ENABLE_V030_FEATURES and redis_cache:
        cached_user = await redis_cache.get(f"user:{id}")
        if cached_user:
            return JSONResponse(
                data={"user": cached_user, "cached": True},
                message="User found in cache"
            )
    
    if id not in db:
        from fennec.exceptions import NotFoundException
        raise NotFoundException(f"User with ID {id} not found")
    
    user = db[id]
    
    # v0.3.0: Cache the result
    if ENABLE_V030_FEATURES and redis_cache:
        await redis_cache.set(f"user:{id}", user, ttl=300)
    
    return JSONResponse(data={"user": user, "cached": False}, message="User found")


@router.post("/users")
async def create_user(request, db=Depends(get_db)):
    """
    ➕ Create new user (with background task)
    
    Creates a new user with automatic validation and sends welcome email.
    
    Request Body:
        name (str): User's full name (2-50 characters)
        email (str): User's email address
        age (int): User's age (0-150)
        role (str): User role (optional, default: "user")
    """
    global next_id
    
    # Get request body
    data = await request.json()
    
    # Validate with model (automatic validation!)
    try:
        user = User(**data)
    except Exception as e:
        raise ValidationException(str(e))
    
    # Add to database
    user_dict = user.dict()
    user_dict["id"] = next_id
    user_dict["password"] = "default123"  # In production: hash password!
    db[next_id] = user_dict
    next_id += 1
    
    # Background task: Send welcome email (doesn't block response)
    background_tasks = BackgroundTasks()
    background_tasks.add_task(send_welcome_email, user_dict["email"], user_dict["name"])
    
    # Execute background tasks after response
    import asyncio
    asyncio.create_task(background_tasks.execute_all())
    
    # v0.3.0: Invalidate cache
    if ENABLE_V030_FEATURES and redis_cache:
        await redis_cache.delete("all_users")
    
    # Remove password from response
    response_data = {k: v for k, v in user_dict.items() if k != "password"}
    
    return JSONResponse(
        data={"user": response_data},
        message="User created successfully! Welcome email sent.",
        status_code=201
    )


@router.put("/users/{id}")
async def update_user(request, id: int, db=Depends(get_db)):
    """
    Update user
    Updates an existing user
    
    Request Body:
        name (str): User's full name (2-50 characters)
        email (str): User's email address
        age (int): User's age (0-150)
    """
    if id not in db:
        from fennec.exceptions import NotFoundException

        raise NotFoundException(f"User with ID {id} not found")

    # Get request body
    data = await request.json()

    # Validate with model
    try:
        user = User(**data)
    except Exception as e:
        from fennec.exceptions import ValidationException

        raise ValidationException(str(e))

    # Update database
    user_dict = user.dict()
    user_dict["id"] = id
    db[id] = user_dict

    return JSONResponse(data={"user": user_dict}, message="User updated")


@router.delete("/users/{id}")
async def delete_user(id: int, db=Depends(get_db)):
    """
    Delete user
    Deletes a user by ID
    """
    if id not in db:
        from fennec.exceptions import NotFoundException

        raise NotFoundException(f"User with ID {id} not found")

    del db[id]

    return JSONResponse(data=None, message="User deleted")


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@auth_router.post("/login")
async def login(request, db=Depends(get_db)):
    """
    🔐 Login endpoint
    
    Authenticate user and return JWT token.
    
    Request Body:
        email (str): User's email
        password (str): User's password
    
    Returns:
        access_token: JWT token for authentication
        token_type: "bearer"
    """
    data = await request.json()
    
    try:
        login_data = LoginRequest(**data)
    except Exception as e:
        raise ValidationException(str(e))
    
    # Find user by email
    user = None
    for u in db.values():
        if u["email"] == login_data.email:
            user = u
            break
    
    # v0.2.0: Verify hashed password
    if not user:
        raise UnauthorizedException("Invalid email or password")
    
    try:
        password_valid = password_hasher.verify(login_data.password, user.get("password", ""))
        if not password_valid:
            raise UnauthorizedException("Invalid email or password")
    except Exception as e:
        raise UnauthorizedException("Invalid email or password")
    
    # v0.2.0: Generate access and refresh tokens
    access_token = jwt_handler.create_access_token({
        "user_id": user["id"],
        "email": user["email"],
        "role": user.get("role", "user")
    }, expires_in=3600)  # 1 hour
    
    refresh_token = jwt_handler.create_refresh_token({
        "user_id": user["id"],
        "email": user["email"],
        "role": user.get("role", "user")
    }, expires_in=604800)  # 7 days
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "user")
        }
    }


@auth_router.get("/me")
@requires_auth
async def get_current_user_info(request):
    """
    👤 Get current user info (Protected route)
    
    Returns information about the currently authenticated user.
    Requires: Authorization header with Bearer token
    """
    user = get_current_user(request)
    
    # Remove password from response
    user_data = {k: v for k, v in user.items() if k != "password"}
    
    return JSONResponse(
        data={"user": user_data},
        message="User info retrieved"
    )


# ============================================================================
# ADMIN ROUTES (Protected)
# ============================================================================

@admin_router.get("/users")
@requires_auth
async def admin_list_all_users(request, db=Depends(get_db)):
    """
    👥 Admin: List all users (Protected)
    
    Returns all users in the system.
    Requires: Admin role
    """
    current_user = get_current_user(request)
    
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise UnauthorizedException("Admin access required")
    
    # Remove passwords from response
    users = [
        {k: v for k, v in user.items() if k != "password"}
        for user in db.values()
    ]
    
    return JSONResponse(
        data={"users": users, "total": len(users)},
        message="All users retrieved"
    )


@admin_router.delete("/users/{id}")
@requires_auth
async def admin_delete_user(request, id: int, db=Depends(get_db)):
    """
    🗑️ Admin: Delete user (Protected)
    
    Deletes a user from the system.
    Requires: Admin role
    """
    current_user = get_current_user(request)
    
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise UnauthorizedException("Admin access required")
    
    # Can't delete yourself
    if current_user["id"] == id:
        raise ValidationException("Cannot delete your own account")
    
    if id not in db:
        raise NotFoundException(f"User with ID {id} not found")
    
    deleted_user = db[id]
    del db[id]
    
    return JSONResponse(
        data={"deleted_user": deleted_user["name"]},
        message="User deleted successfully"
    )


# ============================================================================
# v0.3.0 MONITORING ENDPOINTS
# ============================================================================

if ENABLE_V030_FEATURES:
    @router.get("/metrics")
    async def prometheus_metrics(request):
        """
        📊 Prometheus metrics endpoint (v0.3.0)
        
        Exposes application metrics in Prometheus format.
        """
        from fennec import Response
        return Response(
            metrics.generate_metrics(),
            headers={"content-type": metrics.get_content_type()}
        )
    
    @router.get("/cache/stats")
    async def cache_stats_endpoint(request):
        """
        📈 Cache statistics (v0.3.0)
        
        Returns cache hit/miss statistics.
        """
        if redis_cache:
            stats = await redis_cache.get_stats()
            return JSONResponse(data=stats, message="Cache statistics")
        else:
            return JSONResponse(
                data={"error": "Redis not available"},
                status_code=503
            )
    
    @router.post("/cache/clear")
    async def clear_cache_endpoint(request):
        """
        🗑️ Clear cache (v0.3.0)
        
        Clears all cached data.
        """
        if redis_cache:
            count = await redis_cache.clear()
            await redis_cache.reset_stats()
            return JSONResponse(
                data={"keys_deleted": count},
                message="Cache cleared"
            )
        else:
            return JSONResponse(
                data={"error": "Redis not available"},
                status_code=503
            )

# ============================================================================
# INCLUDE ALL ROUTERS
# ============================================================================

app.include_router(router)
app.include_router(auth_router)
app.include_router(admin_router)

# Include WebSocket router (v0.2.0)
app.include_websocket_router(ws_router)


# ============================================================================
# CUSTOM EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(ValueError)
async def handle_value_error(request, exc):
    """Handle ValueError with custom response"""
    return JSONResponse(
        message=str(exc),
        status="error",
        status_code=400
    )


@app.exception_handler(KeyError)
async def handle_key_error(request, exc):
    """Handle KeyError (missing required fields)"""
    return JSONResponse(
        message=f"Missing required field: {str(exc)}",
        status="error",
        status_code=400
    )


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    try:
        import uvicorn
        
        print("\n" + "="*60)
        print("🦊 Fennec Framework - Complete Demo API v0.3.0")
        print("="*60)
        print("\n📚 Features Demonstrated:")
        print("  ✓ Routing with path parameters")
        print("  ✓ Request validation (BaseModel)")
        print("  ✓ Dependency injection")
        print("  ✓ Middleware (CORS, Rate Limiting, Logging)")
        print("  ✓ JWT Authentication")
        print("  ✓ Role-based authorization")
        print("  ✓ Background tasks")
        print("  ✓ Exception handling")
        print("  ✓ OpenAPI documentation")
        print("  ✓ WebSocket support")
        print("  ✓ GraphQL API")
        
        if ENABLE_V030_FEATURES:
            print("\n🆕 v0.3.0 Features:")
            print("  ✓ Redis caching")
            print("  ✓ Prometheus metrics")
            print("  ✓ Distributed tracing")
            print("  ✓ Structured logging")
            print("  ✓ Health checks")
            print("  ✓ Admin dashboard")
        
        print("\n🌐 Server Info:")
        print("  URL: http://localhost:8001")
        print("  Docs: http://localhost:8001/docs")
        print("  OpenAPI: http://localhost:8001/openapi.json")
        print("  GraphQL: http://localhost:8001/graphql")
        print("  GraphiQL: http://localhost:8001/graphql/graphiql")
        
        if ENABLE_V030_FEATURES:
            print("\n📊 v0.3.0 Endpoints:")
            print("  Metrics: http://localhost:8001/metrics")
            print("  Health: http://localhost:8001/health")
            print("  Liveness: http://localhost:8001/health/live")
            print("  Readiness: http://localhost:8001/health/ready")
            print("  Admin: http://localhost:8001/admin")
            print("  Cache Stats: http://localhost:8001/cache/stats")
        
        print("\n🔌 WebSocket Endpoints:")
        print("  Echo: ws://localhost:8001/ws/echo")
        print("  Chat: ws://localhost:8001/ws/chat/{room}")
        print("\n🔐 Test Credentials:")
        print("  Email: admin@fennec.dev")
        print("  Password: admin123")
        print("\n💡 Quick Test:")
        print("  1. Visit http://localhost:8001/docs")
        print("  2. Try POST /auth/login with test credentials")
        print("  3. Copy the access_token")
        print("  4. Click 'Authorize' and paste token")
        print("  5. Try protected endpoints!")
        
        if ENABLE_V030_FEATURES:
            print("\n📊 Monitor Your API:")
            print("  1. Visit http://localhost:8001/admin")
            print("  2. See real-time metrics and requests")
            print("  3. Check cache stats at /cache/stats")
        
        print("\n🔌 Test WebSocket:")
        print("  1. Open examples/websocket_chat/client.html")
        print("  2. Or use: wscat -c ws://localhost:8001/ws/echo")
        print("\n" + "="*60)
        print("Press CTRL+C to stop")
        print("="*60 + "\n")
        
        uvicorn.run(app, host="0.0.0.0", port=8001)
        
    except ImportError:
        print("\n❌ Error: uvicorn is not installed")
        print("Install it with: pip install uvicorn")
        print("\nOr install with Fennec:")
        print("pip install fennec-framework uvicorn")

