# Microservices Example 🦊

A microservices architecture demonstrating service decomposition, API gateway pattern, and inter-service communication using Fennec Framework.

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   API Gateway   │  (Port 8000)
│  (gateway.py)   │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│  User  │ │ Order  │
│Service │ │Service │
│(8001)  │ │(8002)  │
└────────┘ └────────┘
```

## Services

### 1. User Service (Port 8001)
Manages user data and authentication.

**Endpoints:**
- `GET /api/users` - List all users
- `GET /api/users/{id}` - Get user by ID
- `POST /api/users` - Create user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
- `GET /api/users/health` - Health check

### 2. Order Service (Port 8002)
Manages orders and transactions.

**Endpoints:**
- `GET /api/orders` - List all orders
- `GET /api/orders/{id}` - Get order by ID
- `POST /api/orders` - Create order
- `PUT /api/orders/{id}/status` - Update order status
- `DELETE /api/orders/{id}` - Cancel order
- `GET /api/orders/user/{user_id}` - Get user's orders
- `GET /api/orders/health` - Health check

### 3. API Gateway (Port 8000)
Routes requests and aggregates data from multiple services.

**Endpoints:**
- All user and order endpoints (proxied)
- `GET /api/users/{id}/profile` - Aggregated user profile with orders
- `GET /api/dashboard` - Aggregated statistics
- `GET /api/health` - Health check for all services

## Installation

1. Install Fennec:
```bash
pip install fennec
```

2. Install dependencies:
```bash
pip install uvicorn httpx
```

## Running the Services

You need to run all three services in separate terminals:

### Terminal 1: User Service
```bash
python user_service.py
```

### Terminal 2: Order Service
```bash
python order_service.py
```

### Terminal 3: API Gateway
```bash
python gateway.py
```

## Using the API

All requests should go through the API Gateway at `http://localhost:8000`

### Create a User

```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

### Get All Users

```bash
curl http://localhost:8000/api/users
```

### Create an Order

```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "product": "Laptop",
    "quantity": 1,
    "total": 999.99
  }'
```

### Get User Profile (Aggregated)

```bash
curl http://localhost:8000/api/users/1/profile
```

**Response:**
```json
{
  "data": {
    "user": {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "role": "admin"
    },
    "orders": [
      {
        "id": 1,
        "user_id": 1,
        "product": "Laptop",
        "quantity": 1,
        "total": 999.99,
        "status": "completed"
      }
    ],
    "total_orders": 1
  }
}
```

### Get Dashboard (Aggregated)

```bash
curl http://localhost:8000/api/dashboard
```

**Response:**
```json
{
  "data": {
    "total_users": 3,
    "total_orders": 5,
    "pending_orders": 2,
    "completed_orders": 2,
    "total_revenue": 1549.97
  }
}
```

### Health Check

```bash
curl http://localhost:8000/api/health
```

## Key Concepts

### 1. Service Decomposition

Each service has a single responsibility:
- **User Service**: User management
- **Order Service**: Order management
- **API Gateway**: Request routing and aggregation

### 2. API Gateway Pattern

The gateway provides:
- Single entry point for clients
- Request routing to appropriate services
- Response aggregation from multiple services
- Centralized authentication/authorization (can be added)
- Rate limiting and caching (can be added)

### 3. Inter-Service Communication

Services communicate via HTTP/REST:

```python
async def call_service(url: str, method: str = "GET", json_data: dict = None):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### 4. Data Aggregation

Gateway combines data from multiple services:

```python
@router.get("/users/{user_id}/profile")
async def get_user_profile(user_id: int):
    # Get user from user service
    user_data = await call_service(f"{USER_SERVICE_URL}/api/users/{user_id}")
    
    # Get orders from order service
    orders_data = await call_service(f"{ORDER_SERVICE_URL}/api/orders/user/{user_id}")
    
    # Combine and return
    return {"user": user_data, "orders": orders_data}
```

## Benefits

1. **Scalability**: Scale services independently
2. **Maintainability**: Smaller, focused codebases
3. **Flexibility**: Use different technologies per service
4. **Resilience**: Failure in one service doesn't crash entire system
5. **Team Autonomy**: Teams can work on services independently

## Challenges & Solutions

### 1. Service Discovery

**Challenge**: Services need to find each other

**Solution**: Use environment variables or service registry
```python
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
```

### 2. Data Consistency

**Challenge**: Data spread across services

**Solution**: Use event-driven architecture or saga pattern

### 3. Network Latency

**Challenge**: Multiple network calls increase latency

**Solution**: 
- Cache frequently accessed data
- Use async/await for parallel requests
- Implement circuit breakers

### 4. Monitoring

**Challenge**: Tracking requests across services

**Solution**: Implement distributed tracing
```python
# Add correlation ID to requests
headers = {"X-Correlation-ID": correlation_id}
```

## Advanced Patterns

### Circuit Breaker

Prevent cascading failures:

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.state = "closed"
    
    async def call(self, func):
        if self.state == "open":
            raise Exception("Circuit breaker is open")
        
        try:
            result = await func()
            self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise e
```

### Service Mesh

For production, consider using a service mesh like Istio or Linkerd for:
- Service discovery
- Load balancing
- Encryption
- Observability

### Event-Driven Architecture

Use message queues for async communication:

```python
# Publish event when user is created
await message_queue.publish("user.created", user_data)

# Order service subscribes to user events
@message_queue.subscribe("user.created")
async def on_user_created(user_data):
    # Handle new user
    pass
```

## Production Considerations

1. **Service Discovery**: Use Consul, etcd, or Kubernetes DNS
2. **Load Balancing**: Use nginx, HAProxy, or cloud load balancers
3. **Authentication**: Implement JWT validation in gateway
4. **Rate Limiting**: Add rate limiting per service
5. **Monitoring**: Use Prometheus, Grafana, or ELK stack
6. **Logging**: Centralized logging with correlation IDs
7. **Database**: Each service should have its own database
8. **Deployment**: Use Docker and Kubernetes
9. **CI/CD**: Independent deployment pipelines per service
10. **Testing**: Contract testing between services

## Testing

### Unit Tests

Test each service independently:

```python
from fennec.testing import TestClient

def test_create_user():
    client = TestClient(app)
    response = client.post("/api/users", json={
        "name": "Test User",
        "email": "test@example.com"
    })
    assert response.status_code == 201
```

### Integration Tests

Test service communication:

```python
async def test_user_profile():
    # Start all services
    # Make request to gateway
    response = await client.get("/api/users/1/profile")
    assert "user" in response.json()["data"]
    assert "orders" in response.json()["data"]
```

## Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  user-service:
    build: .
    command: python user_service.py
    ports:
      - "8001:8001"
  
  order-service:
    build: .
    command: python order_service.py
    ports:
      - "8002:8002"
  
  gateway:
    build: .
    command: python gateway.py
    ports:
      - "8000:8000"
    depends_on:
      - user-service
      - order-service
```

### Kubernetes

Deploy each service as a separate deployment with its own service and ingress.

## Learn More

- [Microservices Patterns](https://microservices.io/patterns/)
- [API Gateway Pattern](https://microservices.io/patterns/apigateway.html)
- [Service Mesh](https://servicemesh.io/)
- [Fennec Documentation](https://github.com/your-repo/fennec)
