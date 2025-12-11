"""JSON parser for data parsing."""
import json
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import re

from app.models.data_models import (
    DataParserConfig, ParsingResult, SummaryStats, ValidationError, DataFormat
)
from app.schemas.data_schemas import DataSchema, FieldType


class JSONParser:
    """Parser for JSON files."""
    
    def __init__(self, config: DataParserConfig):
        """Initialize JSON parser with configuration."""
        self.config = config
        self.schema = DataSchema(**config.schema)
        self.validation_errors: List[ValidationError] = []
        self.parse_errors: List[str] = []
        self.total_records_processed = 0
    
    def parse_string(self, json_content: str) -> ParsingResult:
        """Parse JSON content from string."""
        start_time = time.time()
        
        try:
            json_data = json.loads(json_content)
            return self._parse_json_data(json_data, start_time)
        except json.JSONDecodeError as e:
            self.parse_errors.append(f"Invalid JSON format: {str(e)}")
            return self._create_empty_result(start_time)
        except Exception as e:
            self.parse_errors.append(f"Failed to parse JSON string: {str(e)}")
            return self._create_empty_result(start_time)
    
    def parse_file(self, file_path: str) -> ParsingResult:
        """Parse JSON file."""
        start_time = time.time()
        
        try:
            with open(file_path, 'r', encoding=self.config.encoding) as json_file:
                json_data = json.load(json_file)
                return self._parse_json_data(json_data, start_time)
        except json.JSONDecodeError as e:
            self.parse_errors.append(f"Invalid JSON in file {file_path}: {str(e)}")
            return self._create_empty_result(start_time)
        except Exception as e:
            self.parse_errors.append(f"Failed to parse JSON file {file_path}: {str(e)}")
            return self._create_empty_result(start_time)
    
    def parse_files(self, file_paths: List[str]) -> List[ParsingResult]:
        """Parse multiple JSON files."""
        results = []
        for file_path in file_paths:
            result = self.parse_file(file_path)
            results.append(result)
        return results
    
    def _parse_json_data(self, json_data: Any, start_time: float) -> ParsingResult:
        """Parse JSON data."""
        self.validation_errors = []
        self.parse_errors = []
        self.total_records_processed = 0
        data = []
        
        # Handle different JSON structures
        if isinstance(json_data, list):
            # JSON array of objects
            records = json_data
        elif isinstance(json_data, dict):
            # JSON object - check if it contains an array
            if 'data' in json_data and isinstance(json_data['data'], list):
                records = json_data['data']
            elif 'records' in json_data and isinstance(json_data['records'], list):
                records = json_data['records']
            elif 'items' in json_data and isinstance(json_data['items'], list):
                records = json_data['items']
            else:
                # Single object
                records = [json_data]
        else:
            self.parse_errors.append("JSON must contain an object or array of objects")
            return self._create_empty_result(start_time)
        
        # Process each record
        for row_number, record in enumerate(records, start=1):
            self.total_records_processed += 1
            if not isinstance(record, dict):
                self.parse_errors.append(f"Record at position {row_number} is not an object")
                continue
            
            # Apply schema validation if enabled
            if self.config.validate_on_parse:
                validated_record, record_errors = self._validate_record(record, row_number)
                if validated_record is not None:
                    data.append(validated_record)
                self.validation_errors.extend(record_errors)
            else:
                data.append(record)
            
            # Limit errors if configured
            if len(self.validation_errors) >= self.config.max_errors:
                break
        
        # Create summary
        processing_time = (time.time() - start_time) * 1000
        summary = self._create_summary(data, processing_time)
        
        return ParsingResult(data=data, summary=summary, errors=self.parse_errors)
    
    def _validate_record(self, record: Dict[str, Any], record_number: int) -> tuple[Optional[Dict[str, Any]], List[ValidationError]]:
        """Validate a single record against the schema."""
        validated_data = {}
        errors = []
        
        for field_name, rule in self.schema.fields.items():
            value = record.get(field_name)
            
            # Handle required fields
            if rule.required and (value is None or value == ""):
                errors.append(ValidationError(
                    field=field_name,
                    message="Field is required",
                    value=value,
                    row_number=record_number
                ))
                continue
            
            # Skip validation for missing optional fields
            if value is None:
                if rule.default is not None:
                    validated_data[field_name] = rule.default
                continue
            
            # Type validation and conversion
            try:
                validated_value = self._convert_and_validate_field(value, rule, field_name, record_number)
                validated_data[field_name] = validated_value
            except ValueError as e:
                errors.append(ValidationError(
                    field=field_name,
                    message=str(e),
                    value=value,
                    row_number=record_number
                ))
        
        # Return None if there are any validation errors and validation is strict
        if errors and self.config.validate_on_parse:
            return None, errors
        
        return validated_data, errors
    
    def _convert_and_validate_field(self, value: Any, rule, field_name: str, record_number: int) -> Any:
        """Convert and validate a field value."""
        if rule.field_type == FieldType.STRING:
            return self._validate_string(value, rule, field_name, record_number)
        elif rule.field_type == FieldType.INTEGER:
            return self._validate_integer(value, rule, field_name, record_number)
        elif rule.field_type == FieldType.FLOAT:
            return self._validate_float(value, rule, field_name, record_number)
        elif rule.field_type == FieldType.BOOLEAN:
            return self._validate_boolean(value, rule, field_name, record_number)
        elif rule.field_type == FieldType.DATE:
            return self._validate_date(value, rule, field_name, record_number)
        elif rule.field_type == FieldType.EMAIL:
            return self._validate_email(value, rule, field_name, record_number)
        elif rule.field_type == FieldType.PHONE:
            return self._validate_phone(value, rule, field_name, record_number)
        else:
            return value
    
    def _validate_string(self, value: Any, rule, field_name: str, record_number: int) -> str:
        """Validate string field."""
        if not isinstance(value, str):
            raise ValueError(f"Expected string, got {type(value).__name__}")
        
        str_value = value
        if rule.min_length and len(str_value) < rule.min_length:
            raise ValueError(f"String too short (min: {rule.min_length})")
        if rule.max_length and len(str_value) > rule.max_length:
            raise ValueError(f"String too long (max: {rule.max_length})")
        if rule.pattern and not re.match(rule.pattern, str_value):
            raise ValueError(f"String does not match pattern")
        if rule.choices and str_value not in rule.choices:
            raise ValueError(f"Value not in allowed choices: {rule.choices}")
        return str_value
    
    def _validate_integer(self, value: Any, rule, field_name: str, record_number: int) -> int:
        """Validate integer field."""
        if isinstance(value, str):
            try:
                int_value = int(value)
            except ValueError:
                raise ValueError("Invalid integer value")
        elif isinstance(value, int):
            int_value = value
        elif isinstance(value, float):
            if value.is_integer():
                int_value = int(value)
            else:
                # For JSON, we can be more lenient and truncate
                int_value = int(value)
        else:
            raise ValueError(f"Cannot convert {type(value).__name__} to integer")
        
        if rule.min_value is not None and int_value < rule.min_value:
            raise ValueError(f"Value too small (min: {rule.min_value})")
        if rule.max_value is not None and int_value > rule.max_value:
            raise ValueError(f"Value too large (max: {rule.max_value})")
        return int_value
    
    def _validate_float(self, value: Any, rule, field_name: str, record_number: int) -> float:
        """Validate float field."""
        if isinstance(value, str):
            try:
                float_value = float(value)
            except ValueError:
                raise ValueError("Invalid float value")
        elif isinstance(value, (int, float)):
            float_value = float(value)
        else:
            raise ValueError(f"Cannot convert {type(value).__name__} to float")
        
        if rule.min_value is not None and float_value < rule.min_value:
            raise ValueError(f"Value too small (min: {rule.min_value})")
        if rule.max_value is not None and float_value > rule.max_value:
            raise ValueError(f"Value too large (max: {rule.max_value})")
        return float_value
    
    def _validate_boolean(self, value: Any, rule, field_name: str, record_number: int) -> bool:
        """Validate boolean field."""
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            if value.lower() in ('true', '1', 'yes', 'on'):
                return True
            elif value.lower() in ('false', '0', 'no', 'off'):
                return False
            else:
                raise ValueError("Invalid boolean string value")
        elif isinstance(value, int):
            return bool(value)
        else:
            raise ValueError(f"Cannot convert {type(value).__name__} to boolean")
    
    def _validate_date(self, value: Any, rule, field_name: str, record_number: int) -> str:
        """Validate date field."""
        if not isinstance(value, str):
            raise ValueError(f"Date must be string, got {type(value).__name__}")
        
        # Try common date formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%dT%H:%M:%S']:
            try:
                datetime.strptime(value, fmt)
                return value
            except ValueError:
                continue
        raise ValueError("Invalid date format")
    
    def _validate_email(self, value: Any, rule, field_name: str, record_number: int) -> str:
        """Validate email field."""
        if not isinstance(value, str):
            raise ValueError(f"Email must be string, got {type(value).__name__}")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValueError("Invalid email format")
        return value
    
    def _validate_phone(self, value: Any, rule, field_name: str, record_number: int) -> str:
        """Validate phone field."""
        if not isinstance(value, str):
            raise ValueError(f"Phone must be string, got {type(value).__name__}")
        
        # Basic phone validation - can be enhanced
        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
        if not re.match(phone_pattern.replace(' ', '').replace('-', '').replace('(', '').replace(')', ''), value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
            raise ValueError("Invalid phone format")
        return value
    
    def _create_summary(self, data: List[Dict[str, Any]], processing_time: float) -> SummaryStats:
        """Create summary statistics."""
        # Count total processed records and unique invalid records
        total_records = self.total_records_processed
        valid_records = len(data)
        
        # Count unique records with validation errors
        invalid_record_numbers = set(error.row_number for error in self.validation_errors if error.row_number is not None)
        invalid_records = len(invalid_record_numbers)
        
        return SummaryStats(
            total_records=total_records,
            valid_records=valid_records,
            invalid_records=invalid_records,
            validation_errors=self.validation_errors,
            parse_errors=self.parse_errors,
            processing_time_ms=processing_time,
            data_format=DataFormat.JSON
        )
    
    def _create_empty_result(self, start_time: float) -> ParsingResult:
        """Create empty result with error information."""
        processing_time = (time.time() - start_time) * 1000
        summary = SummaryStats(
            total_records=0,
            valid_records=0,
            invalid_records=0,
            validation_errors=[],
            parse_errors=self.parse_errors,
            processing_time_ms=processing_time,
            data_format=DataFormat.JSON
        )
        return ParsingResult(data=[], summary=summary, errors=self.parse_errors)