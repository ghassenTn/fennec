"""
GraphQL resolver decorators
"""

from typing import Callable, Dict
from functools import wraps


# Global resolver registry
_resolvers: Dict[str, Dict[str, Callable]] = {
    'Query': {},
    'Mutation': {},
    'Subscription': {}
}


def query(field_name: str):
    """
    Decorator for GraphQL query resolvers

    Usage:
        @query("user")
        async def resolve_user(parent, info, id: int):
            return get_user_by_id(id)

    Args:
        field_name: Name of the query field
    """
    def decorator(func: Callable):
        _resolvers['Query'][field_name] = func

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def mutation(field_name: str):
    """
    Decorator for GraphQL mutation resolvers

    Usage:
        @mutation("createUser")
        async def resolve_create_user(parent, info, name: str, email: str):
            return create_user(name, email)

    Args:
        field_name: Name of the mutation field
    """
    def decorator(func: Callable):
        _resolvers['Mutation'][field_name] = func

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def subscription(field_name: str):
    """
    Decorator for GraphQL subscription resolvers

    Usage:
        @subscription("userCreated")
        async def resolve_user_created(parent, info):
            async for user in user_stream():
                yield user

    Args:
        field_name: Name of the subscription field
    """
    def decorator(func: Callable):
        _resolvers['Subscription'][field_name] = func

        @wraps(func)
        async def wrapper(*args, **kwargs):
            async for item in func(*args, **kwargs):
                yield item

        return wrapper

    return decorator


def get_resolver(type_name: str, field_name: str) -> Callable:
    """
    Get resolver for a field

    Args:
        type_name: Type name (Query, Mutation, Subscription)
        field_name: Field name

    Returns:
        Resolver function or None
    """
    return _resolvers.get(type_name, {}).get(field_name)


def clear_resolvers():
    """
    Clear all registered resolvers (useful for testing)
    """
    _resolvers['Query'].clear()
    _resolvers['Mutation'].clear()
    _resolvers['Subscription'].clear()
