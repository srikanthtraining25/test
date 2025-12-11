"""Integration tests for data parsers."""
import pytest
import tempfile
import os
import json

from app.services.parsers import DataParserService
from app.models.data_models import DataParserConfig, DataFormat
from tests.fixtures.data_fixtures import (
    VALID_USER_CSV, VALID_USER_JSON, VALID_PRODUCT_CSV, VALID_PRODUCT_JSON,
    WRAPPED_USER_JSON, create_temp_csv_file, create_temp_json_file, cleanup_temp_file
)
from tests.fixtures.schemas import USER_SCHEMA, PRODUCT_SCHEMA


class TestIntegrationParsing:
    """Integration tests for data parsing workflow."""
    
    def test_csv_to_json_workflow(self):
        """Test CSV parsing followed by JSON output."""
        # Parse CSV data
        csv_config = DataParserConfig(
            format=DataFormat.CSV,
            schema=USER_SCHEMA,
            validate_on_parse=True
        )
        csv_service = DataParserService(csv_config)
        csv_result = csv_service.parse_content(VALID_USER_CSV)
        
        # Verify CSV parsing worked
        assert csv_result.errors == []
        assert len(csv_result.data) == 3
        
        # Convert to JSON
        json_data = json.dumps(csv_result.data, indent=2)
        json_parsed = json.loads(json_data)
        
        # Verify JSON round-trip
        assert len(json_parsed) == 3
        assert json_parsed[0]["name"] == "John Doe"
        assert json_parsed[1]["email"] == "jane@example.com"
    
    def test_json_to_csv_workflow(self):
        """Test JSON parsing followed by CSV output."""
        # Parse JSON data
        json_config = DataParserConfig(
            format=DataFormat.JSON,
            schema=USER_SCHEMA,
            validate_on_parse=True
        )
        json_service = DataParserService(json_config)
        json_result = json_service.parse_content(VALID_USER_JSON)
        
        # Verify JSON parsing worked
        assert json_result.errors == []
        assert len(json_result.data) == 3
        
        # Convert to CSV manually (for testing purposes)
        import csv
        import io
        
        output = io.StringIO()
        if json_result.data:
            writer = csv.DictWriter(output, fieldnames=json_result.data[0].keys())
            writer.writeheader()
            writer.writerows(json_result.data)
        
        csv_content = output.getvalue()
        lines = csv_content.strip().split('\n')
        
        # Verify CSV structure
        assert len(lines) == 4  # Header + 3 data rows
        assert lines[0] == "id,name,email,age,active"
        assert "John Doe" in csv_content
        assert "jane@example.com" in csv_content
    
    def test_mixed_format_parsing(self):
        """Test parsing both CSV and JSON with same schema."""
        # Parse CSV
        csv_config = DataParserConfig(
            format=DataFormat.CSV,
            schema=USER_SCHEMA,
            validate_on_parse=True
        )
        csv_service = DataParserService(csv_config)
        csv_result = csv_service.parse_content(VALID_USER_CSV)
        
        # Parse JSON
        json_config = DataParserConfig(
            format=DataFormat.JSON,
            schema=USER_SCHEMA,
            validate_on_parse=True
        )
        json_service = DataParserService(json_config)
        json_result = json_service.parse_content(VALID_USER_JSON)
        
        # Both should have same number of records
        assert len(csv_result.data) == len(json_result.data)
        assert csv_result.summary.valid_records == json_result.summary.valid_records
        
        # Verify data structure is similar
        if csv_result.data and json_result.data:
            assert set(csv_result.data[0].keys()) == set(json_result.data[0].keys())
    
    def test_large_dataset_processing(self):
        """Test processing larger datasets."""
        # Generate larger CSV dataset
        large_csv = "id,name,email,age,active\n"
        for i in range(100):
            large_csv += f"{i},User {i},user{i}@example.com,{20 + (i % 50)},true\n"
        
        csv_config = DataParserConfig(
            format=DataFormat.CSV,
            schema=USER_SCHEMA,
            validate_on_parse=True
        )
        csv_service = DataParserService(csv_config)
        result = csv_service.parse_content(large_csv)
        
        # Should process all records without issues
        assert result.summary.total_records == 100
        assert result.summary.valid_records == 100
        assert result.summary.invalid_records == 0
        assert len(result.data) == 100
        
        # Verify some sample records
        assert result.data[0]["name"] == "User 0"
        assert result.data[99]["name"] == "User 99"
        assert result.data[50]["age"] == 20
    
    def test_file_based_processing_workflow(self):
        """Test complete file-based processing workflow."""
        # Create temporary files
        csv_file = create_temp_csv_file(VALID_USER_CSV)
        json_file = create_temp_json_file(VALID_USER_JSON)
        
        try:
            # Process CSV file
            csv_config = DataParserConfig(
                format=DataFormat.CSV,
                schema=USER_SCHEMA,
                validate_on_parse=True
            )
            csv_service = DataParserService(csv_config)
            csv_result = csv_service.parse_file(csv_file)
            
            # Process JSON file
            json_config = DataParserConfig(
                format=DataFormat.JSON,
                schema=USER_SCHEMA,
                validate_on_parse=True
            )
            json_service = DataParserService(json_config)
            json_result = json_service.parse_file(json_file)
            
            # Compare results
            assert csv_result.summary.total_records == json_result.summary.total_records
            assert len(csv_result.data) == len(json_result.data)
            
            # Both should be valid
            assert csv_result.errors == []
            assert json_result.errors == []
            
        finally:
            cleanup_temp_file(csv_file)
            cleanup_temp_file(json_file)
    
    def test_error_handling_integration(self):
        """Test error handling across different formats."""
        invalid_csv = """id,name,email,age,active
1,,invalid-email,abc,true"""
        
        invalid_json = json.dumps([
            {"id": 1, "name": "", "email": "invalid-email", "age": "abc"}
        ])
        
        # Test CSV error handling
        csv_config = DataParserConfig(
            format=DataFormat.CSV,
            schema=USER_SCHEMA,
            validate_on_parse=True
        )
        csv_service = DataParserService(csv_config)
        csv_result = csv_service.parse_content(invalid_csv)
        
        # Test JSON error handling
        json_config = DataParserConfig(
            format=DataFormat.JSON,
            schema=USER_SCHEMA,
            validate_on_parse=True
        )
        json_service = DataParserService(json_config)
        json_result = json_service.parse_content(invalid_json)
        
        # Both should have validation errors
        assert len(csv_result.summary.validation_errors) > 0
        assert len(json_result.summary.validation_errors) > 0
        
        # Both should have invalid records
        assert csv_result.summary.invalid_records > 0
        assert json_result.summary.invalid_records > 0
        
        # Neither should have parse errors
        assert len(csv_result.errors) == 0
        assert len(json_result.errors) == 0
    
    def test_performance_comparison(self):
        """Test performance comparison between formats."""
        # Create dataset for performance testing
        test_data = []
        for i in range(50):
            test_data.append({
                "id": i,
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "age": 20 + (i % 50),
                "active": i % 2 == 0
            })
        
        json_content = json.dumps(test_data)
        
        # Convert to CSV
        import csv
        import io
        output = io.StringIO()
        if test_data:
            writer = csv.DictWriter(output, fieldnames=test_data[0].keys())
            writer.writeheader()
            writer.writerows(test_data)
        csv_content = output.getvalue()
        
        # Parse both formats
        config = DataParserConfig(
            format=DataFormat.CSV,
            schema=USER_SCHEMA,
            validate_on_parse=True
        )
        csv_service = DataParserService(config)
        csv_result = csv_service.parse_content(csv_content)
        
        config.format = DataFormat.JSON
        json_service = DataParserService(config)
        json_result = json_service.parse_content(json_content)
        
        # Both should process successfully
        assert csv_result.summary.total_records == 50
        assert json_result.summary.total_records == 50
        
        # Performance should be reasonable for both
        assert csv_result.summary.processing_time_ms < 5000
        assert json_result.summary.processing_time_ms < 5000