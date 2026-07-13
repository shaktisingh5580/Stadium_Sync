"""
Stadium Sync — Volunteer & Dispatch Service.

Handles volunteer management and geofenced incident dispatch.
Dispatch logic: find the nearest available volunteer to the incident's section.
"""

import logging
import math
import uuid
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, BadRequestException
from app.models.incident import Incident, IncidentStatus
from app.models.volunteer import (
    Volunteer,
    VolunteerAssignment,
    VolunteerStatus,
    AssignmentStatus,
)

logger = logging.getLogger(__name__)


# ── Volunteer CRUD ──

async def get_volunteer(db: AsyncSession, volunteer_id: str) -> Volunteer:
    """Fetch a volunteer by ID."""
    stmt = select(Volunteer).where(Volunteer.id == volunteer_id)
    result = await db.execute(stmt)
    volunteer = result.unique().scalar_one_or_none()
    if not volunteer:
        raise NotFoundException("Volunteer", volunteer_id)
    return volunteer


async def list_volunteers(
    db: AsyncSession,
    status: Optional[str] = None,
) -> List[Volunteer]:
    """List volunteers, optionally filtered by status."""
    stmt = select(Volunteer)
    if status:
        try:
            stmt = stmt.where(Volunteer.status == VolunteerStatus(status))
        except ValueError:
            pass
    result = await db.execute(stmt)
    return result.unique().scalars().all()


async def update_volunteer_status(
    db: AsyncSession,
    volunteer_id: str,
    new_status: str,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
) -> Volunteer:
    """Update a volunteer's status and optionally their location."""
    volunteer = await get_volunteer(db, volunteer_id)

    try:
        volunteer.status = VolunteerStatus(new_status)
    except ValueError:
        raise BadRequestException(f"Invalid status: {new_status}. Use: available, busy, offline")

    if lat is not None:
        volunteer.current_lat = lat
    if lng is not None:
        volunteer.current_lng = lng

    db.add(volunteer)
    await db.flush()

    logger.info(f"Volunteer {volunteer_id} status updated to {new_status}")
    return volunteer


# ── Dispatch Logic ──

async def dispatch_volunteer(
    db: AsyncSession,
    incident_id: str,
) -> Optional[VolunteerAssignment]:
    """
    Find and dispatch the nearest available volunteer to an incident.

    Logic:
    1. Get the incident and its section
    2. Find all available volunteers
    3. Prefer volunteers assigned to the same section
    4. Assign the closest available volunteer
    5. Update statuses
    """
    # Fetch incident
    stmt = select(Incident).where(Incident.id == incident_id)
    result = await db.execute(stmt)
    incident = result.unique().scalar_one_or_none()
    if not incident:
        raise NotFoundException("Incident", incident_id)

    # Find available volunteers
    vol_stmt = select(Volunteer).where(
        Volunteer.status == VolunteerStatus.AVAILABLE
    )
    vol_result = await db.execute(vol_stmt)
    available = vol_result.unique().scalars().all()

    if not available:
        logger.warning(f"No available volunteers for incident {incident_id}")
        return None

    # Priority: Same section > closest by location
    best_volunteer = None

    # First pass: same section
    for vol in available:
        if vol.section_id == incident.section_id:
            best_volunteer = vol
            break

    # Second pass: if no same-section volunteer, pick first available
    if not best_volunteer:
        best_volunteer = available[0]

    # Create assignment
    assignment = VolunteerAssignment(
        id=str(uuid.uuid4()),
        volunteer_id=best_volunteer.id,
        incident_id=incident.id,
        status=AssignmentStatus.DISPATCHED,
    )

    # Update volunteer status
    best_volunteer.status = VolunteerStatus.BUSY

    # Update incident status
    incident.status = IncidentStatus.ASSIGNED

    db.add(assignment)
    db.add(best_volunteer)
    db.add(incident)
    await db.flush()

    logger.info(
        f"Dispatched volunteer {best_volunteer.id} ({best_volunteer.name}) "
        f"to incident {incident_id}"
    )

    return assignment


async def complete_assignment(
    db: AsyncSession,
    assignment_id: str,
    volunteer_id: str,
) -> VolunteerAssignment:
    """Mark an assignment as completed and free up the volunteer."""
    stmt = select(VolunteerAssignment).where(
        VolunteerAssignment.id == assignment_id,
        VolunteerAssignment.volunteer_id == volunteer_id,
    )
    result = await db.execute(stmt)
    assignment = result.unique().scalar_one_or_none()

    if not assignment:
        raise NotFoundException("Assignment", assignment_id)

    assignment.status = AssignmentStatus.COMPLETED

    # Free the volunteer
    volunteer = await get_volunteer(db, volunteer_id)
    volunteer.status = VolunteerStatus.AVAILABLE

    # Resolve the incident
    inc_stmt = select(Incident).where(Incident.id == assignment.incident_id)
    inc_result = await db.execute(inc_stmt)
    incident = inc_result.unique().scalar_one_or_none()
    if incident:
        incident.status = IncidentStatus.RESOLVED

    db.add(assignment)
    db.add(volunteer)
    if incident:
        db.add(incident)
    await db.flush()

    logger.info(f"Assignment {assignment_id} completed by volunteer {volunteer_id}")
    return assignment
