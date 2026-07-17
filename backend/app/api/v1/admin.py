"""
Stadium Sync — Admin API Router.

Endpoints for the Organizer Command Center.
"""

import random
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.models.ticket import Stadium
from app.models.incident import Incident
from app.services.crowd_service import get_stadium_crowd_map
from app.services.gemini_client import admin_chat
from app.api.v1.websocket import manager
from typing import Optional

router = APIRouter(prefix="/admin", tags=["admin"])

class AdminChatRequest(BaseModel):
    message: str
    history: list = []

class EvacuateRequest(BaseModel):
    hazard_zone: Optional[str] = None

@router.get("/state")
async def get_admin_state(db: AsyncSession = Depends(get_db)):
    """
    Get the digital twin stadium state (incidents + crowd + predictions).
    """
    # Grab the first stadium for demo purposes
    stmt = select(Stadium).limit(1)
    result = await db.execute(stmt)
    stadium = result.unique().scalar_one_or_none()

    if not stadium:
        return {"error": "No stadium configured"}

    # Get active incidents (OPEN or ASSIGNED)
    stmt = select(Incident).where(Incident.status.in_(["open", "assigned"])).order_by(Incident.created_at.desc()).limit(100)
    result = await db.execute(stmt)
    incidents = result.unique().scalars().all()
    
    # Get crowd map
    crowd_map = await get_stadium_crowd_map(db, stadium.id)

    # Format incident output
    incident_data = []
    for inc in incidents:
        vol_name = None
        if inc.assigned_volunteer_id:
            from app.models.volunteer import Volunteer
            vol_stmt = select(Volunteer.name).where(Volunteer.id == inc.assigned_volunteer_id)
            vol_name = (await db.execute(vol_stmt)).scalar_one_or_none()

        incident_data.append({
            "id": inc.id,
            "severity": inc.severity.value,
            "category": inc.category,
            "status": inc.status.value,
            "description": inc.description,
            "volunteer_name": vol_name
        })

    return {
        "stadium_id": stadium.id,
        "incidents": incident_data,
        "crowd_map": crowd_map.dict()
    }


@router.post("/chat")
async def chat_with_admin_ai(request: AdminChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Chat with the Admin Copilot using the live stadium state.
    """
    # Fetch state
    state = await get_admin_state(db)
    
    # Chat with Gemini
    response = await admin_chat(request.message, state, request.history)
    
    return response

@router.post("/evacuate")
async def trigger_emergency_evacuation(request: EvacuateRequest, db: AsyncSession = Depends(get_db)):
    """
    Trigger a stadium-wide emergency evacuation.
    Broadcasts specialized egress routes to all fans.
    """
    await manager.broadcast_all({
        "type": "emergency_evacuate",
        "hazard_zone": request.hazard_zone,
        "message": "EMERGENCY EVACUATION. PLEASE PROCEED TO THE NEAREST SAFE EXIT IMMEDIATELY."
    })
    
    return {"status": "evacuation_triggered"}

@router.post("/evaluate-promotions")
async def evaluate_vendor_promotions(db: AsyncSession = Depends(get_db)):
    """
    Simulates AI analyzing crowd densities to trigger flash sales at underutilized vendors.
    """
    state = await get_admin_state(db)
    if "error" in state:
        return state
        
    crowd_map = state["crowd_map"]
    sections = crowd_map.get("sections", [])
    
    # Find low density sections
    low_density_sections = [s for s in sections if s["density_pct"] < 50]
    
    if not low_density_sections:
        return {"status": "no_promotions", "message": "All vendors are currently busy."}
        
    target_section = random.choice(low_density_sections)
    
    # Simulate a vendor in this section
    vendor_name = f"{target_section['section_name']} Concessions"
    discount = random.choice(["20% OFF", "FREE DRINK", "BUY 1 GET 1 FREE"])
    
    promotion_payload = {
        "type": "flash_sale",
        "vendor_name": vendor_name,
        "section_id": target_section["section_id"],
        "discount": discount,
        "message": f"FLASH SALE! Lines are short at {vendor_name}. {discount} for the next 10 minutes!",
        "duration_mins": 10
    }
    
    # Broadcast to all users
    await manager.broadcast_all(promotion_payload)
    
    return {"status": "promotions_triggered", "promotion": promotion_payload}
