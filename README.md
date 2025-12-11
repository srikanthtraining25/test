# Data Parsers for CSV and JSON

A comprehensive Python library for parsing CSV and JSON data with schema validation, error collection, and summary statistics.

## Features

- **CSV and JSON parsing** - Support for both single files and multiple file processing
- **Schema validation** - Transform data using predefined or custom schemas
- **Error collection** - Collect and categorize validation and parsing errors
- **Summary statistics** - Track processing metrics including timing and error counts
- **Type conversion** - Automatic conversion of string data to appropriate types
- **Flexible configuration** - Configurable validation rules and error handling
- **Multiple file formats** - Support for various JSON structures and CSV configurations

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### CSV Parsing

```python
from app.services.parsers import parse_csv_string

csv_content = """id,name,email,age,active
1,John Doe,john@example.com,25,true
2,Jane Smith,jane@example.com,30,false"""

user_schema = {
    "name": "user",
    "fields": {
        "id": {"field_type": "integer", "required": True},
        "name": {"field_type": "string", "required": True},
        "email": {"field_type": "email", "required": True},
        "age": {"field_type": "integer", "min_value": 0},
        "active": {"field_type": "boolean", "default": True}
    }
}

result = parse_csv_string(csv_content, user_schema)
print(f"Processed {result.summary.valid_records} valid records")
print(f"Found {result.summary.invalid_records} invalid records")
```

### JSON Parsing

```python
from app.services.parsers import parse_json_string
import json

json_content = json.dumps([
    {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 25},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 30}
])

result = parse_json_string(json_content, user_schema)
print(f"Processing time: {result.summary.processing_time_ms}ms")
```

## Schema Definition

### Field Types

- `string` - Text validation with length constraints
- `integer` - Integer validation with min/max values
- `float` - Float validation with min/max values  
- `boolean` - Boolean conversion from various formats
- `date` - Date validation with common formats
- `email` - Email format validation
- `phone` - Phone number format validation

### Validation Rules

```python
{
    "field_type": "string",        # Required: field type
    "required": False,             # Optional: field is required
    "min_length": 1,               # Optional: minimum length
    "max_length": 100,             # Optional: maximum length
    "min_value": 0,                # Optional: minimum numeric value
    "max_value": 150,              # Optional: maximum numeric value
    "pattern": r"^[A-Z]+$",        # Optional: regex pattern
    "choices": ["A", "B", "C"],    # Optional: allowed values
    "default": True                # Optional: default value
}
```

### Predefined Schemas

The library includes several predefined schemas:

```python
from app.schemas.data_schemas import USER_SCHEMA, PRODUCT_SCHEMA, TRANSACTION_SCHEMA

# User schema - includes id, name, email, age, active
# Product schema - includes id, name, price, category, in_stock  
# Transaction schema - includes transaction_id, user_id, amount, timestamp, status
```

## Advanced Usage

### File Processing

```python
from app.services.parsers import DataParserService
from app.models.data_models import DataParserConfig, DataFormat

config = DataParserConfig(
    format=DataFormat.CSV,
    schema=user_schema,
    validate_on_parse=True,
    max_errors=100,
    encoding="utf-8"
)

service = DataParserService(config)

# Parse single file
result = service.parse_file("data/users.csv")

# Parse multiple files
results = service.parse_files(["data/users1.csv", "data/users2.csv"])

# Parse directory
results = service.parse_directory("data/", ".csv")
```

### Custom Configuration

```python
config = DataParserConfig(
    format=DataFormat.JSON,
    schema=custom_schema,
    validate_on_parse=True,    # Enable validation
    max_errors=50,            # Limit error collection
    encoding="utf-8"          # File encoding
)
```

### Error Handling

```python
result = parse_csv_string(csv_content, schema)

# Check for errors
if result.errors:
    print("Parse errors:", result.errors)

# Check validation errors
for error in result.summary.validation_errors:
    print(f"Row {error.row_number}: {error.field} - {error.message}")
    print(f"  Invalid value: {error.value}")

# Summary statistics
summary = result.summary
print(f"Total records: {summary.total_records}")
print(f"Valid records: {summary.valid_records}")
print(f"Invalid records: {summary.invalid_records}")
print(f"Processing time: {summary.processing_time_ms}ms")
print(f"Data format: {summary.data_format}")
```

## JSON Support

The JSON parser supports various JSON structures:

- **Array of objects**: `[{"id": 1, "name": "John"}, ...]`
- **Object with data field**: `{"data": [{"id": 1, ...}, ...]}`
- **Object with records field**: `{"records": [{"id": 1, ...}, ...]}`
- **Object with items field**: `{"items": [{"id": 1, ...}, ...]}`
- **Single object**: `{"id": 1, "name": "John"}`

## CSV Support

The CSV parser supports:

- **Standard CSV format** with headers
- **Flexible delimiter detection**
- **Encoding specification**
- **Automatic type conversion** (string, integer, float, boolean, date)
- **Required field validation**
- **Length and range constraints**

## Type Conversion

### Boolean Conversion
- `true`, `1`, `yes`, `on` → `True`
- `false`, `0`, `no`, `off` → `False`

### Integer Conversion
- String numbers are converted to integers
- Float numbers without decimal parts are converted to integers
- Invalid conversions raise validation errors

### Float Conversion
- String numbers are converted to floats
- Integers are converted to floats
- Invalid conversions raise validation errors

### Date Validation
Supported formats:
- `YYYY-MM-DD` (ISO format)
- `MM/DD/US` format
- `DD/MM/EU` format
- `YYYY-MM-DDTHH:MM:SS` (ISO datetime)

## Error Types

### Validation Errors
- Missing required fields
- Type conversion failures
- Length constraints violations
- Range constraints violations
- Pattern mismatches
- Invalid choice values

### Parse Errors
- Malformed CSV content
- Invalid JSON format
- File encoding issues
- File access errors

## Performance Considerations

- Processing time is tracked for all operations
- Error collection can be limited with `max_errors` parameter
- Large files are processed efficiently with streaming where possible
- Memory usage is optimized for large datasets

## Testing

The library includes comprehensive tests:

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests  
pytest tests/integration/

# Run all tests
pytest tests/
```

Test coverage includes:
- Valid data parsing
- Invalid data error handling
- Type conversion validation
- File I/O operations
- Error collection accuracy
- Performance tracking
- Schema validation
- Multiple format support

## Example Data

### Sample CSV
```csv
id,name,email,age,active
1,John Doe,john@example.com,25,true
2,Jane Smith,jane@example.com,30,false
3,Bob Johnson,bob@example.com,45,true
```

### Sample JSON
```json
[
  {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 25, "active": true},
  {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 30, "active": false},
  {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "age": 45, "active": true}
]
```

## API Reference

### Main Functions

- `parse_csv_string(content, schema, validate=True)` - Parse CSV from string
- `parse_csv_file(file_path, schema, validate=True)` - Parse CSV from file
- `parse_json_string(content, schema, validate=True)` - Parse JSON from string  
- `parse_json_file(file_path, schema, validate=True)` - Parse JSON from file

### Classes

- `DataParserService` - Unified parser service
- `CSVParser` - CSV-specific parser
- `JSONParser` - JSON-specific parser
- `DataParserConfig` - Parser configuration
- `ParsingResult` - Parsing result container
- `SummaryStats` - Processing statistics
- `ValidationError` - Individual validation error

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.