"""
GraphQL schema parsing and validation
"""

from typing import Dict, List, Optional, Any
import re


class GraphQLError(Exception):
    """GraphQL-specific exception"""

    def __init__(self, message: str, path: Optional[List[str]] = None):
        self.message = message
        self.path = path or []
        super().__init__(self.message)


class GraphQLSchema:
    """
    Represents a parsed GraphQL schema
    """

    def __init__(self, schema_sdl: str):
        """
        Initialize schema from SDL

        Args:
            schema_sdl: GraphQL Schema Definition Language string
        """
        self.sdl = schema_sdl
        self.types: Dict[str, Dict] = {}
        self.query_type: Optional[str] = None
        self.mutation_type: Optional[str] = None
        self.subscription_type: Optional[str] = None
        self._parse()

    def _parse(self):
        """
        Parse SDL into schema structure
        """
        # Remove comments
        sdl = re.sub(r'#.*$', '', self.sdl, flags=re.MULTILINE)

        # Parse type definitions
        type_pattern = r'type\s+(\w+)\s*\{([^}]+)\}'
        for match in re.finditer(type_pattern, sdl):
            type_name = match.group(1)
            fields_str = match.group(2)

            # Parse fields
            fields = self._parse_fields(fields_str)
            self.types[type_name] = {
                'kind': 'OBJECT',
                'fields': fields
            }

            # Identify special types
            if type_name == 'Query':
                self.query_type = type_name
            elif type_name == 'Mutation':
                self.mutation_type = type_name
            elif type_name == 'Subscription':
                self.subscription_type = type_name

        # Parse input types
        input_pattern = r'input\s+(\w+)\s*\{([^}]+)\}'
        for match in re.finditer(input_pattern, sdl):
            type_name = match.group(1)
            fields_str = match.group(2)

            fields = self._parse_fields(fields_str)
            self.types[type_name] = {
                'kind': 'INPUT_OBJECT',
                'fields': fields
            }

        # Parse enums
        enum_pattern = r'enum\s+(\w+)\s*\{([^}]+)\}'
        for match in re.finditer(enum_pattern, sdl):
            type_name = match.group(1)
            values_str = match.group(2)

            values = [v.strip() for v in values_str.split('\n') if v.strip()]
            self.types[type_name] = {
                'kind': 'ENUM',
                'values': values
            }

    def _parse_fields(self, fields_str: str) -> Dict[str, Dict]:
        """
        Parse field definitions

        Args:
            fields_str: String containing field definitions

        Returns:
            Dictionary of field definitions
        """
        fields = {}
        field_pattern = r'(\w+)(\([^)]*\))?\s*:\s*(\[?[\w!]+\]?!?)'

        for line in fields_str.split('\n'):
            line = line.strip()
            if not line:
                continue

            match = re.match(field_pattern, line)
            if match:
                field_name = match.group(1)
                args_str = match.group(2)
                type_str = match.group(3)

                # Parse arguments
                args = {}
                if args_str:
                    args = self._parse_arguments(args_str[1:-1])  # Remove parentheses

                # Parse type
                field_type = self._parse_type(type_str)

                fields[field_name] = {
                    'type': field_type,
                    'args': args
                }

        return fields

    def _parse_arguments(self, args_str: str) -> Dict[str, Dict]:
        """
        Parse field arguments

        Args:
            args_str: String containing argument definitions

        Returns:
            Dictionary of argument definitions
        """
        args = {}
        arg_pattern = r'(\w+)\s*:\s*(\[?[\w!]+\]?!?)'

        for arg_match in re.finditer(arg_pattern, args_str):
            arg_name = arg_match.group(1)
            type_str = arg_match.group(2)

            args[arg_name] = {
                'type': self._parse_type(type_str)
            }

        return args

    def _parse_type(self, type_str: str) -> Dict:
        """
        Parse type string

        Args:
            type_str: Type string (e.g., "String!", "[Int]", "[User!]!")

        Returns:
            Type definition dictionary
        """
        is_required = type_str.endswith('!')
        if is_required:
            type_str = type_str[:-1]

        is_list = type_str.startswith('[') and type_str.endswith(']')
        if is_list:
            type_str = type_str[1:-1]
            item_required = type_str.endswith('!')
            if item_required:
                type_str = type_str[:-1]

            return {
                'kind': 'LIST',
                'ofType': type_str,
                'required': is_required,
                'itemRequired': item_required
            }

        return {
            'kind': 'SCALAR' if type_str in ['String', 'Int', 'Float', 'Boolean', 'ID'] else 'OBJECT',
            'name': type_str,
            'required': is_required
        }

    def get_introspection_schema(self) -> Dict:
        """
        Get introspection schema

        Returns:
            Introspection schema dictionary
        """
        types = []

        for type_name, type_def in self.types.items():
            if type_def['kind'] == 'OBJECT':
                fields = []
                for field_name, field_def in type_def['fields'].items():
                    fields.append({
                        'name': field_name,
                        'type': field_def['type'],
                        'args': field_def.get('args', {})
                    })

                types.append({
                    'kind': type_def['kind'],
                    'name': type_name,
                    'fields': fields
                })

        return {
            '__schema': {
                'queryType': {'name': self.query_type} if self.query_type else None,
                'mutationType': {'name': self.mutation_type} if self.mutation_type else None,
                'subscriptionType': {'name': self.subscription_type} if self.subscription_type else None,
                'types': types
            }
        }
