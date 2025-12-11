# Contributing to FastAPI Service

## Development Setup

### Prerequisites
- Python 3.10 or higher
- pip or Poetry
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fastapi-service
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
# OR
poetry install
```

4. Copy environment file:
```bash
cp .env.example .env
```

## Code Style Guidelines

We follow strict code quality standards to maintain consistency and readability.

### Formatting
- **Code Formatter**: Black
  - Line length: 100 characters
  - Target Python: 3.10+

```bash
black app/ config/ tests/
```

### Import Sorting
- **Tool**: isort
- **Profile**: black (compatible with Black formatter)

```bash
isort app/ config/ tests/
```

### Linting
- **Tool**: flake8
- **Max line length**: 100 characters
- Excluded patterns defined in `.flake8`

```bash
flake8 app/ config/ tests/
```

### Type Checking
- **Tool**: mypy
- **Python Version**: 3.10
- **Strict Checks**: Enabled for untyped definitions

```bash
mypy app/ config/
```

## Testing

### Running Tests
```bash
# All tests
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=app --cov-report=html
```

### Writing Tests
- Place tests in `tests/` directory
- Use `.test_*.py` or `*_test.py` naming convention
- Use pytest fixtures from `conftest.py`
- Tests should be independent and idempotent

Example test:
```python
def test_my_endpoint(client):
    """Test description."""
    response = client.get("/api/v1/my-endpoint")
    assert response.status_code == 200
    assert response.json()["key"] == "value"
```

## Code Review Checklist

Before submitting a pull request, ensure:
- [ ] Code passes all tests: `pytest`
- [ ] Code is properly formatted: `black --check` and `isort --check-only`
- [ ] Linting passes: `flake8`
- [ ] Type checking passes: `mypy`
- [ ] No unused imports or variables
- [ ] Added tests for new functionality
- [ ] Updated documentation if needed
- [ ] Commit messages are descriptive
- [ ] No debug code left in (print statements, pdb, etc.)

## Pre-commit Setup (Optional)

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

This will automatically run checks before committing.

## Adding a New Feature

### 1. Create a Router

Create a new router in `app/routers/`:

```python
# app/routers/items.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Item(BaseModel):
    """Item model."""

    name: str
    price: float


@router.get("/items")
async def list_items():
    """List all items."""
    return {"items": []}


@router.post("/items")
async def create_item(item: Item):
    """Create a new item."""
    return item
```

### 2. Include the Router

Add the router to `app/main.py`:

```python
from app.routers import items

app.include_router(items.router, prefix="/api/v1", tags=["items"])
```

### 3. Create a Service (Optional)

For business logic, create a service in `app/services/`:

```python
# app/services/items.py
from typing import List


class ItemService:
    """Service for item operations."""

    async def get_all_items(self) -> List[dict]:
        """Get all items."""
        return []

    async def create_item(self, name: str, price: float) -> dict:
        """Create a new item."""
        return {"name": name, "price": price}
```

### 4. Use the Service in Router

```python
from app.services.items import ItemService

item_service = ItemService()


@router.get("/items")
async def list_items():
    """List all items."""
    items = await item_service.get_all_items()
    return {"items": items}
```

### 5. Write Tests

Create tests in `tests/`:

```python
# tests/test_items.py
def test_list_items(client):
    """Test listing items."""
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    assert "items" in response.json()


def test_create_item(client):
    """Test creating an item."""
    payload = {"name": "Test Item", "price": 9.99}
    response = client.post("/api/v1/items", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"
```

## Project Conventions

### Directory Structure
- `app/` - Application code
- `app/routers/` - API route handlers
- `app/services/` - Business logic
- `config/` - Configuration and settings
- `tests/` - Unit and integration tests

### Naming Conventions
- **Files**: snake_case (e.g., `user_service.py`)
- **Classes**: PascalCase (e.g., `UserService`)
- **Functions/Variables**: snake_case (e.g., `get_user`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_ITEMS`)

### API Naming
- Use REST conventions (GET, POST, PUT, DELETE)
- Pluralize resource names (e.g., `/items`, not `/item`)
- Use lowercase with hyphens (e.g., `/api/v1/user-profile`)
- Version your API (e.g., `/api/v1/`, `/api/v2/`)

## Troubleshooting

### Import Errors
Ensure the virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Type Checking Failures
Add type hints to your functions:
```python
async def get_item(item_id: int) -> dict:
    """Get an item by ID."""
    return {"id": item_id}
```

### Formatting Issues
Auto-format your code:
```bash
black app/ config/ tests/
isort app/ config/ tests/
```

## Getting Help

- Check existing issues in the repository
- Review the README for API documentation
- Look at similar endpoints for patterns
- Ask in discussions or comments

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).
