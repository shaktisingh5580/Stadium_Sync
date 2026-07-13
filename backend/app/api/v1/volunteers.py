"""
Stadium Sync — Volunteer API Routes.

Endpoints:
    GET  /api/v1/volunteers/                          — List volunteers
    GET  /api/v1/volunteers/me                         — Get current volunteer profile
    POST /api/v1/volunteers/status                     — Update status & location
    POST /api/v1/volunteers/assignments/{id}/complete  — Complete an assignment
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_volunteer, get_db
from app.core.config import get_settings
from app.core.rate_limiter import limiter
from app.schemas.volunteer import (
    AssignmentResponse,
    VolunteerListResponse,
    VolunteerResponse,
    VolunteerStatusUpdate,
)
from app.services.dispatch_service import (
    complete_assignment,
    get_volunteer,
    list_volunteers,
    update_volunteer_status,
)

settings = get_settings()
router = APIRouter(prefix="/volunteers", tags=["Volunteers"])


# ──────────────────────────────────────────────
# GET /volunteers/ — List all volunteers
# ──────────────────────────────────────────────

@router.get(
    "/",
    response_model=None,
    summary="List volunteers",
    description="List all volunteers, optionally filtered by status.",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_all_volunteers(
    request: Request,
    status: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List volunteers with optional status filter."""
    volunteers = await list_volunteers(db, status)

    items = [
        VolunteerResponse(
            id=v.id,
            name=v.name,
            section_id=v.section_id,
            status=v.status.value,
            current_lat=v.current_lat,
            current_lng=v.current_lng,
        )
        for v in volunteers
    ]

    return {
        "success": True,
        "data": VolunteerListResponse(
            volunteers=items,
            total=len(items),
        ).model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }


# ──────────────────────────────────────────────
# GET /volunteers/me — Current volunteer's profile
# ──────────────────────────────────────────────

@router.get(
    "/me",
    response_model=None,
    summary="Get volunteer profile",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_my_profile(
    request: Request,
    current_vol: Dict[str, Any] = Depends(get_current_volunteer),
    db: AsyncSession = Depends(get_db),
):
    """Get the current volunteer's profile data."""
    volunteer = await get_volunteer(db, current_vol["sub"])

    return {
        "success": True,
        "data": VolunteerResponse(
            id=volunteer.id,
            name=volunteer.name,
            section_id=volunteer.section_id,
            status=volunteer.status.value,
            current_lat=volunteer.current_lat,
            current_lng=volunteer.current_lng,
        ).model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }


# ──────────────────────────────────────────────
# POST /volunteers/status — Update status & location
# ──────────────────────────────────────────────

@router.post(
    "/status",
    response_model=None,
    summary="Update volunteer status",
    description="Update availability status and optionally GPS location.",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def update_status(
    request: Request,
    body: VolunteerStatusUpdate,
    current_vol: Dict[str, Any] = Depends(get_current_volunteer),
    db: AsyncSession = Depends(get_db),
):
    """Volunteer updates their status (available/busy/offline) and location."""
    volunteer = await update_volunteer_status(
        db=db,
        volunteer_id=current_vol["sub"],
        new_status=body.status,
        lat=body.lat,
        lng=body.lng,
    )

    return {
        "success": True,
        "message": f"Status updated to {body.status}",
        "data": VolunteerResponse(
            id=volunteer.id,
            name=volunteer.name,
            section_id=volunteer.section_id,
            status=volunteer.status.value,
            current_lat=volunteer.current_lat,
            current_lng=volunteer.current_lng,
        ).model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }


# ──────────────────────────────────────────────
# POST /volunteers/assignments/{id}/complete
# ──────────────────────────────────────────────

@router.post(
    "/assignments/{assignment_id}/complete",
    response_model=None,
    summary="Complete an assignment",
    description="Volunteer marks an assignment as completed.",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def complete_volunteer_assignment(
    request: Request,
    assignment_id: str,
    current_vol: Dict[str, Any] = Depends(get_current_volunteer),
    db: AsyncSession = Depends(get_db),
):
    """Volunteer completes their assigned task."""
    assignment = await complete_assignment(
        db=db,
        assignment_id=assignment_id,
        volunteer_id=current_vol["sub"],
    )

    return {
        "success": True,
        "message": "Assignment completed",
        "data": AssignmentResponse(
            id=assignment.id,
            volunteer_id=assignment.volunteer_id,
            incident_id=assignment.incident_id,
            status=assignment.status.value,
            assigned_at=assignment.created_at,
        ).model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }
