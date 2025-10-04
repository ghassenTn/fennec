"""
Admin Metrics Collector

Collects real-time metrics for the admin dashboard.
"""

import time
import psutil
from typing import Dict, Any, List
from collections import deque
from datetime import datetime


class MetricsCollector:
    """Collects and aggregates metrics for admin dashboard."""
    
    def __init__(self, history_size: int = 100):
        """
        Initialize metrics collector.
        
        Args:
            history_size: Number of historical data points to keep
        """
        self.history_size = history_size
        self.start_time = time.time()
        
        # Request metrics
        self.request_history = deque(maxlen=history_size)
        self.error_history = deque(maxlen=history_size)
        
        # Counters
        self.total_requests = 0
        self.total_errors = 0
        self.requests_by_method = {}
        self.requests_by_endpoint = {}
        self.errors_by_type = {}
        
        # Response time tracking
        self.response_times = deque(maxlen=1000)
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        duration: float
    ):
        """
        Record HTTP request.
        
        Args:
            method: HTTP method
            endpoint: Request endpoint
            status: Response status
            duration: Request duration in seconds
        """
        self.total_requests += 1
        
        # Track by method
        self.requests_by_method[method] = self.requests_by_method.get(method, 0) + 1
        
        # Track by endpoint
        self.requests_by_endpoint[endpoint] = self.requests_by_endpoint.get(endpoint, 0) + 1
        
        # Track response time
        self.response_times.append(duration)
        
        # Add to history
        self.request_history.append({
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'endpoint': endpoint,
            'status': status,
            'duration_ms': round(duration * 1000, 2)
        })
        
        # Track errors
        if status >= 400:
            self.total_errors += 1
            self.error_history.append({
                'timestamp': datetime.now().isoformat(),
                'method': method,
                'endpoint': endpoint,
                'status': status
            })
    
    def record_error(self, error_type: str):
        """
        Record error by type.
        
        Args:
            error_type: Type of error
        """
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics.
        
        Returns:
            Dictionary of metrics
        """
        uptime = time.time() - self.start_time
        
        # Calculate request rate (requests per second)
        request_rate = self.total_requests / uptime if uptime > 0 else 0
        
        # Calculate error rate
        error_rate = (self.total_errors / self.total_requests * 100) if self.total_requests > 0 else 0
        
        # Calculate average response time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        # Calculate p95 response time
        if self.response_times:
            sorted_times = sorted(self.response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
        else:
            p95_response_time = 0
        
        return {
            'uptime_seconds': round(uptime, 2),
            'total_requests': self.total_requests,
            'total_errors': self.total_errors,
            'request_rate': round(request_rate, 2),
            'error_rate': round(error_rate, 2),
            'avg_response_time_ms': round(avg_response_time * 1000, 2),
            'p95_response_time_ms': round(p95_response_time * 1000, 2),
            'requests_by_method': self.requests_by_method,
            'requests_by_endpoint': dict(sorted(
                self.requests_by_endpoint.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),  # Top 10 endpoints
            'errors_by_type': self.errors_by_type,
            'recent_requests': list(self.request_history)[-20:],  # Last 20 requests
            'recent_errors': list(self.error_history)[-20:]  # Last 20 errors
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get system resource metrics.
        
        Returns:
            Dictionary of system metrics
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_mb': round(memory.used / 1024 / 1024, 2),
                'memory_total_mb': round(memory.total / 1024 / 1024, 2),
                'disk_percent': disk.percent,
                'disk_used_gb': round(disk.used / 1024 / 1024 / 1024, 2),
                'disk_total_gb': round(disk.total / 1024 / 1024 / 1024, 2)
            }
        except Exception as e:
            return {
                'error': str(e),
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0
            }
    
    def get_realtime_data(self) -> Dict[str, Any]:
        """
        Get real-time data for dashboard updates.
        
        Returns:
            Real-time metrics
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.get_metrics(),
            'system': self.get_system_metrics()
        }
