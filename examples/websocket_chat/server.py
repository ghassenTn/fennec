"""
WebSocket Chat Server Example

A real-time chat application demonstrating WebSocket support in Fennec.
Features multiple chat rooms and message broadcasting.
"""

from fennec import Application, WebSocketRouter, WebSocket, WebSocketManager
import uuid
import json
from datetime import datetime


# Create application
app = Application(title="Chat Server")

# Create WebSocket router and manager
ws_router = WebSocketRouter()
ws_manager = WebSocketManager()

# Store user information
users = {}


@ws_router.websocket("/ws/chat/{room}")
async def chat_room(websocket: WebSocket, room: str):
    """
    WebSocket endpoint for chat rooms
    
    Args:
        websocket: WebSocket connection
        room: Chat room name
    """
    # Accept connection
    await websocket.accept()
    
    # Generate client ID
    client_id = str(uuid.uuid4())
    
    # Register connection
    await ws_manager.connect(websocket, client_id)
    ws_manager.join_room(client_id, room)
    
    # Default username
    username = f"User-{client_id[:8]}"
    users[client_id] = {
        "username": username,
        "room": room,
        "joined_at": datetime.now().isoformat()
    }
    
    # Send welcome message
    await websocket.send_json({
        "type": "system",
        "message": f"Welcome to room '{room}'!",
        "client_id": client_id,
        "timestamp": datetime.now().isoformat()
    })
    
    # Notify others
    await ws_manager.broadcast_json(
        {
            "type": "user_joined",
            "username": username,
            "message": f"{username} joined the room",
            "timestamp": datetime.now().isoformat()
        },
        room=room,
        exclude=client_id
    )
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            message_type = data.get("type", "message")
            
            if message_type == "set_username":
                # Update username
                new_username = data.get("username", username)
                old_username = users[client_id]["username"]
                users[client_id]["username"] = new_username
                
                # Notify room
                await ws_manager.broadcast_json(
                    {
                        "type": "username_changed",
                        "old_username": old_username,
                        "new_username": new_username,
                        "message": f"{old_username} is now known as {new_username}",
                        "timestamp": datetime.now().isoformat()
                    },
                    room=room
                )
                
            elif message_type == "message":
                # Broadcast message to room
                message_content = data.get("message", "")
                
                await ws_manager.broadcast_json(
                    {
                        "type": "message",
                        "username": users[client_id]["username"],
                        "message": message_content,
                        "client_id": client_id,
                        "timestamp": datetime.now().isoformat()
                    },
                    room=room
                )
            
            elif message_type == "typing":
                # Broadcast typing indicator
                await ws_manager.broadcast_json(
                    {
                        "type": "typing",
                        "username": users[client_id]["username"],
                        "timestamp": datetime.now().isoformat()
                    },
                    room=room,
                    exclude=client_id
                )
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up on disconnect
        username = users[client_id]["username"]
        
        # Notify others
        await ws_manager.broadcast_json(
            {
                "type": "user_left",
                "username": username,
                "message": f"{username} left the room",
                "timestamp": datetime.now().isoformat()
            },
            room=room,
            exclude=client_id
        )
        
        # Remove user
        await ws_manager.disconnect(client_id)
        del users[client_id]


@ws_router.websocket("/ws/lobby")
async def lobby(websocket: WebSocket):
    """
    WebSocket endpoint for lobby (list active rooms)
    """
    await websocket.accept()
    client_id = str(uuid.uuid4())
    await ws_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Send active rooms info
            rooms_info = {}
            for room_name, clients in ws_manager.rooms.items():
                rooms_info[room_name] = {
                    "users": len(clients),
                    "usernames": [users.get(cid, {}).get("username", "Unknown") for cid in clients]
                }
            
            await websocket.send_json({
                "type": "rooms_update",
                "rooms": rooms_info,
                "timestamp": datetime.now().isoformat()
            })
            
            # Wait for next request
            await websocket.receive_text()
    
    except:
        pass
    
    finally:
        await ws_manager.disconnect(client_id)


# Include WebSocket router
app.include_websocket_router(ws_router)


if __name__ == "__main__":
    import uvicorn
    print("🦊 Fennec Chat Server")
    print("=" * 50)
    print("WebSocket endpoints:")
    print("  - ws://localhost:8000/ws/chat/{room}")
    print("  - ws://localhost:8000/ws/lobby")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
