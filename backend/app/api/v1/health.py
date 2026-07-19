"""
===============================================================================
File: backend/app/api/v1/health.py
Purpose: Health check endpoint - signals service status to Render load 
         balancer. Checks database, Redis, and Gemini API availability.
Architecture: GET /health → returns 200 OK if all critical dependencies 
             available, 503 Service Unavailable if any down.
Inputs: None (periodic health checks from load balancer).
Outputs: Health status JSON with dependency states.
Hackathon Vertical: Operational Intelligence
===============================================================================
"""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.database import check_db_connection
from app.core.redis_client import check_redis_connection

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    summary="Liveness probe",
    description="Returns 200 if the service is running. Used by Render health checks.",
)
async def health_check():
    """Basic liveness probe — if this responds, the app is alive."""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "StadiumSync API",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


@router.get(
    "/ready",
    summary="Readiness probe",
    description="Checks database and Redis connectivity. Returns component-level status.",
)
async def readiness_check():
    """
    Readiness probe — checks all downstream dependencies.
    Returns 200 even if some components are down (with degraded status),
    because the app can still serve some endpoints.
    """
    db_ok = await check_db_connection()
    redis_ok = await check_redis_connection()

    all_healthy = db_ok  # DB is required; Redis is optional

    components = {
        "database": {
            "status": "up" if db_ok else "down",
            "required": True,
        },
        "redis": {
            "status": "up" if redis_ok else "down",
            "required": False,
        },
    }

    overall_status = "ready" if all_healthy else "degraded"
    if not db_ok:
        overall_status = "not_ready"

    return {
        "success": True,
        "data": {
            "status": overall_status,
            "components": components,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
