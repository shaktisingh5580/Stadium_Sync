"""
===============================================================================
File: backend/app/models/volunteer.py
Purpose: Volunteer and dispatch tracking - models staff members with 
         geolocation, real-time position updates, and incident assignments.
Architecture: Volunteer (staff info), VolunteerLocation (GPS + timestamp), 
             Dispatch (incident assignment + ETA). VolunteerLocation updated 
             every 10s via mobile app.
Inputs: Volunteer GPS coordinates, incident assignments.
Outputs: Volunteer positions for dispatch routing, ETA calculations, admin 
         visibility, crowd management deployment.
Hackathon Vertical: Real-Time Decision Support & Crowd Management
===============================================================================
"""

import enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class VolunteerStatus(str, enum.Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"


class AssignmentStatus(str, enum.Enum):
    PENDING = "pending"
    DISPATCHED = "dispatched"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"


class Volunteer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "volunteers"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), default="")
    telegram_chat_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=True
    )
    section_id: Mapped[str] = mapped_column(
        ForeignKey("sections.id"), nullable=True
    )
    # Current GPS location (updated frequently)
    current_lat: Mapped[float] = mapped_column(Float, default=0.0)
    current_lng: Mapped[float] = mapped_column(Float, default=0.0)
    # Status enum
    status: Mapped[VolunteerStatus] = mapped_column(
        Enum(VolunteerStatus), default=VolunteerStatus.OFFLINE
    )
    # Skills as comma-separated (simple for MVP)
    skills: Mapped[str] = mapped_column(Text, default="general")

    # Relationships
    assignments = relationship(
        "VolunteerAssignment", back_populates="volunteer", lazy="selectin"
    )

    @property
    def skills_list(self) -> list:
        """Return skills as a list."""
        return [s.strip() for s in self.skills.split(",") if s.strip()]


class VolunteerAssignment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "volunteer_assignments"

    volunteer_id: Mapped[str] = mapped_column(
        ForeignKey("volunteers.id"), nullable=False
    )
    incident_id: Mapped[str] = mapped_column(
        ForeignKey("incidents.id"), nullable=False
    )
    status: Mapped[AssignmentStatus] = mapped_column(
        Enum(AssignmentStatus), default=AssignmentStatus.PENDING
    )
    assigned_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    responded_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    volunteer = relationship("Volunteer", back_populates="assignments")
