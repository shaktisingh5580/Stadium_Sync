"""
===============================================================================
File: backend/app/core/rate_limiter.py
Purpose: Request rate limiting via SlowAPI - prevents DDoS, brute-force 
         attacks, and fair-queues API access. Per-endpoint and per-user 
         limits (auth: 10/min, AI: 20/min, IoT: 300/min).
Architecture: SlowAPI uses Redis backend (or in-memory fallback) to track 
             request counts with TTL windows. Decorators like 
             @limiter.limit("10/minute") applied to route handlers.
Inputs: Limiter configuration from settings (rate limits per endpoint).
Outputs: 429 Too Many Requests response when limit exceeded.
Hackathon Vertical: Security & Authentication
===============================================================================
"""

import logging
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_client_ip(request: Request) -> str:
    """
    Extract client IP for rate limiting.
    Handles reverse proxies (Render, Cloudflare) via X-Forwarded-For.
    """
    # Check for proxy headers first (Render uses these)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    return get_remote_address(request)


def _get_key_func(request: Request) -> str:
    """
    Key function for rate limiting.
    Uses JWT subject (ticket_id) if authenticated, otherwise IP.
    """
    # Try to extract user from JWT for per-user rate limiting
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            from app.core.security import verify_token
            token = auth_header.split(" ")[1]
            payload = verify_token(token)
            return f"user:{payload.get('sub', _get_client_ip(request))}"
        except Exception:
            pass
    return f"ip:{_get_client_ip(request)}"


# ── Initialize Limiter ──
# Storage URI: Redis if available, else in-memory
_storage_uri = settings.REDIS_URL if settings.REDIS_URL else "memory://"

limiter = Limiter(
    key_func=_get_key_func,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    storage_uri=_storage_uri,
    enabled=settings.RATE_LIMIT_ENABLED,
    strategy="moving-window",
)


def _rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> ORJSONResponse:
    """Custom 429 response matching our error schema."""
    request_id = getattr(request.state, "request_id", "unknown")
    retry_after = exc.detail  # e.g., "10 per 1 minute"

    return ORJSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit exceeded: {retry_after}",
                "request_id": request_id,
                "details": {
                    "limit": str(retry_after),
                    "tip": "Please slow down your requests.",
                },
            },
        },
        headers={
            "Retry-After": "60",
            "X-RateLimit-Limit": str(retry_after),
        },
    )


def setup_rate_limiter(app: FastAPI) -> None:
    """Attach rate limiter to the FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info(
        f"⚡ Rate limiter initialized "
        f"(storage={'redis' if settings.REDIS_URL else 'memory'}, "
        f"default={settings.RATE_LIMIT_DEFAULT})"
    )


async def check_ticket_abuse(ticket_id: str) -> bool:
    """
    Check if a ticket is being scanned excessively in a short window.
    Returns True if safe, False if abuse detected.
    """
    if not settings.REDIS_ENABLED:
        return True
        
    from app.core.redis_client import get_redis
    redis = await get_redis()
    if not redis:
        return True
        
    key = f"abuse:ticket:{ticket_id}"
    try:
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, 900)  # 15 minute window
            
        if count > 20:
            logger.warning(f"🚨 Ticket abuse detected for ticket {ticket_id}: {count} scans in 15m")
            return False
    except Exception as e:
        logger.error(f"Failed to check ticket abuse: {e}")
        
    return True
