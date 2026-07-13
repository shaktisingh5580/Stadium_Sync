"""
Stadium Sync — Stadium Amenity and Waste Bin Models.

Tracks restrooms, food courts, first-aid stations, and waste bins
with SVG coordinates for map rendering.
"""

import enum

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AmenityType(str, enum.Enum):
    RESTROOM = "restroom"
    FOOD = "food"
    FIRST_AID = "first_aid"
    WATER = "water"
    INFO = "info"
    MERCHANDISE = "merchandise"
    ATM = "atm"


class BinType(str, enum.Enum):
    COMPOST = "compost"
    RECYCLE = "recycle"
    LANDFILL = "landfill"
    SPECIAL = "special"  # e-waste, batteries, etc.


class AmenityPoint(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "amenity_points"

    stadium_id: Mapped[str] = mapped_column(
        ForeignKey("stadiums.id"), nullable=False
    )
    section_id: Mapped[str] = mapped_column(
        ForeignKey("sections.id"), nullable=True
    )
    amenity_type: Mapped[AmenityType] = mapped_column(
        Enum(AmenityType), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    # GPS coordinates
    lat: Mapped[float] = mapped_column(Float, default=0.0)
    lng: Mapped[float] = mapped_column(Float, default=0.0)
    # SVG position for map rendering
    svg_x: Mapped[float] = mapped_column(Float, default=0.0)
    svg_y: Mapped[float] = mapped_column(Float, default=0.0)
    # Operating status
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)
    floor_level: Mapped[int] = mapped_column(Integer, default=1)


class WasteBin(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "waste_bins"

    stadium_id: Mapped[str] = mapped_column(
        ForeignKey("stadiums.id"), nullable=False
    )
    section_id: Mapped[str] = mapped_column(
        ForeignKey("sections.id"), nullable=True
    )
    bin_type: Mapped[BinType] = mapped_column(
        Enum(BinType), nullable=False
    )
    # GPS coordinates
    lat: Mapped[float] = mapped_column(Float, default=0.0)
    lng: Mapped[float] = mapped_column(Float, default=0.0)
    # SVG position
    svg_x: Mapped[float] = mapped_column(Float, default=0.0)
    svg_y: Mapped[float] = mapped_column(Float, default=0.0)
    # Status
    is_full: Mapped[bool] = mapped_column(Boolean, default=False)
    fill_level_pct: Mapped[int] = mapped_column(Integer, default=0)


class EcoClassification(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Log of all Eco-Vision waste classification events."""
    __tablename__ = "eco_classifications"

    ticket_id: Mapped[str] = mapped_column(
        ForeignKey("tickets.id"), nullable=False
    )
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    bin_type: Mapped[BinType] = mapped_column(Enum(BinType), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    image_url: Mapped[str] = mapped_column(String(500), default="")
    instructions: Mapped[str] = mapped_column(String(500), default="")
