"""
===============================================================================
File: backend/app/schemas/incident.py
Purpose: Incident schemas - validates incident reports and structures AI 
         triage responses with severity/category/action.
Architecture: IncidentReportRequest (description), IncidentTriageResponse 
             (severity enum, category enum, recommended_actions).
Inputs: Fan/volunteer incident description.
Outputs: AI-determined severity level and category for automation + dispatch.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class IncidentCreateRequest(BaseModel):
    """Request body when a fan reports an incident."""
    description: str = Field(
        ...,
        description="Description of the issue",
        min_length=5,
        max_length=500,
        examples=["There's a large spill near the stairs in section S204"],
    )
    location_description: Optional[str] = Field(
        None,
        description="Additional location details",
        max_length=200,
    )
    image_base64: Optional[str] = Field(
        None,
        description="Optional photo of the issue (base64 encoded)",
    )


class IncidentResponse(BaseModel):
    """Response after creating or fetching an incident."""
    id: str
    ticket_id: str
    description: str
    severity: str
    category: str
    status: str
    section_name: Optional[str] = None
    estimated_response_mins: int
    suggested_action: Optional[str] = None
    created_at: datetime


class IncidentUpdateResponse(BaseModel):
    """Response for an incident status update."""
    id: str
    incident_id: str
    status: str
    note: str
    updated_by: str
    created_at: datetime


class IncidentListResponse(BaseModel):
    """Paginated list of incidents."""
    incidents: List[IncidentResponse]
    total: int
    page: int
    page_size: int
