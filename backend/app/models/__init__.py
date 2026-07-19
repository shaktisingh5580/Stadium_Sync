"""
===============================================================================
File: backend/app/models/__init__.py
Purpose: Core Backend Application Module.
Architecture: FastAPI backend module.
Inputs: standard API requests or internal service calls.
Outputs: structured responses/models.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""
Stadium Sync — Model Registry.

Imports all models so SQLAlchemy metadata can discover them
for table creation and Alembic migrations.
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
