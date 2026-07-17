"""
Stadium Sync — Centralized Configuration.

All environment variables are loaded and validated here via pydantic-settings.
Use `get_settings()` to access the singleton instance.
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──
    APP_NAME: str = "StadiumSync"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000  # Render sets $PORT automatically

    # ── Security ──
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 240  # 4 hours per match

    # ── Database (Neon Serverless PostgreSQL) ──
    DATABASE_URL: str = "sqlite+aiosqlite:///./stadium_sync.db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_ECHO: bool = False

    # ── Redis ──
    REDIS_URL: str = ""
    REDIS_ENABLED: bool = False

    # ── Google Gemini AI & NVIDIA ──
    GEMINI_API_KEY_1: str = ""
    GEMINI_API_KEY_2: str = ""
    GEMINI_API_KEY_3: str = ""
    NVIDIA_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # ── Telegram Bots ──
    TELEGRAM_FAN_BOT_TOKEN: str = ""
    TELEGRAM_VOLUNTEER_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_BASE_URL: str = ""

    # ── Rate Limiting ──
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "60/minute"
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_AI: str = "10/minute"
    RATE_LIMIT_UPLOAD: str = "10/minute"
    RATE_LIMIT_IOT: str = "300/minute"
    RATE_LIMIT_VOLUNTEER_LOCATION: str = "120/minute"

    # ── CORS ──
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "*",  # Allow all origins for Vercel preview URLs
    ]

    # ── IoT API Key ──
    IOT_API_KEY: str = "dev-iot-key-change-in-production"

    # ── Celery (optional) ──
    CELERY_BROKER_URL: str = ""

    @field_validator("REDIS_ENABLED", mode="before")
    @classmethod
    def set_redis_enabled(cls, v, info):
        """Auto-enable Redis if REDIS_URL is set."""
        if info.data.get("REDIS_URL"):
            return True
        return bool(v)

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def database_url_sync(self) -> str:
        """Convert async URL to sync for Alembic."""
        return self.DATABASE_URL.replace("+asyncpg", "").replace("+aiosqlite", "")


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings singleton."""
    return Settings()
