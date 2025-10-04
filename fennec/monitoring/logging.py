"""
Structured Logging

Provides JSON-formatted structured logging with trace correlation.
"""

import json
import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime
from .tracing import trace_id_var, span_id_var


class StructuredLogger:
    """Structured JSON logger with trace correlation."""
    
    def __init__(
        self,
        name: str = "fennec",
        level: int = logging.INFO,
        output_stream=None
    ):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            level: Logging level
            output_stream: Output stream (default: stdout)
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Add JSON handler
        handler = logging.StreamHandler(output_stream or sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
    
    def _log(
        self,
        level: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        """
        Log message with structured data.
        
        Args:
            level: Log level
            message: Log message
            extra: Additional structured data
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            'logger': self.name
        }
        
        # Add trace context
        trace_id = trace_id_var.get()
        span_id = span_id_var.get()
        
        if trace_id:
            log_data['trace_id'] = trace_id
        if span_id:
            log_data['span_id'] = span_id
        
        # Add extra fields
        if extra:
            log_data.update(extra)
        
        # Log based on level
        log_method = getattr(self.logger, level.lower())
        log_method(json.dumps(log_data))
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log('DEBUG', message, kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log('INFO', message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log('WARNING', message, kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log('ERROR', message, kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log('CRITICAL', message, kwargs)
    
    def log_request(
        self,
        method: str,
        path: str,
        status: int,
        duration: float,
        **kwargs
    ):
        """
        Log HTTP request.
        
        Args:
            method: HTTP method
            path: Request path
            status: Response status
            duration: Request duration in seconds
            **kwargs: Additional fields
        """
        self.info(
            f"{method} {path} {status}",
            http_method=method,
            http_path=path,
            http_status=status,
            duration_ms=round(duration * 1000, 2),
            **kwargs
        )
    
    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Log error with context.
        
        Args:
            error: Exception instance
            context: Additional context
        """
        self.error(
            str(error),
            error_type=type(error).__name__,
            error_message=str(error),
            **(context or {})
        )


class JSONFormatter(logging.Formatter):
    """JSON log formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record
            
        Returns:
            JSON formatted string
        """
        # If message is already JSON, return as-is
        try:
            json.loads(record.getMessage())
            return record.getMessage()
        except (json.JSONDecodeError, ValueError):
            # Format as JSON
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'message': record.getMessage(),
                'logger': record.name
            }
            
            # Add exception info if present
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            
            return json.dumps(log_data)


class LoggingMiddleware:
    """Middleware for automatic request logging."""
    
    def __init__(self, logger: StructuredLogger):
        """
        Initialize middleware.
        
        Args:
            logger: StructuredLogger instance
        """
        self.logger = logger
    
    async def __call__(self, request, handler):
        """
        Process request with logging.
        
        Args:
            request: HTTP request
            handler: Request handler
            
        Returns:
            Response
        """
        import time
        start_time = time.time()
        
        try:
            response = await handler(request)
            duration = time.time() - start_time
            
            # Log successful request
            status = getattr(response, 'status', getattr(response, 'status_code', 200))
            self.logger.log_request(
                method=request.method,
                path=request.path,
                status=status,
                duration=duration,
                user_agent=request.headers.get('user-agent', 'unknown')
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Log error
            self.logger.log_error(
                e,
                context={
                    'http_method': request.method,
                    'http_path': request.path,
                    'duration_ms': round(duration * 1000, 2)
                }
            )
            
            raise
