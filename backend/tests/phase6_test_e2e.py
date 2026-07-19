"""
===============================================================================
FILE: backend/tests/phase6_test_e2e.py
PURPOSE: Core Backend Application Module.
ARCHITECTURE: Python/FastAPI module
INPUTS: Standard application requests
OUTPUTS: Structured models and responses
HACKATHON VERTICAL: Code Quality & Testing
===============================================================================
"""
"""
Stadium Sync — Phase 6 Test Script: E2E Integration + Error Handling

Scenario 1: Full Happy Path Fan Journey (QR→Nav→Eco→Incident→Crowd→Egress)
Scenario 2: Error Handling & Edge Cases (invalid tokens, 404s, validation)
Scenario 3: API Endpoint Registry Verification (all routes respond)
"""
import base64
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Gate, GateType, Seat, Section, SectionType, Stadium, Ticket
from app.models.volunteer import Volunteer, VolunteerStatus
from app.services.ticket_service import generate_qr_payload
from tests.conftest import TestData, make_volunteer_token


# Base64 image payload long enough to pass min_length=100 schema validation
TINY_JPEG_B64 = base64.b64encode(b"\xff\xd8\xff\xe0" + b"\x00" * 200 + b"\xff\xd9").decode()


@pytest.fixture(autouse=True)
async def setup_e2e_data(db_session: AsyncSession):
    """Seed a complete minimal stadium for E2E flow."""
    stadium = Stadium(
        id=TestData.STADIUM_ID, name="MetLife E2E", city="NYC", country="USA", capacity=90000
    )
    db_session.add(stadium)

    section = Section(
        id=TestData.SECTION_ID, stadium_id=TestData.STADIUM_ID, name="Block 101",
        section_type=SectionType.GENERAL, capacity=1000, svg_x=100, svg_y=100,
        svg_width=50, svg_height=50,
    )
    db_session.add(section)

    seat = Seat(
        id=TestData.SEAT_ID, section_id=TestData.SECTION_ID, row="A", number=1,
        svg_x=110, svg_y=110
    )
    db_session.add(seat)

    gate_bus = Gate(
        id=TestData.GATE_NORTH_ID, stadium_id=TestData.STADIUM_ID, name="Bus Gate",
        gate_type=GateType.ENTRY_EXIT, capacity=3000, lat=51.5, lng=-0.2,
        svg_x=10, svg_y=10, nearest_transit="bus"
    )
    gate_metro = Gate(
        id="gate-metro-001", stadium_id=TestData.STADIUM_ID, name="Metro Gate",
        gate_type=GateType.ENTRY_EXIT, capacity=5000, lat=51.51, lng=-0.21,
        svg_x=200, svg_y=200, nearest_transit="metro"
    )
    db_session.add_all([gate_bus, gate_metro])

    ticket = Ticket(
        id=TestData.TICKET_ID,
        match_id=TestData.MATCH_ID,
        seat_id=TestData.SEAT_ID,
        qr_payload=generate_qr_payload(TestData.TICKET_ID, TestData.MATCH_ID),
        holder_name="E2E Fan",
        is_active=True,
    )
    db_session.add(ticket)

    # Volunteer for dispatch tests
    vol = Volunteer(
        id=TestData.VOLUNTEER_ID, name="E2E Volunteer",
        section_id=TestData.SECTION_ID, status=VolunteerStatus.AVAILABLE,
    )
    db_session.add(vol)

    await db_session.commit()


# ════════════════════════════════════════════════════
# Scenario 1: Full Happy Path Fan Journey
# ════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_e2e_full_fan_journey(client: AsyncClient):
    """
    Complete stadium experience:
    QR Scan → Transit → Navigation → Eco-Vision → Incident → Crowd → Egress
    """
    # ── Step 1: Auth — Scan QR ──
    qr_payload = generate_qr_payload(TestData.TICKET_ID, TestData.MATCH_ID)
    auth_resp = await client.post(
        "/api/v1/auth/scan-ticket",
        json={"qr_payload": qr_payload}
    )
    assert auth_resp.status_code == 200, f"Auth failed: {auth_resp.json()}"
    token = auth_resp.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify fan session with /me
    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["data"]["ticket_id"] == TestData.TICKET_ID

    # ── Step 2: Navigation — Set transit + get route ──
    transit_resp = await client.post(
        "/api/v1/navigation/transit",
        headers=headers,
        json={"transit_method": "metro"}
    )
    assert transit_resp.status_code == 200

    nav_resp = await client.get("/api/v1/navigation/route", headers=headers)
    assert nav_resp.status_code == 200
    nav_data = nav_resp.json()["data"]
    assert nav_data["target_gate_name"] == "Metro Gate"
    assert len(nav_data["path"]) >= 2

    # ── Step 3: Eco-Vision — Classify waste ──
    eco_resp = await client.post(
        "/api/v1/eco-vision/classify",
        headers=headers,
        json={"image_base64": TINY_JPEG_B64, "mime_type": "image/jpeg"}
    )
    assert eco_resp.status_code == 200
    eco_data = eco_resp.json()["data"]
    assert eco_data["category"] in ("compost", "recycle", "landfill", "hazardous")
    assert eco_data["bin_color"] in ("green", "blue", "black", "red")

    # ── Step 4: Incident — Report a problem ──
    incident_resp = await client.post(
        "/api/v1/incidents/",
        headers=headers,
        json={"description": "Lighting is flickering in my row"}
    )
    assert incident_resp.status_code == 200
    inc_data = incident_resp.json()["data"]
    assert inc_data["severity"] in ("low", "medium", "high", "critical")
    assert "id" in inc_data

    # Verify incident is fetchable
    inc_id = inc_data["id"]
    get_inc = await client.get(f"/api/v1/incidents/{inc_id}", headers=headers)
    assert get_inc.status_code == 200

    # Verify incidents list works
    list_inc = await client.get("/api/v1/incidents/", headers=headers)
    assert list_inc.status_code == 200
    assert list_inc.json()["data"]["total"] >= 1

    # ── Step 5: IoT Crowd Data ──
    iot_resp = await client.post(
        "/api/v1/crowd/ingest",
        headers={"X-API-Key": "test-iot-key"},
        json={"section_id": TestData.SECTION_ID, "density_pct": 72.0}
    )
    assert iot_resp.status_code == 200
    assert iot_resp.json()["data"]["density_level"] == "high"

    # Verify crowd map
    crowd_map_resp = await client.get(
        f"/api/v1/crowd/map/{TestData.STADIUM_ID}", headers=headers
    )
    assert crowd_map_resp.status_code == 200
    assert len(crowd_map_resp.json()["data"]["sections"]) >= 1

    # ── Step 6: Egress Trigger at 80th minute ──
    egress_resp = await client.post(
        "/api/v1/egress/trigger",
        headers=headers,
        json={"match_minute": 80}
    )
    assert egress_resp.status_code == 200
    assert egress_resp.json()["data"]["status"] == "active"
    assert egress_resp.json()["data"]["routes_computed"] >= 1

    # ── Step 7: Fan fetches egress route ──
    route_resp = await client.get("/api/v1/egress/route", headers=headers)
    assert route_resp.status_code == 200
    route_data = route_resp.json()["data"]
    assert route_data is not None
    assert route_data["ticket_id"] == TestData.TICKET_ID
    assert route_data["route"]["gate_name"] == "Metro Gate"
    assert "path" in route_data["route"]


# ════════════════════════════════════════════════════
# Scenario 2: Error Handling & Edge Cases
# ════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_e2e_invalid_jwt_rejected(client: AsyncClient):
    """All protected endpoints reject invalid tokens."""
    bad_headers = {"Authorization": "Bearer totally-invalid-token"}

    endpoints = [
        ("GET", "/api/v1/auth/me"),
        ("POST", "/api/v1/navigation/transit"),
        ("GET", "/api/v1/navigation/route"),
        ("POST", "/api/v1/eco-vision/classify"),
        ("POST", "/api/v1/incidents/"),
        ("GET", "/api/v1/incidents/"),
        ("POST", "/api/v1/egress/trigger"),
        ("GET", "/api/v1/egress/route"),
    ]

    for method, path in endpoints:
        if method == "GET":
            resp = await client.get(path, headers=bad_headers)
        else:
            resp = await client.post(path, headers=bad_headers, json={})
        assert resp.status_code == 401, f"{method} {path} returned {resp.status_code}, expected 401"


@pytest.mark.asyncio
async def test_e2e_nonexistent_incident_404(client: AsyncClient):
    """Fetching a non-existent incident returns 404."""
    token = TestData.fan_token()
    resp = await client.get(
        "/api/v1/incidents/does-not-exist-999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_e2e_egress_too_early_rejected(client: AsyncClient):
    """Egress agent rejects trigger before 75th minute."""
    token = TestData.fan_token()
    resp = await client.post(
        "/api/v1/egress/trigger",
        headers={"Authorization": f"Bearer {token}"},
        json={"match_minute": 10, "force": False}
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_e2e_crowd_ingest_requires_api_key(client: AsyncClient):
    """IoT endpoint requires X-API-Key header."""
    resp = await client.post(
        "/api/v1/crowd/ingest",
        json={"section_id": TestData.SECTION_ID, "density_pct": 50.0}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_e2e_validation_errors(client: AsyncClient):
    """Invalid request bodies return 422 with field errors."""
    token = TestData.fan_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Empty incident description
    resp = await client.post(
        "/api/v1/incidents/",
        headers=headers,
        json={"description": "ab"}  # too short, min_length=5
    )
    assert resp.status_code == 422


# ════════════════════════════════════════════════════
# Scenario 3: API Endpoint Registry Smoke Test
# ════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_e2e_health_endpoints(client: AsyncClient):
    """Health endpoints always respond."""
    health = await client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["data"]["status"] == "healthy"

    ready = await client.get("/api/v1/health/ready")
    assert ready.status_code == 200


@pytest.mark.asyncio
async def test_e2e_volunteer_flow(client: AsyncClient):
    """Volunteer status update and assignment flow."""
    vol_token = make_volunteer_token(
        volunteer_id=TestData.VOLUNTEER_ID, name="E2E Volunteer"
    )
    vol_headers = {"Authorization": f"Bearer {vol_token}"}

    # Update status
    resp = await client.post(
        "/api/v1/volunteers/status",
        headers=vol_headers,
        json={"status": "available", "lat": 40.8125, "lng": -74.0745}
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "available"
