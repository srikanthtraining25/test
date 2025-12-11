"""Schema definitions for testing."""
from typing import Dict, Any


# User schema for testing
USER_SCHEMA = {
    "name": "user",
    "description": "User data schema for testing",
    "fields": {
        "id": {
            "field_type": "integer",
            "required": True
        },
        "name": {
            "field_type": "string",
            "required": True,
            "min_length": 1,
            "max_length": 100
        },
        "email": {
            "field_type": "email",
            "required": True
        },
        "age": {
            "field_type": "integer",
            "min_value": 0,
            "max_value": 150
        },
        "active": {
            "field_type": "boolean",
            "default": True
        }
    }
}

# Product schema for testing
PRODUCT_SCHEMA = {
    "name": "product",
    "description": "Product data schema for testing",
    "fields": {
        "id": {
            "field_type": "integer",
            "required": True
        },
        "name": {
            "field_type": "string",
            "required": True,
            "min_length": 1,
            "max_length": 200
        },
        "price": {
            "field_type": "float",
            "required": True,
            "min_value": 0
        },
        "category": {
            "field_type": "string",
            "required": True
        },
        "in_stock": {
            "field_type": "boolean",
            "default": True
        }
    }
}

# Transaction schema for testing
TRANSACTION_SCHEMA = {
    "name": "transaction",
    "description": "Transaction data schema for testing",
    "fields": {
        "transaction_id": {
            "field_type": "string",
            "required": True
        },
        "user_id": {
            "field_type": "integer",
            "required": True
        },
        "amount": {
            "field_type": "float",
            "required": True,
            "min_value": 0
        },
        "timestamp": {
            "field_type": "date",
            "required": True
        },
        "status": {
            "field_type": "string",
            "required": True,
            "choices": ["pending", "completed", "failed"]
        }
    }
}