"""
===============================================================================
File: backend/app/api/v1/auth.py
Purpose: Core Backend Application Module.
Architecture: FastAPI backend module.
Inputs: standard API requests or internal service calls.
Outputs: structured responses/models.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""
Stadium Sync — Auth API Routes.

Endpoints:
    POST /api/v1/auth/scan-ticket   — Scan QR → validate → JWT
    GET  /api/v1/auth/me            — Get current session
    POST /api/v1/auth/refresh       — Refresh JWT token
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import get_settings

from app.core.rate_limiter import limiter
from app.core.security import (
    create_access_token,
    is_token_expiring_soon,
    verify_token,
)
from app.schemas.auth import (
    FanSession,
    MeResponse,
    QRScanRequest,
    QRScanResponse,
    TokenRefreshResponse,
)
from app.services.ticket_service import (
    build_fan_session,
    decode_qr_payload,
    mark_ticket_scanned,
    validate_ticket,
)

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ──────────────────────────────────────────────
# POST /auth/scan-ticket
# ──────────────────────────────────────────────

@router.post(
    "/scan-ticket",
    response_model=None,
    summary="Scan QR ticket and authenticate",
    description=(
        "Decode the QR code payload, validate the ticket against the database, "
        "and return a JWT access token with the fan's seat and section info."
    ),
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def scan_ticket(
    request: Request,
    body: QRScanRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Fan scans their ticket QR code → gets a JWT session.

    Flow:
    1. Decode QR payload (JSON with ticket_id, match_id, checksum)
    2. Verify checksum integrity
    3. Validate ticket exists in DB and is active
    4. Build fan session with seat/section details
    5. Create JWT with session data
    6. Return token + fan session
    """
    # Step 1-2: Decode and verify QR payload
    qr_data = decode_qr_payload(body.qr_payload)
    logger.info(f"QR scanned: ticket={qr_data['ticket_id']}, match={qr_data['match_id']}")

    # Step 3: Validate ticket
    ticket = await validate_ticket(db, qr_data["ticket_id"], qr_data["match_id"])

    # Step 4: Build fan session
    fan_session = build_fan_session(ticket)

    # Step 5: Mark ticket as scanned
    await mark_ticket_scanned(db, ticket)

    # Step 6: Create JWT
    expires_delta = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    expires_at = datetime.now(timezone.utc) + expires_delta

    token = create_access_token(
        data={
            "sub": fan_session.ticket_id,
            "holder_name": fan_session.holder_name,
            "match_id": fan_session.match_id,
            "seat": fan_session.seat.model_dump(),
            "transit_choice": fan_session.transit_choice,
            "needs_accessibility": fan_session.needs_accessibility,
            "role": "fan",
        },
        expires_delta=expires_delta,
    )

    return {
        "success": True,
        "data": QRScanResponse(
            token=token,
            expires_at=expires_at,
            fan=fan_session,
        ).model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }


# ──────────────────────────────────────────────
# GET /auth/me
# ──────────────────────────────────────────────

@router.get(
    "/me",
    response_model=None,
    summary="Get current session info",
    description="Returns the authenticated fan's session data from their JWT.",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_me(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Return the current user's session data from their JWT payload."""
    me = MeResponse(
        ticket_id=current_user["sub"],
        holder_name=current_user.get("holder_name", ""),
        match_id=current_user.get("match_id", ""),
        role=current_user.get("role", "fan"),
        seat=current_user.get("seat", {}),
        transit_choice=current_user.get("transit_choice"),
        needs_accessibility=current_user.get("needs_accessibility", False),
    )

    return {
        "success": True,
        "data": me.model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }


# ──────────────────────────────────────────────
# POST /auth/refresh
# ──────────────────────────────────────────────

@router.post(
    "/refresh",
    response_model=None,
    summary="Refresh JWT token",
    description="Issue a new JWT if the current one is valid but approaching expiry.",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def refresh_token(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Refresh the JWT token.

    Creates a new token with the same payload but a fresh expiration.
    Useful for long matches (extra time, penalties).
    """
    expires_delta = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    expires_at = datetime.now(timezone.utc) + expires_delta

    # Build new token with same user data
    new_token = create_access_token(
        data={
            "sub": current_user["sub"],
            "holder_name": current_user.get("holder_name", ""),
            "match_id": current_user.get("match_id", ""),
            "seat": current_user.get("seat", {}),
            "transit_choice": current_user.get("transit_choice"),
            "needs_accessibility": current_user.get("needs_accessibility", False),
            "role": current_user.get("role", "fan"),
        },
        expires_delta=expires_delta,
    )

    return {
        "success": True,
        "data": TokenRefreshResponse(
            token=new_token,
            expires_at=expires_at,
        ).model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }
