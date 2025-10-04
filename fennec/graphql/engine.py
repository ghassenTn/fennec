"""
GraphQL execution engine
"""

from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass
from fennec.graphql.schema import GraphQLSchema, GraphQLError
from fennec.graphql.resolvers import get_resolver
import re
import json


@dataclass
class GraphQLContext:
    """
    GraphQL execution context
    """
    request: Any = None
    user: Optional[Dict] = None
    db: Optional[Any] = None


class GraphQLEngine:
    """
    GraphQL execution engine
    """

    def __init__(self):
        self.schema: Optional[GraphQLSchema] = None
        self.resolvers: Dict[str, Dict[str, Callable]] = {}

    def set_schema(self, schema_sdl: str):
        """
        Set GraphQL schema from SDL

        Args:
            schema_sdl: GraphQL Schema Definition Language string
        """
        self.schema = GraphQLSchema(schema_sdl)

    def add_resolver(self, type_name: str, field_name: str, resolver: Callable):
        """
        Add resolver for a field

        Args:
            type_name: Type name (Query, Mutation, etc.)
            field_name: Field name
            resolver: Resolver function
        """
        if type_name not in self.resolvers:
            self.resolvers[type_name] = {}

        self.resolvers[type_name][field_name] = resolver

    async def execute(
        self,
        query: str,
        variables: Optional[Dict] = None,
        context: Optional[GraphQLContext] = None,
        operation_name: Optional[str] = None
    ) -> Dict:
        """
        Execute GraphQL query

        Args:
            query: GraphQL query string
            variables: Query variables
            context: Execution context
            operation_name: Operation name (for multiple operations)

        Returns:
            Execution result dictionary
        """
        if not self.schema:
            return {
                'errors': [{'message': 'Schema not set'}]
            }

        try:
            # Parse query
            parsed = self._parse_query(query)

            # Handle introspection
            if self._is_introspection_query(parsed):
                return {
                    'data': self.schema.get_introspection_schema()
                }

            # Execute query
            result = await self._execute_operation(
                parsed,
                variables or {},
                context or GraphQLContext()
            )

            return {'data': result}

        except GraphQLError as e:
            return {
                'errors': [{
                    'message': e.message,
                    'path': e.path
                }]
            }
        except Exception as e:
            return {
                'errors': [{
                    'message': str(e)
                }]
            }

    def _parse_query(self, query: str) -> Dict:
        """
        Parse GraphQL query string

        Args:
            query: GraphQL query string

        Returns:
            Parsed query dictionary
        """
        # Remove comments
        query = re.sub(r'#.*$', '', query, flags=re.MULTILINE)

        # Detect operation type
        operation_type = 'query'
        if query.strip().startswith('mutation'):
            operation_type = 'mutation'
        elif query.strip().startswith('subscription'):
            operation_type = 'subscription'

        # Extract operation name if present
        operation_name = None
        name_match = re.search(r'(query|mutation|subscription)\s+(\w+)', query)
        if name_match:
            operation_name = name_match.group(2)

        # Extract selection set
        selection_match = re.search(r'\{([^}]+)\}', query, re.DOTALL)
        if not selection_match:
            raise GraphQLError('Invalid query: no selection set found')

        selection_set = selection_match.group(1)

        # Parse fields
        fields = self._parse_selection_set(selection_set)

        return {
            'operation': operation_type,
            'name': operation_name,
            'fields': fields
        }

    def _parse_selection_set(self, selection_set: str) -> Dict:
        """
        Parse selection set into fields

        Args:
            selection_set: Selection set string

        Returns:
            Dictionary of fields
        """
        fields = {}

        # Simple field parsing (handles basic queries)
        # Pattern: fieldName(arg: value) { subfields }
        field_pattern = r'(\w+)(\([^)]*\))?\s*(\{[^}]*\})?'

        for match in re.finditer(field_pattern, selection_set):
            field_name = match.group(1)
            args_str = match.group(2)
            subfields_str = match.group(3)

            # Parse arguments
            args = {}
            if args_str:
                args = self._parse_arguments(args_str[1:-1])

            # Parse subfields
            subfields = {}
            if subfields_str:
                subfields = self._parse_selection_set(subfields_str[1:-1])

            fields[field_name] = {
                'args': args,
                'fields': subfields
            }

        return fields

    def _parse_arguments(self, args_str: str) -> Dict:
        """
        Parse field arguments

        Args:
            args_str: Arguments string

        Returns:
            Dictionary of arguments
        """
        args = {}

        # Pattern: argName: value
        arg_pattern = r'(\w+)\s*:\s*([^,\s]+)'

        for match in re.finditer(arg_pattern, args_str):
            arg_name = match.group(1)
            arg_value = match.group(2).strip()

            # Parse value
            if arg_value.startswith('"') and arg_value.endswith('"'):
                arg_value = arg_value[1:-1]
            elif arg_value.startswith('$'):
                # Variable reference
                pass
            elif arg_value.lower() == 'true':
                arg_value = True
            elif arg_value.lower() == 'false':
                arg_value = False
            elif arg_value.lower() == 'null':
                arg_value = None
            else:
                try:
                    arg_value = int(arg_value)
                except ValueError:
                    try:
                        arg_value = float(arg_value)
                    except ValueError:
                        pass

            args[arg_name] = arg_value

        return args

    def _is_introspection_query(self, parsed: Dict) -> bool:
        """
        Check if query is an introspection query

        Args:
            parsed: Parsed query

        Returns:
            True if introspection query
        """
        fields = parsed.get('fields', {})
        return '__schema' in fields or '__type' in fields

    async def _execute_operation(
        self,
        parsed: Dict,
        variables: Dict,
        context: GraphQLContext
    ) -> Dict:
        """
        Execute parsed operation

        Args:
            parsed: Parsed query
            variables: Query variables
            context: Execution context

        Returns:
            Execution result
        """
        operation_type = parsed['operation']
        fields = parsed['fields']

        # Map operation type to schema type
        type_name = {
            'query': 'Query',
            'mutation': 'Mutation',
            'subscription': 'Subscription'
        }.get(operation_type, 'Query')

        result = {}

        for field_name, field_data in fields.items():
            # Get resolver
            resolver = get_resolver(type_name, field_name)

            if not resolver:
                # Try custom resolvers
                resolver = self.resolvers.get(type_name, {}).get(field_name)

            if not resolver:
                raise GraphQLError(
                    f'No resolver found for {type_name}.{field_name}',
                    path=[field_name]
                )

            # Resolve variables in arguments
            args = field_data['args'].copy()
            for arg_name, arg_value in args.items():
                if isinstance(arg_value, str) and arg_value.startswith('$'):
                    var_name = arg_value[1:]
                    if var_name in variables:
                        args[arg_name] = variables[var_name]

            # Execute resolver
            try:
                field_result = await resolver(None, context, **args)
                result[field_name] = field_result
            except Exception as e:
                raise GraphQLError(
                    f'Error resolving {field_name}: {str(e)}',
                    path=[field_name]
                )

        return result

    def get_introspection_schema(self) -> Dict:
        """
        Get introspection schema

        Returns:
            Introspection schema dictionary
        """
        if not self.schema:
            return {}

        return self.schema.get_introspection_schema()
