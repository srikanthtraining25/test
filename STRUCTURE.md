# Project Structure

This document describes the structure of the FastAPI Service project.

## Directory Layout

```
fastapi-service/
│
├── app/                          # Application code
│   ├── __init__.py
│   ├── main.py                   # FastAPI app initialization, middleware setup
│   ├── routers/                  # API route handlers (modular endpoints)
│   │   ├── __init__.py
│   │   └── health.py             # Health check endpoints
│   └── services/                 # Business logic layer
│       └── __init__.py
│
├── config/                        # Configuration and settings
│   ├── __init__.py
│   └── settings.py               # Pydantic BaseSettings for app config
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py              # pytest fixtures and configuration
│   └── test_main.py             # Tests for main app and routers
│
├── venv/                          # Virtual environment (git-ignored)
│
├── asgi.py                        # ASGI entrypoint (production server entry)
├── Dockerfile                     # Multi-stage Docker build
├── docker-compose.yml             # Local development environment
├── .dockerignore                  # Docker build ignore rules
├── .env.example                   # Environment variables template
├── .flake8                        # Flake8 linting configuration
├── .gitignore                     # Git ignore rules
├── .mypy_cache/                   # Type checker cache (git-ignored)
├── .pytest_cache/                 # Test cache (git-ignored)
│
├── Makefile                       # Development task automation
├── README.md                      # Project documentation
├── CONTRIBUTING.md                # Contribution guidelines
├── STRUCTURE.md                   # This file
│
├── requirements.txt               # pip dependencies
├── pyproject.toml                 # Poetry config and tool settings
│
└── .git/                          # Git repository
```

## File Purposes

### Application Files

#### `app/main.py`
The main FastAPI application setup:
- Creates the FastAPI app instance
- Configures CORS middleware for cross-origin requests
- Registers API routers
- Defines root endpoint

#### `app/routers/health.py`
Health check endpoints:
- `GET /api/v1/health` - Simple health status
- `GET /api/v1/ready` - Readiness check for orchestration systems

#### `config/settings.py`
Application configuration using Pydantic Settings:
- Loads from environment variables or `.env` file
- Provides type-safe configuration management
- Defines app metadata (name, version, description)
- Configures CORS allowed origins

### Testing Files

#### `tests/conftest.py`
pytest configuration and fixtures:
- Provides `client` fixture for API testing
- Uses TestClient for synchronous API testing

#### `tests/test_main.py`
Tests for main application:
- Root endpoint tests
- Health check endpoint tests
- HTTP status code verification
- JSON response validation

### Configuration Files

#### `pyproject.toml`
Poetry package configuration:
- Project metadata (name, version, description)
- Dependencies (FastAPI, Uvicorn, Pydantic, etc.)
- Development dependencies (pytest, black, mypy, etc.)
- Tool configurations:
  - Black (code formatter)
  - isort (import sorter)
  - mypy (type checker)
  - pytest (test runner)

#### `requirements.txt`
pip requirements file (alternative to poetry):
- Lists all direct dependencies
- Can be installed with: `pip install -r requirements.txt`

#### `.flake8`
Flake8 linting configuration:
- Maximum line length: 100 characters
- Excluded directories and files
- Per-file ignores (e.g., F401 in `__init__.py`)

#### `.env.example`
Template for environment variables:
- Copy to `.env` to override defaults
- Contains app settings and future feature placeholders
- Git-ignored in production

### Docker Files

#### `Dockerfile`
Multi-stage Docker build:
- Stage 1: Build Python wheels with Poetry
- Stage 2: Runtime image with application
- Includes health check configuration
- Exposes port 8000

#### `docker-compose.yml`
Local development Docker setup:
- API service with live reload
- Volume mounts for development
- Environment variable configuration
- Health check settings
- Commented PostgreSQL database setup (for future use)

### Development Files

#### `Makefile`
Common development tasks:
- `make install` - Install dependencies
- `make dev` - Run development server
- `make test` - Run tests
- `make quality` - Run all quality checks
- `make docker-build` - Build Docker image
- `make docker-up/down` - Manage Docker containers

#### `asgi.py`
ASGI application entrypoint:
- Imports the FastAPI app from `app.main`
- Can be run with: `uvicorn asgi:app`
- Entry point for production ASGI servers
- Can also be run directly: `python asgi.py`

#### `.gitignore`
Git ignore patterns:
- Python cache files (`__pycache__`, `.pyc`)
- Virtual environments (`venv/`, `.venv`)
- IDE files (`.vscode/`, `.idea/`)
- Testing artifacts (`.pytest_cache/`, `.coverage`)
- Environment files (`.env`, `.env.local`)

#### `.dockerignore`
Docker build ignore patterns:
- Prevents unnecessary files from being copied into container
- Reduces Docker image size

### Documentation Files

#### `README.md`
Comprehensive project documentation:
- Features overview
- Installation instructions
- Configuration guide
- Running the application
- API documentation links
- Testing instructions
- Code quality tools usage
- Future features planning
- Contributing guidelines

#### `CONTRIBUTING.md`
Development contribution guidelines:
- Development setup
- Code style requirements
- Testing guidelines
- Review checklist
- Feature addition walkthrough
- Project conventions
- Troubleshooting

#### `STRUCTURE.md`
This file - project structure documentation

## API Route Organization

### Current Routes

```
GET  /                  - Welcome message
GET  /docs              - Swagger UI (auto-generated)
GET  /redoc             - ReDoc (auto-generated)
GET  /openapi.json      - OpenAPI schema (auto-generated)
GET  /api/v1/health     - Health check
GET  /api/v1/ready      - Readiness check
```

### Adding New Routes

1. Create new router in `app/routers/new_feature.py`
2. Include in `app/main.py`:
   ```python
   from app.routers import new_feature
   app.include_router(new_feature.router, prefix="/api/v1", tags=["new_feature"])
   ```
3. Routes will be automatically available and documented

## Environment Variables

See `.env.example` for all available settings:
- `APP_NAME` - Application name (default: "FastAPI Service")
- `APP_DESCRIPTION` - Application description
- `APP_VERSION` - Application version
- `DEBUG` - Enable debug mode (default: false)
- `LOG_LEVEL` - Logging level (default: INFO)
- `ALLOWED_ORIGINS` - CORS allowed origins (JSON list)

## Development Workflow

1. **Activate environment**: `source venv/bin/activate`
2. **Make changes**: Edit code in `app/` directory
3. **Test**: `make test` or `pytest`
4. **Format**: `make format` (black + isort)
5. **Lint**: `make lint` (flake8)
6. **Type check**: `mypy app/ config/`
7. **Run dev server**: `make dev`
8. **Commit**: `git commit -am "descriptive message"`

## Future Expansion Points

### Routers
- `app/routers/users.py` - User management
- `app/routers/items.py` - Item management
- `app/routers/auth.py` - Authentication

### Services
- `app/services/user_service.py` - User business logic
- `app/services/item_service.py` - Item business logic
- `app/services/auth_service.py` - Auth business logic

### Models
- `app/models/user.py` - User data models
- `app/models/item.py` - Item data models

### Database
- Update `config/settings.py` with `DATABASE_URL`
- Add database connection logic
- Create SQLAlchemy session management

### Middleware
- Add request/response logging
- Add request ID tracking
- Add rate limiting

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **ASGI Server**: Uvicorn 0.24.0
- **Config**: Pydantic Settings 2.1.0
- **Validation**: Pydantic 2.5.0
- **Testing**: pytest 7.4.3, pytest-asyncio 0.21.1
- **Code Quality**: black, flake8, isort, mypy
- **Package Manager**: Poetry (alternative: pip)
