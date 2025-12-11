"""Test fixtures for data parsing."""
import json
import tempfile
import os
from typing import Dict, Any


# Sample CSV data for testing
VALID_USER_CSV = """id,name,email,age,active
1,John Doe,john@example.com,25,true
2,Jane Smith,jane@example.com,30,false
3,Bob Johnson,bob@example.com,45,true"""

INVALID_USER_CSV = """id,name,email,age,active
1,John Doe,john@example.com,25,true
2,,jane@example.com,30,false
3,Bob Johnson,invalid-email,abc,true
4,Alice Brown,alice@example.com,200,true"""

VALID_PRODUCT_CSV = """id,name,price,category,in_stock
1,Laptop,999.99,Electronics,true
2,Mouse,25.50,Accessories,false
3,Keyboard,75.00,Accessories,true"""

INVALID_PRODUCT_CSV = """id,name,price,category,in_stock
1,,999.99,Electronics,true
2,Mouse,-25.50,Accessories,false
3,Keyboard,abc,Accessories,true"""

# Sample JSON data for testing
VALID_USER_JSON = json.dumps([
    {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 25, "active": True},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 30, "active": False},
    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "age": 45, "active": True}
])

INVALID_USER_JSON = json.dumps([
    {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 25, "active": True},
    {"id": 2, "name": "", "email": "jane@example.com", "age": 30, "active": False},
    {"id": 3, "name": "Bob Johnson", "email": "invalid-email", "age": "abc", "active": "yes"},
    {"id": 4, "name": "Alice Brown", "email": "alice@example.com", "age": 200, "active": True}
])

VALID_PRODUCT_JSON = json.dumps([
    {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Mouse", "price": 25.50, "category": "Accessories", "in_stock": False},
    {"id": 3, "name": "Keyboard", "price": 75.00, "category": "Accessories", "in_stock": True}
])

INVALID_PRODUCT_JSON = json.dumps([
    {"id": 1, "name": "", "price": 999.99, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Mouse", "price": -25.50, "category": "Accessories", "in_stock": False},
    {"id": 3, "name": "Keyboard", "price": "abc", "category": "Accessories", "in_stock": "yes"}
])

# JSON with wrapper structure
WRAPPED_USER_JSON = json.dumps({
    "status": "success",
    "data": [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 25, "active": True},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 30, "active": False}
    ],
    "count": 2
})

# Invalid JSON
INVALID_JSON = """{"invalid": json content}"""


def create_temp_csv_file(content: str) -> str:
    """Create a temporary CSV file with given content."""
    fd, path = tempfile.mkstemp(suffix='.csv', text=True)
    try:
        with os.fdopen(fd, 'w') as temp_file:
            temp_file.write(content)
        return path
    except:
        os.close(fd)
        raise


def create_temp_json_file(content: str) -> str:
    """Create a temporary JSON file with given content."""
    fd, path = tempfile.mkstemp(suffix='.json', text=True)
    try:
        with os.fdopen(fd, 'w') as temp_file:
            temp_file.write(content)
        return path
    except:
        os.close(fd)
        raise


def cleanup_temp_file(path: str):
    """Clean up temporary file."""
    try:
        os.unlink(path)
    except OSError:
        pass