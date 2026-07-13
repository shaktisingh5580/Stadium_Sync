"""
Stadium Sync — Navigation Schemas.

Pydantic models for transit selection and SVG pathfinding.
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
