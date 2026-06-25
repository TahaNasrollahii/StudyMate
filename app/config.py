"""
Application configuration using pydantic-settings.
"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/learnova"
    REDIS_URL: str = "redis://localhost:6379"
    OPENROUTER_API_KEY: str = ""
    APP_NAME: str = "Learnova API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }


settings = Settings()
