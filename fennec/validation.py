"""
Validation engine - Type-hint based validation
"""

from typing import Any, Dict, get_type_hints, get_origin, get_args, Union
import json
import inspect


class ValidationError(Exception):
    """
    خطأ في الـ validation
    """
    def __init__(self, errors: Dict[str, str]):
        self.errors = errors
        super().__init__(f"Validation failed: {errors}")


class BaseModel:
    """
    Base class لجميع models مع validation تلقائي
    يستخدم type hints للـ validation
    """
    
    _validators: Dict[str, Any] = {}
    
    def __init__(self, **data):
        self._errors: Dict[str, str] = {}
        self._validate(data)
        
        if self._errors:
            raise ValidationError(self._errors)
        
        # Set attributes
        for key, value in data.items():
            setattr(self, key, value)
    
    def _validate(self, data: Dict):
        """
        Validate data ضد type hints
        """
        # Get type hints for the class
        try:
            hints = get_type_hints(self.__class__)
        except Exception:
            hints = {}
        
        # Check required fields and validate types
        for field_name, field_type in hints.items():
            # Skip private fields
            if field_name.startswith("_"):
                continue
            
            # Check if field exists
            if field_name not in data:
                # Check if field has default value
                if hasattr(self.__class__, field_name):
                    default = getattr(self.__class__, field_name)
                    if isinstance(default, Field):
                        if default.required:
                            self._errors[field_name] = "Field is required"
                        else:
                            data[field_name] = default.default
                    else:
                        data[field_name] = default
                else:
                    self._errors[field_name] = "Field is required"
                continue
            
            value = data[field_name]
            
            # Validate type
            if not self._check_type(value, field_type):
                self._errors[field_name] = f"Expected type {field_type}, got {type(value).__name__}"
            
            # Check Field constraints
            if hasattr(self.__class__, field_name):
                class_attr = getattr(self.__class__, field_name)
                if isinstance(class_attr, Field):
                    field_errors = self._validate_field_constraints(value, class_attr)
                    if field_errors:
                        self._errors[field_name] = field_errors
            
            # Run custom validators
            validator_name = f"validate_{field_name}"
            if hasattr(self.__class__, validator_name):
                validator = getattr(self.__class__, validator_name)
                try:
                    validated_value = validator(self, value)
                    if validated_value is not None:
                        data[field_name] = validated_value
                except ValueError as e:
                    self._errors[field_name] = str(e)
    
    def _validate_field_constraints(self, value: Any, field: 'Field') -> str:
        """
        التحقق من قيود الـ Field
        """
        # Check min_length
        if field.min_length is not None:
            if isinstance(value, (str, list, dict)):
                if len(value) < field.min_length:
                    return f"Minimum length is {field.min_length}"
        
        # Check max_length
        if field.max_length is not None:
            if isinstance(value, (str, list, dict)):
                if len(value) > field.max_length:
                    return f"Maximum length is {field.max_length}"
        
        return ""
    
    def _check_type(self, value: Any, expected_type: Any) -> bool:
        """
        التحقق من نوع البيانات
        """
        # Handle None
        if value is None:
            origin = get_origin(expected_type)
            if origin is Union:
                args = get_args(expected_type)
                return type(None) in args
            return False
        
        # Handle Union types (e.g., Optional[str])
        origin = get_origin(expected_type)
        if origin is Union:
            args = get_args(expected_type)
            return any(self._check_type(value, arg) for arg in args)
        
        # Handle basic types
        if expected_type in (int, str, float, bool, dict, list):
            return isinstance(value, expected_type)
        
        # Handle Any
        if expected_type is Any:
            return True
        
        # Default: check instance
        try:
            return isinstance(value, expected_type)
        except TypeError:
            return True
    
    @classmethod
    def validator(cls, field: str):
        """
        Decorator لإضافة custom validators
        """
        def decorator(func):
            setattr(cls, f"validate_{field}", func)
            return func
        return decorator
    
    def dict(self) -> Dict:
        """
        تحويل model إلى dictionary
        """
        result = {}
        hints = get_type_hints(self.__class__)
        
        for field_name in hints.keys():
            if field_name.startswith("_"):
                continue
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                # Convert nested BaseModel to dict
                if isinstance(value, BaseModel):
                    result[field_name] = value.dict()
                elif isinstance(value, list):
                    result[field_name] = [
                        item.dict() if isinstance(item, BaseModel) else item
                        for item in value
                    ]
                else:
                    result[field_name] = value
        
        return result
    
    def json(self) -> str:
        """
        تحويل model إلى JSON string
        """
        return json.dumps(self.dict())


class Field:
    """
    يمثل field في model مع validation rules
    """
    
    def __init__(
        self, 
        default: Any = None, 
        required: bool = True, 
        min_length: int = None, 
        max_length: int = None
    ):
        self.default = default
        self.required = required
        self.min_length = min_length
        self.max_length = max_length
