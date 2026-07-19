"""
===============================================================================
File: backend/app/schemas/eco_vision.py
Purpose: Eco-Vision AI schemas - validates waste camera image input and 
         structures Gemini Vision classification response.
Architecture: WasteClassificationRequest (base64 image), 
             WasteClassificationResponse (waste_type, bin_color, confidence, 
             eco_fact).
Inputs: Base64-encoded camera image from fan.
Outputs: AI-classified waste type, bin color, and nearest bin routing.
Hackathon Vertical: Sustainability
===============================================================================
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
