"""
Fennec gRPC Module

Provides gRPC support for high-performance microservices.
"""

from .server import GRPCServer
from .client import GRPCClient
from .decorators import rpc_method

__all__ = ['GRPCServer', 'GRPCClient', 'rpc_method']
