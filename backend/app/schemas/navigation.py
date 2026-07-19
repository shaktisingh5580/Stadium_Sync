"""
===============================================================================
File: backend/app/schemas/navigation.py
Purpose: Navigation schemas - validates transit preferences and structures 
         computed exit route responses.
Architecture: TransitPreferenceRequest (enum: metro/bus/rideshare/parking), 
             RouteResponse (path coordinates, duration, accessibility_safe).
Inputs: Fan's transit preference selection.
Outputs: Computed route to nearest transit station of chosen type.
Hackathon Vertical: Navigation & Transportation
===============================================================================
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ── Transit Selection ──

class TransitChoiceRequest(BaseModel):
    """Request body when a fan selects their post-match transit method."""
    transit_method: str = Field(
        ...,
        description="The selected transit method (e.g., 'metro', 'bus', 'rideshare', 'parking')",
        examples=["metro"],
    )


class Point2D(BaseModel):
    """A 2D coordinate on the SVG stadium map."""
    x: float
    y: float


# ── Route Response ──

class EgressRouteResponse(BaseModel):
    """Response containing the optimal egress route to a gate."""
    ticket_id: str
    transit_method: str
    target_gate_id: str
    target_gate_name: str
    distance_meters: int
    estimated_time_mins: int
    path: List[Point2D] = Field(
        ...,
        description="List of SVG points representing the route from seat to gate"
    )
    accessibility_features: Optional[List[str]] = Field(
        default=None,
        description="List of accessibility features on the route (e.g., 'Elevators', 'Ramps')"
    )
