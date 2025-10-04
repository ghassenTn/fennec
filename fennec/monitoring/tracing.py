"""
Distributed Tracing

Provides request tracing with correlation IDs for distributed systems.
"""

import uuid
import time
from typing import Optional, Dict, Any
from contextvars import ContextVar


# Context variable for trace ID
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
span_id_var: ContextVar[Optional[str]] = ContextVar('span_id', default=None)


class RequestTracer:
    """Distributed request tracer with correlation IDs."""
    
    def __init__(self, service_name: str = "fennec_app"):
        """
        Initialize request tracer.
        
        Args:
            service_name: Name of the service
        """
        self.service_name = service_name
        self.traces = {}
    
    def generate_trace_id(self) -> str:
        """
        Generate unique trace ID.
        
        Returns:
            Trace ID string
        """
        return str(uuid.uuid4())
    
    def generate_span_id(self) -> str:
        """
        Generate unique span ID.
        
        Returns:
            Span ID string
        """
        return str(uuid.uuid4())[:8]
    
    def start_trace(self, trace_id: Optional[str] = None) -> str:
        """
        Start a new trace.
        
        Args:
            trace_id: Existing trace ID (for distributed tracing)
            
        Returns:
            Trace ID
        """
        if trace_id is None:
            trace_id = self.generate_trace_id()
        
        trace_id_var.set(trace_id)
        
        self.traces[trace_id] = {
            'trace_id': trace_id,
            'service': self.service_name,
            'start_time': time.time(),
            'spans': []
        }
        
        return trace_id
    
    def start_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new span within the current trace.
        
        Args:
            name: Span name
            attributes: Additional span attributes
            
        Returns:
            Span ID
        """
        trace_id = trace_id_var.get()
        if not trace_id:
            trace_id = self.start_trace()
        
        span_id = self.generate_span_id()
        span_id_var.set(span_id)
        
        span = {
            'span_id': span_id,
            'name': name,
            'start_time': time.time(),
            'attributes': attributes or {}
        }
        
        if trace_id in self.traces:
            self.traces[trace_id]['spans'].append(span)
        
        return span_id
    
    def end_span(self, span_id: str, status: str = "ok"):
        """
        End a span.
        
        Args:
            span_id: Span ID to end
            status: Span status ('ok' or 'error')
        """
        trace_id = trace_id_var.get()
        if not trace_id or trace_id not in self.traces:
            return
        
        for span in self.traces[trace_id]['spans']:
            if span['span_id'] == span_id:
                span['end_time'] = time.time()
                span['duration'] = span['end_time'] - span['start_time']
                span['status'] = status
                break
    
    def end_trace(self) -> Optional[Dict[str, Any]]:
        """
        End the current trace.
        
        Returns:
            Trace data
        """
        trace_id = trace_id_var.get()
        if not trace_id or trace_id not in self.traces:
            return None
        
        trace = self.traces[trace_id]
        trace['end_time'] = time.time()
        trace['duration'] = trace['end_time'] - trace['start_time']
        
        # Clean up
        trace_id_var.set(None)
        span_id_var.set(None)
        
        return trace
    
    def get_current_trace_id(self) -> Optional[str]:
        """
        Get current trace ID.
        
        Returns:
            Trace ID or None
        """
        return trace_id_var.get()
    
    def get_current_span_id(self) -> Optional[str]:
        """
        Get current span ID.
        
        Returns:
            Span ID or None
        """
        return span_id_var.get()
    
    def add_span_attribute(self, key: str, value: Any):
        """
        Add attribute to current span.
        
        Args:
            key: Attribute key
            value: Attribute value
        """
        trace_id = trace_id_var.get()
        span_id = span_id_var.get()
        
        if not trace_id or not span_id or trace_id not in self.traces:
            return
        
        for span in self.traces[trace_id]['spans']:
            if span['span_id'] == span_id:
                span['attributes'][key] = value
                break


class TracingMiddleware:
    """Middleware for automatic request tracing."""
    
    def __init__(self, tracer: RequestTracer):
        """
        Initialize middleware.
        
        Args:
            tracer: RequestTracer instance
        """
        self.tracer = tracer
    
    async def __call__(self, request, handler):
        """
        Process request with tracing.
        
        Args:
            request: HTTP request
            handler: Request handler
            
        Returns:
            Response with trace headers
        """
        # Check for existing trace ID
        trace_id = request.headers.get('X-Trace-ID')
        
        # Start trace
        trace_id = self.tracer.start_trace(trace_id)
        
        # Start request span
        span_id = self.tracer.start_span(
            f"{request.method} {request.path}",
            attributes={
                'http.method': request.method,
                'http.path': request.path,
                'http.user_agent': request.headers.get('user-agent', 'unknown')
            }
        )
        
        try:
            response = await handler(request)
            
            # Convert dict responses to Response objects
            if isinstance(response, dict):
                from fennec.request import JSONResponse
                response = JSONResponse(data=response)
            
            # Add response attributes
            status = getattr(response, 'status', getattr(response, 'status_code', 200))
            self.tracer.add_span_attribute('http.status', status)
            self.tracer.end_span(span_id, status='ok')
            
            # Add trace headers to response
            response.headers['X-Trace-ID'] = trace_id
            response.headers['X-Span-ID'] = span_id
            
            return response
            
        except Exception as e:
            self.tracer.add_span_attribute('error', str(e))
            self.tracer.end_span(span_id, status='error')
            raise
            
        finally:
            self.tracer.end_trace()
