"""
===============================================================================
FILE: backend/tests/phase2_test_auth.py
PURPOSE: Core Backend Application Module.
ARCHITECTURE: Python/FastAPI module
INPUTS: Standard application requests
OUTPUTS: Structured models and responses
HACKATHON VERTICAL: Code Quality & Testing
===============================================================================
"""
"""
Stadium Sync — Phase 2 Test Script: Auth & QR Ticket Scanning

Tests:
  1. POST /scan-ticket with valid payload returns JWT + Fan Session
  2. POST /scan-ticket with invalid JSON payload returns 400
  3. POST /scan-ticket with missing fields returns 400
  4. POST /scan-ticket with invalid checksum returns 400
  5. POST /scan-ticket with unknown ticket returns 404
  6. POST /scan-ticket with inactive ticket returns 403
  7. GET /me with valid token returns session data
  8. GET /me without token returns 401
  9. POST /refresh returns new token
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Seat, Section, SectionType, Stadium, Ticket
from app.services.ticket_service import generate_qr_payload
from tests.conftest import TestData


@pytest.fixture(autouse=True)
async def setup_test_data(db_session: AsyncSession):
    """Seed the in-memory database with test data for auth tests."""
    stadium = Stadium(
        id=TestData.STADIUM_ID, name="MetLife Test", city="NYC", country="USA", capacity=100
    )
    db_session.add(stadium)

    section = Section(
        id=TestData.SECTION_ID, stadium_id=TestData.STADIUM_ID, name="S204",
        section_type=SectionType.GENERAL, capacity=10, svg_x=10, svg_y=10,
        svg_width=50, svg_height=50
    )
    db_session.add(section)

    seat = Seat(
        id=TestData.SEAT_ID, section_id=TestData.SECTION_ID, row="12", number=5,
        svg_x=15, svg_y=15
    )
    db_session.add(seat)

    # Active Ticket
    ticket1 = Ticket(
        id=TestData.TICKET_ID,
        match_id=TestData.MATCH_ID,
        seat_id=TestData.SEAT_ID,
        qr_payload=generate_qr_payload(TestData.TICKET_ID, TestData.MATCH_ID),
        holder_name="Active Fan",
        is_active=True,
    )
    db_session.add(ticket1)

    # Inactive Ticket
    ticket2 = Ticket(
        id="ticket-inactive-001",
        match_id=TestData.MATCH_ID,
        seat_id=TestData.SEAT_ID,
        qr_payload=generate_qr_payload("ticket-inactive-001", TestData.MATCH_ID),
        holder_name="Inactive Fan",
        is_active=False,
    )
    db_session.add(ticket2)

    await db_session.commit()


# ──────────────────────────────────────────────
# Test 1: Valid QR Scan
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_valid_qr_scan(client: AsyncClient):
    payload = generate_qr_payload(TestData.TICKET_ID, TestData.MATCH_ID)
    
    response = await client.post(
        "/api/v1/auth/scan-ticket",
        json={"qr_payload": payload},
    )
    assert response.status_code == 200
    
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert "token" in data
    assert data["fan"]["ticket_id"] == TestData.TICKET_ID
    assert data["fan"]["holder_name"] == "Active Fan"
    assert data["fan"]["seat"]["section_name"] == "S204"


# ──────────────────────────────────────────────
# Test 2: Invalid JSON Payload
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_invalid_json_payload(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/scan-ticket",
        json={"qr_payload": "not-a-json-string"},
    )
    assert response.status_code == 401
    assert "Malformed security token" in response.json()["detail"]


# ──────────────────────────────────────────────
# Test 3: Missing Fields in Payload
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_missing_fields_payload(client: AsyncClient):
    import json
    # Missing checksum
    payload = json.dumps({"ticket_id": "123", "match_id": "456"})
    response = await client.post(
        "/api/v1/auth/scan-ticket",
        json={"qr_payload": payload},
    )
    assert response.status_code == 401
    assert "Malformed security token" in response.json()["detail"]


# ──────────────────────────────────────────────
# Test 4: Invalid Checksum
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_invalid_checksum(client: AsyncClient):
    import json
    payload = json.dumps({
        "ticket_id": TestData.TICKET_ID,
        "match_id": TestData.MATCH_ID,
        "checksum": "wrong-checksum"
    })
    
    response = await client.post(
        "/api/v1/auth/scan-ticket",
        json={"qr_payload": payload},
    )
    assert response.status_code == 401
    assert "Malformed security token" in response.json()["detail"]


# ──────────────────────────────────────────────
# Test 5: Unknown Ticket
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_unknown_ticket(client: AsyncClient):
    payload = generate_qr_payload("ticket-unknown-001", TestData.MATCH_ID)
    
    response = await client.post(
        "/api/v1/auth/scan-ticket",
        json={"qr_payload": payload},
    )
    assert response.status_code == 404
    assert "Ticket not found" in response.json()["error"]["message"]


# ──────────────────────────────────────────────
# Test 6: Inactive Ticket
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_inactive_ticket(client: AsyncClient):
    payload = generate_qr_payload("ticket-inactive-001", TestData.MATCH_ID)
    
    response = await client.post(
        "/api/v1/auth/scan-ticket",
        json={"qr_payload": payload},
    )
    assert response.status_code == 403
    assert "deactivated" in response.json()["error"]["message"]


# ──────────────────────────────────────────────
# Test 7: GET /me with valid token
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_me_valid_token(client: AsyncClient):
    token = TestData.fan_token()
    
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["ticket_id"] == TestData.TICKET_ID
    assert data["role"] == "fan"


# ──────────────────────────────────────────────
# Test 8: GET /me without token
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


# ──────────────────────────────────────────────
# Test 9: POST /refresh
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    token = TestData.fan_token()
    
    response = await client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "token" in data
    assert data["token"] != token  # Should be a newly generated token string
