"""
===============================================================================
File: backend/app/services/incident_service.py
Purpose: Core Backend Application Module.
Architecture: FastAPI backend module.
Inputs: standard API requests or internal service calls.
Outputs: structured responses/models.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""
Stadium Sync — Incident Service.

Handles incident reporting, AI triage, and status tracking.
"""

import logging
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import NotFoundException, ForbiddenException
from app.core.audit_logger import write_operational_event
from app.models.incident import Incident, IncidentStatus, IncidentUpdate, Severity
from app.models.ticket import Seat, Section
from app.services.gemini_client import triage_incident
from app.api.v1.websocket import manager

logger = logging.getLogger(__name__)


async def create_incident(
    db: AsyncSession,
    ticket_id: str,
    description: str,
    seat_info: dict,
    location_description: Optional[str] = None,
    severity: str = "medium",
    category: str = "other",
    ai_triage_result: Optional[dict] = None,
    suggested_action: Optional[str] = None,
    image_url: Optional[str] = None,
) -> Incident:
    """
    Create a new incident and run AI triage.

    Flow:
    1. Extract section/row from the fan's seat info
    2. Run Gemini triage to classify severity
    3. Persist incident to the database
    """
    section_name = seat_info.get("section_name", "Unknown")
    
    # AI Triage
    if not ai_triage_result:
        triage = await triage_incident(description, section_name, seat_info.get("row", "Unknown"))
    else:
        triage = ai_triage_result

    # Map triage severity string to enum
    severity_map = {
        "low": Severity.LOW,
        "medium": Severity.MEDIUM,
        "high": Severity.HIGH,
        "critical": Severity.CRITICAL,
    }
    severity_enum = severity_map.get(triage.get("severity", severity), Severity.MEDIUM)

    incident = Incident(
        id=str(uuid.uuid4()),
        ticket_id=ticket_id,
        section_id=seat_info.get("section_id"),
        description=description,
        location_description=location_description,
        severity=severity_enum,
        category=triage.get("category", "other"),
        status=IncidentStatus.OPEN,
        ai_triage_result=triage,
        suggested_action=triage.get("suggested_action"),
        estimated_response_mins=triage.get("estimated_response_mins", 10),
        image_url=image_url,
    )

    # Automatically dispatch an available volunteer
    from app.models.volunteer import Volunteer, VolunteerStatus
    vol_stmt = select(Volunteer).where(Volunteer.status == VolunteerStatus.AVAILABLE).limit(1)
    vol_res = await db.execute(vol_stmt)
    volunteer = vol_res.scalar_one_or_none()

    if volunteer:
        incident.assigned_volunteer_id = volunteer.id
        incident.status = IncidentStatus.ASSIGNED
        volunteer.status = VolunteerStatus.BUSY

    db.add(incident)
    await db.flush()

    logger.info(
        f"Incident created: id={incident.id}, severity={severity_enum.value}, "
        f"category={triage.get('category')}, section={section_name}"
    )

    await manager.broadcast_to_admins({"type": "admin_refresh_required"})
    await write_operational_event(
        "incident_created",
        {
            "incident_id": incident.id,
            "ticket_id": incident.ticket_id,
            "section_id": incident.section_id,
            "severity": incident.severity,
            "category": incident.category,
            "status": incident.status,
        },
    )

    return incident


async def get_incident(db: AsyncSession, incident_id: str) -> Incident:
    """Fetch an incident by ID."""
    stmt = select(Incident).where(Incident.id == incident_id)
    result = await db.execute(stmt)
    incident = result.unique().scalar_one_or_none()

    if not incident:
        raise NotFoundException("Incident", incident_id)

    return incident


async def list_incidents(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    ticket_id: Optional[str] = None,
) -> Tuple[List[Incident], int]:
    """
    List incidents with optional filtering and pagination.
    """
    stmt = select(Incident).order_by(Incident.created_at.desc())

    # Filters
    if status:
        try:
            stmt = stmt.where(Incident.status == IncidentStatus(status))
        except ValueError:
            pass
    if severity:
        try:
            stmt = stmt.where(Incident.severity == Severity(severity))
        except ValueError:
            pass
    if ticket_id:
        stmt = stmt.where(Incident.ticket_id == ticket_id)

    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # Paginate
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    incidents = result.unique().scalars().all()

    return incidents, total


async def update_incident_status(
    db: AsyncSession,
    incident_id: str,
    new_status: str,
    note: str,
    updated_by: str,
) -> IncidentUpdate:
    """
    Update an incident's status and add a tracking note.
    """
    incident = await get_incident(db, incident_id)

    # Update status on the incident
    try:
        incident.status = IncidentStatus(new_status)
    except ValueError:
        from app.core.exceptions import BadRequestException
        raise BadRequestException(f"Invalid status: {new_status}")

    # Create update record
    update = IncidentUpdate(
        id=str(uuid.uuid4()),
        incident_id=incident.id,
        status=IncidentStatus(new_status),
        note=note,
        updated_by=updated_by,
    )

    db.add(incident)
    db.add(update)
    await db.flush()

    logger.info(f"Incident {incident_id} updated to {new_status} by {updated_by}")

    # Notify admins to refresh their dashboard
    await manager.broadcast_to_admins({"type": "admin_refresh_required"})

    # Send a confirmation message directly to the fan who reported it
    await manager.send_to_fan(
        incident.ticket_id,
        {
            "type": "chat_message",
            "role": "assistant",
            "content": f"✅ **Update on your report:** The incident has been marked as **{new_status.replace('_', ' ').upper()}**. \n\n*Note: {note}*"
        }
    )

    return update
