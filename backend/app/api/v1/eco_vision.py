"""
===============================================================================
File: backend/app/api/v1/eco_vision.py
Purpose: Sustainability: waste classification API - camera image → Gemini 
         Vision classifies waste type → routes to nearest bin with eco facts.
Architecture: POST /eco-vision/classify (base64 image) → Gemini Vision → 
             returns waste classification + bin routing.
Inputs: Base64-encoded waste image.
Outputs: Waste type, bin color, nearest bin location, environmental fact.
Hackathon Vertical: Sustainability
===============================================================================
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_fan, get_db
from app.core.config import get_settings
from app.core.rate_limiter import limiter
from app.schemas.eco_vision import EcoVisionRequest, EcoVisionResponse
from app.services.gemini_client import classify_waste_image

settings = get_settings()
router = APIRouter(prefix="/eco-vision", tags=["Eco-Vision"])


@router.post(
    "/classify",
    response_model=None,
    summary="Classify waste from photo",
    description="Upload a base64-encoded photo of waste. Gemini AI will classify it and tell you which bin to use.",
)
@limiter.limit(settings.RATE_LIMIT_AI)
async def classify_waste(
    request: Request,
    body: EcoVisionRequest,
    current_fan: Dict[str, Any] = Depends(get_current_fan),
    db: AsyncSession = Depends(get_db),
):
    """
    Fan snaps a photo of trash → AI identifies what bin to use.
    """
    result = await classify_waste_image(body.image_base64, body.mime_type)

    return {
        "success": True,
        "data": EcoVisionResponse(**result).model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }
