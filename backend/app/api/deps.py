"""
Stadium Sync — Dependency Injection.

Provides FastAPI dependencies for:
- Database sessions
- JWT authentication (fan, volunteer, admin)
- API key validation (IoT endpoints)
- Redis client
"""

from typing import Any, Dict, Optional

from fastapi import Depends, Header, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db  # noqa: F401 — re-exported
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.redis_client import get_redis  # noqa: F401 — re-exported
from app.core.security import verify_token

settings = get_settings()


async def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    Extract and verify the current user from the JWT token.

    Looks for the token in:
    1. Authorization: Bearer <token> header
    2. token query parameter (for WebSocket connections)

    Returns the decoded JWT payload containing:
    - sub: ticket_id
    - seat: { section, row, number }
    - holder_name: fan's name
    - role: "fan" | "volunteer" | "admin"
    """
    token = None

    # Try Authorization header first
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    # Fallback to query parameter (WebSocket support)
    if not token:
        token = request.query_params.get("token")

    if not token:
        raise UnauthorizedException("Missing authentication token")

    payload = verify_token(token)

    # Attach to request state for downstream use
    request.state.current_user = payload
    return payload


async def get_current_fan(
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Ensure the current user is a fan (or any role — fans are default)."""
    # Fans don't need a special role check; all authenticated users can act as fans
    return user


async def get_current_volunteer(
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Ensure the current user is a volunteer."""
    if user.get("role") != "volunteer":
        raise ForbiddenException("Volunteer access required")
    return user


async def get_current_admin(
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Ensure the current user is an admin."""
    if user.get("role") != "admin":
        raise ForbiddenException("Admin access required")
    return user


async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> str:
    """
    Validate IoT API key for machine-to-machine endpoints.
    Used by crowd density ingest endpoints.
    """
    if not x_api_key:
        raise UnauthorizedException("Missing X-API-Key header")
    if x_api_key != settings.IOT_API_KEY:
        raise UnauthorizedException("Invalid API key")
    return x_api_key


async def get_optional_user(
    request: Request,
    authorization: Optional[str] = Header(None),
) -> Optional[Dict[str, Any]]:
    """
    Optionally extract user from JWT. Returns None if no token provided.
    Useful for endpoints that work both authenticated and anonymously.
    """
    try:
        return await get_current_user(request, authorization)
    except UnauthorizedException:
        return None
