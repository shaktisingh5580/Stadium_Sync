"""
Stadium Sync — Async Database Engine and Session Management.

Uses SQLAlchemy 2.0 async engine. Supports both PostgreSQL (asyncpg)
for production/Neon and SQLite (aiosqlite) for local dev.
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

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# ── Engine Configuration ──
# Neon Serverless works best with NullPool (connection-per-request)
# Local PostgreSQL/SQLite uses QueuePool for connection reuse

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")
_is_neon = "neon" in settings.DATABASE_URL or settings.is_production

engine_kwargs = {
    "echo": settings.DATABASE_ECHO,
}

if _is_sqlite:
    # SQLite: no pool needed, enable check_same_thread=False
    engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 15}
    engine_kwargs["poolclass"] = NullPool
elif _is_neon:
    # Neon Serverless: NullPool recommended (serverless connections)
    engine_kwargs["poolclass"] = NullPool
else:
    # Standard PostgreSQL: connection pooling
    engine_kwargs["poolclass"] = QueuePool
    engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300  # Recycle connections every 5 min

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
        except Exception:
            await session.rollback()
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
        except Exception:
            await session.rollback()
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
            await conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def dispose_engine() -> None:
    """Dispose the engine on shutdown."""
    await engine.dispose()
    logger.info("🔌 Database engine disposed")
