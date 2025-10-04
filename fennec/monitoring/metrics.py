"""
Prometheus Metrics

Collects and exposes application metrics in Prometheus format.
"""

import time
from typing import Optional
from prometheus_client import (
    Counter, Histogram, Gauge, Info,
    generate_latest, CONTENT_TYPE_LATEST
)


class PrometheusMetrics:
    """Prometheus metrics collector for Fennec applications."""
    
    def __init__(self, app_name: str = "fennec_app"):
        """
        Initialize Prometheus metrics.
        
        Args:
            app_name: Application name for metric labels
        """
        self.app_name = app_name
        
        # Request metrics
        self.request_count = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint']
        )
        
        self.request_size = Histogram(
            'http_request_size_bytes',
            'HTTP request size in bytes',
            ['method', 'endpoint']
        )
        
        self.response_size = Histogram(
            'http_response_size_bytes',
            'HTTP response size in bytes',
            ['method', 'endpoint']
        )
        
        # Application metrics
        self.active_requests = Gauge(
            'http_requests_active',
            'Number of active HTTP requests'
        )
        
        self.error_count = Counter(
            'http_errors_total',
            'Total HTTP errors',
            ['method', 'endpoint', 'error_type']
        )
        
        # WebSocket metrics
        self.websocket_connections = Gauge(
            'websocket_connections_active',
            'Number of active WebSocket connections'
        )
        
        self.websocket_messages = Counter(
            'websocket_messages_total',
            'Total WebSocket messages',
            ['direction']  # sent/received
        )
        
        # Database metrics
        self.db_query_duration = Histogram(
            'db_query_duration_seconds',
            'Database query duration in seconds',
            ['query_type']
        )
        
        self.db_connections = Gauge(
            'db_connections_active',
            'Number of active database connections'
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'cache_hits_total',
            'Total cache hits'
        )
        
        self.cache_misses = Counter(
            'cache_misses_total',
            'Total cache misses'
        )
        
        # Application info
        self.app_info = Info(
            'app_info',
            'Application information'
        )
        self.app_info.info({
            'app_name': app_name,
            'version': '0.3.0'
        })
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        duration: float,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None
    ):
        """
        Record HTTP request metrics.
        
        Args:
            method: HTTP method
            endpoint: Request endpoint
            status: Response status code
            duration: Request duration in seconds
            request_size: Request size in bytes
            response_size: Response size in bytes
        """
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        self.request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        if request_size is not None:
            self.request_size.labels(
                method=method,
                endpoint=endpoint
            ).observe(request_size)
        
        if response_size is not None:
            self.response_size.labels(
                method=method,
                endpoint=endpoint
            ).observe(response_size)
    
    def record_error(self, method: str, endpoint: str, error_type: str):
        """
        Record HTTP error.
        
        Args:
            method: HTTP method
            endpoint: Request endpoint
            error_type: Type of error
        """
        self.error_count.labels(
            method=method,
            endpoint=endpoint,
            error_type=error_type
        ).inc()
    
    def increment_active_requests(self):
        """Increment active requests counter."""
        self.active_requests.inc()
    
    def decrement_active_requests(self):
        """Decrement active requests counter."""
        self.active_requests.dec()
    
    def record_websocket_connection(self, delta: int):
        """
        Record WebSocket connection change.
        
        Args:
            delta: Change in connections (+1 or -1)
        """
        if delta > 0:
            self.websocket_connections.inc(delta)
        else:
            self.websocket_connections.dec(abs(delta))
    
    def record_websocket_message(self, direction: str):
        """
        Record WebSocket message.
        
        Args:
            direction: 'sent' or 'received'
        """
        self.websocket_messages.labels(direction=direction).inc()
    
    def record_db_query(self, query_type: str, duration: float):
        """
        Record database query.
        
        Args:
            query_type: Type of query (SELECT, INSERT, etc.)
            duration: Query duration in seconds
        """
        self.db_query_duration.labels(query_type=query_type).observe(duration)
    
    def set_db_connections(self, count: int):
        """
        Set active database connections.
        
        Args:
            count: Number of active connections
        """
        self.db_connections.set(count)
    
    def record_cache_hit(self):
        """Record cache hit."""
        self.cache_hits.inc()
    
    def record_cache_miss(self):
        """Record cache miss."""
        self.cache_misses.inc()
    
    def generate_metrics(self) -> bytes:
        """
        Generate Prometheus metrics output.
        
        Returns:
            Metrics in Prometheus text format
        """
        return generate_latest()
    
    def get_content_type(self) -> str:
        """
        Get Prometheus content type.
        
        Returns:
            Content type string
        """
        return CONTENT_TYPE_LATEST


class MetricsMiddleware:
    """Middleware for automatic metrics collection."""
    
    def __init__(self, metrics: PrometheusMetrics):
        """
        Initialize middleware.
        
        Args:
            metrics: PrometheusMetrics instance
        """
        self.metrics = metrics
    
    async def __call__(self, request, handler):
        """
        Process request and collect metrics.
        
        Args:
            request: HTTP request
            handler: Request handler
            
        Returns:
            Response
        """
        self.metrics.increment_active_requests()
        start_time = time.time()
        
        try:
            response = await handler(request)
            duration = time.time() - start_time
            
            # Record metrics
            status = getattr(response, 'status', getattr(response, 'status_code', 200))
            response_size = None
            if hasattr(response, 'body'):
                response_size = len(response.body)
            elif hasattr(response, 'content'):
                try:
                    response_size = len(str(response.content))
                except:
                    pass
            
            # Convert request size to int
            request_size = None
            content_length = request.headers.get('content-length')
            if content_length:
                try:
                    request_size = int(content_length)
                except (ValueError, TypeError):
                    pass
            
            self.metrics.record_request(
                method=request.method,
                endpoint=request.path,
                status=status,
                duration=duration,
                request_size=request_size,
                response_size=response_size
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Record error
            self.metrics.record_error(
                method=request.method,
                endpoint=request.path,
                error_type=type(e).__name__
            )
            
            raise
            
        finally:
            self.metrics.decrement_active_requests()
