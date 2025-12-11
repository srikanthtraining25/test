"""Unit tests for CSV parser."""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from app.services.parsers.csv_parser import CSVParser
from app.models.data_models import DataParserConfig, DataFormat
from tests.fixtures.data_fixtures import (
    VALID_USER_CSV, INVALID_USER_CSV, VALID_PRODUCT_CSV, INVALID_PRODUCT_CSV,
    create_temp_csv_file, cleanup_temp_file
)
from tests.fixtures.schemas import USER_SCHEMA, PRODUCT_SCHEMA, TRANSACTION_SCHEMA


class TestCSVParser:
    """Test cases for CSVParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.user_config = DataParserConfig(
            format=DataFormat.CSV,
            schema=USER_SCHEMA,
            validate_on_parse=True
        )
        self.product_config = DataParserConfig(
            format=DataFormat.CSV,
            schema=PRODUCT_SCHEMA,
            validate_on_parse=True
        )
    
    def test_parse_valid_user_csv_string(self):
        """Test parsing valid user CSV from string."""
        parser = CSVParser(self.user_config)
        result = parser.parse_string(VALID_USER_CSV)
        
        assert result.errors == []
        assert len(result.data) == 3
        assert result.summary.total_records == 3
        assert result.summary.valid_records == 3
        assert result.summary.invalid_records == 0
        assert result.summary.data_format == DataFormat.CSV
        
        # Check first record
        first_user = result.data[0]
        assert first_user["id"] == 1
        assert first_user["name"] == "John Doe"
        assert first_user["email"] == "john@example.com"
        assert first_user["age"] == 25
        assert first_user["active"] is True
    
    def test_parse_invalid_user_csv_string(self):
        """Test parsing invalid user CSV from string."""
        parser = CSVParser(self.user_config)
        result = parser.parse_string(INVALID_USER_CSV)
        
        assert len(result.data) == 1  # Only first record is valid
        assert result.summary.total_records == 4
        assert result.summary.valid_records == 1
        assert result.summary.invalid_records == 3
        assert len(result.summary.validation_errors) == 4  # Row 2: 1 error, Row 3: 2 errors, Row 4: 1 error
        assert len(result.errors) == 0  # No parse errors, only validation errors
    
    def test_parse_valid_product_csv_string(self):
        """Test parsing valid product CSV from string."""
        parser = CSVParser(self.product_config)
        result = parser.parse_string(VALID_PRODUCT_CSV)
        
        assert result.errors == []
        assert len(result.data) == 3
        assert result.summary.total_records == 3
        assert result.summary.valid_records == 3
        assert result.summary.invalid_records == 0
        
        # Check first record
        first_product = result.data[0]
        assert first_product["id"] == 1
        assert first_product["name"] == "Laptop"
        assert first_product["price"] == 999.99
        assert first_product["category"] == "Electronics"
        assert first_product["in_stock"] is True
    
    def test_parse_invalid_product_csv_string(self):
        """Test parsing invalid product CSV from string."""
        parser = CSVParser(self.product_config)
        result = parser.parse_string(INVALID_PRODUCT_CSV)
        
        assert len(result.data) == 1  # Only last valid record
        assert result.summary.total_records == 3
        assert result.summary.valid_records == 1
        assert result.summary.invalid_records == 2
        assert len(result.summary.validation_errors) == 2
    
    def test_parse_csv_file(self):
        """Test parsing CSV file."""
        temp_file = create_temp_csv_file(VALID_USER_CSV)
        
        try:
            parser = CSVParser(self.user_config)
            result = parser.parse_file(temp_file)
            
            assert result.errors == []
            assert len(result.data) == 3
            assert result.summary.total_records == 3
            assert result.summary.valid_records == 3
        finally:
            cleanup_temp_file(temp_file)
    
    def test_parse_multiple_csv_files(self):
        """Test parsing multiple CSV files."""
        temp_file1 = create_temp_csv_file(VALID_USER_CSV)
        temp_file2 = create_temp_csv_file(VALID_PRODUCT_CSV)
        
        try:
            parser = CSVParser(self.user_config)
            results = parser.parse_files([temp_file1, temp_file2])
            
            assert len(results) == 2
            assert results[0].errors == []
            assert len(results[0].data) == 3
            assert results[1].errors == []
            assert len(results[1].data) == 3
        finally:
            cleanup_temp_file(temp_file1)
            cleanup_temp_file(temp_file2)
    
    def test_csv_validation_errors(self):
        """Test CSV validation error collection."""
        parser = CSVParser(self.user_config)
        result = parser.parse_string(INVALID_USER_CSV)
        
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
        assert "Invalid integer value" in age_errors[0].message
        assert age_errors[0].value == "abc"
    
    def test_csv_without_validation(self):
        """Test CSV parsing without validation."""
        config = DataParserConfig(
            format=DataFormat.CSV,
            schema=USER_SCHEMA,
            validate_on_parse=False
        )
        parser = CSVParser(config)
        result = parser.parse_string(INVALID_USER_CSV)
        
        # Should include all data without validation
        assert len(result.data) == 4
        assert result.summary.total_records == 4
        assert result.summary.valid_records == 4
        assert result.summary.invalid_records == 0
        assert len(result.summary.validation_errors) == 0
    
    def test_csv_with_encoding_error(self):
        """Test CSV parsing with encoding error."""
        parser = CSVParser(self.user_config)
        
        # Test with invalid CSV content
        invalid_csv = "id,name,email\n1,\x00\x01invalid"
        result = parser.parse_string(invalid_csv)
        
        assert len(result.errors) > 0
        assert "Failed to parse CSV string" in result.errors[0]
    
    def test_csv_field_type_validation(self):
        """Test different field type validations."""
        config = DataParserConfig(
            format=DataFormat.CSV,
            schema=TRANSACTION_SCHEMA,
            validate_on_parse=True
        )
        parser = CSVParser(config)
        
        transaction_csv = """transaction_id,user_id,amount,timestamp,status
TX001,123,99.99,2023-01-01,completed
TX002,456,-50.00,2023-01-02,invalid_status"""
        
        result = parser.parse_string(transaction_csv)
        
        # First record should be valid
        assert len(result.data) == 1
        assert result.data[0]["transaction_id"] == "TX001"
        assert result.data[0]["user_id"] == 123
        assert result.data[0]["amount"] == 99.99
        
        # Second record should have validation errors
        validation_errors = result.summary.validation_errors
        assert len(validation_errors) >= 1
        
        amount_errors = [e for e in validation_errors if e.field == "amount"]
        status_errors = [e for e in validation_errors if e.field == "status"]
        
        assert len(amount_errors) > 0  # Negative amount
        assert len(status_errors) > 0  # Invalid status
    
    def test_csv_boolean_conversion(self):
        """Test boolean field conversion."""
        parser = CSVParser(self.user_config)
        
        boolean_test_csv = """id,name,email,age,active
1,Test User,test@example.com,25,True
2,Test User2,test2@example.com,30,FALSE
3,Test User3,test3@example.com,35,1
4,Test User4,test4@example.com,40,0"""
        
        result = parser.parse_string(boolean_test_csv)
        
        assert len(result.data) == 4
        assert result.data[0]["active"] is True
        assert result.data[1]["active"] is False
        assert result.data[2]["active"] is True
        assert result.data[3]["active"] is False
    
    def test_csv_processing_time_tracking(self):
        """Test that processing time is tracked correctly."""
        parser = CSVParser(self.user_config)
        result = parser.parse_string(VALID_USER_CSV)
        
        assert result.summary.processing_time_ms > 0
        assert result.summary.processing_time_ms < 10000  # Should be fast