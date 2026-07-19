"""
===============================================================================
File: backend/app/schemas/auth.py
Purpose: Authentication request/response schemas - validates QR scan input, 
         JWT token format, and fan session deserialization.
Architecture: Pydantic models for QRScanRequest, QRScanResponse, 
             TokenRefreshResponse, FanSession with type validation and 
             field constraints (max_length, regex, etc.).
Inputs: QR payload (JSON string with ticket_id, match_id, checksum).
Outputs: Validated FanSession with ticket, seat, accessibility, transit data 
         for JWT payload and API responses.
Hackathon Vertical: Security & Authentication
===============================================================================
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
    ticket_id: str = Field(..., description="Unique ticket identifier", examples=["TICKET-12345"])
    holder_name: str = Field(..., description="Name of the fan holding the ticket", examples=["John Doe"])
    match_id: str = Field(..., description="ID of the match the ticket is for", examples=["MATCH-101"])
    seat: SeatInfo = Field(..., description="Detailed seat information including SVG coordinates")
    transit_choice: Optional[str] = Field(None, description="Fan's chosen transit method to the stadium", examples=["metro"])
    needs_accessibility: bool = Field(False, description="Whether the fan requires accessible routing")
    is_scanned: bool = Field(True, description="Whether the ticket has been scanned at the gate")


# ── Auth Responses ──

class QRScanResponse(BaseModel):
    """Response after successful QR scan authentication."""
    token: str = Field(..., description="JWT access token for API authentication")
    token_type: str = Field("bearer", description="Token type, always 'bearer'")
    expires_at: datetime = Field(..., description="Timestamp when the token expires")
    fan: FanSession = Field(..., description="The fan's active session data")


class MeResponse(BaseModel):
    """Response for GET /auth/me — current session data."""
    ticket_id: str = Field(..., description="Unique ticket identifier")
    holder_name: str = Field(..., description="Name of the fan holding the ticket")
    match_id: str = Field(..., description="ID of the match")
    role: str = Field(..., description="User role, e.g. 'fan' or 'staff'")
    seat: dict = Field(..., description="Seat coordinates and details")
    transit_choice: Optional[str] = Field(None, description="Selected transit choice")
    needs_accessibility: bool = Field(False, description="Whether the fan requires accessible routing")


class TokenRefreshResponse(BaseModel):
    """Response for POST /auth/refresh."""
    token: str = Field(..., description="New JWT access token")
    token_type: str = Field("bearer", description="Token type, always 'bearer'")
    expires_at: datetime = Field(..., description="Timestamp when the new token expires")
