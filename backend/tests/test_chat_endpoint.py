"""
===============================================================================
FILE: backend/tests/test_chat_endpoint.py
PURPOSE: Core Backend Application Module.
ARCHITECTURE: Python/FastAPI module
INPUTS: Standard application requests
OUTPUTS: Structured models and responses
HACKATHON VERTICAL: Code Quality & Testing
===============================================================================
"""
"""
Tests for the new Agentic Chat endpoint.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock
from tests.conftest import make_fan_token

@pytest.fixture
def test_fan_token():
    return make_fan_token()

@pytest.mark.asyncio
async def test_agentic_chat_greeting(client: AsyncClient, test_fan_token: str):
    """Test that a basic greeting returns NONE ui_action."""
    response = await client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {test_fan_token}"},
        json={"message": "hello stadium sync!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    chat_resp = data["data"]
    assert "message" in chat_resp
    assert chat_resp["ui_action"] == "NONE"


@pytest.mark.asyncio
async def test_agentic_chat_washroom(client: AsyncClient, test_fan_token: str):
    """Test asking for a washroom triggers SHOW_MAP action."""
    response = await client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {test_fan_token}"},
        json={"message": "where is the nearest washroom?"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["ui_action"] == "SHOW_MAP"
    assert data["payload"].get("target") == "washroom"


@pytest.mark.asyncio
async def test_agentic_chat_seat(client: AsyncClient, test_fan_token: str):
    """Test asking for seat directions triggers SHOW_ROUTE."""
    with patch("app.api.v1.chat.agentic_chat", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = {
            "message": "Let me show you the way to your seat! 🎯",
            "ui_action": "SHOW_ROUTE",
            "payload": {"target": "seat"}
        }
        with patch("app.api.v1.chat.compute_egress_route", new_callable=AsyncMock) as mock_route:
            mock_route.return_value = MagicMock(
                target_gate_name="Gate North",
                distance_meters=100,
                estimated_time_mins=2,
                path=[]
            )
            response = await client.post(
                "/api/v1/chat",
                headers={"Authorization": f"Bearer {test_fan_token}"},
                json={"message": "how do I find my seat?"}
            )
            assert response.status_code == 200
            data = response.json()["data"]
            assert data["ui_action"] == "SHOW_ROUTE"


@pytest.mark.asyncio
async def test_agentic_chat_incident_dispatch(client: AsyncClient, test_fan_token: str):
    """Test reporting a spill creates an incident via DISPATCH_INCIDENT."""
    with patch("app.api.v1.chat.agentic_chat", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = {
            "message": "I'm sorry to hear that! 🚨",
            "ui_action": "DISPATCH_INCIDENT",
            "payload": {"description": "Spill"}
        }
        with patch("app.api.v1.chat.create_incident", new_callable=AsyncMock) as mock_incident:
            mock_incident.return_value = MagicMock(
                id="inc-123",
                severity=MagicMock(value="medium"),
                category="maintenance",
                status=MagicMock(value="reported"),
                estimated_response_mins=5
            )
            response = await client.post(
                "/api/v1/chat",
                headers={"Authorization": f"Bearer {test_fan_token}"},
                json={"message": "there is a huge coffee spill on the stairs"}
            )
            assert response.status_code == 200
            data = response.json()["data"]
            assert data["ui_action"] == "DISPATCH_INCIDENT"
            assert data["payload"]["incident_id"] == "inc-123"

