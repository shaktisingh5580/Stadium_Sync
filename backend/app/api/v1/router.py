"""
Stadium Sync — V1 API Router Aggregator.

Includes all v1 route modules with their prefixes and tags.
New modules are added here as they are built in each phase.
"""

from fastapi import APIRouter

from app.api.v1.health import router as health_router

# ── Create the main V1 router ──
v1_router = APIRouter()

# ── Phase 1: Health ──
v1_router.include_router(health_router)

# ── Phase 2: Auth ──
from app.api.v1.auth import router as auth_router
v1_router.include_router(auth_router)

# ── Phase 3: Navigation ──
from app.api.v1.navigation import router as navigation_router
v1_router.include_router(navigation_router)

# ── Phase 4: Eco-Vision ──
from app.api.v1.eco_vision import router as eco_vision_router
v1_router.include_router(eco_vision_router)

# ── Phase 4: Incidents ──
from app.api.v1.incidents import router as incidents_router
v1_router.include_router(incidents_router)

# ── Phase 4: Volunteers ──
from app.api.v1.volunteers import router as volunteers_router
v1_router.include_router(volunteers_router)

# ── Phase 4: Webhooks (uncomment when built) ──
# from app.api.v1.webhooks.telegram import router as telegram_webhook_router
# v1_router.include_router(telegram_webhook_router)

# ── Phase 5: Crowd Data ──
from app.api.v1.crowd import router as crowd_router
v1_router.include_router(crowd_router)

# ── Phase 5: Egress ──
from app.api.v1.egress import router as egress_router
v1_router.include_router(egress_router)

# ── Phase 5: WebSocket ──
from app.api.v1.websocket import router as websocket_router
v1_router.include_router(websocket_router)

# ── Phase 6: Agentic Chat ──
from app.api.v1.chat import router as chat_router
v1_router.include_router(chat_router)

# ── Phase 7: Admin Command Center ──
from app.api.v1.admin import router as admin_router
v1_router.include_router(admin_router)

