"""
gRPC Server

Implements gRPC server with HTTP/2 support.
"""

import asyncio
import logging
from typing import Dict, Any, Callable
from concurrent import futures


logger = logging.getLogger(__name__)


class GRPCServer:
    """gRPC server for Fennec applications."""
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 50051,
        max_workers: int = 10
    ):
        """
        Initialize gRPC server.
        
        Args:
            host: Server host
            port: Server port
            max_workers: Maximum number of worker threads
        """
        self.host = host
        self.port = port
        self.max_workers = max_workers
        self.server = None
        self.services = {}
    
    def add_service(self, service_class, service_instance):
        """
        Add gRPC service.
        
        Args:
            service_class: Generated service class
            service_instance: Service implementation instance
        """
        self.services[service_class.__name__] = {
            'class': service_class,
            'instance': service_instance
        }
    
    async def start(self):
        """Start gRPC server."""
        try:
            import grpc
        except ImportError:
            raise ImportError(
                "grpcio package is required for gRPC support. "
                "Install it with: pip install grpcio grpcio-tools"
            )
        
        # Create server
        self.server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=self.max_workers)
        )
        
        # Add services
        for service_name, service_info in self.services.items():
            service_class = service_info['class']
            service_instance = service_info['instance']
            
            # Add servicer to server
            add_servicer_fn = getattr(
                service_class,
                f'add_{service_class.__name__}Servicer_to_server',
                None
            )
            
            if add_servicer_fn:
                add_servicer_fn(service_instance, self.server)
                logger.info(f"Added gRPC service: {service_name}")
        
        # Bind port
        address = f"{self.host}:{self.port}"
        self.server.add_insecure_port(address)
        
        # Start server
        await self.server.start()
        logger.info(f"gRPC server started on {address}")
        
        # Wait for termination
        await self.server.wait_for_termination()
    
    async def stop(self, grace: int = 5):
        """
        Stop gRPC server.
        
        Args:
            grace: Grace period in seconds
        """
        if self.server:
            logger.info("Stopping gRPC server...")
            await self.server.stop(grace)
            logger.info("gRPC server stopped")
    
    def run(self):
        """Run gRPC server (blocking)."""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")


class GRPCServicer:
    """Base class for gRPC servicers."""
    
    def __init__(self):
        """Initialize servicer."""
        self.interceptors = []
    
    def add_interceptor(self, interceptor: Callable):
        """
        Add interceptor (middleware).
        
        Args:
            interceptor: Interceptor function
        """
        self.interceptors.append(interceptor)
    
    async def _call_with_interceptors(
        self,
        method: Callable,
        request,
        context
    ):
        """
        Call method with interceptors.
        
        Args:
            method: RPC method
            request: Request message
            context: gRPC context
            
        Returns:
            Response message
        """
        # Build interceptor chain
        async def handler(req, ctx):
            return await method(req, ctx)
        
        for interceptor in reversed(self.interceptors):
            current_handler = handler
            
            async def handler(req, ctx, h=current_handler, i=interceptor):
                return await i(req, ctx, h)
        
        return await handler(request, context)
