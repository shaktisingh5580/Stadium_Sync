"""
Stadium Sync — Egress Agent Service.

The egress agent is triggered at the 80th minute of a match.
It computes personalized egress routes for all active fans and
pushes them via WebSocket.

State machine: IDLE → COMPUTING → ACTIVE → COMPLETED
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import BadRequestException, NotFoundException
from app.models.crowd import (
    EgressAgentState,
    EgressAgentStatus,
    EgressRoute,
)
from app.models.ticket import Gate, Seat, Section, Ticket
from app.services.navigation_service import compute_egress_route

logger = logging.getLogger(__name__)


async def get_agent_state(db: AsyncSession, match_id: str) -> Optional[EgressAgentState]:
    """Get the current egress agent state for a match."""
    stmt = select(EgressAgentState).where(EgressAgentState.match_id == match_id)
    result = await db.execute(stmt)
    return result.unique().scalar_one_or_none()


async def trigger_egress_agent(
    db: AsyncSession,
    match_id: str,
    match_minute: int,
    force: bool = False,
) -> EgressAgentState:
    """
    Trigger the egress agent to compute routes for all active fans.

    The agent is normally triggered at the 80th minute, but can be forced.

    Args:
        db: Database session.
        match_id: Match identifier.
        match_minute: Current match minute.
        force: Override the 80-minute threshold.

    Returns:
        Updated EgressAgentState.
    """
    if match_minute < 75 and not force:
        raise BadRequestException(
            f"Egress agent cannot be triggered before the 75th minute "
            f"(current: {match_minute}). Use force=true to override."
        )

    # Check if already triggered
    existing = await get_agent_state(db, match_id)
    if existing and existing.status in (EgressAgentStatus.COMPUTING, EgressAgentStatus.ACTIVE):
        logger.info(f"Egress agent already {existing.status.value} for match {match_id}")
        return existing

    # Create or update agent state
    if existing:
        existing.status = EgressAgentStatus.COMPUTING
        existing.triggered_at = datetime.now(timezone.utc)
        existing.match_minute = match_minute
        agent_state = existing
    else:
        agent_state = EgressAgentState(
            id=str(uuid.uuid4()),
            match_id=match_id,
            status=EgressAgentStatus.COMPUTING,
            triggered_at=datetime.now(timezone.utc),
            match_minute=match_minute,
        )
        db.add(agent_state)

    await db.flush()

    # Compute routes for all active tickets in this match
    routes_computed = await _compute_batch_routes(db, match_id)

    # Update state
    agent_state.status = EgressAgentStatus.ACTIVE
    agent_state.routes_computed = routes_computed
    db.add(agent_state)
    await db.flush()

    logger.info(
        f"Egress agent triggered for match {match_id} at minute {match_minute}. "
        f"Computed {routes_computed} routes."
    )

    return agent_state


async def _compute_batch_routes(
    db: AsyncSession,
    match_id: str,
) -> int:
    """
    Compute egress routes for all active tickets in a match.
    Stores pre-computed routes in the egress_routes table.
    """
    # Get all active tickets for this match
    stmt = (
        select(Ticket)
        .options(joinedload(Ticket.seat).joinedload(Seat.section))
        .where(Ticket.match_id == match_id, Ticket.is_active == True)
    )
    result = await db.execute(stmt)
    tickets = result.unique().scalars().all()

    routes_computed = 0

    for ticket in tickets:
        try:
            route_data = await compute_egress_route(db, ticket.id)

            egress_route = EgressRoute(
                id=str(uuid.uuid4()),
                ticket_id=ticket.id,
                match_id=match_id,
                gate_id=route_data.target_gate_id,
                path_json={
                    "path": [p.model_dump() for p in route_data.path],
                    "gate_name": route_data.target_gate_name,
                    "transit_method": route_data.transit_method,
                    "distance_meters": route_data.distance_meters,
                    "estimated_time_mins": route_data.estimated_time_mins,
                },
            )
            db.add(egress_route)
            routes_computed += 1
        except Exception as e:
            logger.warning(f"Failed to compute route for ticket {ticket.id}: {e}")

    await db.flush()
    return routes_computed


async def get_fan_egress_route(
    db: AsyncSession,
    ticket_id: str,
    match_id: str,
) -> Optional[EgressRoute]:
    """Get the pre-computed egress route for a specific fan."""
    stmt = (
        select(EgressRoute)
        .where(
            EgressRoute.ticket_id == ticket_id,
            EgressRoute.match_id == match_id,
        )
        .order_by(EgressRoute.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.unique().scalar_one_or_none()
