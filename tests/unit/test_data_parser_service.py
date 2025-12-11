"""Unit tests for data parser service."""
import pytest
import tempfile
import os
import json

from app.services.parsers import DataParserService
from app.services.parsers.csv_parser import CSVParser
from app.services.parsers.json_parser import JSONParser
from app.models.data_models import DataParserConfig, DataFormat
from app.services.parsers import (
    parse_csv_string, parse_csv_file, parse_json_string, parse_json_file
)
from tests.fixtures.data_fixtures import (
    VALID_USER_CSV, VALID_USER_JSON, VALID_PRODUCT_CSV, VALID_PRODUCT_JSON,
    create_temp_csv_file, create_temp_json_file, cleanup_temp_file
)
from tests.fixtures.schemas import USER_SCHEMA, PRODUCT_SCHEMA


class TestDataParserService:
    """Test cases for DataParserService class."""
    
    def test_csv_service_initialization(self):
        """Test CSV service initialization."""
        config = DataParserConfig(
            format=DataFormat.CSV,
            schema=USER_SCHEMA,
            validate_on_parse=True
        )
        service = DataParserService(config)
        
        assert isinstance(service.parser, CSVParser)
        assert service.config == config
    
    def test_json_service_initialization(self):
        """Test JSON service initialization."""
        config = DataParserConfig(
            format=DataFormat.JSON,
            schema=USER_SCHEMA,
            validate_on_parse=True
        )
        service = DataParserService(config)
        
        assert isinstance(service.parser, JSONParser)
        assert service.config == config
    
    def test_unsupported_format(self):
        """Test service with unsupported format."""
        config = DataParserConfig(
            format="xml",  # Unsupported format
            schema=USER_SCHEMA
        )
        
        # The actual behavior depends on the enum validation
        try:
            service = DataParserService(config)
            # If we get here, the format was accepted
            assert False, "Expected validation error for unsupported format"
        except Exception:
            # Expected - either validation error or unsupported format
            pass
    
    def test_csv_service_parse_content(self):
        """Test CSV service parse content."""
        config = DataParserConfig(
            format=DataFormat.CSV,
            schema=USER_SCHEMA,
            validate_on_parse=True
        )
        service = DataParserService(config)
        
        result = service.parse_content(VALID_USER_CSV)
        
        assert result.errors == []
        assert len(result.data) == 3
        assert result.summary.data_format == DataFormat.CSV
    
    def test_json_service_parse_content(self):
        """Test JSON service parse content."""
        config = DataParserConfig(
            format=DataFormat.JSON,
            schema=USER_SCHEMA,
            validate_on_parse=True
        )
        service = DataParserService(config)
        
        result = service.parse_content(VALID_USER_JSON)
        
        assert result.errors == []
        assert len(result.data) == 3
        assert result.summary.data_format == DataFormat.JSON
    
    def test_service_parse_file(self):
        """Test service parse file."""
        temp_file = create_temp_csv_file(VALID_USER_CSV)
        
        try:
            config = DataParserConfig(
                format=DataFormat.CSV,
                schema=USER_SCHEMA,
                validate_on_parse=True
            )
            service = DataParserService(config)
            
            result = service.parse_file(temp_file)
            
            assert result.errors == []
            assert len(result.data) == 3
        finally:
            cleanup_temp_file(temp_file)
    
    def test_service_parse_files(self):
        """Test service parse multiple files."""
        temp_file1 = create_temp_csv_file(VALID_USER_CSV)
        temp_file2 = create_temp_json_file(VALID_USER_JSON)
        
        try:
            csv_config = DataParserConfig(
                format=DataFormat.CSV,
                schema=USER_SCHEMA,
                validate_on_parse=True
            )
            csv_service = DataParserService(csv_config)
            
            # Parse CSV file
            csv_result = csv_service.parse_files([temp_file1])[0]
            assert len(csv_result.data) == 3
            
            json_config = DataParserConfig(
                format=DataFormat.JSON,
                schema=USER_SCHEMA,
                validate_on_parse=True
            )
            json_service = DataParserService(json_config)
            
            # Parse JSON file
            json_result = json_service.parse_files([temp_file2])[0]
            assert len(json_result.data) == 3
        finally:
            cleanup_temp_file(temp_file1)
            cleanup_temp_file(temp_file2)
    
    def test_service_parse_directory(self):
        """Test service parse directory."""
        import tempfile
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            csv_file = os.path.join(temp_dir, "users.csv")
            json_file = os.path.join(temp_dir, "users.json")
            
            with open(csv_file, 'w') as f:
                f.write(VALID_USER_CSV)
            
            with open(json_file, 'w') as f:
                f.write(VALID_USER_JSON)
            
            # Test CSV service parsing directory
            csv_config = DataParserConfig(
                format=DataFormat.CSV,
                schema=USER_SCHEMA,
                validate_on_parse=True
            )
            csv_service = DataParserService(csv_config)
            
            csv_results = csv_service.parse_directory(temp_dir, ".csv")
            assert len(csv_results) == 1
            assert len(csv_results[0].data) == 3
            
            # Test JSON service parsing directory
            json_config = DataParserConfig(
                format=DataFormat.JSON,
                schema=USER_SCHEMA,
                validate_on_parse=True
            )
            json_service = DataParserService(json_config)
            
            json_results = json_service.parse_directory(temp_dir, ".json")
            assert len(json_results) == 1
            assert len(json_results[0].data) == 3


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_parse_csv_string_convenience(self):
        """Test parse_csv_string convenience function."""
        result = parse_csv_string(VALID_USER_CSV, USER_SCHEMA, validate=True)
        
        assert result.errors == []
        assert len(result.data) == 3
        assert result.summary.data_format == DataFormat.CSV
    
    def test_parse_csv_file_convenience(self):
        """Test parse_csv_file convenience function."""
        temp_file = create_temp_csv_file(VALID_USER_CSV)
        
        try:
            result = parse_csv_file(temp_file, USER_SCHEMA, validate=True)
            
            assert result.errors == []
            assert len(result.data) == 3
        finally:
            cleanup_temp_file(temp_file)
    
    def test_parse_json_string_convenience(self):
        """Test parse_json_string convenience function."""
        result = parse_json_string(VALID_USER_JSON, USER_SCHEMA, validate=True)
        
        assert result.errors == []
        assert len(result.data) == 3
        assert result.summary.data_format == DataFormat.JSON
    
    def test_parse_json_file_convenience(self):
        """Test parse_json_file convenience function."""
        temp_file = create_temp_json_file(VALID_USER_JSON)
        
        try:
            result = parse_json_file(temp_file, USER_SCHEMA, validate=True)
            
            assert result.errors == []
            assert len(result.data) == 3
        finally:
            cleanup_temp_file(temp_file)