"""
Stadium Sync — Rate Limiter Setup.

Uses SlowAPI with sliding-window rate limiting.
Supports Redis backend (production) or in-memory (dev).

Rate Limit Tiers:
    Tier 1 — Auth:              10/minute   (brute force prevention)
    Tier 2 — AI Endpoints:      10/minute   (Gemini cost control)
    Tier 3 — Standard Read:     60/minute   (normal usage)
    Tier 4 — Frequent Write:    120/minute  (volunteer location)
    Tier 5 — IoT Ingest:        300/minute  (machine-to-machine)
    Tier 6 — Health:            Unlimited   (monitoring probes)
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
