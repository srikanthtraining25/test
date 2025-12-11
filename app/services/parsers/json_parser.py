"""JSON data parser."""
import json
import time
from typing import Dict, List, Any, Optional
from app.models.data_models import (
    DataFormat,
    ValidationError,
    SummaryStats,
    ParsingResult,
    DataParserConfig,
)


def _extract_records(data: Any) -> List[Dict[str, Any]]:
    """Extract records from various JSON structures."""
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Try common field names
        for key in ["data", "records", "items"]:
            if key in data:
                items = data[key]
                if isinstance(items, list):
                    return items
        # Single object
        return [data]
    return []


def _convert_value(value: Any, field_type: str) -> tuple[Any, Optional[str]]:
    """Convert a value to the appropriate type."""
    if value is None:
        return None, None

    try:
        if field_type == "integer":
            return int(value), None
        elif field_type == "float":
            return float(value), None
        elif field_type == "boolean":
            if isinstance(value, bool):
                return value, None
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on"), None
            return bool(value), None
        elif field_type == "date":
            return str(value), None
        elif field_type == "email":
            value_str = str(value)
            if "@" in value_str and "." in value_str.split("@")[1]:
                return value_str, None
            return None, f"Invalid email format: {value}"
        elif field_type == "phone":
            return str(value), None
        else:
            return value, None
    except (ValueError, TypeError, AttributeError) as e:
        return None, f"Type conversion error: {str(e)}"


def parse_json_string(content: str, schema: Dict[str, Any]) -> ParsingResult:
    """
    Parse JSON content from a string.
    
    Args:
        content: JSON content as string
        schema: Schema definition dictionary
        
    Returns:
        ParsingResult with parsed data and statistics
    """
    start_time = time.time()
    data = []
    errors = []
    validation_errors = []
    parse_errors = []

    try:
        # Parse JSON
        parsed_json = json.loads(content)
        records = _extract_records(parsed_json)

        fields = schema.get("fields", {})
        row_number = 1

        for record_data in records:
            if not isinstance(record_data, dict):
                parse_errors.append(f"Invalid record type at row {row_number}: expected dict")
                row_number += 1
                continue

            record = {}
            row_errors = []

            for field_name, field_def in fields.items():
                value = record_data.get(field_name)
                field_type = field_def.get("field_type", "string")
                required = field_def.get("required", False)

                if value is None:
                    if required:
                        row_errors.append(
                            ValidationError(
                                field=field_name,
                                message="Required field is missing",
                                value=value,
                                row_number=row_number,
                            )
                        )
                    elif "default" in field_def:
                        record[field_name] = field_def["default"]
                else:
                    converted, error = _convert_value(value, field_type)
                    if error:
                        row_errors.append(
                            ValidationError(
                                field=field_name,
                                message=error,
                                value=value,
                                row_number=row_number,
                            )
                        )
                    else:
                        record[field_name] = converted

            if row_errors:
                validation_errors.extend(row_errors)
            else:
                data.append(record)

            row_number += 1

    except json.JSONDecodeError as e:
        parse_errors.append(f"Invalid JSON: {str(e)}")
    except Exception as e:
        parse_errors.append(f"JSON parsing error: {str(e)}")

    processing_time = (time.time() - start_time) * 1000
    total = len(data) + len([e for e in validation_errors if e.row_number])
    valid = len(data)
    invalid = total - valid

    return ParsingResult(
        data=data,
        summary=SummaryStats(
            total_records=total,
            valid_records=valid,
            invalid_records=invalid,
            validation_errors=validation_errors,
            parse_errors=parse_errors,
            processing_time_ms=processing_time,
            data_format=DataFormat.JSON,
        ),
        errors=errors,
    )


async def parse_json_file(filepath: str, schema: Dict[str, Any]) -> ParsingResult:
    """
    Parse JSON content from a file.
    
    Args:
        filepath: Path to JSON file
        schema: Schema definition dictionary
        
    Returns:
        ParsingResult with parsed data and statistics
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return parse_json_string(content, schema)
    except FileNotFoundError:
        return ParsingResult(
            data=[],
            summary=SummaryStats(
                total_records=0,
                valid_records=0,
                invalid_records=0,
                validation_errors=[],
                parse_errors=[f"File not found: {filepath}"],
                processing_time_ms=0,
                data_format=DataFormat.JSON,
            ),
            errors=[f"File not found: {filepath}"],
        )
    except Exception as e:
        return ParsingResult(
            data=[],
            summary=SummaryStats(
                total_records=0,
                valid_records=0,
                invalid_records=0,
                validation_errors=[],
                parse_errors=[str(e)],
                processing_time_ms=0,
                data_format=DataFormat.JSON,
            ),
            errors=[str(e)],
        )
