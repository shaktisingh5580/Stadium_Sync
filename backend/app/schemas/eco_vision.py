"""
===============================================================================
File: backend/app/schemas/eco_vision.py
Purpose: Core Backend Application Module.
Architecture: FastAPI backend module.
Inputs: standard API requests or internal service calls.
Outputs: structured responses/models.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""
Stadium Sync — Eco-Vision Schemas.

Pydantic models for waste classification via photo.
"""

from pydantic import BaseModel, Field


class EcoVisionRequest(BaseModel):
    """Request body for waste image classification."""
    image_base64: str = Field(
        ...,
        description="Base64-encoded image of the waste item",
        min_length=100,
    )
    mime_type: str = Field(
        default="image/jpeg",
        description="MIME type of the image",
    )


class EcoVisionResponse(BaseModel):
    """Classification result from Gemini."""
    category: str
    item_name: str
    confidence: float
    bin_color: str
    instructions: str
    fun_fact: str
