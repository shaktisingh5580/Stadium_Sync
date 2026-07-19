"""
===============================================================================
File: backend/app/api/v1/navigation.py
Purpose: Core Backend Application Module.
Architecture: FastAPI backend module.
Inputs: standard API requests or internal service calls.
Outputs: structured responses/models.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""
Stadium Sync — Navigation API Routes.

Endpoints:
    POST /api/v1/navigation/transit     — Set post-match transit method
    GET  /api/v1/navigation/route       — Get dynamic egress route to gate
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_fan, get_db
from app.core.config import get_settings
from app.core.rate_limiter import limiter
from app.schemas.navigation import EgressRouteResponse, TransitChoiceRequest
from app.services.navigation_service import compute_egress_route, set_transit_choice

settings = get_settings()
router = APIRouter(prefix="/navigation", tags=["Navigation"])


# ──────────────────────────────────────────────
# POST /navigation/transit
# ──────────────────────────────────────────────

@router.post(
    "/transit",
    response_model=None,
    summary="Set transit preference",
    description="Updates the fan's preferred post-match transportation method.",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def update_transit_choice(
    request: Request,
    body: TransitChoiceRequest,
    current_fan: Dict[str, Any] = Depends(get_current_fan),
    db: AsyncSession = Depends(get_db),
):
    """
    Set the fan's transit choice (e.g., 'metro', 'bus', 'rideshare').
    This influences which gate they are routed to during egress.
    """
    ticket_id = current_fan["sub"]
    await set_transit_choice(db, ticket_id, body.transit_method)

    return {
        "success": True,
        "message": "Transit preference updated successfully",
        "data": {"transit_method": body.transit_method},
        "request_id": getattr(request.state, "request_id", ""),
    }


# ──────────────────────────────────────────────
# GET /navigation/route
# ──────────────────────────────────────────────

@router.get(
    "/route",
    response_model=None,
    summary="Get personalized egress route",
    description="Returns SVG path points and estimated time from seat to optimal gate.",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_egress_route(
    request: Request,
    current_fan: Dict[str, Any] = Depends(get_current_fan),
    db: AsyncSession = Depends(get_db),
):
    """
    Compute the personalized egress route for the current fan.
    """
    ticket_id = current_fan["sub"]
    route = await compute_egress_route(db, ticket_id)

    return {
        "success": True,
        "data": route.model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }
