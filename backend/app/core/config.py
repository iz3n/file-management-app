from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation. Loads from .env and environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = Field(..., min_length=1, description="Database connection URL")
    UPLOAD_DIR: str = Field(default="data/uploads", description="Directory for uploaded files")
    MAX_UPLOAD_BYTES: int = Field(default=50 * 1024 * 1024, ge=1, description="Max upload size in bytes (default 50 MB)")
    STORAGE_BACKEND: str = Field(default="local", description="Storage backend to use")
    MINIO_ENDPOINT: str = Field(..., min_length=1, description="Minio endpoint")
    MINIO_ACCESS_KEY: str = Field(..., min_length=1, description="Minio access key")
    MINIO_SECRET_KEY: str = Field(..., min_length=1, description="Minio secret key")
    MINIO_BUCKET: str = Field(..., min_length=1, description="Minio bucket")
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", description="Allowed origins for CORS")


def get_settings() -> Settings:
    """Return validated settings. Fails at import/startup if required env is missing."""
    return Settings()
