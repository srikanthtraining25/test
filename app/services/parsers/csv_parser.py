"""CSV parser for data parsing."""
import csv
import io
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import re

from app.models.data_models import (
    DataParserConfig, ParsingResult, SummaryStats, ValidationError, DataFormat
)
from app.schemas.data_schemas import DataSchema, FieldType


class CSVParser:
    """Parser for CSV files."""
    
    def __init__(self, config: DataParserConfig):
        """Initialize CSV parser with configuration."""
        self.config = config
        self.schema = DataSchema(**config.schema)
        self.validation_errors: List[ValidationError] = []
        self.parse_errors: List[str] = []
        self.total_rows_processed = 0
    
    def parse_string(self, csv_content: str) -> ParsingResult:
        """Parse CSV content from string."""
        start_time = time.time()
        
        try:
            # Use StringIO to treat string as file
            csv_file = io.StringIO(csv_content)
            return self._parse_csv_file(csv_file, start_time)
        except Exception as e:
            self.parse_errors.append(f"Failed to parse CSV string: {str(e)}")
            return self._create_empty_result(start_time)
    
    def parse_file(self, file_path: str) -> ParsingResult:
        """Parse CSV file."""
        start_time = time.time()
        
        try:
            with open(file_path, 'r', encoding=self.config.encoding) as csv_file:
                return self._parse_csv_file(csv_file, start_time)
        except Exception as e:
            self.parse_errors.append(f"Failed to parse CSV file {file_path}: {str(e)}")
            return self._create_empty_result(start_time)
    
    def parse_files(self, file_paths: List[str]) -> List[ParsingResult]:
        """Parse multiple CSV files."""
        results = []
        for file_path in file_paths:
            result = self.parse_file(file_path)
            results.append(result)
        return results
    
    def _parse_csv_file(self, csv_file, start_time: float) -> ParsingResult:
        """Parse CSV file object."""
        self.validation_errors = []
        self.parse_errors = []
        self.total_rows_processed = 0
        data = []
        
        try:
            reader = csv.DictReader(csv_file)
            
            for row_number, row in enumerate(reader, start=1):
                # Apply schema validation if enabled
                if self.config.validate_on_parse:
                    validated_row, row_errors = self._validate_row(row, row_number)
                    if validated_row is not None:
                        data.append(validated_row)
                    self.validation_errors.extend(row_errors)
                else:
                    data.append(dict(row))
                
                self.total_rows_processed += 1
                
                # Limit errors if configured
                if len(self.validation_errors) >= self.config.max_errors:
                    break
            
        except Exception as e:
            self.parse_errors.append(f"CSV parsing error at row {row_number}: {str(e)}")
        
        # Create summary
        processing_time = (time.time() - start_time) * 1000
        summary = self._create_summary(data, processing_time)
        
        return ParsingResult(data=data, summary=summary, errors=self.parse_errors)
    
    def _validate_row(self, row: Dict[str, str], row_number: int) -> tuple[Optional[Dict[str, Any]], List[ValidationError]]:
        """Validate a single row against the schema."""
        validated_data = {}
        errors = []
        
        for field_name, rule in self.schema.fields.items():
            value = row.get(field_name)
            
            # Handle required fields
            if rule.required and (value is None or value == ""):
                errors.append(ValidationError(
                    field=field_name,
                    message="Field is required",
                    value=value,
                    row_number=row_number
                ))
                continue
            
            # Skip validation for missing optional fields
            if value is None or value == "":
                if rule.default is not None:
                    validated_data[field_name] = rule.default
                continue
            
            # Type conversion and validation
            try:
                validated_value = self._convert_and_validate_field(value, rule, field_name, row_number)
                validated_data[field_name] = validated_value
            except ValueError as e:
                errors.append(ValidationError(
                    field=field_name,
                    message=str(e),
                    value=value,
                    row_number=row_number
                ))
        
        # Return None if there are any validation errors and validation is strict
        if errors and self.config.validate_on_parse:
            return None, errors
        
        return validated_data, errors
    
    def _convert_and_validate_field(self, value: str, rule, field_name: str, row_number: int) -> Any:
        """Convert and validate a field value."""
        if rule.field_type == FieldType.STRING:
            return self._validate_string(value, rule, field_name, row_number)
        elif rule.field_type == FieldType.INTEGER:
            return self._validate_integer(value, rule, field_name, row_number)
        elif rule.field_type == FieldType.FLOAT:
            return self._validate_float(value, rule, field_name, row_number)
        elif rule.field_type == FieldType.BOOLEAN:
            return self._validate_boolean(value, rule, field_name, row_number)
        elif rule.field_type == FieldType.DATE:
            return self._validate_date(value, rule, field_name, row_number)
        elif rule.field_type == FieldType.EMAIL:
            return self._validate_email(value, rule, field_name, row_number)
        elif rule.field_type == FieldType.PHONE:
            return self._validate_phone(value, rule, field_name, row_number)
        else:
            return value
    
    def _validate_string(self, value: str, rule, field_name: str, row_number: int) -> str:
        """Validate string field."""
        if rule.min_length and len(value) < rule.min_length:
            raise ValueError(f"String too short (min: {rule.min_length})")
        if rule.max_length and len(value) > rule.max_length:
            raise ValueError(f"String too long (max: {rule.max_length})")
        if rule.pattern and not re.match(rule.pattern, value):
            raise ValueError(f"String does not match pattern")
        if rule.choices and value not in rule.choices:
            raise ValueError(f"Value not in allowed choices: {rule.choices}")
        return value
    
    def _validate_integer(self, value: str, rule, field_name: str, row_number: int) -> int:
        """Validate integer field."""
        try:
            int_value = int(value)
        except ValueError:
            raise ValueError("Invalid integer value")
        
        if rule.min_value is not None and int_value < rule.min_value:
            raise ValueError(f"Value too small (min: {rule.min_value})")
        if rule.max_value is not None and int_value > rule.max_value:
            raise ValueError(f"Value too large (max: {rule.max_value})")
        return int_value
    
    def _validate_float(self, value: str, rule, field_name: str, row_number: int) -> float:
        """Validate float field."""
        try:
            float_value = float(value)
        except ValueError:
            raise ValueError("Invalid float value")
        
        if rule.min_value is not None and float_value < rule.min_value:
            raise ValueError(f"Value too small (min: {rule.min_value})")
        if rule.max_value is not None and float_value > rule.max_value:
            raise ValueError(f"Value too large (max: {rule.max_value})")
        return float_value
    
    def _validate_boolean(self, value: str, rule, field_name: str, row_number: int) -> bool:
        """Validate boolean field."""
        if value.lower() in ('true', '1', 'yes', 'on'):
            return True
        elif value.lower() in ('false', '0', 'no', 'off'):
            return False
        else:
            raise ValueError("Invalid boolean value")
    
    def _validate_date(self, value: str, rule, field_name: str, row_number: int) -> str:
        """Validate date field."""
        try:
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    datetime.strptime(value, fmt)
                    return value
                except ValueError:
                    continue
            raise ValueError("Invalid date format")
        except ValueError:
            raise ValueError("Invalid date value")
    
    def _validate_email(self, value: str, rule, field_name: str, row_number: int) -> str:
        """Validate email field."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValueError("Invalid email format")
        return value
    
    def _validate_phone(self, value: str, rule, field_name: str, row_number: int) -> str:
        """Validate phone field."""
        # Basic phone validation - can be enhanced
        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
        if not re.match(phone_pattern.replace(' ', '').replace('-', '').replace('(', '').replace(')', ''), value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
            raise ValueError("Invalid phone format")
        return value
    
    def _create_summary(self, data: List[Dict[str, Any]], processing_time: float) -> SummaryStats:
        """Create summary statistics."""
        # Count total processed rows and unique invalid rows
        total_records = self.total_rows_processed
        valid_records = len(data)
        
        # Count unique rows with validation errors
        invalid_row_numbers = set(error.row_number for error in self.validation_errors if error.row_number is not None)
        invalid_records = len(invalid_row_numbers)
        
        return SummaryStats(
            total_records=total_records,
            valid_records=valid_records,
            invalid_records=invalid_records,
            validation_errors=self.validation_errors,
            parse_errors=self.parse_errors,
            processing_time_ms=processing_time,
            data_format=DataFormat.CSV
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
            data_format=DataFormat.CSV
        )
        return ParsingResult(data=[], summary=summary, errors=self.parse_errors)