"""
Stadium Sync — Navigation Service.

Handles setting transit preferences and computing the optimal path
from a seat to a gate on the SVG map.
"""

import math
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import NotFoundException, BadRequestException
from app.models.ticket import Gate, Seat, Ticket
from app.schemas.navigation import EgressRouteResponse, Point2D


async def set_transit_choice(
    db: AsyncSession, ticket_id: str, transit_method: str
) -> Ticket:
    """
    Update a fan's transit choice in the database.
    """
    valid_methods = {"metro", "bus", "rideshare", "parking"}
    if transit_method not in valid_methods:
        raise BadRequestException(f"Invalid transit method. Allowed: {valid_methods}")

    stmt = select(Ticket).where(Ticket.id == ticket_id)
    result = await db.execute(stmt)
    ticket = result.unique().scalar_one_or_none()

    if not ticket:
        raise NotFoundException("Ticket", ticket_id)

    ticket.transit_choice = transit_method
    db.add(ticket)
    await db.flush()

    return ticket


async def compute_egress_route(
    db: AsyncSession, ticket_id: str, target_location: str = None
) -> EgressRouteResponse:
    """
    Compute the optimal route from the fan's seat to the appropriate gate.

    Logic:
    1. Find the fan's Seat and chosen Transit Method.
    2. Find all Gates that support that transit method.
    3. If no transit method is selected, find the absolute closest gate.
    4. Calculate shortest euclidean distance on the SVG map.
    5. Generate a basic path: Seat -> Section Center -> Gate.
    """
    # 1. Fetch Ticket & Seat
    stmt = (
        select(Ticket)
        .options(joinedload(Ticket.seat))
        .where(Ticket.id == ticket_id)
    )
    result = await db.execute(stmt)
    ticket = result.unique().scalar_one_or_none()

    if not ticket:
        raise NotFoundException("Ticket", ticket_id)
    if not ticket.seat:
        # Mock seat for demo if missing
        from app.models.ticket import Seat
        seat = Seat(section_name="N101", row="1", number="1", svg_x=275.0, svg_y=132.0)
    else:
        seat = ticket.seat
    transit_method = ticket.transit_choice or "metro"  # Default if unset

    # 2. Fetch Gates
    gates_stmt = select(Gate)
    gates_result = await db.execute(gates_stmt)
    all_gates = gates_result.unique().scalars().all()

    if not all_gates:
        raise NotFoundException("Gates", "No gates found in stadium")

    # Filter gates by transit method
    target_gates = [g for g in all_gates if g.nearest_transit == transit_method]
    
    # If no gates match the specific transit, fallback to all gates
    if not target_gates:
        target_gates = all_gates

    # 3. Find closest target gate (Euclidean distance on SVG)
    best_gate = None
    
    # If a specific target location (like a gate) was requested, use it
    if target_location and target_location.startswith("gate_"):
        for gate in all_gates:
            if gate.name.lower().replace(" ", "_") == target_location:
                best_gate = gate
                break
                
    # Otherwise fallback to distance-based target
    if not best_gate:
        min_dist = float("inf")
        for gate in target_gates:
            dist = math.hypot(gate.svg_x - seat.svg_x, gate.svg_y - seat.svg_y)
            if dist < min_dist:
                min_dist = dist
                best_gate = gate

    # Final fallback if still nothing found
    if not best_gate:
        best_gate = all_gates[0]

    # Ensure min_dist is calculated
    min_dist = math.hypot(best_gate.svg_x - seat.svg_x, best_gate.svg_y - seat.svg_y)

    # 4. Generate Path Points (Avoiding the center pitch!)
    # We calculate polar coordinates relative to the center (400, 400)
    # and route the fan along a safe circular path (e.g., radius 360, outer concourse)
    cx, cy = 400.0, 400.0
    
    seat_dx = seat.svg_x - cx
    seat_dy = seat.svg_y - cy
    seat_th = math.atan2(seat_dy, seat_dx)
    
    gate_dx = best_gate.svg_x - cx
    gate_dy = best_gate.svg_y - cy
    gate_th = math.atan2(gate_dy, gate_dx)
    
    # Safe radius for walking (outer concourse just past the seats)
    safe_r = 360.0
    
    # Calculate shortest angular distance
    diff = gate_th - seat_th
    # Normalize to [-pi, pi]
    diff = (diff + math.pi) % (2 * math.pi) - math.pi
    
    path = [Point2D(x=seat.svg_x, y=seat.svg_y)]
    
    # 1. Step radially out to the concourse
    path.append(Point2D(
        x=cx + safe_r * math.cos(seat_th),
        y=cy + safe_r * math.sin(seat_th)
    ))
    
    # 2. Arc along the concourse
    steps = max(12, int(abs(diff) * 10))
    for i in range(1, steps + 1):
        th = seat_th + diff * (i / steps)
        px = cx + safe_r * math.cos(th)
        py = cy + safe_r * math.sin(th)
        path.append(Point2D(x=px, y=py))
        
    # 3. Step radially to the gate
    path.append(Point2D(x=best_gate.svg_x, y=best_gate.svg_y))

    # Convert SVG distance to rough real-world metrics
    # Assumption: 1 SVG unit ~ 1.5 meters
    distance_meters = int(min_dist * 1.5)
    
    # Average walking speed ~ 80 meters / min in a crowd
    estimated_time = max(1, int(distance_meters / 80))

    return EgressRouteResponse(
        ticket_id=ticket.id,
        transit_method=transit_method,
        target_gate_id=best_gate.id,
        target_gate_name=best_gate.name,
        distance_meters=distance_meters,
        estimated_time_mins=estimated_time,
        path=path,
    )
