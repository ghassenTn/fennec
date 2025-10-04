"""
gRPC Client Example

Demonstrates gRPC client usage.
"""

import asyncio
from datetime import datetime
from fennec.grpc import GRPCClient

# Import generated proto files
try:
    import user_pb2
    import user_pb2_grpc
except ImportError:
    print("Error: Proto files not generated.")
    print("Run: python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user.proto")
    exit(1)


async def test_get_user(client):
    """Test GetUser RPC."""
    print("\n1. Testing GetUser (Unary RPC)")
    print("-" * 50)
    
    response = await client.call(
        user_pb2_grpc.UserServiceStub,
        'GetUser',
        user_pb2.GetUserRequest(id=1)
    )
    
    print(f"User ID: {response.id}")
    print(f"Username: {response.username}")
    print(f"Email: {response.email}")


async def test_create_user(client):
    """Test CreateUser RPC."""
    print("\n2. Testing CreateUser (Unary RPC)")
    print("-" * 50)
    
    response = await client.call(
        user_pb2_grpc.UserServiceStub,
        'CreateUser',
        user_pb2.CreateUserRequest(
            username="david",
            email="david@example.com"
        )
    )
    
    print(f"Created User ID: {response.id}")
    print(f"Username: {response.username}")
    print(f"Email: {response.email}")


async def test_list_users(client):
    """Test ListUsers RPC."""
    print("\n3. Testing ListUsers (Server Streaming)")
    print("-" * 50)
    
    count = 0
    async for user in client.call_stream(
        user_pb2_grpc.UserServiceStub,
        'ListUsers',
        user_pb2.ListUsersRequest(limit=5, offset=0)
    ):
        count += 1
        print(f"User {count}: {user.username} ({user.email})")


async def test_update_users(client):
    """Test UpdateUsers RPC."""
    print("\n4. Testing UpdateUsers (Client Streaming)")
    print("-" * 50)
    
    async def request_generator():
        updates = [
            (1, "alice_updated", "alice_new@example.com"),
            (2, "bob_updated", "bob_new@example.com")
        ]
        
        for user_id, username, email in updates:
            print(f"Sending update for user {user_id}")
            yield user_pb2.UpdateUserRequest(
                id=user_id,
                username=username,
                email=email
            )
            await asyncio.sleep(0.5)
    
    response = await client.call(
        user_pb2_grpc.UserServiceStub,
        'UpdateUsers',
        request_generator()
    )
    
    print(f"Updated {response.updated_count} users")


async def test_chat(client):
    """Test Chat RPC."""
    print("\n5. Testing Chat (Bidirectional Streaming)")
    print("-" * 50)
    
    async def message_generator():
        messages = ["Hello", "How are you?", "Goodbye"]
        
        for msg in messages:
            print(f"Sending: {msg}")
            yield user_pb2.ChatMessage(
                user="client",
                message=msg,
                timestamp=datetime.now().isoformat()
            )
            await asyncio.sleep(1)
    
    async for response in client.call_stream(
        user_pb2_grpc.UserServiceStub,
        'Chat',
        message_generator()
    ):
        print(f"Received: {response.message}")


async def main():
    """Run all tests."""
    print("🔌 Connecting to gRPC Server")
    print("📡 Server: localhost:50051")
    
    # Create client
    client = GRPCClient(host="localhost", port=50051)
    
    try:
        # Connect
        await client.connect()
        
        # Run tests
        await test_get_user(client)
        await test_create_user(client)
        await test_list_users(client)
        await test_update_users(client)
        await test_chat(client)
        
        print("\n✅ All tests completed!")
        
    finally:
        # Disconnect
        await client.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Client stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
