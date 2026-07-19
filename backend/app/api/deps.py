"""
===============================================================================
File: backend/app/api/deps.py
Purpose: Core Backend Application Module.
Architecture: FastAPI backend module.
Inputs: standard API requests or internal service calls.
Outputs: structured responses/models.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""
Stadium Sync — Dependency Injection.

Provides FastAPI dependencies for:
- Database sessions
- JWT authentication (fan, volunteer, admin)
- API key validation (IoT endpoints)
- Redis client
"""

import secrets
from typing import Any, Dict, Optional

from fastapi import Depends, Header, Request
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

    Looks for the token in the Authorization: Bearer <token> header.

    Returns the decoded JWT payload containing:
    - sub: ticket_id
    - seat: { section, row, number }
    - holder_name: fan's name
    - role: "fan" | "volunteer" | "admin"
    """
    token = None

    # Query-string tokens leak easily through logs, history and referrers.
    # WebSocket authentication is handled only by its dedicated endpoint.
    if authorization:
        scheme, _, credentials = authorization.partition(" ")
        if scheme.lower() == "bearer" and credentials.strip():
            token = credentials.strip()

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
    if user.get("role") != "fan":
        raise ForbiddenException("Fan access required")
    return user


async def get_current_staff(
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Ensure the current user is an authorized volunteer or organizer."""
    if user.get("role") not in {"volunteer", "admin"}:
        raise ForbiddenException("Volunteer or admin access required")
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
    """    Validate IoT API key for machine-to-machine endpoints.
    Used by crowd density ingest endpoints.

    """
    if not x_api_key:
        raise UnauthorizedException("Missing X-API-Key header")
    if not settings.IOT_API_KEY or not secrets.compare_digest(
        x_api_key, settings.IOT_API_KEY
    ):
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
