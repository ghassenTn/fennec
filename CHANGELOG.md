# Changelog

All notable changes to Fennec Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-01-04

### Added - Production-Grade Features
- **Redis Caching Layer**
  - High-performance Redis client with connection pooling
  - `@cache` decorator for automatic function caching
  - Cache-aside and write-through strategies
  - TTL support and cache invalidation
  - Hit/miss statistics tracking

- **Database Migrations**
  - Version-controlled schema management
  - Timestamped migration files (Python & SQL)
  - Apply/rollback functionality with transaction safety
  - Migration history tracking
  - CLI commands for migration management

- **Monitoring & Observability**
  - Prometheus metrics integration
  - Distributed tracing with correlation IDs
  - Structured JSON logging
  - Health check endpoints (liveness/readiness)
  - Request/response tracking

- **Admin Dashboard**
  - Real-time web-based monitoring interface
  - Application metrics visualization
  - System metrics (CPU, memory, disk)
  - Recent requests table with auto-refresh
  - Beautiful, responsive UI

- **Message Queues**
  - Multiple backend support (Redis, RabbitMQ, AWS SQS)
  - `@task` decorator for async task definition
  - Worker processes with configurable concurrency
  - Automatic retry with exponential backoff
  - Delayed/scheduled message delivery

- **gRPC Support**
  - Protocol Buffers support
  - All RPC types (unary, streaming, bidirectional)
  - gRPC interceptors (middleware)
  - Method decorators for logging and validation

### Examples
- Added caching example
- Added migration example
- Added monitoring setup example
- Added admin dashboard example
- Added message queue example
- Added gRPC service example
- Added simple CRUD example

### Documentation
- Complete v0.3.0 features guide
- Deployment guide for production
- Updated README with all features
- API reference documentation

## [0.2.0] - 2024-12-15

### Added - Enhanced Features
- **WebSocket Support**
  - Full WebSocket lifecycle management
  - WebSocketManager for connection handling
  - Room-based broadcasting
  - Path parameter support in WebSocket routes

- **GraphQL API**
  - GraphQL engine with SDL parsing
  - Query and mutation decorators
  - GraphQL context support
  - GraphiQL interface integration
  - Introspection support

- **Enhanced Security**
  - bcrypt password hashing
  - Security headers middleware
  - CSRF protection
  - Input sanitization
  - Enhanced JWT with refresh tokens
  - Token revocation support

- **Configuration Management**
  - Environment-based configuration
  - Config class for centralized settings
  - Support for .env files

### Examples
- WebSocket chat application
- GraphQL API example
- Microservices architecture example
- Database integration examples (PostgreSQL, MongoDB)
- OAuth2 authentication example
- Docker deployment example

### Improvements
- Better error handling
- Improved middleware system
- Enhanced request/response handling

## [0.1.0] - 2024-11-01

### Added - Core Features
- **ASGI Application**
  - Full ASGI 3.0 compliance
  - Async/await support throughout
  - HTTP request/response handling

- **Routing System**
  - Path parameter extraction
  - Multiple HTTP methods support
  - Router composition with prefixes
  - Route matching and dispatching

- **Request Validation**
  - BaseModel for automatic validation
  - Field validators with constraints
  - Type checking and conversion
  - Custom validation rules

- **Dependency Injection**
  - Function-based dependencies
  - Automatic dependency resolution
  - Request-scoped dependencies

- **Middleware System**
  - CORS middleware
  - Rate limiting middleware
  - Custom middleware support
  - Middleware chaining

- **Authentication & Authorization**
  - JWT token handling
  - Role-based access control
  - `@requires_auth` decorator
  - Custom authentication handlers

- **Background Tasks**
  - Async background task execution
  - Task queuing
  - Non-blocking operations

- **Exception Handling**
  - Custom exception handlers
  - HTTP exception classes
  - Automatic error responses

- **OpenAPI Documentation**
  - Auto-generated OpenAPI 3.0 spec
  - Swagger UI integration
  - Interactive API documentation

- **Database Abstraction**
  - Simple database interface
  - Query builder
  - Connection management

### Documentation
- Initial README
- Quick start guide
- Basic examples
- API reference

---

## Release Notes

### v0.3.0 - Production Ready
This release makes Fennec production-ready with enterprise-grade features including caching, monitoring, message queues, and gRPC support. Perfect for building scalable microservices.

### v0.2.0 - Real-time & Security
Added WebSocket support for real-time applications, GraphQL API capabilities, and enhanced security features. Includes comprehensive examples for various use cases.

### v0.1.0 - Foundation
Initial release with core framework features. Provides a solid foundation for building modern Python web applications with async support.

---

Built with ❤️ in Tunisia 🇹🇳
