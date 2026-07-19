"""
Stadium Sync — Phase 4 Test Script: Eco-Vision, Incidents, Volunteers

Tests:
  1. POST /eco-vision/classify returns classification (mock mode)
  2. POST /incidents/ creates incident with AI triage
  3. GET /incidents/ lists incidents
  4. GET /incidents/{id} fetches a single incident
  5. POST /incidents/{id}/dispatch dispatches a volunteer
  6. POST /volunteers/status updates volunteer status
  7. POST /volunteers/assignments/{id}/complete completes assignment
  8. Full end-to-end: Report → Triage → Dispatch → Complete
"""

import base64
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident, IncidentStatus, Severity
from app.models.ticket import Seat, Section, SectionType, Stadium, Ticket
from app.models.volunteer import Volunteer, VolunteerStatus
from app.services.ticket_service import generate_qr_payload
from tests.conftest import TestData, make_fan_token, make_volunteer_token


# A tiny valid JPEG (1x1 white pixel) for testing image upload
TINY_JPEG_B64 = base64.b64encode(
    bytes.fromhex(
        "ffd8ffe000104a46494600010100000100010000"
        "ffdb004300080606070605080707070909080a0c"
        "140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c"
        "20242e2720222c231c1c2837292c30313434341f"
        "27393d38323c2e333432ffdb004301090909"
        "0c0b0c180d0d1832211c213232323232323232"
        "32323232323232323232323232323232323232"
        "32323232323232323232323232323232323232"
        "3232323232ffc00011080001000103012200021101031101"
        "ffc4001f000001050101010101010000000000000000"
        "0102030405060708090a0bffc40000ffc40000ffc40000"
        "ffda000c03010002110311003f00bf8001ffd9"
    )
).decode()


@pytest.fixture(autouse=True)
async def setup_test_data(db_session: AsyncSession):
    """Seed database with stadium, section, seat, ticket, and volunteers."""
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

    seat = Seat(
        id=TestData.SEAT_ID, section_id=TestData.SECTION_ID, row="12", number=5,
        svg_x=150, svg_y=150
    )
    db_session.add(seat)

    ticket = Ticket(
        id=TestData.TICKET_ID,
        match_id=TestData.MATCH_ID,
        seat_id=TestData.SEAT_ID,
        qr_payload=generate_qr_payload(TestData.TICKET_ID, TestData.MATCH_ID),
        holder_name="Test Fan",
        is_active=True,
    )
    db_session.add(ticket)

    # Two volunteers — one in same section, one elsewhere
    vol1 = Volunteer(
        id=TestData.VOLUNTEER_ID,
        name="Alice Volunteer",
        section_id=TestData.SECTION_ID,
        status=VolunteerStatus.AVAILABLE,
    )
    vol2 = Volunteer(
        id="volunteer-test-002",
        name="Bob Volunteer",
        section_id=None,
        status=VolunteerStatus.AVAILABLE,
    )
    db_session.add_all([vol1, vol2])
    await db_session.commit()


# ──────────────────────────────────────────────
# Test 1: Eco-Vision Classification (Mock)
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_eco_vision_classify(client: AsyncClient):
    token = TestData.fan_token()

    response = await client.post(
        "/api/v1/eco-vision/classify",
        headers={"Authorization": f"Bearer {token}"},
        json={"image_base64": TINY_JPEG_B64, "mime_type": "image/jpeg"},
    )
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["category"] in ("compost", "recycle", "landfill", "hazardous")
    assert "bin_color" in data
    assert "instructions" in data


# ──────────────────────────────────────────────
# Test 2: Report Incident
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_report_incident(client: AsyncClient):
    token = TestData.fan_token()

    response = await client.post(
        "/api/v1/incidents/",
        headers={"Authorization": f"Bearer {token}"},
        json={"description": "There is a small spill near row 12"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["severity"] in ("low", "medium", "high", "critical")
    # Status may be 'assigned' if auto-dispatch triggered for high severity
    assert data["status"] in ("open", "assigned")
    assert "id" in data


# ──────────────────────────────────────────────
# Test 3: Report Critical Incident (Auto-dispatch)
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_critical_incident_auto_dispatch(client: AsyncClient):
    token = TestData.fan_token()

    response = await client.post(
        "/api/v1/incidents/",
        headers={"Authorization": f"Bearer {token}"},
        json={"description": "Medical emergency - person unconscious near exit"},
    )
    assert response.status_code == 200

    body = response.json()
    # The mock triage should detect "medical" + "unconscious" as critical
    assert body["data"]["severity"] == "critical"
    assert body["volunteer_dispatched"] is True


# ──────────────────────────────────────────────
# Test 4: List Incidents
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_list_incidents(client: AsyncClient):
    token = TestData.fan_token()

    # Create an incident first
    await client.post(
        "/api/v1/incidents/",
        headers={"Authorization": f"Bearer {token}"},
        json={"description": "Overflowing trash bin near gate A"},
    )

    response = await client.get(
        "/api/v1/incidents/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["total"] >= 1
    assert len(data["incidents"]) >= 1


# ──────────────────────────────────────────────
# Test 5: Get Incident by ID
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_incident_by_id(client: AsyncClient):
    token = TestData.fan_token()

    # Create
    create_resp = await client.post(
        "/api/v1/incidents/",
        headers={"Authorization": f"Bearer {token}"},
        json={"description": "Broken seat in row 5"},
    )
    incident_id = create_resp.json()["data"]["id"]

    # Fetch
    response = await client.get(
        f"/api/v1/incidents/{incident_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["id"] == incident_id


# ──────────────────────────────────────────────
# Test 6: Update Volunteer Status
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_update_volunteer_status(client: AsyncClient):
    token = make_volunteer_token(
        volunteer_id=TestData.VOLUNTEER_ID, name="Alice Volunteer"
    )

    response = await client.post(
        "/api/v1/volunteers/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "busy", "lat": 40.8125, "lng": -74.0745},
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "busy"


# ──────────────────────────────────────────────
# Test 7: Volunteer Completes Assignment (E2E)
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_full_e2e_incident_lifecycle(client: AsyncClient):
    fan_token = TestData.fan_token()
    vol_token = make_volunteer_token(
        volunteer_id=TestData.VOLUNTEER_ID, name="Alice Volunteer"
    )

    # 1. Fan reports critical incident
    report_resp = await client.post(
        "/api/v1/incidents/",
        headers={"Authorization": f"Bearer {fan_token}"},
        json={"description": "Fire hazard near emergency exit"},
    )
    assert report_resp.status_code == 200
    incident_id = report_resp.json()["data"]["id"]

    # 2. Manual dispatch (in case auto-dispatch already used the volunteer)
    dispatch_resp = await client.post(
        f"/api/v1/incidents/{incident_id}/dispatch",
        headers={"Authorization": f"Bearer {vol_token}"},
    )
    assert dispatch_resp.status_code == 200

    # If a volunteer was dispatched, complete the assignment
    if dispatch_resp.json()["success"] and "data" in dispatch_resp.json():
        assignment_id = dispatch_resp.json()["data"]["assignment_id"]

        # 3. Volunteer completes assignment
        complete_resp = await client.post(
            f"/api/v1/volunteers/assignments/{assignment_id}/complete",
            headers={"Authorization": f"Bearer {vol_token}"},
        )
        assert complete_resp.status_code == 200
        assert complete_resp.json()["data"]["status"] == "completed"


# ──────────────────────────────────────────────
# Test 8: Eco-Vision Unauthenticated
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_eco_vision_unauth(client: AsyncClient):
    response = await client.post(
        "/api/v1/eco-vision/classify",
        json={"image_base64": TINY_JPEG_B64},
    )
    assert response.status_code == 401
