"""
===============================================================================
File: backend/app/services/ticket_service.py
Purpose: Core Backend Application Module.
Architecture: FastAPI backend module.
Inputs: standard API requests or internal service calls.
Outputs: structured responses/models.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""
Stadium Sync — Ticket Service.

Handles QR code decoding, ticket validation, and fan session creation.

QR Payload Format (JSON):
{
    "ticket_id": "uuid-string",
    "match_id": "M2026-QF1",
    "checksum": "abc123"
}
"""

import hashlib
import hmac
import json
import logging
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.core.config import get_settings
from app.models.ticket import Seat, Section, Ticket
from app.schemas.auth import FanSession, SeatInfo

logger = logging.getLogger(__name__)
settings = get_settings()


def decode_qr_payload(raw_payload: str) -> Dict[str, Any]:
    """
    Decode and validate the raw QR code payload.

    Expected format: JSON string with ticket_id, match_id, checksum.
    The checksum is an HMAC signature derived from a server-side signing key.

    Args:
        raw_payload: Raw string from QR code scanner.

    Returns:
        Parsed dict with ticket_id, match_id, checksum.

    Raises:
        BadRequestException: If payload is malformed or checksum invalid.
    """
    try:
        data = json.loads(raw_payload)
    except json.JSONDecodeError:
        raise BadRequestException(
            "Invalid QR code: not valid JSON",
            details={"hint": "The QR payload must be a JSON string"},
        )

    # Validate required fields
    required_fields = ["ticket_id", "match_id", "checksum"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise BadRequestException(
            f"Invalid QR code: missing fields: {', '.join(missing)}",
            details={"missing_fields": missing},
        )

    # Verify checksum
    expected_checksum = _compute_checksum(data["ticket_id"], data["match_id"])
    if data["checksum"] != expected_checksum:
        logger.warning(
            f"QR checksum mismatch for ticket {data['ticket_id']}: "
            f"expected={expected_checksum}, got={data['checksum']}"
        )
        raise BadRequestException(
            "Invalid QR code: checksum verification failed",
            details={"hint": "This ticket may be counterfeit or corrupted"},
        )

    return data


def _compute_checksum(ticket_id: str, match_id: str) -> str:
    """Compute the expected checksum for a ticket."""
    raw = f"{ticket_id}:{match_id}".encode()
    return hmac.new(
        settings.TICKET_QR_SIGNING_KEY.encode(), raw, hashlib.sha256
    ).hexdigest()[:12]


def generate_qr_payload(ticket_id: str, match_id: str) -> str:
    """
    Generate a valid QR payload string for a ticket.
    Used by the seeder script and tests.
    """
    checksum = _compute_checksum(ticket_id, match_id)
    return json.dumps({
        "ticket_id": ticket_id,
        "match_id": match_id,
        "checksum": checksum,
    })


async def validate_ticket(
    db: AsyncSession, ticket_id: str, match_id: str
) -> Ticket:
    """
    Validate that a ticket exists, is active, and matches the given match.

    Args:
        db: Database session.
        ticket_id: Ticket UUID from QR payload.
        match_id: Match ID from QR payload.

    Returns:
        The validated Ticket ORM object with seat relationship loaded.

    Raises:
        NotFoundException: If ticket doesn't exist.
        ForbiddenException: If ticket is inactive or match doesn't match.
    """
    # Query ticket with seat + section eagerly loaded
    stmt = (
        select(Ticket)
        .options(
            joinedload(Ticket.seat).joinedload(Seat.section)
        )
        .where(Ticket.id == ticket_id)
    )
    result = await db.execute(stmt)
    ticket = result.unique().scalar_one_or_none()

    if not ticket:
        raise NotFoundException("Ticket", ticket_id)

    if not ticket.is_active:
        raise ForbiddenException("This ticket has been deactivated")

    if ticket.match_id != match_id:
        raise ForbiddenException("Ticket does not match the specified event")

    return ticket


async def get_seat_with_section(
    db: AsyncSession, seat_id: str
) -> Optional[Seat]:
    """Get a seat with its section eagerly loaded."""
    stmt = (
        select(Seat)
        .options(joinedload(Seat.section))
        .where(Seat.id == seat_id)
    )
    result = await db.execute(stmt)
    return result.unique().scalar_one_or_none()


def build_fan_session(ticket: Ticket) -> FanSession:
    """
    Build a FanSession from a validated ticket.

    Extracts seat and section info for the JWT payload and API response.
    """
    seat = ticket.seat
    section = seat.section

    seat_info = SeatInfo(
        id=seat.id,
        section_id=section.id,
        section_name=section.name,
        section_type=section.section_type.value if hasattr(section.section_type, 'value') else str(section.section_type),
        row=seat.row,
        number=seat.number,
        svg_x=seat.svg_x,
        svg_y=seat.svg_y,
    )

    return FanSession(
        ticket_id=ticket.id,
        holder_name=ticket.holder_name,
        match_id=ticket.match_id,
        seat=seat_info,
        transit_choice=ticket.transit_choice,
        needs_accessibility=ticket.needs_accessibility,
    )


async def mark_ticket_scanned(db: AsyncSession, ticket: Ticket) -> None:
    """Mark a ticket as scanned (first-time QR use)."""
    if not ticket.is_scanned:
        ticket.is_scanned = True
        db.add(ticket)
        await db.flush()
        logger.info(f"Ticket {ticket.id} marked as scanned")
