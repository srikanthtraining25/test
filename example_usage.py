#!/usr/bin/env python3
"""Example script demonstrating data parser functionality."""

import json
import tempfile
import os

from app.services.parsers import (
    DataParserService,
    parse_csv_string,
    parse_json_string,
    parse_csv_file,
    parse_json_file
)
from app.models.data_models import DataParserConfig, DataFormat
from tests.fixtures.schemas import USER_SCHEMA


def demonstrate_csv_parsing():
    """Demonstrate CSV parsing functionality."""
    print("=== CSV Parsing Demo ===")
    
    # Sample CSV data
    csv_data = """id,name,email,age,active
1,John Doe,john@example.com,25,true
2,Jane Smith,jane@example.com,30,false
3,Bob Johnson,bob@example.com,45,true
4,Alice Brown,alice@example.com,,true"""
    
    print("Sample CSV data:")
    print(csv_data)
    print()
    
    # Parse CSV string
    result = parse_csv_string(csv_data, USER_SCHEMA)
    
    print("Parsing results:")
    print(f"Total records: {result.summary.total_records}")
    print(f"Valid records: {result.summary.valid_records}")
    print(f"Invalid records: {result.summary.invalid_records}")
    print(f"Processing time: {result.summary.processing_time_ms:.2f}ms")
    
    if result.summary.validation_errors:
        print("\nValidation errors:")
        for error in result.summary.validation_errors:
            print(f"  Row {error.row_number}, Field '{error.field}': {error.message}")
            print(f"    Invalid value: '{error.value}'")
    
    print(f"\nParsed data:")
    for i, record in enumerate(result.data):
        print(f"  Record {i+1}: {record}")
    
    print()


def demonstrate_json_parsing():
    """Demonstrate JSON parsing functionality."""
    print("=== JSON Parsing Demo ===")
    
    # Sample JSON data
    json_data = [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 25, "active": True},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 30, "active": False},
        {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "age": 45, "active": "yes"}
    ]
    
    json_string = json.dumps(json_data, indent=2)
    print("Sample JSON data:")
    print(json_string)
    print()
    
    # Parse JSON string
    result = parse_json_string(json_string, USER_SCHEMA)
    
    print("Parsing results:")
    print(f"Total records: {result.summary.total_records}")
    print(f"Valid records: {result.summary.valid_records}")
    print(f"Invalid records: {result.summary.invalid_records}")
    print(f"Processing time: {result.summary.processing_time_ms:.2f}ms")
    
    if result.summary.validation_errors:
        print("\nValidation errors:")
        for error in result.summary.validation_errors:
            print(f"  Row {error.row_number}, Field '{error.field}': {error.message}")
            print(f"    Invalid value: '{error.value}'")
    
    print(f"\nParsed data:")
    for i, record in enumerate(result.data):
        print(f"  Record {i+1}: {record}")
    
    print()


def demonstrate_file_parsing():
    """Demonstrate file parsing functionality."""
    print("=== File Parsing Demo ===")
    
    # Create temporary files
    csv_content = """id,name,email,age,active
1,Test User,test@example.com,25,true
2,Another User,another@example.com,30,false"""
    
    json_content = json.dumps([
        {"id": 1, "name": "Test User", "email": "test@example.com", "age": 25},
        {"id": 2, "name": "Another User", "email": "another@example.com", "age": 30}
    ])
    
    # Create temp files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(json_content)
        json_file = f.name
    
    try:
        print(f"Created temporary files:")
        print(f"  CSV: {csv_file}")
        print(f"  JSON: {json_file}")
        print()
        
        # Parse files
        csv_result = parse_csv_file(csv_file, USER_SCHEMA)
        json_result = parse_json_file(json_file, USER_SCHEMA)
        
        print("CSV file parsing:")
        print(f"  Valid records: {csv_result.summary.valid_records}")
        print(f"  Processing time: {csv_result.summary.processing_time_ms:.2f}ms")
        
        print("\nJSON file parsing:")
        print(f"  Valid records: {json_result.summary.valid_records}")
        print(f"  Processing time: {json_result.summary.processing_time_ms:.2f}ms")
        
    finally:
        # Clean up
        os.unlink(csv_file)
        os.unlink(json_file)
        print("\nCleaned up temporary files")
    
    print()


def demonstrate_advanced_parsing():
    """Demonstrate advanced parsing features."""
    print("=== Advanced Parsing Demo ===")
    
    # Invalid data to demonstrate error handling
    invalid_csv = """id,name,email,age,active
1,,invalid-email,abc,true
2,Valid User,valid@example.com,25,false
3,Another Invalid,,30,maybe"""
    
    print("Invalid CSV data (for error handling demo):")
    print(invalid_csv)
    print()
    
    # Parse with validation
    result = parse_csv_string(invalid_csv, USER_SCHEMA, validate=True)
    
    print("Parsing with validation:")
    print(f"Total records: {result.summary.total_records}")
    print(f"Valid records: {result.summary.valid_records}")
    print(f"Invalid records: {result.summary.invalid_records}")
    
    if result.summary.validation_errors:
        print(f"\nFound {len(result.summary.validation_errors)} validation errors:")
        for error in result.summary.validation_errors:
            print(f"  Row {error.row_number}:")
            print(f"    Field: {error.field}")
            print(f"    Message: {error.message}")
            print(f"    Value: '{error.value}'")
    
    print(f"\nValid records extracted:")
    for i, record in enumerate(result.data):
        print(f"  {i+1}. {record}")
    
    print()
    
    # Parse without validation (include all data)
    print("Parsing without validation (all data included):")
    result_no_validation = parse_csv_string(invalid_csv, USER_SCHEMA, validate=False)
    
    print(f"Total records: {result_no_validation.summary.total_records}")
    print(f"Valid records: {result_no_validation.summary.valid_records}")
    print(f"Invalid records: {result_no_validation.summary.invalid_records}")
    print(f"Validation errors: {len(result_no_validation.summary.validation_errors)}")
    
    print(f"\nAll records (including invalid):")
    for i, record in enumerate(result_no_validation.data):
        print(f"  {i+1}. {record}")
    
    print()


def demonstrate_service_usage():
    """Demonstrate using DataParserService directly."""
    print("=== DataParserService Demo ===")
    
    # Create service configuration
    config = DataParserConfig(
        format=DataFormat.CSV,
        schema=USER_SCHEMA,
        validate_on_parse=True,
        max_errors=10,
        encoding="utf-8"
    )
    
    service = DataParserService(config)
    
    csv_data = """id,name,email,age,active
1,Service User,service@example.com,35,true
2,Another Service User,service2@example.com,40,false"""
    
    print("Using DataParserService:")
    result = service.parse_content(csv_data)
    
    print(f"Records processed: {result.summary.valid_records}")
    print(f"Processing time: {result.summary.processing_time_ms:.2f}ms")
    
    for record in result.data:
        print(f"  {record['name']} ({record['email']})")
    
    print()


def demonstrate_wrapped_json():
    """Demonstrate parsing wrapped JSON structures."""
    print("=== Wrapped JSON Demo ===")
    
    # JSON with wrapper structure
    wrapped_json = {
        "status": "success",
        "data": [
            {"id": 1, "name": "Wrapped User 1", "email": "wrap1@example.com", "age": 25},
            {"id": 2, "name": "Wrapped User 2", "email": "wrap2@example.com", "age": 30}
        ],
        "count": 2,
        "timestamp": "2023-12-01T10:00:00Z"
    }
    
    json_string = json.dumps(wrapped_json, indent=2)
    print("Wrapped JSON data:")
    print(json_string)
    print()
    
    result = parse_json_string(json_string, USER_SCHEMA)
    
    print("Parsing results:")
    print(f"Total records: {result.summary.total_records}")
    print(f"Valid records: {result.summary.valid_records}")
    print(f"Data extracted from 'data' field automatically")
    
    print(f"\nExtracted records:")
    for record in result.data:
        print(f"  {record}")
    
    print()


def main():
    """Run all demonstration functions."""
    print("Data Parsers for CSV and JSON - Demo Script")
    print("=" * 50)
    print()
    
    try:
        demonstrate_csv_parsing()
        demonstrate_json_parsing()
        demonstrate_file_parsing()
        demonstrate_advanced_parsing()
        demonstrate_service_usage()
        demonstrate_wrapped_json()
        
        print("=== Demo Complete ===")
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()