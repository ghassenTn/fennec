"""
OpenAPI documentation generator
"""

from typing import Dict, Type, Callable, Any, get_type_hints, Optional
import inspect


class OpenAPIGenerator:
    """
    يولد OpenAPI specification من routes
    يستخرج معلومات من type hints و docstrings
    """

    def __init__(self, app):
        self.app = app

    def generate_spec(self) -> Dict:
        """
        توليد OpenAPI specification كامل
        """
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": self.app.title,
                "version": self.app.version,
            },
            "paths": {},
            "components": {"schemas": {}},
        }

        # Generate paths from routes
        for route in self.app.router.routes:
            path = route.path
            if path not in spec["paths"]:
                spec["paths"][path] = {}

            # Extract route info
            route_info = self.extract_route_info(route.handler)

            # Add for each method
            for method in route.methods:
                spec["paths"][path][method.lower()] = route_info

        return spec

    def extract_route_info(self, handler: Callable) -> Dict:
        """
        استخراج معلومات route من handler
        """
        info = {
            "summary": handler.__name__.replace("_", " ").title(),
            "description": "",
            "parameters": [],
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": {"application/json": {"schema": {"type": "object"}}},
                }
            },
        }

        # Extract docstring
        if handler.__doc__:
            info["description"] = handler.__doc__.strip()

        # Extract parameters from signature
        sig = inspect.signature(handler)
        hints = get_type_hints(handler)
        
        # Check if this is a POST/PUT/PATCH method that needs request body
        has_request_param = "request" in sig.parameters

        for param_name, param in sig.parameters.items():
            if param_name in ("self",):
                continue
            
            # Skip request parameter but note that we need a request body
            if param_name == "request":
                continue

            # Check if it's a dependency (has Depends as default)
            from fennec.dependencies import DependencyMarker
            if isinstance(param.default, DependencyMarker):
                continue

            param_info = {
                "name": param_name,
                "in": "path",  # Default to path parameter
                "required": param.default == inspect.Parameter.empty,
                "schema": {"type": "string"},
            }

            # Get type from hints
            if param_name in hints:
                param_type = hints[param_name]
                param_info["schema"]["type"] = self._get_json_type(param_type)

            info["parameters"].append(param_info)
        
        # If handler has 'request' parameter, add request body schema
        if has_request_param:
            # Try to extract request body schema from docstring
            request_body_schema = self._extract_request_body_from_docstring(handler)
            
            if not request_body_schema:
                # Add a generic request body for POST/PUT/PATCH
                request_body_schema = {
                    "type": "object",
                    "properties": {
                        "data": {"type": "object", "description": "Request data"}
                    }
                }
            
            info["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": request_body_schema
                    }
                }
            }

        return info
    
    def _extract_request_body_from_docstring(self, handler: Callable) -> Optional[Dict]:
        """
        استخراج request body schema من docstring
        """
        if not handler.__doc__:
            return None
        
        docstring = handler.__doc__
        
        # Look for "Request Body:" section
        if "Request Body:" not in docstring:
            return None
        
        # Extract the Request Body section
        lines = docstring.split("\n")
        in_request_body = False
        properties = {}
        
        for line in lines:
            line = line.strip()
            
            if "Request Body:" in line:
                in_request_body = True
                continue
            
            if in_request_body:
                # Stop if we hit another section or empty line after content
                if line and not line.startswith(" ") and ":" in line and "(" not in line:
                    break
                
                # Parse field definition: name (type): description
                if "(" in line and ")" in line and ":" in line:
                    # Extract field name
                    field_name = line.split("(")[0].strip()
                    
                    # Extract type
                    type_str = line.split("(")[1].split(")")[0].strip()
                    
                    # Extract description
                    description = line.split(":", 1)[1].strip() if ":" in line else ""
                    
                    # Map Python types to JSON schema types
                    json_type = "string"
                    if type_str == "int":
                        json_type = "integer"
                    elif type_str == "float":
                        json_type = "number"
                    elif type_str == "bool":
                        json_type = "boolean"
                    elif type_str == "list":
                        json_type = "array"
                    elif type_str == "dict":
                        json_type = "object"
                    
                    properties[field_name] = {
                        "type": json_type,
                        "description": description
                    }
                    
                    # Add example based on field name
                    if field_name == "name":
                        properties[field_name]["example"] = "John Doe"
                    elif field_name == "email":
                        properties[field_name]["example"] = "john@example.com"
                    elif field_name == "age":
                        properties[field_name]["example"] = 30
        
        if properties:
            return {
                "type": "object",
                "properties": properties,
                "required": list(properties.keys())
            }
        
        return None

    def generate_schema(self, model: Type) -> Dict:
        """
        توليد JSON schema من BaseModel
        """
        from fennec.validation import BaseModel

        if not issubclass(model, BaseModel):
            return {"type": "object"}

        schema = {"type": "object", "properties": {}, "required": []}

        try:
            hints = get_type_hints(model)

            for field_name, field_type in hints.items():
                if field_name.startswith("_"):
                    continue

                schema["properties"][field_name] = {
                    "type": self._get_json_type(field_type)
                }

                # Check if required
                if hasattr(model, field_name):
                    from fennec.validation import Field

                    field_obj = getattr(model, field_name)
                    if isinstance(field_obj, Field):
                        if field_obj.required:
                            schema["required"].append(field_name)
                    else:
                        schema["required"].append(field_name)
                else:
                    schema["required"].append(field_name)

        except Exception:
            pass

        return schema

    def _get_json_type(self, python_type: Any) -> str:
        """
        تحويل Python type إلى JSON schema type
        """
        type_mapping = {
            int: "integer",
            str: "string",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }

        # Handle Optional types
        if hasattr(python_type, "__origin__"):
            origin = python_type.__origin__
            if origin in type_mapping:
                return type_mapping[origin]

        if python_type in type_mapping:
            return type_mapping[python_type]

        return "string"
