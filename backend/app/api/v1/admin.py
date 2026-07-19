"""
===============================================================================
File: backend/app/api/v1/admin.py
Purpose: Admin command center API - provides operational dashboard, AI copilot, 
         emergency evacuation triggers, computer vision webhook intake, flash 
         sale targeting.
Architecture: Protected routes (admin-only). Endpoints: /admin/state (full 
             dashboard), /admin/chat (Gemini with context), /admin/evacuate 
             (broadcast routes), /admin/cv-webhook (edge node analysis).
Inputs: Admin queries, evacuation triggers, CV frames from edge cameras.
Outputs: Operational state (crowd density, incidents, volunteers), AI 
         recommendations, emergency broadcasts.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""

import random
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_admin, get_db, verify_api_key
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
async def get_admin_state(
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """
    Get the digital twin stadium state (incidents + crowd + predictions).
    """
    # Grab the first stadium for demo purposes
    stmt = select(Stadium).options(selectinload(Stadium.sections)).limit(1)
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
            "ticket_id": inc.ticket_id,
            "severity": inc.severity.value,
            "category": inc.category,
            "status": inc.status.value,
            "description": inc.description,
            "location_description": inc.location_description,
            "image_url": inc.image_url,
            "volunteer_name": vol_name
        })

    return {
        "stadium_id": stadium.id,
        "incidents": incident_data,
        "crowd_map": crowd_map.dict()
    }


@router.post("/chat")
async def chat_with_admin_ai(
    request: AdminChatRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """
    Chat with the Admin Copilot using the live stadium state.
    """
    # Fetch state
    state = await get_admin_state(db)
    
    # Chat with Gemini
    response = await admin_chat(request.message, state, request.history)
    
    if response.get("action") == "BROADCAST" and response.get("broadcast_payload"):
        payload = response["broadcast_payload"]
        await manager.broadcast_all(payload)
    
    return response

@router.post("/evacuate")
async def trigger_emergency_evacuation(
    request: EvacuateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
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
async def evaluate_vendor_promotions(
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
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

class CVWebhookRequest(BaseModel):
    type: str = Field(..., pattern="^(CROWD_CRITICAL|SECURITY_BREACH|MEDICAL_EMERGENCY)$")
    location: str = Field(..., max_length=100)
    confidence: float = Field(..., ge=0.0, le=1.0)
    description: str = Field("", max_length=500)

@router.post("/cv-webhook")
async def cv_webhook(
    request: CVWebhookRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """
    Webhook for Computer Vision edge nodes to report events.
    """
    state = await get_admin_state(db)
    
    # Let AI process the event without holding unnecessary locks
    
    # Let AI process the event
    from app.services.gemini_client import process_cv_event
    cv_data = request.dict()
    ai_response = await process_cv_event(cv_data, state)
    
    # Update crowd density by ingesting a new high-density snapshot
    if cv_data['type'] == 'CROWD_CRITICAL':
        from sqlalchemy import select
        from app.models.ticket import Section
        from app.services.crowd_service import ingest_crowd_data
        
        section_result = await db.execute(select(Section).where(Section.name == cv_data['location']))
        section = section_result.scalar_one_or_none()
        
        if section:
            # Ingest 98.5% density to trigger frontend filters
            await ingest_crowd_data(db, section.id, density_pct=98.5, source="camera")
    
    # Create incident in the DB
    from app.services.incident_service import create_incident
    
    ticket_id = "sim-cv-node"
    image_url = cv_data.get('image_url')
    
    incident = await create_incident(
        db=db,
        ticket_id=ticket_id,
        description=f"CV Alert ({cv_data['type']}): {cv_data['description']}",
        seat_info={"section_name": cv_data['location'], "section_id": "sim-sec"},
        location_description=cv_data['location'],
        severity=ai_response.get("severity", "high"),
        category=ai_response.get("category", "other"),
        ai_triage_result=ai_response,
        suggested_action=ai_response.get("action", "NONE"),
        image_url=image_url
    )
    
    await db.commit()
    
    # Broadcast to admins so chat pops up
    if ai_response.get("action") in ["ALERT_ADMIN", "AUTO_RESOLVE"]:
        payload = {
            "type": "chat_message",
            "role": "assistant",
            "content": ai_response.get("message", "CV Event Detected.")
        }
        if image_url:
            payload["image"] = image_url
            
        await manager.broadcast_to_admins(payload)
        
    return {"status": "success", "ai_decision": ai_response}
