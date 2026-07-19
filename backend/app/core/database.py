"""
===============================================================================
File: backend/app/core/database.py
Purpose: Async SQLAlchemy engine and session management - configures connection 
         pool optimized for deployment target (SQLite for local, PostgreSQL 
         with QueuePool for staging, Neon Serverless with NullPool for prod).
Architecture: Creates AsyncSession factory with automatic transaction management 
             (auto-commit on success, auto-rollback on error). Connection pool 
             strategy varies by database type: NullPool for serverless, QueuePool 
             for persistent database.
Inputs: DATABASE_URL from config, connection pool settings 
        (pool_size, max_overflow, pool_recycle).
Outputs: get_db() dependency for routes (provides AsyncSession), 
         engine.connect() for admin scripts, health check function.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import text

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# ── Engine Configuration ──
# Neon Serverless works best with NullPool (connection-per-request)
# Local PostgreSQL/SQLite uses QueuePool for connection reuse

from urllib.parse import urlparse
from typing import Any

def _parse_database_url(url: str) -> tuple[str, bool, bool]:
    """Parse DATABASE_URL to determine driver, protocol, and pool strategy."""
    try:
        parsed = urlparse(url)
        driver = parsed.scheme.split("+")[0] if "+" in parsed.scheme else parsed.scheme
        is_sqlite = driver == "sqlite"
        is_neon = "neon" in parsed.netloc or settings.is_production
        return driver, is_sqlite, is_neon
    except Exception as e:
        logger.error(f"Failed to parse DATABASE_URL: {e}")
        raise ValueError(f"Invalid DATABASE_URL format: {url}") from e

driver_name, _is_sqlite, _is_neon = _parse_database_url(settings.DATABASE_URL)
logger.info(f"Database: driver={driver_name}, sqlite={_is_sqlite}, neon={_is_neon}")

engine_kwargs: dict[str, Any] = {
    "echo": settings.DATABASE_ECHO,
}

if _is_sqlite:
    # SQLite: no pool needed, enable check_same_thread=False
    engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30}
    engine_kwargs["poolclass"] = NullPool
    logger.info("Using SQLite with NullPool")
elif _is_neon:
    # Neon Serverless: NullPool recommended
    engine_kwargs["poolclass"] = NullPool
    logger.info("Using Neon Serverless with NullPool")
else:
    # Standard PostgreSQL: connection pooling
    engine_kwargs["poolclass"] = QueuePool
    engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 900
    logger.info(f"Using standard DB with QueuePool (size={settings.DATABASE_POOL_SIZE})")

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

# ── Session Factory ──
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# ── Dependency Injection ──
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async database session.

    Usage in routes:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database transaction failed; rolled back: {type(e).__name__}: {e}")
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager version for use outside of FastAPI routes
    (e.g., in services, scripts, background tasks).
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database context transaction failed; rolled back: {type(e).__name__}: {e}")
            raise
        finally:
            await session.close()


# ── Lifecycle ──
async def create_tables() -> None:
    """Create all tables. Use only in dev — production uses Alembic."""
    from app.models import Base  # noqa: F811

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables created")


async def check_db_connection() -> bool:
    """Ping the database to verify connectivity."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def dispose_engine() -> None:
    """Dispose the engine on shutdown."""
    await engine.dispose()
    logger.info("🔌 Database engine disposed")
