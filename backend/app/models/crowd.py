"""
===============================================================================
File: backend/app/models/crowd.py
Purpose: Core Backend Application Module.
Architecture: FastAPI backend module.
Inputs: standard API requests or internal service calls.
Outputs: structured responses/models.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""
Stadium Sync — Crowd Density and Egress Route Models.

Tracks real-time crowd snapshots from IoT sensors and computed exit routes.
"""

import enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DensityLevel(str, enum.Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class CrowdSource(str, enum.Enum):
    IOT_SENSOR = "sensor"
    CAMERA = "camera"
    MANUAL = "manual"
    SIMULATOR = "simulator"


class EgressAgentStatus(str, enum.Enum):
    IDLE = "idle"
    COMPUTING = "computing"
    ACTIVE = "active"
    COMPLETED = "completed"


class CrowdSnapshot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Real-time crowd density data point from an IoT sensor."""
    __tablename__ = "crowd_snapshots"

    section_id: Mapped[str] = mapped_column(
        ForeignKey("sections.id"), nullable=False
    )
    stadium_id: Mapped[str] = mapped_column(
        ForeignKey("stadiums.id"), nullable=False
    )
    density_pct: Mapped[float] = mapped_column(Float, nullable=False)
    density_level: Mapped[DensityLevel] = mapped_column(
        Enum(DensityLevel), default=DensityLevel.LOW
    )
    source: Mapped[CrowdSource] = mapped_column(
        Enum(CrowdSource), default=CrowdSource.IOT_SENSOR
    )
    occupancy_count: Mapped[int] = mapped_column(Integer, default=0)


class EgressRoute(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Pre-computed exit route for a specific fan."""
    __tablename__ = "egress_routes"

    ticket_id: Mapped[str] = mapped_column(
        ForeignKey("tickets.id"), nullable=False
    )
    match_id: Mapped[str] = mapped_column(String(50), nullable=False)
    gate_id: Mapped[str] = mapped_column(
        ForeignKey("gates.id"), nullable=False
    )
    path_json: Mapped[dict] = mapped_column(SQLiteJSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class EgressAgentState(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Tracks the egress agent's state machine for a match."""
    __tablename__ = "egress_agent_state"

    match_id: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[EgressAgentStatus] = mapped_column(
        Enum(EgressAgentStatus), default=EgressAgentStatus.IDLE
    )
    match_minute: Mapped[int] = mapped_column(Integer, default=0)
    routes_computed: Mapped[int] = mapped_column(Integer, default=0)
    triggered_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
