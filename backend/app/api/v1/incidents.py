"""
===============================================================================
File: backend/app/api/v1/incidents.py
Purpose: Incident reporting API - fans/volunteers report problems, Gemini AI 
         triages (severity, category, action), dispatches volunteer, broadcasts 
         alert.
Architecture: POST /incidents (report) → Gemini triage → create DB record → 
             dispatch → broadcast.
Inputs: Incident description, category hint.
Outputs: Incident record with AI triage, dispatch action, alert broadcast.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_fan, get_current_staff, get_current_user, get_db
from app.core.exceptions import ForbiddenException
from app.core.config import get_settings
from app.core.rate_limiter import limiter
from app.schemas.incident import (
    IncidentCreateRequest,
    IncidentListResponse,
    IncidentResponse,
)
from app.services.dispatch_service import dispatch_volunteer
from app.services.incident_service import (
    create_incident,
    get_incident,
    list_incidents,
)

settings = get_settings()
router = APIRouter(prefix="/incidents", tags=["Incidents"])


# ──────────────────────────────────────────────
# POST /incidents/ — Report an incident
# ──────────────────────────────────────────────

@router.post(
    "/",
    response_model=None,
    summary="Report a new incident",
    description="Fan reports an issue (spill, broken seat, etc.). AI triage classifies severity.",
)
@limiter.limit(settings.RATE_LIMIT_AI)
async def report_incident(
    request: Request,
    body: IncidentCreateRequest,
    current_fan: Dict[str, Any] = Depends(get_current_fan),
    db: AsyncSession = Depends(get_db),
):
    """
    Fan reports an issue → AI triage → Incident created → Auto-dispatch if severe.
    """
    ticket_id = current_fan["sub"]
    seat_info = current_fan.get("seat", {})

    incident = await create_incident(
        db=db,
        ticket_id=ticket_id,
        description=body.description,
        seat_info=seat_info,
        location_description=body.location_description,
        image_url=body.image_base64,
    )

    # Auto-dispatch for high/critical severity
    assignment = None
    if incident.severity.value in ("high", "critical"):
        assignment = await dispatch_volunteer(db, incident.id)

    response_data = IncidentResponse(
        id=incident.id,
        ticket_id=incident.ticket_id,
        description=incident.description,
        severity=incident.severity.value,
        category=incident.category,
        status=incident.status.value,
        section_name=seat_info.get("section_name"),
        estimated_response_mins=incident.estimated_response_mins,
        suggested_action=incident.suggested_action,
        created_at=incident.created_at,
    )

    return {
        "success": True,
        "data": response_data.model_dump(),
        "volunteer_dispatched": assignment is not None,
        "request_id": getattr(request.state, "request_id", ""),
    }


# ──────────────────────────────────────────────
# GET /incidents/ — List incidents
# ──────────────────────────────────────────────

@router.get(
    "/",
    response_model=None,
    summary="List incidents",
    description="List incidents with optional filters. Accessible to any authenticated user.",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_all_incidents(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List incidents with pagination and filters."""
    role = current_user.get("role")
    if role not in {"fan", "volunteer", "admin"}:
        raise ForbiddenException("Authenticated stadium role required")
    # Fans may review only their own reports; staff see the operational queue.
    ticket_id = current_user["sub"] if role == "fan" else None
    incidents, total = await list_incidents(
        db, page, page_size, status, severity, ticket_id=ticket_id
    )

    items = [
        IncidentResponse(
            id=inc.id,
            ticket_id=inc.ticket_id,
            description=inc.description,
            severity=inc.severity.value,
            category=inc.category,
            status=inc.status.value,
            estimated_response_mins=inc.estimated_response_mins,
            suggested_action=inc.suggested_action,
            created_at=inc.created_at,
        )
        for inc in incidents
    ]

    return {
        "success": True,
        "data": IncidentListResponse(
            incidents=items,
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }


# ──────────────────────────────────────────────
# GET /incidents/{incident_id}
# ──────────────────────────────────────────────

@router.get(
    "/{incident_id}",
    response_model=None,
    summary="Get incident details",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_incident_detail(
    request: Request,
    incident_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get details for a specific incident."""
    incident = await get_incident(db, incident_id)
    if current_user.get("role") == "fan" and incident.ticket_id != current_user["sub"]:
        raise ForbiddenException("Fans can view only their own incident reports")

    return {
        "success": True,
        "data": IncidentResponse(
            id=incident.id,
            ticket_id=incident.ticket_id,
            description=incident.description,
            severity=incident.severity.value,
            category=incident.category,
            status=incident.status.value,
            estimated_response_mins=incident.estimated_response_mins,
            suggested_action=incident.suggested_action,
            created_at=incident.created_at,
        ).model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }


# ──────────────────────────────────────────────
# POST /incidents/{incident_id}/dispatch
# ──────────────────────────────────────────────

@router.post(
    "/{incident_id}/dispatch",
    response_model=None,
    summary="Manually dispatch a volunteer",
    description="Manually trigger volunteer dispatch for a specific incident.",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def manual_dispatch(
    request: Request,
    incident_id: str,
    current_user: Dict[str, Any] = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """Manually dispatch a volunteer to an incident."""
    assignment = await dispatch_volunteer(db, incident_id)

    if assignment:
        return {
            "success": True,
            "message": "Volunteer dispatched",
            "data": {
                "assignment_id": assignment.id,
                "volunteer_id": assignment.volunteer_id,
            },
            "request_id": getattr(request.state, "request_id", ""),
        }
    else:
        return {
            "success": False,
            "message": "No available volunteers at this time",
            "request_id": getattr(request.state, "request_id", ""),
        }


# ──────────────────────────────────────────────
# POST /incidents/{incident_id}/resolve
# ──────────────────────────────────────────────

@router.post(
    "/{incident_id}/resolve",
    response_model=None,
    summary="Resolve incident",
    description="Resolves the incident, frees the assigned volunteer, and notifies the fan.",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def resolve_incident_endpoint(
    request: Request,
    incident_id: str,
    current_user: Dict[str, Any] = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """Resolve an incident and free the assigned volunteer."""
    from app.models.incident import IncidentStatus
    from app.models.volunteer import Volunteer, VolunteerStatus
    from sqlalchemy import select
    from app.api.v1.websocket import manager
    
    incident = await get_incident(db, incident_id)
    if incident.status == IncidentStatus.RESOLVED:
        return {"success": True, "message": "Already resolved"}
        
    incident.status = IncidentStatus.RESOLVED
    
    if incident.assigned_volunteer_id:
        vol_stmt = select(Volunteer).where(Volunteer.id == incident.assigned_volunteer_id)
        vol = (await db.execute(vol_stmt)).scalar_one_or_none()
        if vol:
            vol.status = VolunteerStatus.AVAILABLE
            db.add(vol)
            
    db.add(incident)
    # db.commit() is handled automatically by the get_db dependency
    
    # Notify admin dashboard to refresh
    await manager.broadcast_to_admins({"type": "admin_refresh_required"})
    
    # Notify fan
    await manager.send_to_fan(
        incident.ticket_id, 
        {
            "type": "chat_message", 
            "role": "assistant", 
            "content": "✅ **UPDATE**: Your reported issue has been completely resolved and all set. Thank you for keeping the stadium safe!"
        }
    )
    
    return {"success": True, "message": "Incident resolved successfully"}
