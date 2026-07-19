"""
===============================================================================
File: backend/app/core/redis_client.py
Purpose: Core Backend Application Module.
Architecture: FastAPI backend module.
Inputs: standard API requests or internal service calls.
Outputs: structured responses/models.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""
Stadium Sync — Redis Async Client.

Provides async Redis connection pool for:
- Real-time crowd density state
- Fan session caching
- Egress route caching
- Rate limiter backend
- WebSocket pub/sub

Gracefully degrades if Redis is unavailable.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Redis client — lazy initialized
_redis_client = None


async def init_redis() -> Optional[Any]:
    """Initialize Redis connection pool. Call during app startup."""
    global _redis_client

    from app.core.config import get_settings
    settings = get_settings()

    if not settings.REDIS_URL:
        logger.warning("⚠️  REDIS_URL not set — Redis features disabled")
        return None

    try:
        import redis.asyncio as aioredis

        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )

        # Verify connection
        await _redis_client.ping()
        logger.info("✅ Redis connected")
        return _redis_client

    except Exception as e:
        logger.warning(f"⚠️  Redis connection failed: {e} — features degraded")
        _redis_client = None
        return None


async def get_redis() -> Optional[Any]:
    """
    Get the Redis client instance.

    Returns None if Redis is unavailable (graceful degradation).
    Services must handle None redis gracefully.
    """
    return _redis_client


async def check_redis_connection() -> bool:
    """Check if Redis is connected and responsive."""
    if _redis_client is None:
        return False
    try:
        await _redis_client.ping()
        return True
    except Exception:
        return False


async def close_redis() -> None:
    """Close Redis connection pool. Call during app shutdown."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        logger.info("🔌 Redis connection closed")
        _redis_client = None


# ── Convenience Helpers ──

async def redis_set(key: str, value: str, ttl: int = 3600) -> bool:
    """Set a key with TTL. Returns False if Redis unavailable."""
    if _redis_client is None:
        return False
    try:
        await _redis_client.set(key, value, ex=ttl)
        return True
    except Exception as e:
        logger.error(f"Redis SET failed for {key}: {e}")
        return False


async def redis_get(key: str) -> Optional[str]:
    """Get a key. Returns None if Redis unavailable or key missing."""
    if _redis_client is None:
        return None
    try:
        return await _redis_client.get(key)
    except Exception as e:
        logger.error(f"Redis GET failed for {key}: {e}")
        return None


async def redis_delete(key: str) -> bool:
    """Delete a key. Returns False if Redis unavailable."""
    if _redis_client is None:
        return False
    try:
        await _redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Redis DELETE failed for {key}: {e}")
        return False


async def redis_incr(key: str, ttl: int = 3600) -> Optional[int]:
    """Increment a counter. Returns None if Redis unavailable."""
    if _redis_client is None:
        return None
    try:
        pipe = _redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, ttl)
        results = await pipe.execute()
        return results[0]
    except Exception as e:
        logger.error(f"Redis INCR failed for {key}: {e}")
        return None
