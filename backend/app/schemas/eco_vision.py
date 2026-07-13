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
