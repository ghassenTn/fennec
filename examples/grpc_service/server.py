"""
gRPC Server Example

Demonstrates gRPC service implementation.
"""

import asyncio
from datetime import datetime
from fennec.grpc import GRPCServer, rpc_method

# Import generated proto files (run protoc first)
try:
    import user_pb2
    import user_pb2_grpc
except ImportError:
    print("Error: Proto files not generated.")
    print("Run: python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user.proto")
    exit(1)


# Fake database
users_db = {
    1: {"id": 1, "username": "alice", "email": "alice@example.com"},
    2: {"id": 2, "username": "bob", "email": "bob@example.com"},
    3: {"id": 3, "username": "charlie", "email": "charlie@example.com"}
}
next_user_id = 4


class UserServicer(user_pb2_grpc.UserServiceServicer):
    """User service implementation."""
    
    @rpc_method(log_requests=True)
    async def GetUser(self, request, context):
        """Get user by ID (unary RPC)."""
        user_id = request.id
        
        if user_id not in users_db:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User {user_id} not found")
            return user_pb2.User()
        
        user = users_db[user_id]
        return user_pb2.User(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            created_at=datetime.now().isoformat()
        )
    
    @rpc_method(log_requests=True)
    async def CreateUser(self, request, context):
        """Create new user (unary RPC)."""
        global next_user_id
        
        user = {
            'id': next_user_id,
            'username': request.username,
            'email': request.email
        }
        
        users_db[next_user_id] = user
        next_user_id += 1
        
        return user_pb2.User(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            created_at=datetime.now().isoformat()
        )
    
    @rpc_method(log_requests=True)
    async def ListUsers(self, request, context):
        """List users (server streaming RPC)."""
        limit = request.limit or 10
        offset = request.offset or 0
        
        user_list = list(users_db.values())[offset:offset + limit]
        
        for user in user_list:
            yield user_pb2.User(
                id=user['id'],
                username=user['username'],
                email=user['email'],
                created_at=datetime.now().isoformat()
            )
            await asyncio.sleep(0.1)  # Simulate delay
    
    @rpc_method(log_requests=True)
    async def UpdateUsers(self, request_iterator, context):
        """Update users (client streaming RPC)."""
        count = 0
        
        async for request in request_iterator:
            if request.id in users_db:
                users_db[request.id]['username'] = request.username
                users_db[request.id]['email'] = request.email
                count += 1
        
        return user_pb2.UpdateUsersResponse(updated_count=count)
    
    @rpc_method(log_requests=True)
    async def Chat(self, request_iterator, context):
        """Chat (bidirectional streaming RPC)."""
        async for message in request_iterator:
            # Echo message back
            yield user_pb2.ChatMessage(
                user="server",
                message=f"Echo: {message.message}",
                timestamp=datetime.now().isoformat()
            )
            await asyncio.sleep(0.1)


async def main():
    """Start gRPC server."""
    print("🚀 Starting gRPC Server")
    print("📡 Listening on 0.0.0.0:50051")
    print("\n📝 Available RPC methods:")
    print("   GetUser       - Get user by ID")
    print("   CreateUser    - Create new user")
    print("   ListUsers     - List users (streaming)")
    print("   UpdateUsers   - Update users (streaming)")
    print("   Chat          - Chat (bidirectional)")
    
    # Create server
    server = GRPCServer(host="0.0.0.0", port=50051)
    
    # Add service
    server.add_service(user_pb2_grpc, UserServicer())
    
    # Start server
    await server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped")
