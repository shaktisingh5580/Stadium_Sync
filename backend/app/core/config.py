"""
===============================================================================
File: backend/app/core/config.py
Purpose: Core Backend Application Module.
Architecture: FastAPI backend module.
Inputs: standard API requests or internal service calls.
Outputs: structured responses/models.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""
Stadium Sync — Centralized Configuration.

All environment variables are loaded and validated here via pydantic-settings.
Use `get_settings()` to access the singleton instance.
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator, model_validator
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
    # Secrets intentionally have no usable fallback. Production startup validates them.
    SECRET_KEY: str = ""
    TICKET_QR_SIGNING_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 240  # 4 hours per match

    # ── Google Cloud ──
    # Demo fallbacks are useful in local development but must never create
    # fabricated operational data in a production deployment.
    ALLOW_AI_MOCK_FALLBACK: bool = False
    ALLOW_DEMO_FEATURES: bool = False

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
    GEMINI_API_KEY_3: str = ""
    NVIDIA_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

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
    ]

    # ── IoT API Key ──
    IOT_API_KEY: str = ""

    # ── Celery (optional) ──
    CELERY_BROKER_URL: str = ""

    @field_validator("REDIS_ENABLED", mode="before")
    @classmethod
    def set_redis_enabled(cls, v, info):
        """Auto-enable Redis if REDIS_URL is set."""
        if info.data.get("REDIS_URL"):
            return True
        return bool(v)

    @model_validator(mode="after")
    def validate_production_security(self):
        """Refuse an unsafe production configuration before serving traffic."""
        if not self.is_production:
            return self

        errors = []
        if self.DEBUG:
            errors.append("DEBUG must be false")
        if "*" in self.CORS_ORIGINS:
            errors.append("CORS_ORIGINS cannot contain '*' when APP_ENV is production")
        if len(self.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be at least 32 characters")
        if len(self.TICKET_QR_SIGNING_KEY) < 32:
            errors.append("TICKET_QR_SIGNING_KEY must be at least 32 characters")
        if len(self.IOT_API_KEY) < 32:
            errors.append("IOT_API_KEY must be at least 32 characters")
        if self.ALLOW_AI_MOCK_FALLBACK:
            errors.append("ALLOW_AI_MOCK_FALLBACK must be false")
        if self.ALLOW_DEMO_FEATURES:
            errors.append("ALLOW_DEMO_FEATURES must be false")
        if errors:
            raise ValueError("Unsafe production configuration: " + ";".join(errors))
        return self

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
