"""Schema definitions for data validation."""
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import re


class FieldType(str, Enum):
    """Supported field types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    EMAIL = "email"
    PHONE = "phone"


class ValidationRule(BaseModel):
    """Validation rule for a field."""
    field_type: FieldType
    required: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    choices: Optional[List[Any]] = None
    default: Optional[Any] = None


class DataSchema(BaseModel):
    """Data schema definition."""
    name: str
    description: Optional[str] = None
    fields: Dict[str, ValidationRule]
    version: str = "1.0.0"

    @field_validator("fields")
    @classmethod
    def validate_fields(cls, v):
        """Validate that fields are properly defined."""
        if not v:
            raise ValueError("Schema must have at least one field")
        return v


# Predefined schemas for common use cases
USER_SCHEMA = DataSchema(
    name="user",
    description="User data schema",
    fields={
        "id": ValidationRule(field_type=FieldType.INTEGER, required=True),
        "name": ValidationRule(field_type=FieldType.STRING, required=True, min_length=1, max_length=100),
        "email": ValidationRule(field_type=FieldType.EMAIL, required=True),
        "age": ValidationRule(field_type=FieldType.INTEGER, min_value=0, max_value=150),
        "active": ValidationRule(field_type=FieldType.BOOLEAN, default=True),
    }
)

PRODUCT_SCHEMA = DataSchema(
    name="product",
    description="Product data schema",
    fields={
        "id": ValidationRule(field_type=FieldType.INTEGER, required=True),
        "name": ValidationRule(field_type=FieldType.STRING, required=True, min_length=1, max_length=200),
        "price": ValidationRule(field_type=FieldType.FLOAT, required=True, min_value=0),
        "category": ValidationRule(field_type=FieldType.STRING, required=True),
        "in_stock": ValidationRule(field_type=FieldType.BOOLEAN, default=True),
    }
)

TRANSACTION_SCHEMA = DataSchema(
    name="transaction",
    description="Transaction data schema",
    fields={
        "transaction_id": ValidationRule(field_type=FieldType.STRING, required=True),
        "user_id": ValidationRule(field_type=FieldType.INTEGER, required=True),
        "amount": ValidationRule(field_type=FieldType.FLOAT, required=True, min_value=0),
        "timestamp": ValidationRule(field_type=FieldType.DATE, required=True),
        "status": ValidationRule(field_type=FieldType.STRING, required=True, choices=["pending", "completed", "failed"]),
    }
)