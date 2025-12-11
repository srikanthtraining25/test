# FastAPI LDIF Generation Service

A scalable, production-ready FastAPI-based API service for generating LDIF (LDAP Data Interchange Format) output from CSV/JSON data. Includes comprehensive tooling for development, testing, and deployment.

## Features

- ⚡ FastAPI framework with async/await support
- 📤 CSV/JSON file upload and data ingestion
- 🔄 Asynchronous LDIF generation with job management
- 📊 Multiple schema support (user, product, transaction) with extensibility
- 📥 Streaming LDIF file download
- 🔧 CORS middleware for cross-origin requests
- 📝 Comprehensive API documentation (Swagger UI, ReDoc)
- 🧪 Testing setup with pytest and pytest-asyncio
- 📐 Code quality tools (black, flake8, isort, mypy)
- 🐳 Ready for containerization (ASGI entrypoint included)
- ⚙️ Environment-based configuration with pydantic-settings
- 🏥 Health check endpoints for orchestration systems
- 📋 Detailed logging and error handling

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   ├── data_models.py         # Data parsing models
│   │   └── generation_models.py   # LDIF generation models
│   ├── routers/                   # API route handlers
│   │   ├── __init__.py
│   │   ├── health.py              # Health check endpoints
│   │   └── generation.py          # LDIF generation endpoints
│   ├── schemas/                   # Data schemas
│   │   ├── __init__.py
│   │   └── data_schemas.py        # Schema definitions
│   └── services/                  # Business logic layer
│       ├── __init__.py
│       ├── generation_service.py  # LDIF generation service
│       ├── ldif/                  # LDIF generation module
│       │   ├── __init__.py
│       │   ├── models.py          # LDAP entry models
│       │   ├── generator.py       # LDIF generator
│       │   ├── utils.py           # LDIF utilities
│       │   └── validator.py       # LDIF validation
│       └── parsers/               # Data parser module
│           ├── __init__.py
│           ├── data_parser.py     # Unified parser service
│           ├── csv_parser.py      # CSV parser
│           └── json_parser.py     # JSON parser
├── config/
│   ├── __init__.py
│   └── settings.py                # Application configuration
├── tests/                         # Unit and integration tests
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   ├── test_main.py              # Main app tests
│   └── test_generation_api.py    # Generation API tests
├── asgi.py                       # ASGI entrypoint
├── pyproject.toml               # Poetry configuration and dependencies
├── requirements.txt             # pip requirements
├── .flake8                      # flake8 linting configuration
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
├── GENERATION_API.md            # LDIF Generation API documentation
└── Dockerfile                   # Docker configuration
```

## Prerequisites

- Python 3.10 or higher
- pip or Poetry package manager

## Installation

### Using pip

```bash
pip install -r requirements.txt
```

### Using Poetry

```bash
poetry install
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Update `.env` with your settings (optional, defaults are provided)

Environment variables available:
- `APP_NAME`: Application name
- `APP_DESCRIPTION`: Application description
- `APP_VERSION`: Application version
- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)
- `ALLOWED_ORIGINS`: CORS allowed origins (JSON list)

## Running the Application

### Development Server

```bash
# Using uvicorn directly
uvicorn asgi:app --reload --host 0.0.0.0 --port 8000

# Using the ASGI entrypoint
python asgi.py
```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Quick Start: LDIF Generation

### 1. Generate LDIF from JSON Data
```bash
curl -X POST http://localhost:8000/api/v1/generation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 25}
    ],
    "schema_name": "user",
    "base_dn": "dc=example,dc=com"
  }'
```

### 2. Upload CSV File
```bash
curl -X POST http://localhost:8000/api/v1/generation/upload/csv \
  -F "file=@users.csv" \
  -F "schema_name=user" \
  -F "base_dn=dc=example,dc=com"
```

### 3. Check Available Schemas
```bash
curl http://localhost:8000/api/v1/generation/schemas
```

### 4. Create Job and Check Status
```bash
# Create job
JOB_ID=$(curl -s -X POST http://localhost:8000/api/v1/generation/jobs \
  -H "Content-Type: application/json" \
  -d '{"data": [{"id": 1, "name": "Test", "email": "test@example.com"}], "schema_name": "user"}' \
  | jq -r '.job_id')

# Check status
curl http://localhost:8000/api/v1/generation/jobs/$JOB_ID
```

For more examples and detailed API documentation, see [GENERATION_API.md](GENERATION_API.md)

## Testing

### Run all tests
```bash
pytest
```

### Run tests with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_health.py
```

## Code Quality

### Format code with black
```bash
black app/ config/ tests/
```

### Check imports with isort
```bash
isort app/ config/ tests/
```

### Lint with flake8
```bash
flake8 app/ config/ tests/
```

### Type checking with mypy
```bash
mypy app/ config/
```

### Run all checks
```bash
black app/ config/ tests/
isort app/ config/ tests/
flake8 app/ config/ tests/
mypy app/ config/
pytest
```

## API Endpoints

### Health Checks
- `GET /api/v1/health` - Health check status
- `GET /api/v1/ready` - Readiness check for orchestration

### LDIF Generation
- `POST /api/v1/generation/generate` - Generate LDIF synchronously
- `POST /api/v1/generation/jobs` - Create a generation job
- `GET /api/v1/generation/jobs` - List all jobs (with optional status filter)
- `GET /api/v1/generation/jobs/{job_id}` - Get job status
- `POST /api/v1/generation/jobs/{job_id}/process` - Process a pending job
- `GET /api/v1/generation/jobs/{job_id}/result` - Get job result (with optional download)

### File Upload
- `POST /api/v1/generation/upload/csv` - Upload CSV file for LDIF generation
- `POST /api/v1/generation/upload/json` - Upload JSON file for LDIF generation

### Schema Management
- `GET /api/v1/generation/schemas` - List available schemas

### Root
- `GET /` - Welcome message

For detailed API documentation, see [GENERATION_API.md](GENERATION_API.md)

## Future Features

The following infrastructure is prepared for future enhancements:

### Database Integration
- Update `config/settings.py` to add `DATABASE_URL`
- Create database models in `app/models/`
- Create database services in `app/services/`

### Authentication & Authorization
- Add JWT token validation
- Implement role-based access control (RBAC)
- Create auth router in `app/routers/auth.py`

### Request Validation & Error Handling
- Use Pydantic models for request/response validation
- Implement custom exception handlers
- Add comprehensive error logging

### Logging
- Configure structured logging (e.g., with structlog)
- Add request/response logging middleware

### Deployment
- Docker support (add Dockerfile)
- Kubernetes manifests
- Environment-specific configurations

## Adding a New Endpoint

1. Create a new router in `app/routers/`:
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/items")
async def list_items():
    return {"items": []}
```

2. Include the router in `app/main.py`:
```python
from app.routers import items

app.include_router(items.router, prefix="/api/v1", tags=["items"])
```

## Adding a New Service

1. Create a service in `app/services/`:
```python
class ItemService:
    async def get_all_items(self):
        # Business logic here
        return []
```

2. Use the service in routers:
```python
from app.services.items import ItemService

item_service = ItemService()

@router.get("/items")
async def list_items():
    return await item_service.get_all_items()
```

## Contributing

1. Create a feature branch
2. Make changes following the code quality standards
3. Run tests and checks
4. Create a pull request

## License

MIT
