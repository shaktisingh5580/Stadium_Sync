"""
===============================================================================
File: backend/app/models/__init__.py
Purpose: Package initialization for SQLAlchemy ORM models - centralizes model 
         exports and Base class for easy importing throughout codebase.
Architecture: Exports Base class (declarative base) and all model classes 
             (Ticket, Section, Incident, Crowd, Volunteer, etc.) to avoid 
             circular imports.
Inputs: None (package initialization)
Outputs: Centralized access to ORM models and Base for schema definition.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""

from app.models.base import Base  # noqa: F401

# ── Ticket & Stadium Topology ──
from app.models.ticket import (  # noqa: F401
    Gate,
    GateType,
    Seat,
    Section,
    SectionType,
    Stadium,
    Ticket,
    TransitMethod,
)

# ── Incidents ──
from app.models.incident import (  # noqa: F401
    Incident,
    IncidentStatus,
    IncidentUpdate,
    Severity,
    UpdateAuthorType,
)

# ── Volunteers ──
from app.models.volunteer import (  # noqa: F401
    AssignmentStatus,
    Volunteer,
    VolunteerAssignment,
    VolunteerStatus,
)

# ── Stadium Amenities ──
from app.models.stadium import (  # noqa: F401
    AmenityPoint,
    AmenityType,
    BinType,
    EcoClassification,
    WasteBin,
)

# ── Crowd & Egress ──
from app.models.crowd import (  # noqa: F401
    CrowdSnapshot,
    CrowdSource,
    DensityLevel,
    EgressAgentState,
    EgressAgentStatus,
    EgressRoute,
)

__all__ = [
    "Base",
    "Stadium", "Section", "Gate", "Seat", "Ticket",
    "SectionType", "GateType", "TransitMethod",
    "Incident", "IncidentUpdate", "Severity",
    "IncidentStatus", "UpdateAuthorType",
    "Volunteer", "VolunteerAssignment", "AssignmentStatus", "VolunteerStatus",
    "AmenityPoint", "WasteBin", "EcoClassification",
    "AmenityType", "BinType",
    "CrowdSnapshot", "EgressRoute", "EgressAgentState",
    "DensityLevel", "CrowdSource", "EgressAgentStatus",
]
