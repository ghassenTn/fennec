# Fennec gRPC Service Example

Demonstrates gRPC support with Protocol Buffers.

## Features

- **Unary RPC**: Simple request-response
- **Server Streaming**: Server sends multiple responses
- **Client Streaming**: Client sends multiple requests
- **Bidirectional Streaming**: Both sides stream messages
- **Protocol Buffers**: Type-safe message definitions
- **Interceptors**: Middleware for gRPC methods

## Installation

```bash
pip install grpcio grpcio-tools
```

## Generate Code from Proto

```bash
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  user.proto
```

This generates:
- `user_pb2.py` - Message classes
- `user_pb2_grpc.py` - Service classes

## Running the Example

### 1. Generate Proto Code

```bash
cd examples/grpc_service
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user.proto
```

### 2. Start Server

```bash
python server.py
```

### 3. Run Client

In another terminal:

```bash
python client.py
```

## RPC Methods

### Unary RPC

Simple request-response:

```python
# Server
async def GetUser(self, request, context):
    user = get_user_by_id(request.id)
    return user_pb2.User(
        id=user['id'],
        username=user['username'],
        email=user['email']
    )

# Client
response = await client.call(
    user_pb2_grpc.UserServiceStub,
    'GetUser',
    user_pb2.GetUserRequest(id=1)
)
```

### Server Streaming

Server sends multiple responses:

```python
# Server
async def ListUsers(self, request, context):
    users = get_all_users(request.limit, request.offset)
    for user in users:
        yield user_pb2.User(
            id=user['id'],
            username=user['username'],
            email=user['email']
        )

# Client
async for user in client.call_stream(
    user_pb2_grpc.UserServiceStub,
    'ListUsers',
    user_pb2.ListUsersRequest(limit=10)
):
    print(user)
```

### Client Streaming

Client sends multiple requests:

```python
# Server
async def UpdateUsers(self, request_iterator, context):
    count = 0
    async for request in request_iterator:
        update_user(request.id, request.username, request.email)
        count += 1
    return user_pb2.UpdateUsersResponse(updated_count=count)

# Client
async def request_generator():
    for i in range(5):
        yield user_pb2.UpdateUserRequest(
            id=i,
            username=f"user{i}",
            email=f"user{i}@example.com"
        )

response = await client.call(
    user_pb2_grpc.UserServiceStub,
    'UpdateUsers',
    request_generator()
)
```

### Bidirectional Streaming

Both sides stream:

```python
# Server
async def Chat(self, request_iterator, context):
    async for message in request_iterator:
        # Echo message back
        yield user_pb2.ChatMessage(
            user="server",
            message=f"Echo: {message.message}",
            timestamp=datetime.now().isoformat()
        )

# Client
async def chat():
    async def message_generator():
        for i in range(5):
            yield user_pb2.ChatMessage(
                user="client",
                message=f"Message {i}",
                timestamp=datetime.now().isoformat()
            )
    
    async for response in client.call_stream(
        user_pb2_grpc.UserServiceStub,
        'Chat',
        message_generator()
    ):
        print(response)
```

## Interceptors

Add middleware to gRPC methods:

```python
async def logging_interceptor(request, context, handler):
    print(f"Request: {request}")
    response = await handler(request, context)
    print(f"Response: {response}")
    return response

servicer = UserServicer()
servicer.add_interceptor(logging_interceptor)
```

## Authentication

Protect RPC methods:

```python
from fennec.grpc import require_auth

def check_token(context):
    metadata = dict(context.invocation_metadata())
    token = metadata.get('authorization')
    return verify_token(token)

@require_auth(check_token)
async def GetUser(self, request, context):
    return user
```

## Error Handling

Handle errors with gRPC status codes:

```python
async def GetUser(self, request, context):
    user = get_user_by_id(request.id)
    
    if not user:
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(f"User {request.id} not found")
        return user_pb2.User()
    
    return user_pb2.User(...)
```

## Testing

Test gRPC services:

```python
import pytest
from grpc.aio import insecure_channel

@pytest.mark.asyncio
async def test_get_user():
    async with insecure_channel('localhost:50051') as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        response = await stub.GetUser(user_pb2.GetUserRequest(id=1))
        assert response.id == 1
```

## Production Deployment

### TLS/SSL

Use secure channels in production:

```python
# Server
credentials = grpc.ssl_server_credentials([
    (private_key, certificate_chain)
])
server.add_secure_port('[::]:50051', credentials)

# Client
credentials = grpc.ssl_channel_credentials(root_certificates)
channel = grpc.aio.secure_channel('server:50051', credentials)
```

### Load Balancing

Use client-side load balancing:

```python
channel = grpc.aio.insecure_channel(
    'dns:///service.example.com:50051',
    options=[('grpc.lb_policy_name', 'round_robin')]
)
```

### Health Checks

Implement health check service:

```python
from grpc_health.v1 import health_pb2, health_pb2_grpc

class HealthServicer(health_pb2_grpc.HealthServicer):
    async def Check(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING
        )
```

## Best Practices

1. **Use Proto3**: Modern syntax with better defaults
2. **Version Services**: Include version in package name
3. **Keep Messages Small**: Avoid large payloads
4. **Use Streaming**: For large datasets or real-time data
5. **Handle Errors**: Use appropriate status codes
6. **Add Timeouts**: Prevent hanging requests
7. **Enable Compression**: Reduce bandwidth usage

## Troubleshooting

### Import errors

Make sure generated files are in Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Connection refused

Check server is running and port is correct:
```bash
netstat -an | grep 50051
```

### Proto compilation errors

Verify proto syntax and run protoc with verbose flag:
```bash
python -m grpc_tools.protoc --version
```

## Next Steps

- Add authentication and authorization
- Implement service discovery
- Add metrics and monitoring
- Deploy with Kubernetes
- Use gRPC gateway for REST compatibility
