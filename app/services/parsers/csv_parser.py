"""CSV data parser."""
import csv
import io
import time
from typing import Dict, List, Any, Optional
from app.models.data_models import (
    DataFormat,
    ValidationError,
    SummaryStats,
    ParsingResult,
    DataParserConfig,
)


def _convert_value(value: str, field_type: str) -> tuple[Any, Optional[str]]:
    """Convert a value to the appropriate type."""
    if not value and value != "0":
        return None, None

    try:
        if field_type == "integer":
            return int(value), None
        elif field_type == "float":
            return float(value), None
        elif field_type == "boolean":
            return value.lower() in ("true", "1", "yes", "on"), None
        elif field_type == "date":
            return value, None
        elif field_type == "email":
            if "@" in value and "." in value.split("@")[1]:
                return value, None
            return None, f"Invalid email format: {value}"
        elif field_type == "phone":
            return value, None
        else:
            return value, None
    except (ValueError, TypeError) as e:
        return None, f"Type conversion error: {str(e)}"


def parse_csv_string(content: str, schema: Dict[str, Any]) -> ParsingResult:
    """
    Parse CSV content from a string.
    
    Args:
        content: CSV content as string
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
        # Parse CSV
        reader = csv.DictReader(io.StringIO(content))
        if not reader.fieldnames:
            parse_errors.append("No headers found in CSV")
            return ParsingResult(
                data=[],
                summary=SummaryStats(
                    total_records=0,
                    valid_records=0,
                    invalid_records=0,
                    validation_errors=[],
                    parse_errors=parse_errors,
                    processing_time_ms=(time.time() - start_time) * 1000,
                    data_format=DataFormat.CSV,
                ),
                errors=errors,
            )

        fields = schema.get("fields", {})
        row_number = 1

        for row in reader:
            record = {}
            row_errors = []

            for field_name, field_def in fields.items():
                value = row.get(field_name, "")
                field_type = field_def.get("field_type", "string")
                required = field_def.get("required", False)

                if not value:
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

    except Exception as e:
        parse_errors.append(f"CSV parsing error: {str(e)}")

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
            data_format=DataFormat.CSV,
        ),
        errors=errors,
    )


async def parse_csv_file(filepath: str, schema: Dict[str, Any]) -> ParsingResult:
    """
    Parse CSV content from a file.
    
    Args:
        filepath: Path to CSV file
        schema: Schema definition dictionary
        
    Returns:
        ParsingResult with parsed data and statistics
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return parse_csv_string(content, schema)
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
                data_format=DataFormat.CSV,
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
                data_format=DataFormat.CSV,
            ),
            errors=[str(e)],
        )
