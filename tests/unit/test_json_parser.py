"""Unit tests for JSON parser."""
import pytest
import tempfile
import os
import json

from app.services.parsers.json_parser import JSONParser
from app.models.data_models import DataParserConfig, DataFormat
from tests.fixtures.data_fixtures import (
    VALID_USER_JSON, INVALID_USER_JSON, VALID_PRODUCT_JSON, INVALID_PRODUCT_JSON,
    WRAPPED_USER_JSON, INVALID_JSON,
    create_temp_json_file, cleanup_temp_file
)
from tests.fixtures.schemas import USER_SCHEMA, PRODUCT_SCHEMA, TRANSACTION_SCHEMA


class TestJSONParser:
    """Test cases for JSONParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.user_config = DataParserConfig(
            format=DataFormat.JSON,
            schema=USER_SCHEMA,
            validate_on_parse=True
        )
        self.product_config = DataParserConfig(
            format=DataFormat.JSON,
            schema=PRODUCT_SCHEMA,
            validate_on_parse=True
        )
    
    def test_parse_valid_user_json_string(self):
        """Test parsing valid user JSON from string."""
        parser = JSONParser(self.user_config)
        result = parser.parse_string(VALID_USER_JSON)
        
        assert result.errors == []
        assert len(result.data) == 3
        assert result.summary.total_records == 3
        assert result.summary.valid_records == 3
        assert result.summary.invalid_records == 0
        assert result.summary.data_format == DataFormat.JSON
        
        # Check first record
        first_user = result.data[0]
        assert first_user["id"] == 1
        assert first_user["name"] == "John Doe"
        assert first_user["email"] == "john@example.com"
        assert first_user["age"] == 25
        assert first_user["active"] is True
    
    def test_parse_invalid_user_json_string(self):
        """Test parsing invalid user JSON from string."""
        parser = JSONParser(self.user_config)
        result = parser.parse_string(INVALID_USER_JSON)
        
        assert len(result.data) == 1  # Only first record is valid
        assert result.summary.total_records == 4
        assert result.summary.valid_records == 1
        assert result.summary.invalid_records == 3
        assert len(result.summary.validation_errors) == 3
        assert len(result.errors) == 0  # No parse errors, only validation errors
    
    def test_parse_wrapped_json(self):
        """Test parsing JSON with wrapper structure."""
        parser = JSONParser(self.user_config)
        result = parser.parse_string(WRAPPED_USER_JSON)
        
        assert result.errors == []
        assert len(result.data) == 2  # Should extract array from 'data' field
        assert result.summary.total_records == 2
        assert result.summary.valid_records == 2
        assert result.summary.invalid_records == 0
    
    def test_parse_invalid_json_string(self):
        """Test parsing invalid JSON string."""
        parser = JSONParser(self.user_config)
        result = parser.parse_string(INVALID_JSON)
        
        assert len(result.errors) > 0
        assert "Invalid JSON format" in result.errors[0]
        assert len(result.data) == 0
        assert result.summary.total_records == 0
    
    def test_parse_json_file(self):
        """Test parsing JSON file."""
        temp_file = create_temp_json_file(VALID_USER_JSON)
        
        try:
            parser = JSONParser(self.user_config)
            result = parser.parse_file(temp_file)
            
            assert result.errors == []
            assert len(result.data) == 3
            assert result.summary.total_records == 3
            assert result.summary.valid_records == 3
        finally:
            cleanup_temp_file(temp_file)
    
    def test_parse_multiple_json_files(self):
        """Test parsing multiple JSON files."""
        temp_file1 = create_temp_json_file(VALID_USER_JSON)
        temp_file2 = create_temp_json_file(VALID_PRODUCT_JSON)
        
        try:
            parser = JSONParser(self.user_config)
            results = parser.parse_files([temp_file1, temp_file2])
            
            assert len(results) == 2
            assert results[0].errors == []
            assert len(results[0].data) == 3
            assert results[1].errors == []
            assert len(results[1].data) == 3
        finally:
            cleanup_temp_file(temp_file1)
            cleanup_temp_file(temp_file2)
    
    def test_json_validation_errors(self):
        """Test JSON validation error collection."""
        parser = JSONParser(self.user_config)
        result = parser.parse_string(INVALID_USER_JSON)
        
        # Check validation errors
        validation_errors = result.summary.validation_errors
        assert len(validation_errors) == 2
        
        # Find errors by field
        name_errors = [e for e in validation_errors if e.field == "name"]
        email_errors = [e for e in validation_errors if e.field == "email"]
        age_errors = [e for e in validation_errors if e.field == "age"]
        
        assert len(name_errors) == 1  # Empty name
        assert name_errors[0].message == "Field is required"
        assert name_errors[0].value == ""
        assert name_errors[0].row_number == 2
        
        assert len(email_errors) == 1  # Invalid email
        assert "Invalid email format" in email_errors[0].message
        assert email_errors[0].value == "invalid-email"
        
        assert len(age_errors) == 1  # Non-integer age
        assert "Cannot convert string to integer" in age_errors[0].message
        assert age_errors[0].value == "abc"
    
    def test_json_without_validation(self):
        """Test JSON parsing without validation."""
        config = DataParserConfig(
            format=DataFormat.JSON,
            schema=USER_SCHEMA,
            validate_on_parse=False
        )
        parser = JSONParser(config)
        result = parser.parse_string(INVALID_USER_JSON)
        
        # Should include all data without validation
        assert len(result.data) == 4
        assert result.summary.total_records == 4
        assert result.summary.valid_records == 4
        assert result.summary.invalid_records == 0
        assert len(result.summary.validation_errors) == 0
    
    def test_json_different_structures(self):
        """Test parsing JSON with different structures."""
        parser = JSONParser(self.user_config)
        
        # Test with array
        result1 = parser.parse_string(VALID_USER_JSON)
        assert len(result1.data) == 3
        
        # Test with object containing data field
        result2 = parser.parse_string(WRAPPED_USER_JSON)
        assert len(result2.data) == 2
        
        # Test with single object
        single_user_json = json.dumps({"id": 1, "name": "John Doe", "email": "john@example.com", "age": 25})
        result3 = parser.parse_string(single_user_json)
        assert len(result3.data) == 1
        
        # Test with empty array
        empty_array_json = json.dumps([])
        result4 = parser.parse_string(empty_array_json)
        assert len(result4.data) == 0
    
    def test_json_type_conversions(self):
        """Test JSON type conversions."""
        parser = JSONParser(self.user_config)
        
        # Test with mixed types
        mixed_json = json.dumps([
            {"id": "1", "name": "User 1", "email": "user1@example.com", "age": "25", "active": "true"},
            {"id": 2.0, "name": "User 2", "email": "user2@example.com", "age": 30.5, "active": False},
            {"id": 3, "name": "User 3", "email": "user3@example.com", "age": 35, "active": 1}
        ])
        
        result = parser.parse_string(mixed_json)
        
        assert len(result.data) == 3
        assert result.data[0]["id"] == 1  # String "1" converted to int
        assert result.data[0]["age"] == 25  # String "25" converted to int
        assert result.data[0]["active"] is True  # String "true" converted to bool
        assert result.data[1]["id"] == 2  # Float 2.0 converted to int
        assert result.data[1]["age"] == 30  # Float 30.5 converted to int (truncated)
        assert result.data[1]["active"] is False  # False stays False
        assert result.data[2]["active"] is True  # Int 1 converted to bool
    
    def test_json_field_type_validation(self):
        """Test different field type validations in JSON."""
        config = DataParserConfig(
            format=DataFormat.JSON,
            schema=TRANSACTION_SCHEMA,
            validate_on_parse=True
        )
        parser = JSONParser(config)
        
        transaction_json = json.dumps([
            {
                "transaction_id": "TX001",
                "user_id": 123,
                "amount": 99.99,
                "timestamp": "2023-01-01",
                "status": "completed"
            },
            {
                "transaction_id": "TX002",
                "user_id": "456",  # String instead of int
                "amount": -50.00,  # Negative amount
                "timestamp": "invalid-date",
                "status": "invalid_status"
            }
        ])
        
        result = parser.parse_string(transaction_json)
        
        # First record should be valid
        assert len(result.data) == 1
        assert result.data[0]["transaction_id"] == "TX001"
        assert result.data[0]["user_id"] == 456  # String "456" converted to int
        assert result.data[0]["amount"] == 99.99
        
        # Second record should have validation errors
        validation_errors = result.summary.validation_errors
        assert len(validation_errors) >= 3
        
        amount_errors = [e for e in validation_errors if e.field == "amount"]
        timestamp_errors = [e for e in validation_errors if e.field == "timestamp"]
        status_errors = [e for e in validation_errors if e.field == "status"]
        
        assert len(amount_errors) > 0  # Negative amount
        assert len(timestamp_errors) > 0  # Invalid date
        assert len(status_errors) > 0  # Invalid status
    
    def test_json_email_validation(self):
        """Test email validation in JSON."""
        parser = JSONParser(self.user_config)
        
        email_test_json = json.dumps([
            {"id": 1, "name": "User 1", "email": "valid@example.com"},
            {"id": 2, "name": "User 2", "email": "invalid-email"},
            {"id": 3, "name": "User 3", "email": "user@domain"},
            {"id": 4, "name": "User 4", "email": "@domain.com"}
        ])
        
        result = parser.parse_string(email_test_json)
        
        # Only first record should be valid
        assert len(result.data) == 1
        assert result.data[0]["email"] == "valid@example.com"
        
        # Should have 3 validation errors
        validation_errors = result.summary.validation_errors
        assert len(validation_errors) == 3
        
        email_errors = [e for e in validation_errors if e.field == "email"]
        assert len(email_errors) == 3
    
    def test_json_processing_time_tracking(self):
        """Test that processing time is tracked correctly."""
        parser = JSONParser(self.user_config)
        result = parser.parse_string(VALID_USER_JSON)
        
        assert result.summary.processing_time_ms > 0
        assert result.summary.processing_time_ms < 10000  # Should be fast