"""
WebSocket support for real-time bidirectional communication
"""

from typing import Dict, Set, Callable, Optional, Any
import json
import uuid


class WebSocketException(Exception):
    """WebSocket-specific exception"""

    def __init__(self, code: int, reason: str):
        self.code = code
        self.reason = reason
        super().__init__(f"WebSocket error {code}: {reason}")


class WebSocket:
    """
    Represents a WebSocket connection
    """

    def __init__(self, scope: Dict, receive: Callable, send: Callable):
        """
        Initialize WebSocket connection

        Args:
            scope: ASGI scope dictionary
            receive: ASGI receive callable
            send: ASGI send callable
        """
        self.scope = scope
        self.receive = receive
        self.send = send
        self.client_id: Optional[str] = None
        self.client_state = "connecting"

    async def accept(self, subprotocol: Optional[str] = None):
        """
        Accept WebSocket connection

        Args:
            subprotocol: Optional subprotocol to use
        """
        message = {
            "type": "websocket.accept",
        }
        if subprotocol:
            message["subprotocol"] = subprotocol

        await self.send(message)
        self.client_state = "connected"

    async def close(self, code: int = 1000, reason: str = ""):
        """
        Close WebSocket connection

        Args:
            code: Close code (default: 1000 - normal closure)
            reason: Close reason
        """
        if self.client_state == "connected":
            await self.send({
                "type": "websocket.close",
                "code": code,
                "reason": reason
            })
            self.client_state = "disconnected"

    async def send_text(self, data: str):
        """
        Send text message

        Args:
            data: Text data to send
        """
        if self.client_state != "connected":
            raise WebSocketException(1000, "WebSocket not connected")

        await self.send({
            "type": "websocket.send",
            "text": data
        })

    async def send_bytes(self, data: bytes):
        """
        Send binary message

        Args:
            data: Binary data to send
        """
        if self.client_state != "connected":
            raise WebSocketException(1000, "WebSocket not connected")

        await self.send({
            "type": "websocket.send",
            "bytes": data
        })

    async def send_json(self, data: Any):
        """
        Send JSON message

        Args:
            data: Data to serialize as JSON
        """
        await self.send_text(json.dumps(data))

    async def receive_text(self) -> str:
        """
        Receive text message

        Returns:
            Text data

        Raises:
            WebSocketException: If connection closed or error occurs
        """
        while True:
            message = await self.receive()

            if message["type"] == "websocket.disconnect":
                self.client_state = "disconnected"
                raise WebSocketException(
                    message.get("code", 1000),
                    "Connection closed"
                )

            if message["type"] == "websocket.receive":
                # Return text if available, otherwise continue waiting
                if "text" in message:
                    return message["text"]
                # If bytes received but text expected, skip and continue
                continue
            
            # Skip other message types (like websocket.connect)
            continue

    async def receive_bytes(self) -> bytes:
        """
        Receive binary message

        Returns:
            Binary data

        Raises:
            WebSocketException: If connection closed or error occurs
        """
        while True:
            message = await self.receive()

            if message["type"] == "websocket.disconnect":
                self.client_state = "disconnected"
                raise WebSocketException(
                    message.get("code", 1000),
                    "Connection closed"
                )

            if message["type"] == "websocket.receive":
                # Return bytes if available, otherwise continue waiting
                if "bytes" in message:
                    return message["bytes"]
                # If text received but bytes expected, skip and continue
                continue
            
            # Skip other message types
            continue

    async def receive_json(self) -> Any:
        """
        Receive JSON message

        Returns:
            Deserialized JSON data

        Raises:
            WebSocketException: If connection closed or error occurs
        """
        text = await self.receive_text()
        return json.loads(text)


class WebSocketManager:
    """
    Manages WebSocket connections and rooms
    """

    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> str:
        """
        Register WebSocket connection

        Args:
            websocket: WebSocket instance
            client_id: Optional client ID (generated if not provided)

        Returns:
            Client ID
        """
        if client_id is None:
            client_id = str(uuid.uuid4())

        websocket.client_id = client_id
        self.connections[client_id] = websocket
        return client_id

    async def disconnect(self, client_id: str):
        """
        Unregister WebSocket connection

        Args:
            client_id: Client ID to disconnect
        """
        # Remove from all rooms
        for room in list(self.rooms.keys()):
            self.leave_room(client_id, room)

        # Remove connection
        if client_id in self.connections:
            del self.connections[client_id]

    async def send_message(self, client_id: str, message: str):
        """
        Send message to specific client

        Args:
            client_id: Target client ID
            message: Message to send
        """
        if client_id in self.connections:
            websocket = self.connections[client_id]
            await websocket.send_text(message)

    async def send_json(self, client_id: str, data: Any):
        """
        Send JSON message to specific client

        Args:
            client_id: Target client ID
            data: Data to send as JSON
        """
        if client_id in self.connections:
            websocket = self.connections[client_id]
            await websocket.send_json(data)

    async def broadcast(self, message: str, room: Optional[str] = None, exclude: Optional[str] = None):
        """
        Broadcast message to all clients or room

        Args:
            message: Message to broadcast
            room: Optional room name (broadcasts to all if None)
            exclude: Optional client ID to exclude from broadcast
        """
        if room:
            # Broadcast to room
            if room in self.rooms:
                for client_id in self.rooms[room]:
                    if client_id != exclude:
                        await self.send_message(client_id, message)
        else:
            # Broadcast to all
            for client_id in self.connections:
                if client_id != exclude:
                    await self.send_message(client_id, message)

    async def broadcast_json(self, data: Any, room: Optional[str] = None, exclude: Optional[str] = None):
        """
        Broadcast JSON message to all clients or room

        Args:
            data: Data to broadcast as JSON
            room: Optional room name (broadcasts to all if None)
            exclude: Optional client ID to exclude from broadcast
        """
        message = json.dumps(data)
        await self.broadcast(message, room, exclude)

    def join_room(self, client_id: str, room: str):
        """
        Add client to room

        Args:
            client_id: Client ID
            room: Room name
        """
        if room not in self.rooms:
            self.rooms[room] = set()

        self.rooms[room].add(client_id)

    def leave_room(self, client_id: str, room: str):
        """
        Remove client from room

        Args:
            client_id: Client ID
            room: Room name
        """
        if room in self.rooms:
            self.rooms[room].discard(client_id)

            # Clean up empty rooms
            if not self.rooms[room]:
                del self.rooms[room]

    def get_room_clients(self, room: str) -> Set[str]:
        """
        Get all clients in a room

        Args:
            room: Room name

        Returns:
            Set of client IDs
        """
        return self.rooms.get(room, set()).copy()


class WebSocketRoute:
    """
    Represents a WebSocket route
    """

    def __init__(self, path: str, handler: Callable):
        self.path = path
        self.handler = handler
        self.path_params = {}


class WebSocketRouter:
    """
    Router for WebSocket endpoints
    """

    def __init__(self, prefix: str = ""):
        self.prefix = prefix.rstrip("/")
        self.routes: list[WebSocketRoute] = []

    def websocket(self, path: str):
        """
        Decorator for WebSocket routes

        Usage:
            @ws_router.websocket("/chat")
            async def chat_handler(websocket: WebSocket):
                await websocket.accept()
                while True:
                    data = await websocket.receive_text()
                    await websocket.send_text(f"Echo: {data}")

        Args:
            path: WebSocket path
        """
        def decorator(handler: Callable):
            full_path = self.prefix + path
            self.add_route(full_path, handler)
            return handler
        return decorator

    def add_route(self, path: str, handler: Callable):
        """
        Add WebSocket route

        Args:
            path: WebSocket path
            handler: Handler function
        """
        route = WebSocketRoute(path, handler)
        self.routes.append(route)

    async def match(self, path: str) -> Optional[WebSocketRoute]:
        """
        Find matching WebSocket route with path parameter support

        Args:
            path: Request path

        Returns:
            Matching route or None
        """
        import re
        
        for route in self.routes:
            # Exact match
            if route.path == path:
                return route
            
            # Path parameter match
            # Convert route pattern like /ws/chat/{room} to regex
            pattern = route.path
            param_names = []
            
            # Find all {param} patterns
            param_pattern = r'\{(\w+)\}'
            for match in re.finditer(param_pattern, pattern):
                param_names.append(match.group(1))
            
            # Replace {param} with regex capture groups
            regex_pattern = re.sub(param_pattern, r'([^/]+)', pattern)
            regex_pattern = f'^{regex_pattern}$'
            
            # Try to match
            match = re.match(regex_pattern, path)
            if match:
                # Extract path parameters
                route.path_params = {}
                for i, param_name in enumerate(param_names):
                    route.path_params[param_name] = match.group(i + 1)
                return route

        return None
