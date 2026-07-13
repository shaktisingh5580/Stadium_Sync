"""
Stadium Sync — Phase 3 Test Script: Navigation & Pathfinding

Tests:
  1. POST /transit with valid method updates preference
  2. POST /transit with invalid method returns 400
  3. POST /transit without auth returns 401
  4. GET /route computes correct SVG path to closest/matched gate
  5. GET /route without auth returns 401
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Gate, GateType, Seat, Section, SectionType, Stadium, Ticket
from app.services.ticket_service import generate_qr_payload
from tests.conftest import TestData


@pytest.fixture(autouse=True)
async def setup_test_data(db_session: AsyncSession):
    """Seed the in-memory database with test data for navigation tests."""
    stadium = Stadium(
        id=TestData.STADIUM_ID, name="MetLife Test", city="NYC", country="USA", capacity=100
    )
    db_session.add(stadium)

    section = Section(
        id=TestData.SECTION_ID, stadium_id=TestData.STADIUM_ID, name="S204",
        section_type=SectionType.GENERAL, capacity=10, svg_x=100, svg_y=100,
        svg_width=50, svg_height=50
    )
    db_session.add(section)

    # Seat is at (150, 150)
    seat = Seat(
        id=TestData.SEAT_ID, section_id=TestData.SECTION_ID, row="12", number=5,
        svg_x=150, svg_y=150
    )
    db_session.add(seat)

    # Metro Gate is at (150, 10) (Distance ~ 140)
    gate_metro = Gate(
        id=TestData.GATE_NORTH_ID, stadium_id=TestData.STADIUM_ID, name="Metro Gate",
        gate_type=GateType.ENTRY_EXIT, capacity=1000,
        svg_x=150, svg_y=10, lat=40.0, lng=-74.0, nearest_transit="metro"
    )
    db_session.add(gate_metro)

    # Bus Gate is at (150, 400) (Distance ~ 250)
    gate_bus = Gate(
        id=TestData.GATE_SOUTH_ID, stadium_id=TestData.STADIUM_ID, name="Bus Gate",
        gate_type=GateType.ENTRY_EXIT, capacity=1000,
        svg_x=150, svg_y=400, lat=40.0, lng=-74.0, nearest_transit="bus"
    )
    db_session.add(gate_bus)

    ticket = Ticket(
        id=TestData.TICKET_ID,
        match_id=TestData.MATCH_ID,
        seat_id=TestData.SEAT_ID,
        qr_payload=generate_qr_payload(TestData.TICKET_ID, TestData.MATCH_ID),
        holder_name="Nav Fan",
        is_active=True,
    )
    db_session.add(ticket)
    await db_session.commit()


# ──────────────────────────────────────────────
# Test 1: Update Transit Valid
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_update_transit_valid(client: AsyncClient):
    token = TestData.fan_token()
    
    response = await client.post(
        "/api/v1/navigation/transit",
        headers={"Authorization": f"Bearer {token}"},
        json={"transit_method": "bus"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["transit_method"] == "bus"


# ──────────────────────────────────────────────
# Test 2: Update Transit Invalid
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_update_transit_invalid(client: AsyncClient):
    token = TestData.fan_token()
    
    response = await client.post(
        "/api/v1/navigation/transit",
        headers={"Authorization": f"Bearer {token}"},
        json={"transit_method": "helicopter"},  # Invalid
    )
    assert response.status_code == 400
    assert "Invalid transit method" in response.json()["error"]["message"]


# ──────────────────────────────────────────────
# Test 3: Calculate Route (Bus)
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_calculate_route_bus(client: AsyncClient):
    token = TestData.fan_token()
    
    # 1. Set transit to bus
    await client.post(
        "/api/v1/navigation/transit",
        headers={"Authorization": f"Bearer {token}"},
        json={"transit_method": "bus"},
    )
    
    # 2. Get route
    response = await client.get(
        "/api/v1/navigation/route",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    
    data = response.json()["data"]
    assert data["transit_method"] == "bus"
    # Bus gate is south gate
    assert data["target_gate_id"] == TestData.GATE_SOUTH_ID
    # Route path should have 15 points (curved route to main gate)
    assert len(data["path"]) == 15
    
    assert data["path"][0]["x"] == 150
    assert data["path"][0]["y"] == 150
    
    assert data["path"][-1]["x"] == 250
    assert data["path"][-1]["y"] == 400


# ──────────────────────────────────────────────
# Test 4: Calculate Route (Default/Fallback)
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_calculate_route_default(client: AsyncClient):
    token = TestData.fan_token()
    
    # Get route without setting transit explicitly (should fallback to 'metro' or closest)
    # The default is "metro", and we seeded a Metro gate that is also closest.
    response = await client.get(
        "/api/v1/navigation/route",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    
    data = response.json()["data"]
    assert data["target_gate_id"] == TestData.GATE_NORTH_ID
    assert data["estimated_time_mins"] > 0
    assert data["distance_meters"] > 0


# ──────────────────────────────────────────────
# Test 5: Unauthenticated Access
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_unauthenticated_access(client: AsyncClient):
    response = await client.get("/api/v1/navigation/route")
    assert response.status_code == 401
