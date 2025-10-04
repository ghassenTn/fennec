"""
Fennec Admin Dashboard

Web-based administration interface for monitoring and management.
"""

from .dashboard import AdminDashboard
from .metrics import MetricsCollector

__all__ = ['AdminDashboard', 'MetricsCollector']
