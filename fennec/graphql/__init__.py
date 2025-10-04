"""
GraphQL support for flexible API queries
"""

from fennec.graphql.engine import GraphQLEngine, GraphQLContext
from fennec.graphql.resolvers import query, mutation, subscription
from fennec.graphql.schema import GraphQLError

__all__ = [
    "GraphQLEngine",
    "GraphQLContext",
    "GraphQLError",
    "query",
    "mutation",
    "subscription",
]
