"""
Stadium Sync — Crowd & Egress Schemas.

Pydantic models for crowd density ingestion, egress agent state, and WebSocket messages.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ── Crowd Density ──

class CrowdDensityIngest(BaseModel):
    """Inbound crowd density data from IoT sensors or manual input."""
    section_id: str = Field(..., description="Section being measured")
    density_pct: float = Field(
        ..., ge=0, le=100,
        description="Crowd density as a percentage of section capacity (0-100)"
    )
    source: str = Field(
        default="sensor",
        description="Data source: 'sensor', 'manual', 'camera'"
    )


class CrowdDensityResponse(BaseModel):
    """Response for a single crowd density reading."""
    section_id: str
    section_name: Optional[str] = None
    density_pct: float
    density_level: str  # low, moderate, high, critical
    timestamp: datetime
    predicted_mins_to_85: Optional[int] = None
    trend: Optional[str] = None
    sentiment_score: Optional[float] = None
    acoustic_status: Optional[str] = None


class StadiumCrowdMap(BaseModel):
    """Full stadium crowd density map — all sections."""
    stadium_id: str
    sections: List[CrowdDensityResponse]
    timestamp: datetime
    total_occupancy_pct: float


# ── Egress Agent ──

class EgressTriggerRequest(BaseModel):
    """Request to trigger the egress agent (usually at 80th minute)."""
    match_minute: int = Field(
        ..., ge=0, le=150,
        description="Current match minute (80+ triggers egress)"
    )
    force: bool = Field(
        default=False,
        description="Force trigger even if not at 80th minute"
    )


class EgressAgentStateResponse(BaseModel):
    """Current state of the egress agent."""
    status: str  # idle, computing, active, completed
    triggered_at: Optional[datetime] = None
    routes_computed: int = 0
    match_minute: int = 0


# ── WebSocket Messages ──

class WSMessage(BaseModel):
    """WebSocket message envelope."""
    type: str = Field(..., description="Message type: crowd_update, egress_route, incident_alert, notification")
    data: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
