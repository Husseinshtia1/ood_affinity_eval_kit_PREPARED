from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the PREPARED.ai SaaS wrapper."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "PREPARED.ai API Gateway"
    app_version: str = "0.2.0-p2"
    environment: str = "development"

    repo_root: Path = Path(__file__).resolve().parents[2]
    temp_storage_dir: Path = Path("/tmp/prepared_jobs")
    max_upload_bytes: int = 25 * 1024 * 1024

    redis_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"
    database_url: str = "postgresql+psycopg://prepared:prepared@postgres:5432/prepared"

    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_access_minutes: int = 60

    frontend_url: str = "http://localhost:3000"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str = "no-reply@prepared.ai"

    allowed_origins: list[str] = [
        "http://localhost:3000",
        "https://prepared.ai",
        "https://www.prepared.ai",
    ]

    report_ttl_minutes: int = 60


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.temp_storage_dir.mkdir(parents=True, exist_ok=True)
    return settings
