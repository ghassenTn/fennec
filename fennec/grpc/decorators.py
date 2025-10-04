"""
gRPC Decorators

Provides decorators for gRPC methods.
"""

import functools
import logging
from typing import Callable


logger = logging.getLogger(__name__)


def rpc_method(
    log_requests: bool = True,
    log_responses: bool = False
):
    """
    Decorator for gRPC methods.
    
    Args:
        log_requests: Log incoming requests
        log_responses: Log outgoing responses
        
    Example:
        @rpc_method(log_requests=True)
        async def GetUser(self, request, context):
            return user_pb2.User(id=request.id)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, request, context):
            method_name = func.__name__
            
            if log_requests:
                logger.info(f"RPC call: {method_name}")
                logger.debug(f"Request: {request}")
            
            try:
                response = await func(self, request, context)
                
                if log_responses:
                    logger.debug(f"Response: {response}")
                
                return response
                
            except Exception as e:
                logger.error(f"RPC error in {method_name}: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                raise
        
        return wrapper
    
    return decorator


def validate_request(validator: Callable):
    """
    Decorator to validate request messages.
    
    Args:
        validator: Validation function
        
    Example:
        def validate_user_id(request):
            if request.id <= 0:
                raise ValueError("Invalid user ID")
        
        @validate_request(validate_user_id)
        async def GetUser(self, request, context):
            return user
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, request, context):
            try:
                validator(request)
            except Exception as e:
                logger.error(f"Request validation failed: {e}")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                raise
            
            return await func(self, request, context)
        
        return wrapper
    
    return decorator


def require_auth(auth_check: Callable):
    """
    Decorator to require authentication.
    
    Args:
        auth_check: Function to check authentication
        
    Example:
        def check_token(context):
            metadata = dict(context.invocation_metadata())
            token = metadata.get('authorization')
            return verify_token(token)
        
        @require_auth(check_token)
        async def GetUser(self, request, context):
            return user
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, request, context):
            try:
                if not auth_check(context):
                    context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                    context.set_details("Authentication required")
                    raise Exception("Unauthenticated")
            except Exception as e:
                logger.error(f"Authentication failed: {e}")
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Authentication failed")
                raise
            
            return await func(self, request, context)
        
        return wrapper
    
    return decorator
