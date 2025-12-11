# LDIF Generation API Documentation

## Overview

The LDIF Generation API provides FastAPI endpoints for uploading CSV/JSON payloads, selecting schemas, triggering LDIF generation, and returning LDIF output. The API includes comprehensive job management, error handling, and logging capabilities.

## Features

- **Multiple Input Formats**: Support for CSV and JSON data uploads
- **Flexible Schema Selection**: Use predefined schemas (user, product, transaction) or custom schemas
- **Job Management**: Asynchronous job processing with status tracking
- **Multiple Output Formats**: Generate LDIF or JSON output
- **File Streaming**: Download generated LDIF files directly
- **Comprehensive Logging**: Detailed logging of all operations
- **Error Handling**: Detailed error messages and validation
- **Batch Processing**: Process multiple records in a single request

## API Endpoints

### Job Management

#### Create Generation Job
```
POST /api/v1/generation/jobs
```

Create a new LDIF generation job.

**Request Body:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "age": 25
    }
  ],
  "schema_name": "user",
  "base_dn": "dc=example,dc=com",
  "object_classes": ["inetOrgPerson"],
  "format": "ldif"
}
```

**Response (200 OK):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00",
  "input_records": 1,
  "output_records": 0,
  "progress_percentage": 0
}
```

#### Get Job Status
```
GET /api/v1/generation/jobs/{job_id}
```

Retrieve the current status of a generation job.

**Response (200 OK):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "created_at": "2024-01-01T00:00:00",
  "started_at": "2024-01-01T00:00:01",
  "completed_at": "2024-01-01T00:00:02",
  "input_records": 1,
  "output_records": 1,
  "progress_percentage": 100
}
```

**Status Values:**
- `pending` - Job created but not yet processed
- `processing` - Job currently being processed
- `completed` - Job completed successfully
- `failed` - Job failed with error
- `cancelled` - Job was cancelled

#### List Jobs
```
GET /api/v1/generation/jobs?status=completed
```

List all generation jobs, optionally filtered by status.

**Query Parameters:**
- `status` (optional) - Filter by job status (pending, processing, completed, failed, cancelled)

**Response (200 OK):**
```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "created_at": "2024-01-01T00:00:00",
      "input_records": 1,
      "output_records": 1
    }
  ]
}
```

### Generation

#### Generate LDIF (Synchronous)
```
POST /api/v1/generation/generate
```

Generate LDIF output synchronously from provided data.

**Request Body:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "age": 25
    }
  ],
  "schema_name": "user",
  "base_dn": "dc=example,dc=com",
  "format": "ldif"
}
```

**Response (200 OK):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "message": "Generation completed successfully",
  "output": "dn: uid=1,dc=example,dc=com\nobjectClass: inetOrgPerson\ncn: John Doe\nmail: john@example.com\n",
  "record_count": 1
}
```

#### Process Job
```
POST /api/v1/generation/jobs/{job_id}/process
```

Process a pending generation job.

**Response (200 OK):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "message": "Generation completed successfully",
  "output": "...",
  "record_count": 1
}
```

#### Get Job Result
```
GET /api/v1/generation/jobs/{job_id}/result?download=false
```

Retrieve the result of a completed generation job.

**Query Parameters:**
- `download` (optional, default: false) - If true, returns file as downloadable attachment

**Response (200 OK - as JSON):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "output": "dn: uid=1,dc=example,dc=com\n..."
}
```

**Response (200 OK - as file):**
```
Content-Type: application/octet-stream
Content-Disposition: attachment; filename=ldif_550e8400-e29b-41d4-a716-446655440000.ldif

dn: uid=1,dc=example,dc=com
objectClass: inetOrgPerson
cn: John Doe
...
```

### File Upload

#### Upload CSV
```
POST /api/v1/generation/upload/csv
```

Upload a CSV file for LDIF generation.

**Form Data:**
- `file` (required) - CSV file to upload
- `schema_name` (optional, default: "user") - Schema to use for validation
- `base_dn` (optional, default: "") - Base DN for LDIF entries

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/generation/upload/csv" \
  -F "file=@users.csv" \
  -F "schema_name=user" \
  -F "base_dn=dc=example,dc=com"
```

**Response (200 OK):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00",
  "input_records": 10
}
```

#### Upload JSON
```
POST /api/v1/generation/upload/json
```

Upload a JSON file for LDIF generation.

**Form Data:**
- `file` (required) - JSON file to upload
- `schema_name` (optional, default: "user") - Schema to use for validation
- `base_dn` (optional, default: "") - Base DN for LDIF entries

**Supported JSON Structures:**
- Array of objects: `[{...}, {...}]`
- Object with data field: `{"data": [{...}]}`
- Object with records field: `{"records": [{...}]}`
- Object with items field: `{"items": [{...}]}`

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/generation/upload/json" \
  -F "file=@users.json" \
  -F "schema_name=user"
```

**Response (200 OK):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00",
  "input_records": 5
}
```

### Schemas

#### List Available Schemas
```
GET /api/v1/generation/schemas
```

List all available schemas for generation.

**Response (200 OK):**
```json
{
  "schemas": ["user", "product", "transaction"],
  "details": {
    "user": {
      "name": "user",
      "description": "User data schema",
      "fields": {
        "id": {
          "field_type": "integer",
          "required": true
        },
        "name": {
          "field_type": "string",
          "required": true,
          "min_length": 1,
          "max_length": 100
        },
        "email": {
          "field_type": "email",
          "required": true
        },
        "age": {
          "field_type": "integer",
          "min_value": 0,
          "max_value": 150
        },
        "active": {
          "field_type": "boolean",
          "default": true
        }
      },
      "version": "1.0.0"
    }
  }
}
```

## Schema Definitions

### User Schema
Used for converting user data to LDAP entries.

**Fields:**
- `id` (integer, required) - User ID
- `name` (string, required) - Full name
- `email` (email, required) - Email address
- `age` (integer, optional) - Age (0-150)
- `active` (boolean, optional) - Active status

**Example:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "age": 25,
  "active": true
}
```

### Product Schema
Used for converting product data.

**Fields:**
- `id` (integer, required) - Product ID
- `name` (string, required) - Product name
- `price` (float, required) - Price (>= 0)
- `category` (string, required) - Category
- `in_stock` (boolean, optional) - Stock status

### Transaction Schema
Used for converting transaction data.

**Fields:**
- `transaction_id` (string, required) - Transaction ID
- `user_id` (integer, required) - User ID
- `amount` (float, required) - Amount (>= 0)
- `timestamp` (date, required) - Transaction timestamp
- `status` (string, required) - Status (pending, completed, failed)

## LDIF Output Format

Generated LDIF follows RFC 2849 standard.

**Example Output:**
```
dn: uid=1,dc=example,dc=com
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
uid: 1
cn: John Doe
sn: Doe
mail: john@example.com
age: 25

dn: uid=2,dc=example,dc=com
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
uid: 2
cn: Jane Smith
sn: Smith
mail: jane@example.com
age: 30
```

## Error Handling

The API returns appropriate HTTP status codes and error details.

### Error Responses

**400 Bad Request** - Invalid input data
```json
{
  "detail": "Data cannot be empty"
}
```

**404 Not Found** - Job not found
```json
{
  "detail": "Job not found"
}
```

**500 Internal Server Error** - Server error
```json
{
  "detail": "Internal server error"
}
```

## Usage Examples

### Python Client Example

```python
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/v1/generation"

# Example 1: Generate LDIF directly
def generate_ldif():
    data = {
        "data": [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "age": 25
            }
        ],
        "schema_name": "user",
        "base_dn": "dc=example,dc=com",
        "format": "ldif"
    }
    
    response = requests.post(f"{BASE_URL}/generate", json=data)
    result = response.json()
    
    print(f"Status: {result['status']}")
    print(f"Output:\n{result['output']}")

# Example 2: Upload CSV file
def upload_csv():
    with open("users.csv", "rb") as f:
        response = requests.post(
            f"{BASE_URL}/upload/csv",
            files={"file": f},
            data={
                "schema_name": "user",
                "base_dn": "dc=example,dc=com"
            }
        )
    
    job = response.json()
    job_id = job["job_id"]
    print(f"Job created: {job_id}")
    return job_id

# Example 3: Check job status
def check_job_status(job_id):
    response = requests.get(f"{BASE_URL}/jobs/{job_id}")
    job = response.json()
    
    print(f"Job ID: {job['job_id']}")
    print(f"Status: {job['status']}")
    print(f"Progress: {job['progress_percentage']}%")
    
    return job

# Example 4: Get job result
def get_job_result(job_id):
    response = requests.get(f"{BASE_URL}/jobs/{job_id}/result")
    result = response.json()
    
    print(f"LDIF Output:\n{result['output']}")

# Example 5: List schemas
def list_schemas():
    response = requests.get(f"{BASE_URL}/schemas")
    schemas = response.json()
    
    print(f"Available schemas: {schemas['schemas']}")

# Run examples
if __name__ == "__main__":
    print("=== List Schemas ===")
    list_schemas()
    
    print("\n=== Generate LDIF ===")
    generate_ldif()
    
    print("\n=== Upload CSV ===")
    job_id = upload_csv()
    
    print("\n=== Check Job Status ===")
    check_job_status(job_id)
    
    print("\n=== Get Job Result ===")
    # Note: Job must be processed first
    # get_job_result(job_id)
```

### cURL Examples

```bash
# List available schemas
curl http://localhost:8000/api/v1/generation/schemas

# Generate LDIF directly
curl -X POST http://localhost:8000/api/v1/generation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 25}
    ],
    "schema_name": "user",
    "base_dn": "dc=example,dc=com"
  }'

# Upload CSV file
curl -X POST http://localhost:8000/api/v1/generation/upload/csv \
  -F "file=@users.csv" \
  -F "schema_name=user" \
  -F "base_dn=dc=example,dc=com"

# Upload JSON file
curl -X POST http://localhost:8000/api/v1/generation/upload/json \
  -F "file=@users.json" \
  -F "schema_name=user"

# Get job status
curl http://localhost:8000/api/v1/generation/jobs/{job_id}

# Get job result
curl http://localhost:8000/api/v1/generation/jobs/{job_id}/result

# Download result as file
curl -O http://localhost:8000/api/v1/generation/jobs/{job_id}/result?download=true

# List all jobs
curl http://localhost:8000/api/v1/generation/jobs

# List jobs by status
curl "http://localhost:8000/api/v1/generation/jobs?status=completed"
```

## Running Tests

### Unit Tests
```bash
pytest tests/unit/ -v
```

### Integration Tests
```bash
pytest tests/test_generation_api.py -v
```

### All Tests
```bash
pytest tests/ -v
```

### With Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

## Logging

The API includes comprehensive logging:

```python
import logging

logger = logging.getLogger(__name__)

# Logs are written with the following format:
# YYYY-MM-DD HH:MM:SS - module_name - LEVEL - message
# Example: 2024-01-01 12:00:00 - app.routers.generation - INFO - Creating generation job with 5 records
```

Log levels:
- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages
- `WARNING` - Warning messages for potentially problematic situations
- `ERROR` - Error messages for issues that need attention

## Performance Considerations

1. **Batch Processing**: Upload multiple records at once for better performance
2. **File Size**: Large files should be chunked and processed in batches
3. **Memory**: The API stores results in memory; for large datasets, implement database storage
4. **Async Processing**: Jobs are processed asynchronously to avoid blocking

## Deployment

### Docker
```bash
docker build -t ldif-generation-api .
docker run -p 8000:8000 ldif-generation-api
```

### Requirements
```bash
pip install -r requirements.txt
```

### Running the Server
```bash
uvicorn asgi:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Troubleshooting

### Job Not Found
- Ensure the job_id is correct
- Check that the job hasn't expired (jobs stored in memory)

### Invalid Schema
- Use available schemas: user, product, transaction
- Check schema field names in error message

### CSV/JSON Parsing Error
- Verify file format is valid
- Check for encoding issues (UTF-8 expected)
- Ensure required fields are present

### Large File Timeout
- Split large files into smaller batches
- Implement client-side retries with exponential backoff

## Future Enhancements

- Database persistence for job storage
- Scheduled job cleanup
- Bulk operations API
- Custom schema creation API
- LDIF validation and import
- Search functionality for completed jobs
- Webhook notifications for job completion
