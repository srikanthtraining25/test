.PHONY: help install dev test lint format type-check clean docker-build docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies with pip"
	@echo "  make dev          - Run development server"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters (flake8)"
	@echo "  make format       - Format code with black and isort"
	@echo "  make type-check   - Run type checking with mypy"
	@echo "  make quality      - Run all quality checks"
	@echo "  make clean        - Clean up generated files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"

install:
	pip install -r requirements.txt

dev:
	uvicorn asgi:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term-missing

lint:
	flake8 app/ config/ tests/

format:
	black app/ config/ tests/
	isort app/ config/ tests/

type-check:
	mypy app/ config/

quality: format lint type-check test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '.coverage' -delete
	rm -rf htmlcov/ .mypy_cache/ .pytest_cache/ build/ dist/ *.egg-info

docker-build:
	docker build -t fastapi-service:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api
