"""Regression tests for production-safe security controls."""

from datetime import timedelta

import pytest
from httpx import AsyncClient
from pydantic import ValidationError

from app.api.deps import get_current_staff
from app.core.config import Settings
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import create_access_token, verify_token
from tests.conftest import TestData


def test_expired_jwt_is_rejected():
    """Expired credentials must not be accepted by the authorization layer."""
    token = create_access_token(
        {"sub": "expired-ticket", "role": "fan"},
        expires_delta=timedelta(seconds=-1),
    )
    with pytest.raises(UnauthorizedException):
        verify_token(token)


def test_production_settings_reject_wildcard_cors():
    """A production process fails closed when a wildcard origin is configured."""
    with pytest.raises(ValidationError, match="CORS_ORIGINS"):
        Settings(
            APP_ENV="production",
            DEBUG=False,
            SECRET_KEY="s" * 32,
            TICKET_QR_SIGNING_KEY="q" * 32,
            IOT_API_KEY="i" * 32,
            CORS_ORIGINS=["*"],
        )


@pytest.mark.asyncio
async def test_fan_cannot_gain_staff_incident_controls():
    """A fan token cannot manually dispatch operational staff."""
    with pytest.raises(ForbiddenException):
        await get_current_staff({"sub": TestData.TICKET_ID, "role": "fan"})


@pytest.mark.asyncio
async def test_api_responses_include_browser_hardening_headers(client: AsyncClient):
    """Security headers are consistently applied at the application boundary."""
    response = await client.get("/api/v1/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["cache-control"] == "no-store"
