"""
Stadium Sync — Auth Schemas.

Pydantic models for QR ticket scanning, JWT session, and token management.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── QR Scan ──

class QRScanRequest(BaseModel):
    """Request body when a fan scans their ticket QR code."""
    qr_payload: str = Field(
        ...,
        description="Raw QR code payload string (JSON encoded)",
        min_length=10,
        max_length=2000,
        examples=['{"ticket_id": "ticket-001", "match_id": "M2026-QF1", "checksum": "abc123"}'],
    )


# ── Seat & Section Info ──

class SeatInfo(BaseModel):
    """Seat location details for the authenticated fan."""
    id: str
    section_id: str
    section_name: str
    section_type: str
    row: str
    number: int
    svg_x: float
    svg_y: float


class SectionInfo(BaseModel):
    """Section metadata."""
    id: str
    name: str
    section_type: str
    capacity: int
    svg_x: float
    svg_y: float


# ── Fan Session ──

class FanSession(BaseModel):
    """Complete fan session data returned after authentication."""
    ticket_id: str
    holder_name: str
    match_id: str
    seat: SeatInfo
    transit_choice: Optional[str] = None
    needs_accessibility: bool = False
    is_scanned: bool = True


# ── Auth Responses ──

class QRScanResponse(BaseModel):
    """Response after successful QR scan authentication."""
    token: str
    token_type: str = "bearer"
    expires_at: datetime
    fan: FanSession


class MeResponse(BaseModel):
    """Response for GET /auth/me — current session data."""
    ticket_id: str
    holder_name: str
    match_id: str
    role: str
    seat: dict
    transit_choice: Optional[str] = None
    needs_accessibility: bool = False


class TokenRefreshResponse(BaseModel):
    """Response for POST /auth/refresh."""
    token: str
    token_type: str = "bearer"
    expires_at: datetime
