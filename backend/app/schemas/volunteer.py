"""
Stadium Sync — Volunteer Schemas.

Pydantic models for volunteer management and dispatch.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class VolunteerStatusUpdate(BaseModel):
    """Request body for a volunteer to update their status."""
    status: str = Field(
        ...,
        description="New status: 'available', 'busy', 'offline'",
    )
    lat: Optional[float] = None
    lng: Optional[float] = None


class VolunteerResponse(BaseModel):
    """Volunteer profile data."""
    id: str
    name: str
    section_id: Optional[str] = None
    status: str
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    active_assignments: int = 0


class AssignmentResponse(BaseModel):
    """Volunteer assignment data."""
    id: str
    volunteer_id: str
    incident_id: str
    status: str
    assigned_at: datetime
    completed_at: Optional[datetime] = None


class VolunteerListResponse(BaseModel):
    """Paginated list of volunteers."""
    volunteers: List[VolunteerResponse]
    total: int
