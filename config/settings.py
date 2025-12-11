"""Application settings and configuration."""
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "FastAPI Service"
    app_description: str = "A scalable FastAPI-based API service"
    app_version: str = "0.1.0"
    debug: bool = False
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    log_level: str = "INFO"
