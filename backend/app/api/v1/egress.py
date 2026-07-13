"""
Stadium Sync — Egress Agent API Routes.

Endpoints:
    POST /api/v1/egress/trigger           — Trigger egress agent at 80th minute
    GET  /api/v1/egress/state/{match_id}  — Get agent state
    GET  /api/v1/egress/route             — Get fan's pre-computed egress route
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_fan, get_db
from app.core.config import get_settings
from app.core.rate_limiter import limiter
from app.schemas.crowd import EgressAgentStateResponse, EgressTriggerRequest
from app.services.egress_service import (
    get_agent_state,
    get_fan_egress_route,
    trigger_egress_agent,
)

settings = get_settings()
router = APIRouter(prefix="/egress", tags=["Egress Agent"])


# ──────────────────────────────────────────────
# POST /egress/trigger — Trigger the egress agent
# ──────────────────────────────────────────────

@router.post(
    "/trigger",
    response_model=None,
    summary="Trigger egress agent",
    description="Trigger batch route computation at the 80th minute. Computes routes for all active fans.",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def trigger_egress(
    request: Request,
    body: EgressTriggerRequest,
    current_user: Dict[str, Any] = Depends(get_current_fan),
    db: AsyncSession = Depends(get_db),
):
    """Trigger the egress agent to compute routes for all fans."""
    match_id = current_user.get("match_id", "")
    if not match_id:
        from app.core.exceptions import BadRequestException
        raise BadRequestException("No match_id in token")

    agent_state = await trigger_egress_agent(
        db=db,
        match_id=match_id,
        match_minute=body.match_minute,
        force=body.force,
    )

    return {
        "success": True,
        "data": EgressAgentStateResponse(
            status=agent_state.status.value,
            triggered_at=agent_state.triggered_at,
            routes_computed=agent_state.routes_computed,
            match_minute=agent_state.match_minute,
        ).model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }


# ──────────────────────────────────────────────
# GET /egress/state/{match_id}
# ──────────────────────────────────────────────

@router.get(
    "/state/{match_id}",
    response_model=None,
    summary="Get egress agent state",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_egress_state(
    request: Request,
    match_id: str,
    current_user: Dict[str, Any] = Depends(get_current_fan),
    db: AsyncSession = Depends(get_db),
):
    """Get the current egress agent state for a match."""
    state = await get_agent_state(db, match_id)

    if not state:
        return {
            "success": True,
            "data": EgressAgentStateResponse(
                status="idle",
                routes_computed=0,
                match_minute=0,
            ).model_dump(),
            "request_id": getattr(request.state, "request_id", ""),
        }

    return {
        "success": True,
        "data": EgressAgentStateResponse(
            status=state.status.value,
            triggered_at=state.triggered_at,
            routes_computed=state.routes_computed,
            match_minute=state.match_minute,
        ).model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }


# ──────────────────────────────────────────────
# GET /egress/route — Fan's personal route
# ──────────────────────────────────────────────

@router.get(
    "/route",
    response_model=None,
    summary="Get fan's pre-computed egress route",
    description="Returns the pre-computed egress route for the current fan after the agent trigger.",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_my_egress_route(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_fan),
    db: AsyncSession = Depends(get_db),
):
    """Get the fan's personal egress route."""
    ticket_id = current_user["sub"]
    match_id = current_user.get("match_id", "")

    route = await get_fan_egress_route(db, ticket_id, match_id)

    if not route:
        return {
            "success": True,
            "data": None,
            "message": "No egress route computed yet. Routes are generated near the end of the match.",
            "request_id": getattr(request.state, "request_id", ""),
        }

    return {
        "success": True,
        "data": {
            "ticket_id": route.ticket_id,
            "match_id": route.match_id,
            "gate_id": route.gate_id,
            "route": route.path_json,
            "computed_at": route.created_at.isoformat() if route.created_at else None,
        },
        "request_id": getattr(request.state, "request_id", ""),
    }
