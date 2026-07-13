"""
Stadium Sync — Chat API Route.

The single agentic endpoint that powers the conversational UI.
All fan interactions flow through this route — it orchestrates
navigation, eco-vision, incidents, and crowd data internally.

Endpoints:
    POST /api/v1/chat  — Send a message, get AI response + UI action
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_fan, get_db
from app.core.config import get_settings
from app.core.rate_limiter import limiter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.gemini_client import agentic_chat, classify_waste_image
from app.services.incident_service import create_incident
from app.services.navigation_service import compute_egress_route

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "",
    response_model=None,
    summary="Conversational stadium concierge",
    description=(
        "Send a message to the Stadium AI concierge. "
        "Returns a conversational reply plus a ui_action that tells "
        "the frontend what visual behavior to trigger (show map, "
        "upload widget, incident card, etc.)."
    ),
)
@limiter.limit(settings.RATE_LIMIT_AI)
async def chat(
    request: Request,
    body: ChatRequest,
    current_fan: Dict[str, Any] = Depends(get_current_fan),
    db: AsyncSession = Depends(get_db),
):
    """
    Fan sends a message → Gemini classifies intent →
    Backend orchestrates internal services →
    Returns structured response with UI action.
    """
    ticket_id = current_fan["sub"]
    seat_info = current_fan.get("seat", {})

    # Build fan context for the AI
    fan_context = {
        "holder_name": current_fan.get("holder_name", "Fan"),
        "section": seat_info.get("section_name", "Unknown"),
        "row": seat_info.get("row", "Unknown"),
        "seat_number": seat_info.get("number", "Unknown"),
        "match_id": current_fan.get("match_id", "Unknown"),
        "transit_method": current_fan.get("transit_method", "not set"),
    }

    # Convert history to list of dicts
    history = [{"role": m.role, "content": m.content} for m in body.history]

    # ── Step 1: Get the AI's response ──
    msg = body.message.strip().lower()
    
    if msg == "/seat":
        ai_response = {
            "message": "Let me show you the way to your seat! I'll highlight it on the map. 🎯",
            "ui_action": "SHOW_MAP",
            "payload": {"target": "seat"}
        }
    elif msg == "/eco":
        ai_response = {
            "message": "I can help you sort your waste! 📸 Please upload a photo of the item and I'll tell you which bin to use.",
            "ui_action": "REQUEST_IMAGE",
            "payload": {}
        }
    elif msg == "/report":
        ai_response = {
            "message": "Please describe the incident or issue you'd like to report, or upload a photo.",
            "ui_action": "NONE",
            "payload": {}
        }
    elif msg == "/scan":
        ai_response = {
            "message": "Please scan your QR ticket at the gate terminal to enter the stadium.",
            "ui_action": "NONE",
            "payload": {}
        }
    else:
        ai_response = await agentic_chat(
            message=body.message,
            history=history,
            fan_context=fan_context,
            image_base64=body.image_base64,
        )

    ui_action = ai_response.get("ui_action", "NONE")
    payload = ai_response.get("payload", {})

    # ── Step 2: Execute side-effects based on ui_action ──

    # If incident dispatch → actually create the incident in DB
    if ui_action == "DISPATCH_INCIDENT" and payload.get("description"):
        try:
            incident = await create_incident(
                db=db,
                ticket_id=ticket_id,
                description=payload["description"],
                seat_info=seat_info,
                location_description=f"Section {seat_info.get('section_name', 'Unknown')}",
            )
            payload["incident_id"] = incident.id
            payload["severity"] = incident.severity.value
            payload["category"] = incident.category
            payload["status"] = incident.status.value
            payload["estimated_response_mins"] = incident.estimated_response_mins
            logger.info(f"Chat-dispatched incident {incident.id} for ticket {ticket_id}")
        except Exception as e:
            logger.error(f"Failed to create incident from chat: {e}")
            # Still return the AI message, just without the DB-backed data

    # If show map for seat, inject the seat coordinates
    if ui_action == "SHOW_MAP" and payload.get("target") == "seat":
        try:
            from app.models.ticket import Ticket
            from sqlalchemy.orm import joinedload
            from sqlalchemy import select
            
            stmt = select(Ticket).options(joinedload(Ticket.seat)).where(Ticket.id == ticket_id)
            result = await db.execute(stmt)
            ticket = result.unique().scalar_one_or_none()
            
            if ticket and ticket.seat:
                payload["seat_coordinates"] = {"x": ticket.seat.svg_x, "y": ticket.seat.svg_y}
            else:
                payload["seat_coordinates"] = {"x": 275.0, "y": 132.0}
        except Exception as e:
            logger.error(f"Failed to fetch seat coordinates for SHOW_MAP: {e}")
            payload["seat_coordinates"] = {"x": 275.0, "y": 132.0}

    # If show route → compute the actual SVG route
    if ui_action == "SHOW_ROUTE":
        try:
            target = payload.get("target")
            
            # Fallback: if target is "seat" or not set, try to infer from the AI's message
            if not target or target == "seat":
                msg_lower = ai_response.get("message", "").lower()
                if "south gate" in msg_lower or "gate south" in msg_lower:
                    target = "gate_south"
                elif "north gate" in msg_lower or "gate north" in msg_lower:
                    target = "gate_north"
                elif "east gate" in msg_lower or "gate east" in msg_lower:
                    target = "gate_east"
                elif "west gate" in msg_lower or "gate west" in msg_lower:
                    target = "gate_west"
                    
            route = await compute_egress_route(db, ticket_id, target)
            payload["route"] = {
                "target_gate_name": route.target_gate_name,
                "distance_meters": route.distance_meters,
                "estimated_time_mins": route.estimated_time_mins,
                "path": [{"x": p.x, "y": p.y} for p in route.path],
            }
            logger.info(f"Chat computed route for ticket {ticket_id}")
        except Exception as e:
            logger.error(f"Failed to compute route from chat: {e}")
            # Fallback to just showing the map without route data
            ai_response["ui_action"] = "SHOW_MAP"

    # If eco-vision with image or chat request → classify the waste
    if ui_action in ("SHOW_ECO_RESULT", "REQUEST_IMAGE"):
        try:
            if body.image_base64:
                eco_result = await classify_waste_image(body.image_base64)
                payload.update(eco_result)
                ai_response["ui_action"] = "SHOW_ECO_RESULT"
                
                # Dynamic message based on bin color
                bin_color = eco_result.get('bin_color', 'correct')
                item_name = eco_result.get('item_name', 'item')
                category = eco_result.get('category', 'Recycling')
                
                ai_response["message"] = (
                    f"I've analyzed your image! This looks like a **{item_name}**. "
                    f"Please dispose of it in the **{bin_color.title()} "
                    f"{category.title()} Bin**. "
                    f"💡 {eco_result.get('fun_fact', '')}"
                )
            else:
                # Text-only eco vision interaction (no image provided)
                pass
            
            # Draw a beautiful curved route from the user's seat to the nearest eco bin
            from app.models.ticket import Ticket
            from sqlalchemy.orm import joinedload
            from sqlalchemy import select
            import math
            
            stmt = select(Ticket).options(joinedload(Ticket.seat)).where(Ticket.id == ticket_id)
            result = await db.execute(stmt)
            ticket = result.unique().scalar_one_or_none()
            
            # Default to a nice N1 section seat if no seat in DB
            seat_x = ticket.seat.svg_x if (ticket and ticket.seat) else 275.0
            seat_y = ticket.seat.svg_y if (ticket and ticket.seat) else 132.0
            
            # Nearest Dustbin location at (290, 225) on the SVG
            bin_x, bin_y = 290.0, 225.0
            
            cx, cy = 400.0, 400.0
            seat_th = math.atan2(seat_y - cy, seat_x - cx)
            bin_th = math.atan2(bin_y - cy, bin_x - cx)
            
            diff = bin_th - seat_th
            diff = (diff + math.pi) % (2 * math.pi) - math.pi
            
            safe_r = 340.0 # Outer concourse radius
            
            path = [{"x": seat_x, "y": seat_y}]
            steps = 12
            for i in range(1, steps):
                th = seat_th + diff * (i / steps)
                path.append({"x": cx + safe_r * math.cos(th), "y": cy + safe_r * math.sin(th)})
            path.append({"x": bin_x, "y": bin_y})

            payload["route"] = {
                "target_gate_name": "Nearest Recycling Bin",
                "distance_meters": 45,
                "estimated_time_mins": 1,
                "path": path
            }
            logger.info(f"Chat classified waste for ticket {ticket_id}")
        except Exception as e:
            logger.error(f"Failed to classify waste from chat: {e}")

    # Build final response
    response = ChatResponse(
        message=ai_response.get("message", "I'm here to help!"),
        ui_action=ai_response.get("ui_action", "NONE"),
        payload=payload,
    )

    return {
        "success": True,
        "data": response.model_dump(),
        "request_id": getattr(request.state, "request_id", ""),
    }
