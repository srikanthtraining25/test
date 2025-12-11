# Multi-stage build for FastAPI application
FROM python:3.10-slim as builder

WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Build wheels
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-dev --no-root


FROM python:3.10-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY app ./app
COPY config ./config
COPY asgi.py ./

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')"

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "asgi:app", "--host", "0.0.0.0", "--port", "8000"]
