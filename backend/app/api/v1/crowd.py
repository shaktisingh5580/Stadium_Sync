"""
===============================================================================
File: backend/app/api/v1/crowd.py
Purpose: Crowd data ingestion and broadcasting - IoT sensors post turnstile 
         counts, frontend fetches real-time heatmap, WebSocket broadcasts 
         congestion alerts.
Architecture: POST /crowd/ingest (IoT), GET /crowd/map/{match_id} (heatmap), 
             WebSocket broadcast on density threshold exceeded.
Inputs: IoT turnstile counts, match ID for heatmap query.
Outputs: Real-time density heatmap, WebSocket alerts, predictions.
Hackathon Vertical: Crowd Management & Real-Time Decision Support
===============================================================================
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_fan, get_db, verify_api_key
from app.core.config import get_settings
from app.core.rate_limiter import limiter
from app.schemas.crowd import CrowdDensityIngest, CrowdDensityResponse, StadiumCrowdMap
from app.services.crowd_service import ingest_crowd_data, get_stadium_crowd_map

settings = get_settings()
router = APIRouter(prefix="/crowd", tags=["Crowd Density"])


# ──────────────────────────────────────────────
# POST /crowd/ingest — IoT sensor data ingestion
# ──────────────────────────────────────────────

@router.post(
    "/ingest",
    response_model=None,
    summary="Ingest crowd density data",
    description="IoT sensors push crowd density readings. Authenticated via X-API-Key header.",
)
@limiter.limit(settings.RATE_LIMIT_IOT)
async def ingest_density(
    request: Request,
    body: CrowdDensityIngest,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Ingest crowd density data from IoT sensors."""
    snapshot = await ingest_crowd_data(
        db=db,
        section_id=body.section_id,
        density_pct=body.density_pct,
        source=body.source,
    )

    return {
        "success": True,
        "data": CrowdDensityResponse(
            section_id=snapshot.section_id,
            density_pct=snapshot.density_pct,
            density_level=snapshot.density_level.value,
            timestamp=snapshot.created_at,
        ).model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }


# ──────────────────────────────────────────────
# GET /crowd/map/{stadium_id} — Stadium crowd map
# ──────────────────────────────────────────────

@router.get(
    "/map/{stadium_id}",
    response_model=None,
    summary="Get stadium crowd density map",
    description="Returns latest density readings for all sections in a stadium.",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_crowd_map(
    request: Request,
    stadium_id: str,
    current_user: Dict[str, Any] = Depends(get_current_fan),
    db: AsyncSession = Depends(get_db),
):
    """Get the real-time crowd density map for a stadium."""
    crowd_map = await get_stadium_crowd_map(db, stadium_id)

    return {
        "success": True,
        "data": crowd_map.model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }
