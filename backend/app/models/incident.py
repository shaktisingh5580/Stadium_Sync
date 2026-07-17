"""
Stadium Sync — Incident and Incident Update Models.

Tracks fan-reported issues, AI triage results, and resolution updates.
"""

import enum

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Severity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    TRIAGED = "triaged"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class UpdateAuthorType(str, enum.Enum):
    SYSTEM = "system"
    FAN = "fan"
    VOLUNTEER = "volunteer"
    AI = "ai"


class Incident(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "incidents"

    ticket_id: Mapped[str] = mapped_column(
        ForeignKey("tickets.id"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location_description: Mapped[str] = mapped_column(Text, default="")
    section_id: Mapped[str] = mapped_column(
        ForeignKey("sections.id"), nullable=True
    )
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity), default=Severity.MEDIUM
    )
    category: Mapped[str] = mapped_column(String(50), default="other")
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus), default=IncidentStatus.OPEN
    )
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # AI triage
    ai_triage_result: Mapped[dict] = mapped_column(SQLiteJSON, nullable=True)
    suggested_action: Mapped[str] = mapped_column(Text, nullable=True)
    estimated_response_mins: Mapped[int] = mapped_column(Integer, default=10)

    assigned_volunteer_id: Mapped[str] = mapped_column(
        ForeignKey("volunteers.id"), nullable=True
    )
    resolved_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    updates = relationship(
        "IncidentUpdate", back_populates="incident",
        lazy="selectin", order_by="IncidentUpdate.created_at"
    )
    assigned_volunteer = relationship(
        "app.models.volunteer.Volunteer",
        primaryjoin="Incident.assigned_volunteer_id == foreign(app.models.volunteer.Volunteer.id)",
        lazy="selectin"
    )


class IncidentUpdate(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "incident_updates"

    incident_id: Mapped[str] = mapped_column(
        ForeignKey("incidents.id"), nullable=False
    )
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus), default=IncidentStatus.OPEN
    )
    note: Mapped[str] = mapped_column(Text, nullable=False)
    updated_by: Mapped[str] = mapped_column(String(100), default="system")

    # Relationships
    incident = relationship("Incident", back_populates="updates")
