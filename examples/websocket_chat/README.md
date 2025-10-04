# WebSocket Chat Example 🦊

A real-time chat application demonstrating WebSocket support in Fennec Framework.

## Features

- ✅ Real-time bidirectional communication
- ✅ Multiple chat rooms
- ✅ Message broadcasting
- ✅ User join/leave notifications
- ✅ Typing indicators
- ✅ Username customization
- ✅ Automatic reconnection
- ✅ Beautiful UI with animations

## Project Structure

```
websocket_chat/
├── server.py          # Fennec WebSocket server
├── client.html        # Web-based chat client
└── README.md          # This file
```

## Installation

1. Make sure you have Fennec installed:
```bash
pip install fennec
```

2. Install uvicorn (ASGI server):
```bash
pip install uvicorn
```

## Running the Server

Start the chat server:

```bash
python server.py
```

The server will start on `http://localhost:8000`

## Using the Chat Client

1. Open `client.html` in your web browser
2. The default room is "general"
3. To join a different room, add `?room=roomname` to the URL:
   - `file:///path/to/client.html?room=developers`
   - `file:///path/to/client.html?room=random`

## WebSocket Endpoints

### Chat Room: `/ws/chat/{room}`

Connect to a specific chat room.

**Message Types (Client → Server):**

```json
{
  "type": "message",
  "message": "Hello, world!"
}
```

```json
{
  "type": "set_username",
  "username": "NewUsername"
}
```

```json
{
  "type": "typing"
}
```

**Message Types (Server → Client):**

```json
{
  "type": "system",
  "message": "Welcome to room 'general'!",
  "client_id": "uuid",
  "timestamp": "2024-01-01T12:00:00"
}
```

```json
{
  "type": "message",
  "username": "User123",
  "message": "Hello!",
  "client_id": "uuid",
  "timestamp": "2024-01-01T12:00:00"
}
```

```json
{
  "type": "user_joined",
  "username": "User123",
  "message": "User123 joined the room",
  "timestamp": "2024-01-01T12:00:00"
}
```

```json
{
  "type": "user_left",
  "username": "User123",
  "message": "User123 left the room",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Lobby: `/ws/lobby`

Get information about active rooms.

**Response:**

```json
{
  "type": "rooms_update",
  "rooms": {
    "general": {
      "users": 3,
      "usernames": ["User1", "User2", "User3"]
    },
    "developers": {
      "users": 2,
      "usernames": ["Alice", "Bob"]
    }
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

## Code Walkthrough

### Server Implementation

The server uses Fennec's WebSocket support:

```python
from fennec import Application, WebSocketRouter, WebSocket, WebSocketManager

# Create WebSocket router and manager
ws_router = WebSocketRouter()
ws_manager = WebSocketManager()

@ws_router.websocket("/ws/chat/{room}")
async def chat_room(websocket: WebSocket, room: str):
    # Accept connection
    await websocket.accept()
    
    # Register client
    client_id = str(uuid.uuid4())
    await ws_manager.connect(websocket, client_id)
    ws_manager.join_room(client_id, room)
    
    # Handle messages
    while True:
        data = await websocket.receive_json()
        
        # Broadcast to room
        await ws_manager.broadcast_json(
            {"type": "message", "content": data},
            room=room
        )
```

### Key Features

1. **Connection Management**: WebSocketManager handles all connections
2. **Room Support**: Clients can join different chat rooms
3. **Broadcasting**: Messages are broadcast to all users in a room
4. **JSON Messages**: Structured message format for easy parsing
5. **Error Handling**: Graceful cleanup on disconnect

## Testing

1. Open multiple browser windows with `client.html`
2. Join the same room in different windows
3. Send messages and see them appear in all windows
4. Try different rooms by changing the URL parameter

## Customization

### Change Server Port

Edit `server.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=3000)
```

### Change WebSocket URL in Client

Edit `client.html`:

```javascript
const wsUrl = `ws://localhost:3000/ws/chat/${room}`;
```

### Add Authentication

Add JWT authentication to WebSocket connections:

```python
from fennec.security import JWTHandler

@ws_router.websocket("/ws/chat/{room}")
async def chat_room(websocket: WebSocket, room: str):
    # Get token from query params
    token = websocket.scope["query_string"].decode()
    
    # Verify token
    jwt = JWTHandler(secret_key="your-secret")
    user = jwt.decode(token)
    
    # Continue with authenticated user
    await websocket.accept()
```

## Production Considerations

1. **Use Redis for WebSocketManager**: Store connections in Redis for horizontal scaling
2. **Add Rate Limiting**: Prevent message spam
3. **Implement Message History**: Store messages in database
4. **Add User Authentication**: Require login before joining
5. **Use HTTPS/WSS**: Secure WebSocket connections in production
6. **Add Message Validation**: Sanitize user input
7. **Implement Moderation**: Add admin controls and message filtering

## Learn More

- [Fennec Documentation](https://github.com/your-repo/fennec)
- [WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
- [ASGI Specification](https://asgi.readthedocs.io/)
