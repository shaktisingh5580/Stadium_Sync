"""
Stadium Sync — Test Fixtures (conftest.py)

Shared fixtures for all test phases:
- Test database (SQLite in-memory)
- Test FastAPI client (httpx AsyncClient)
- Auth helper (generate test JWTs)
- Mock Gemini client
"""

import os
import asyncio
from typing import AsyncGenerator, Dict, Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# ── Set test environment BEFORE importing app ──
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = ""
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["RATE_LIMIT_ENABLED"] = "false"  # Disable for most tests
os.environ["GEMINI_API_KEY_1"] = ""
os.environ["GEMINI_API_KEY_3"] = ""
os.environ["NVIDIA_API_KEY"] = ""
os.environ["IOT_API_KEY"] = "test-iot-key"
os.environ["ALLOW_AI_MOCK_FALLBACK"] = "true"
os.environ["ALLOW_DEMO_FEATURES"] = "true"
os.environ["TICKET_QR_SIGNING_KEY"] = "test-qr-signing-key-for-testing"

from app.core.config import get_settings  # noqa: E402
from app.core.database import get_db  # noqa: E402
from app.core.security import (  # noqa: E402
    create_access_token,
    create_admin_token,
    create_volunteer_token,
)
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402


# ── Clear cached settings for test environment ──
get_settings.cache_clear()


# ── Event Loop ──

@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Test Database ──

@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create a fresh in-memory SQLite engine per test."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session."""
    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


# ── Test Client ──

@pytest_asyncio.fixture(scope="function")
async def client(db_engine) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an httpx AsyncClient wired to the test database.
    Overrides the get_db dependency to use our test database.
    """
    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ── Auth Helpers ──

def make_fan_token(
    ticket_id: str = "test-ticket-001",
    seat: Dict[str, Any] = None,
    holder_name: str = "Test Fan",
    match_id: str = "M2026-QF1",
    needs_accessibility: bool = False,
) -> str:
    """Generate a test JWT for a fan."""
    if seat is None:
        seat = {"section": "S204", "row": "12", "number": 5}
    return create_access_token(
        data={
            "sub": ticket_id,
            "seat": seat,
            "holder_name": holder_name,
            "match_id": match_id,
            "needs_accessibility": needs_accessibility,
            "role": "fan",
        }
    )


def make_volunteer_token(
    volunteer_id: str = "test-vol-001",
    name: str = "Test Volunteer",
) -> str:
    """Generate a test JWT for a volunteer."""
    return create_volunteer_token(volunteer_id, name)


def make_admin_token(admin_id: str = "test-admin-001") -> str:
    """Generate a test JWT for an admin."""
    return create_admin_token(admin_id)


def auth_header(token: str) -> Dict[str, str]:
    """Build Authorization header dict."""
    return {"Authorization": f"Bearer {token}"}


# ── Test Data Factories ──

class TestData:
    """Common test data constants."""

    STADIUM_ID = "stadium-metlife-001"
    SECTION_ID = "section-s204-001"
    GATE_NORTH_ID = "gate-north-001"
    GATE_SOUTH_ID = "gate-south-001"
    SEAT_ID = "seat-s204-r12-s5"
    TICKET_ID = "ticket-test-001"
    MATCH_ID = "M2026-QF1"
    VOLUNTEER_ID = "volunteer-test-001"

    QR_PAYLOAD = '{"ticket_id": "ticket-test-001", "match_id": "M2026-QF1", "checksum": "abc123"}'

    @staticmethod
    def fan_token():
        return make_fan_token(ticket_id=TestData.TICKET_ID)

    @staticmethod
    def volunteer_token():
        return make_volunteer_token(volunteer_id=TestData.VOLUNTEER_ID)

    @staticmethod
    def admin_token():
        return make_admin_token()
