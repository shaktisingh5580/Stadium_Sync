"""
Stadium Sync — Chat Schemas.

Pydantic models for the agentic chat endpoint.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in the conversation history."""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""
    message: str = Field(
        ...,
        description="The user's text message",
        min_length=1,
        max_length=2000,
    )
    history: List[ChatMessage] = Field(
        default_factory=list,
        description="Previous messages for conversational context",
    )
    image_base64: Optional[str] = Field(
        None,
        description="Optional base64-encoded image (for Eco-Vision classification)",
    )


class ChatResponse(BaseModel):
    """
    Structured response from the agentic chat.

    ui_action tells the frontend what dynamic action to perform:
    - NONE:              Just display the text message
    - SHOW_MAP:          Slide the stadium map canvas into view
    - HIDE_MAP:          Slide the map canvas out of view
    - REQUEST_IMAGE:     Render an image upload widget in the chat
    - SHOW_ECO_RESULT:   Display eco-vision classification result card
    - DISPATCH_INCIDENT: Display incident report confirmation card
    - SHOW_ROUTE:        Show navigation route on the map canvas
    - SHOW_CROWD:        Show crowd heatmap on the map canvas
    """
    message: str = Field(..., description="The AI's conversational reply")
    ui_action: str = Field(
        default="NONE",
        description="Frontend UI action command",
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Action-specific data (route points, eco result, incident details, etc.)",
    )
