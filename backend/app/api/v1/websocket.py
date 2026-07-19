"""
===============================================================================
File: backend/app/api/v1/websocket.py
Purpose: WebSocket manager - persistent bidirectional connections for 
         real-time alerts (evacuation, crowd, incidents). Replaces polling 
         for instant delivery (< 500ms latency).
Architecture: WS /api/v1/ws?token=jwt → validate JWT → add to connection pool 
             → subscribe to events → broadcast messages → auto-reconnect on 
             failure.
Inputs: JWT token for authentication, real-time events (admin broadcasts, 
        crowd alerts, incident updates).
Outputs: Real-time message delivery to connected fans.
Hackathon Vertical: Real-Time Decision Support & Crowd Management
===============================================================================
"""

import json
import logging
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.core.security import verify_token
from app.core.exceptions import UnauthorizedException

logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSocket"])

# ── Connection Manager ──

class ConnectionManager:
    """
    Manages active WebSocket connections.
    Supports broadcast (all fans) and targeted (by ticket_id) messaging.
    """

    def __init__(self):
        # ticket_id → WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # section_id → set of ticket_ids
        self.section_subscribers: Dict[str, Set[str]] = {}
        # admin ticket_ids
        self.admin_subscribers: Set[str] = set()

    async def connect(self, websocket: WebSocket, ticket_id: str, section_id: str = None, is_admin: bool = False):
        await websocket.accept()
        self.active_connections[ticket_id] = websocket
        if section_id:
            if section_id not in self.section_subscribers:
                self.section_subscribers[section_id] = set()
            self.section_subscribers[section_id].add(ticket_id)
        if is_admin:
            self.admin_subscribers.add(ticket_id)
        logger.info(f"WebSocket connected: {ticket_id} (section: {section_id}, admin: {is_admin})")

    def disconnect(self, ticket_id: str):
        self.active_connections.pop(ticket_id, None)
        # Remove from section subscribers
        for section_subs in self.section_subscribers.values():
            section_subs.discard(ticket_id)
        self.admin_subscribers.discard(ticket_id)
        logger.info(f"WebSocket disconnected: {ticket_id}")

    async def send_to_fan(self, ticket_id: str, message: dict):
        """Send a message to a specific fan."""
        ws = self.active_connections.get(ticket_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to {ticket_id}: {e}")
                self.disconnect(ticket_id)

    async def broadcast_to_section(self, section_id: str, message: dict):
        """Send a message to all fans in a section."""
        ticket_ids = self.section_subscribers.get(section_id, set())
        for tid in list(ticket_ids):
            await self.send_to_fan(tid, message)

    async def broadcast_to_admins(self, message: dict):
        """Send a message to all connected admin dashboards."""
        for tid in list(self.admin_subscribers):
            await self.send_to_fan(tid, message)

    async def broadcast_all(self, message: dict):
        """Send a message to all connected fans."""
        for tid in list(self.active_connections.keys()):
            await self.send_to_fan(tid, message)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()


# ── WebSocket Endpoint ──

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None),
):
    """
    WebSocket endpoint for real-time fan updates.

    Connect: ws://host/api/v1/ws?token=<jwt_token>

    Message types received:
    - ping: Keep-alive
    - subscribe_section: Subscribe to section-specific updates

    Message types sent:
    - crowd_update: Density change for a section
    - egress_route: Personalized egress route push
    - incident_alert: Incident near the fan's section
    - notification: General notification
    """
    # Authenticate via query param token
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    try:
        payload = await verify_token(token)
    except UnauthorizedException:
        await websocket.close(code=4001, reason="Invalid token")
        return

    ticket_id = payload.get("sub", "unknown")
    seat = payload.get("seat", {})
    section_id = seat.get("section_id", "")
    is_admin = payload.get("role") == "admin"

    await manager.connect(websocket, ticket_id, section_id, is_admin)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
                continue

            msg_type = msg.get("type", "")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif msg_type == "subscribe_section":
                new_section = msg.get("section_id", "")
                if new_section:
                    if new_section not in manager.section_subscribers:
                        manager.section_subscribers[new_section] = set()
                    manager.section_subscribers[new_section].add(ticket_id)
                    await websocket.send_json({
                        "type": "subscribed",
                        "section_id": new_section
                    })

            else:
                await websocket.send_json({
                    "type": "echo",
                    "data": msg
                })

    except WebSocketDisconnect:
        manager.disconnect(ticket_id)
    except Exception as e:
        logger.error(f"WebSocket error for {ticket_id}: {e}")
        manager.disconnect(ticket_id)
