"""Unit tests for data models and schemas."""
import pytest
from datetime import datetime

from app.models.data_models import (
    DataFormat, ValidationError, SummaryStats, ParsingResult, DataParserConfig
)
from app.schemas.data_schemas import (
    FieldType, ValidationRule, DataSchema,
    USER_SCHEMA, PRODUCT_SCHEMA, TRANSACTION_SCHEMA
)


class TestDataModels:
    """Test cases for data models."""
    
    def test_data_format_enum(self):
        """Test DataFormat enum."""
        assert DataFormat.CSV == "csv"
        assert DataFormat.JSON == "json"
        assert len(list(DataFormat)) == 2
    
    def test_validation_error_model(self):
        """Test ValidationError model."""
        error = ValidationError(
            field="email",
            message="Invalid email format",
            value="invalid-email",
            row_number=5
        )
        
        assert error.field == "email"
        assert error.message == "Invalid email format"
        assert error.value == "invalid-email"
        assert error.row_number == 5
        
        # Test with None row_number
        error2 = ValidationError(
            field="name",
            message="Required field",
            value=None
        )
        assert error2.row_number is None
    
    def test_summary_stats_model(self):
        """Test SummaryStats model."""
        validation_errors = [
            ValidationError(field="email", message="Invalid", value="bad", row_number=1)
        ]
        parse_errors = ["File not found"]
        
        stats = SummaryStats(
            total_records=100,
            valid_records=95,
            invalid_records=5,
            validation_errors=validation_errors,
            parse_errors=parse_errors,
            processing_time_ms=123.45,
            data_format=DataFormat.CSV
        )
        
        assert stats.total_records == 100
        assert stats.valid_records == 95
        assert stats.invalid_records == 5
        assert len(stats.validation_errors) == 1
        assert len(stats.parse_errors) == 1
        assert stats.processing_time_ms == 123.45
        assert stats.data_format == DataFormat.CSV
    
    def test_parsing_result_model(self):
        """Test ParsingResult model."""
        data = [{"id": 1, "name": "John"}]
        validation_errors = [
            ValidationError(field="email", message="Invalid", value="bad", row_number=1)
        ]
        
        summary = SummaryStats(
            total_records=1,
            valid_records=0,
            invalid_records=1,
            validation_errors=validation_errors,
            parse_errors=[],
            processing_time_ms=50.0,
            data_format=DataFormat.CSV
        )
        
        result = ParsingResult(
            data=data,
            summary=summary,
            errors=["Parse error"]
        )
        
        assert len(result.data) == 1
        assert result.summary.total_records == 1
        assert len(result.errors) == 1
    
    def test_data_parser_config_model(self):
        """Test DataParserConfig model."""
        config = DataParserConfig(
            format=DataFormat.CSV,
            schema={"fields": {}},
            validate_on_parse=True,
            max_errors=50,
            encoding="utf-8"
        )
        
        assert config.format == DataFormat.CSV
        assert config.schema == {"fields": {}}
        assert config.validate_on_parse is True
        assert config.max_errors == 50
        assert config.encoding == "utf-8"
        
        # Test defaults
        config2 = DataParserConfig(
            format=DataFormat.JSON,
            schema={"fields": {}}
        )
        
        assert config2.validate_on_parse is True
        assert config2.max_errors == 100
        assert config2.encoding == "utf-8"


class TestDataSchemas:
    """Test cases for data schemas."""
    
    def test_field_type_enum(self):
        """Test FieldType enum."""
        assert FieldType.STRING == "string"
        assert FieldType.INTEGER == "integer"
        assert FieldType.FLOAT == "float"
        assert FieldType.BOOLEAN == "boolean"
        assert FieldType.DATE == "date"
        assert FieldType.EMAIL == "email"
        assert FieldType.PHONE == "phone"
        assert len(list(FieldType)) == 7
    
    def test_validation_rule_model(self):
        """Test ValidationRule model."""
        rule = ValidationRule(
            field_type=FieldType.STRING,
            required=True,
            min_length=1,
            max_length=100,
            choices=["A", "B", "C"]
        )
        
        assert rule.field_type == FieldType.STRING
        assert rule.required is True
        assert rule.min_length == 1
        assert rule.max_length == 100
        assert rule.choices == ["A", "B", "C"]
        assert rule.default is None
        
        # Test with defaults
        rule2 = ValidationRule(field_type=FieldType.INTEGER)
        assert rule2.required is False
        assert rule2.min_length is None
        assert rule2.max_value is None
        assert rule2.default is None
    
    def test_data_schema_model(self):
        """Test DataSchema model."""
        fields = {
            "id": ValidationRule(field_type=FieldType.INTEGER, required=True),
            "name": ValidationRule(field_type=FieldType.STRING, required=True)
        }
        
        schema = DataSchema(
            name="test_schema",
            description="A test schema",
            fields=fields,
            version="2.0.0"
        )
        
        assert schema.name == "test_schema"
        assert schema.description == "A test schema"
        assert schema.version == "2.0.0"
        assert len(schema.fields) == 2
        assert "id" in schema.fields
        assert "name" in schema.fields
    
    def test_data_schema_validation(self):
        """Test DataSchema validation."""
        # Should raise error for empty fields
        with pytest.raises(ValueError, match="Schema must have at least one field"):
            DataSchema(name="empty", fields={})
        
        # Should work with valid fields
        fields = {
            "field1": ValidationRule(field_type=FieldType.STRING)
        }
        schema = DataSchema(name="valid", fields=fields)
        assert schema.name == "valid"
    
    def test_predefined_user_schema(self):
        """Test predefined USER_SCHEMA."""
        assert USER_SCHEMA.name == "user"
        assert "id" in USER_SCHEMA.fields
        assert "name" in USER_SCHEMA.fields
        assert "email" in USER_SCHEMA.fields
        assert "age" in USER_SCHEMA.fields
        assert "active" in USER_SCHEMA.fields
        
        # Check field types
        assert USER_SCHEMA.fields["id"].field_type == FieldType.INTEGER
        assert USER_SCHEMA.fields["name"].field_type == FieldType.STRING
        assert USER_SCHEMA.fields["email"].field_type == FieldType.EMAIL
        assert USER_SCHEMA.fields["age"].field_type == FieldType.INTEGER
        assert USER_SCHEMA.fields["active"].field_type == FieldType.BOOLEAN
        
        # Check required fields
        assert USER_SCHEMA.fields["id"].required is True
        assert USER_SCHEMA.fields["name"].required is True
        assert USER_SCHEMA.fields["email"].required is True
        assert USER_SCHEMA.fields["age"].required is False
        assert USER_SCHEMA.fields["active"].required is False
    
    def test_predefined_product_schema(self):
        """Test predefined PRODUCT_SCHEMA."""
        assert PRODUCT_SCHEMA.name == "product"
        assert "id" in PRODUCT_SCHEMA.fields
        assert "name" in PRODUCT_SCHEMA.fields
        assert "price" in PRODUCT_SCHEMA.fields
        assert "category" in PRODUCT_SCHEMA.fields
        assert "in_stock" in PRODUCT_SCHEMA.fields
        
        # Check field types
        assert PRODUCT_SCHEMA.fields["id"].field_type == FieldType.INTEGER
        assert PRODUCT_SCHEMA.fields["name"].field_type == FieldType.STRING
        assert PRODUCT_SCHEMA.fields["price"].field_type == FieldType.FLOAT
        assert PRODUCT_SCHEMA.fields["category"].field_type == FieldType.STRING
        assert PRODUCT_SCHEMA.fields["in_stock"].field_type == FieldType.BOOLEAN
        
        # Check constraints
        assert PRODUCT_SCHEMA.fields["price"].min_value == 0
        assert PRODUCT_SCHEMA.fields["in_stock"].default is True
    
    def test_predefined_transaction_schema(self):
        """Test predefined TRANSACTION_SCHEMA."""
        assert TRANSACTION_SCHEMA.name == "transaction"
        assert "transaction_id" in TRANSACTION_SCHEMA.fields
        assert "user_id" in TRANSACTION_SCHEMA.fields
        assert "amount" in TRANSACTION_SCHEMA.fields
        assert "timestamp" in TRANSACTION_SCHEMA.fields
        assert "status" in TRANSACTION_SCHEMA.fields
        
        # Check field types
        assert TRANSACTION_SCHEMA.fields["transaction_id"].field_type == FieldType.STRING
        assert TRANSACTION_SCHEMA.fields["user_id"].field_type == FieldType.INTEGER
        assert TRANSACTION_SCHEMA.fields["amount"].field_type == FieldType.FLOAT
        assert TRANSACTION_SCHEMA.fields["timestamp"].field_type == FieldType.DATE
        assert TRANSACTION_SCHEMA.fields["status"].field_type == FieldType.STRING
        
        # Check choices constraint
        status_rule = TRANSACTION_SCHEMA.fields["status"]
        assert status_rule.choices == ["pending", "completed", "failed"]
        
        # Check amount constraint
        amount_rule = TRANSACTION_SCHEMA.fields["amount"]
        assert amount_rule.min_value == 0