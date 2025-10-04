"""
gRPC Client

Implements gRPC client for calling remote services.
"""

import logging
from typing import Optional, Any


logger = logging.getLogger(__name__)


class GRPCClient:
    """gRPC client for Fennec applications."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 50051,
        secure: bool = False,
        credentials: Optional[Any] = None
    ):
        """
        Initialize gRPC client.
        
        Args:
            host: Server host
            port: Server port
            secure: Use secure channel (TLS)
            credentials: SSL credentials
        """
        self.host = host
        self.port = port
        self.secure = secure
        self.credentials = credentials
        self.channel = None
        self.stubs = {}
    
    async def connect(self):
        """Connect to gRPC server."""
        try:
            import grpc
        except ImportError:
            raise ImportError(
                "grpcio package is required for gRPC support. "
                "Install it with: pip install grpcio"
            )
        
        address = f"{self.host}:{self.port}"
        
        if self.secure and self.credentials:
            self.channel = grpc.aio.secure_channel(address, self.credentials)
        else:
            self.channel = grpc.aio.insecure_channel(address)
        
        logger.info(f"Connected to gRPC server at {address}")
    
    async def disconnect(self):
        """Disconnect from gRPC server."""
        if self.channel:
            await self.channel.close()
            logger.info("Disconnected from gRPC server")
    
    def get_stub(self, stub_class):
        """
        Get or create stub for service.
        
        Args:
            stub_class: Generated stub class
            
        Returns:
            Stub instance
        """
        stub_name = stub_class.__name__
        
        if stub_name not in self.stubs:
            if not self.channel:
                raise RuntimeError("Client not connected. Call connect() first.")
            
            self.stubs[stub_name] = stub_class(self.channel)
        
        return self.stubs[stub_name]
    
    async def call(
        self,
        stub_class,
        method_name: str,
        request,
        timeout: Optional[float] = None
    ):
        """
        Call RPC method.
        
        Args:
            stub_class: Generated stub class
            method_name: Method name
            request: Request message
            timeout: Request timeout in seconds
            
        Returns:
            Response message
        """
        stub = self.get_stub(stub_class)
        method = getattr(stub, method_name)
        
        try:
            response = await method(request, timeout=timeout)
            return response
        except Exception as e:
            logger.error(f"RPC call failed: {e}")
            raise
    
    async def call_stream(
        self,
        stub_class,
        method_name: str,
        request_iterator,
        timeout: Optional[float] = None
    ):
        """
        Call streaming RPC method.
        
        Args:
            stub_class: Generated stub class
            method_name: Method name
            request_iterator: Request message iterator
            timeout: Request timeout in seconds
            
        Yields:
            Response messages
        """
        stub = self.get_stub(stub_class)
        method = getattr(stub, method_name)
        
        try:
            async for response in method(request_iterator, timeout=timeout):
                yield response
        except Exception as e:
            logger.error(f"Streaming RPC call failed: {e}")
            raise
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.disconnect()
