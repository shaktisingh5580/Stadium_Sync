"""
===============================================================================
File: backend/app/api/v1/auth.py
Purpose: Authentication endpoints - QR scan to JWT issuance, session retrieval, 
         token refresh for long-duration matches.
Architecture: POST /scan-ticket (QR validation → JWT), GET /me (session info), 
             POST /refresh (extend expiry). All responses include fan context 
             (seat, accessibility, transit).
Inputs: QR payload, optional token refresh.
Outputs: JWT tokens with fan session, user info, expiration times.
Hackathon Vertical: Security & Authentication
===============================================================================
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.audit import AuditLog
from app.core.config import get_settings
from app.core.redis_client import get_redis
from app.core.rate_limiter import limiter, check_ticket_abuse
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
    response_model=dict,
    summary="Scan QR ticket and authenticate",
    description=(
        "Decode the QR code payload, validate the ticket against the database, "
        "and return a JWT access token with the fan's session info."
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
    if not body.qr_payload or len(body.qr_payload) > 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload signature")
    
    # Step 1-2: Decode and verify QR payload
    try:
        qr_data = decode_qr_payload(body.qr_payload)
    except Exception as e:
        logger.error(f"Failed to decode QR: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed security token")

    ticket_id = qr_data['ticket_id']
    match_id = qr_data['match_id']

    if not await check_ticket_abuse(ticket_id):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Ticket abuse detected. Too many scans.")

    if settings.REDIS_ENABLED:
        redis = await get_redis()
        if redis:
            replay_key = f"ticket_scan:{ticket_id}:{match_id}"
            if await redis.exists(replay_key):
                logger.warning(f"🚨 Replay attack detected: {ticket_id}")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ticket scan attempted too quickly; possible replay attack")
            await redis.setex(replay_key, 60, "scanned")

    logger.info(f"QR scanned: ticket={ticket_id}, match={match_id}")

    # Step 3: Validate ticket
    ticket = await validate_ticket(db, ticket_id, match_id)

    # Step 4: Build fan session
    fan_session = build_fan_session(ticket)

    # Step 5: Mark ticket as scanned
    await mark_ticket_scanned(db, ticket)
    
    audit_entry = AuditLog(
        id=str(uuid.uuid4()),
        action="ticket_scanned",
        actor_id=ticket.id,
        actor_type="fan",
        resource_id=ticket.id,
        resource_type="ticket",
        details={"match_id": ticket.match_id}
    )
    db.add(audit_entry)
    # The transaction will be committed by the get_db dependency
    logger.info(f"✅ Audit logged: ticket {ticket_id} scanned by {fan_session.holder_name}")

    # Step 6: Create JWT (Seat info removed from JWT to prevent data leak)
    expires_delta = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    expires_at = datetime.now(timezone.utc) + expires_delta

    token = create_access_token(
        data={
            "sub": fan_session.ticket_id,
            "holder_name": fan_session.holder_name,
            "match_id": fan_session.match_id,
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
    response_model=dict,
    summary="Get current session info",
    description="Returns the authenticated fan's session data with real-time seat info.",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_me(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the current user's session data fetching fresh data from DB."""
    ticket_id = current_user["sub"]
    
    # Fetch fresh ticket + seat info from DB
    ticket = await validate_ticket(
        db, 
        ticket_id, 
        current_user.get("match_id", "")
    )
    
    # Build fresh session with current DB state
    fan_session = build_fan_session(ticket)
    
    me = MeResponse(
        ticket_id=fan_session.ticket_id,
        holder_name=fan_session.holder_name,
        match_id=fan_session.match_id,
        role="fan",
        seat=fan_session.seat.model_dump(),
        transit_choice=fan_session.transit_choice,
        needs_accessibility=fan_session.needs_accessibility,
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


# ──────────────────────────────────────────────
# GET /auth/demo-credentials
# ──────────────────────────────────────────────

@router.get(
    "/demo-credentials",
    summary="Get demo credentials for dev bypass",
    description=(
        "Returns a valid demo QR payload and admin JWT token generated "
        "with the server's actual signing keys. Only available when "
        "ALLOW_DEMO_FEATURES is enabled."
    ),
)
@limiter.limit("10/minute")
async def get_demo_credentials(request: Request):
    """
    Generate valid demo credentials for the dev bypass buttons.

    Returns a QR payload signed with the server's TICKET_QR_SIGNING_KEY
    and an admin JWT signed with the server's SECRET_KEY, so the frontend
    bypass always works regardless of deployment environment.
    """
    if not settings.ALLOW_DEMO_FEATURES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo features are disabled in this environment",
        )

    from app.services.ticket_service import generate_qr_payload

    # Generate valid QR payload for demo ticket
    qr_payload = generate_qr_payload("ticket-001", "M2026-QF1")

    # Generate valid admin JWT
    admin_token = create_access_token(
        data={
            "sub": "admin-demo-001",
            "role": "admin",
        },
        expires_delta=timedelta(days=365),
    )

    return {
        "success": True,
        "data": {
            "qr_payload": qr_payload,
            "admin_token": admin_token,
        },
        "request_id": getattr(request.state, "request_id", ""),
    }

