"""
Stadium Sync — Ticket, Seat, Section, and Gate Models.

These represent the core stadium topology and fan ticketing data.
"""

import enum

from sqlalchemy import (
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SectionType(str, enum.Enum):
    GENERAL = "general"
    VIP = "vip"
    PREMIUM = "premium"
    ACCESSIBLE = "accessible"


class GateType(str, enum.Enum):
    ENTRY = "entry"
    EXIT = "exit"
    EMERGENCY = "emergency"
    ENTRY_EXIT = "entry_exit"


class TransitMethod(str, enum.Enum):
    METRO = "metro"
    BUS = "bus"
    RIDESHARE = "rideshare"
    WALK = "walk"
    PARKING = "parking"


class Stadium(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "stadiums"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    svg_map_url: Mapped[str] = mapped_column(String(500), default="")

    # Relationships
    sections = relationship("Section", back_populates="stadium", lazy="selectin")
    gates = relationship("Gate", back_populates="stadium", lazy="selectin")


class Section(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "sections"

    stadium_id: Mapped[str] = mapped_column(
        ForeignKey("stadiums.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    section_type: Mapped[SectionType] = mapped_column(
        Enum(SectionType), default=SectionType.GENERAL
    )
    capacity: Mapped[int] = mapped_column(Integer, default=500)
    # SVG bounding box for the section overlay
    svg_x: Mapped[float] = mapped_column(Float, default=0.0)
    svg_y: Mapped[float] = mapped_column(Float, default=0.0)
    svg_width: Mapped[float] = mapped_column(Float, default=100.0)
    svg_height: Mapped[float] = mapped_column(Float, default=100.0)

    # Relationships
    stadium = relationship("Stadium", back_populates="sections")
    seats = relationship("Seat", back_populates="section", lazy="selectin")


class Gate(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "gates"

    stadium_id: Mapped[str] = mapped_column(
        ForeignKey("stadiums.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    gate_type: Mapped[GateType] = mapped_column(
        Enum(GateType), default=GateType.ENTRY_EXIT
    )
    capacity: Mapped[int] = mapped_column(Integer, default=2000)
    # GPS coordinates
    lat: Mapped[float] = mapped_column(Float, default=0.0)
    lng: Mapped[float] = mapped_column(Float, default=0.0)
    # SVG position
    svg_x: Mapped[float] = mapped_column(Float, default=0.0)
    svg_y: Mapped[float] = mapped_column(Float, default=0.0)
    # Transit method this gate is closest to
    nearest_transit: Mapped[str] = mapped_column(String(50), default="walk")

    # Relationships
    stadium = relationship("Stadium", back_populates="gates")


class Seat(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "seats"

    section_id: Mapped[str] = mapped_column(
        ForeignKey("sections.id"), nullable=False
    )
    row: Mapped[str] = mapped_column(String(10), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    # SVG position for seat highlighting
    svg_x: Mapped[float] = mapped_column(Float, default=0.0)
    svg_y: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    section = relationship("Section", back_populates="seats")
    ticket = relationship("Ticket", back_populates="seat", uselist=False)


class Ticket(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "tickets"

    match_id: Mapped[str] = mapped_column(String(50), nullable=False)
    seat_id: Mapped[str] = mapped_column(
        ForeignKey("seats.id"), nullable=False
    )
    qr_payload: Mapped[str] = mapped_column(
        Text, unique=True, nullable=False
    )
    holder_name: Mapped[str] = mapped_column(String(200), nullable=False)
    holder_email: Mapped[str] = mapped_column(String(200), default="")
    transit_choice: Mapped[str] = mapped_column(
        String(20), nullable=True, default=None
    )
    needs_accessibility: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_scanned: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    seat = relationship("Seat", back_populates="ticket", lazy="joined")
