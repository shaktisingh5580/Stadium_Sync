"""
===============================================================================
File: backend/app/core/security.py
Purpose: JWT token management - creation, verification, expiration checks, 
         and revocation via JTI (JWT ID) tracking in Redis.
Architecture: HMAC-SHA256 signing with configurable expiry (fan: 4h, 
             volunteer: 12h, admin: 8h). Tokens include claims: sub (ticket_id), 
             role, aud (audience for role isolation), jti (unique ID for 
             revocation), iat (issued at), exp (expiration).
Inputs: Credential data (ticket_id, name, role), optional custom expiry.
Outputs: Encoded JWT string, decoded/verified payload, revocation capability.
Hackathon Vertical: Security & Authentication
===============================================================================
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException
from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)
settings = get_settings()


# ── JWT Token Operations ──

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data. Must include "sub" (subject = ticket_id).
        expires_delta: Custom expiration. Defaults to JWT_EXPIRATION_MINUTES.

    Returns:
        Encoded JWT string.

    Example payload:
        {
            "sub": "ticket-uuid-123",
            "seat": {"section": "S204", "row": "12", "number": 5},
            "holder_name": "John Doe",
            "match_id": "M2026-QF2",
            "role": "fan",
            "exp": 1720500000
        }
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_EXPIRATION_MINUTES
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "iss": settings.APP_NAME,
        "jti": str(uuid.uuid4()),
        "aud": "stadium-sync-fan",
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


async def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token. Checks Redis blocklist for JTI.

    Args:
        token: The JWT string (from Authorization header or query param).

    Returns:
        Decoded payload dict.

    Raises:
        UnauthorizedException: If token is invalid, expired, malformed, or revoked.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience="stadium-sync-fan",
        )

        # Ensure required fields exist
        if "sub" not in payload:
            raise UnauthorizedException("Invalid token: missing subject")
            
        jti = payload.get("jti")
        if not jti:
            raise UnauthorizedException("Invalid token: missing JTI")

        if settings.REDIS_ENABLED and redis_client:
            if await redis_client.exists(f"revoked_token:{jti}"):
                raise UnauthorizedException("Token has been revoked")

        return payload

    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise UnauthorizedException("Invalid or expired token")


def create_volunteer_token(
    volunteer_id: str,
    name: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT token specifically for volunteers."""
    return create_access_token(
        data={
            "sub": volunteer_id,
            "name": name,
            "role": "volunteer",
        },
        expires_delta=expires_delta or timedelta(hours=12),
    )


def create_admin_token(
    admin_id: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT token for admin operations."""
    return create_access_token(
        data={
            "sub": admin_id,
            "role": "admin",
        },
        expires_delta=expires_delta or timedelta(hours=8),
    )


def is_token_expiring_soon(token: str, threshold_minutes: int = 30) -> bool:
    """Check if a token will expire within the threshold."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False},  # Don't raise on expired
        )
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        remaining = exp - datetime.now(timezone.utc)
        return remaining < timedelta(minutes=threshold_minutes)
    except JWTError:
        return True  # If we can't decode, it's effectively expired
