"""
Fennec Message Queue Module

Provides message queue support with multiple backends.
"""

from .manager import QueueManager
from .worker import Worker

__all__ = ['QueueManager', 'Worker']
