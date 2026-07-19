"""
===============================================================================
File: backend/app/core/firebase_runtime.py
Purpose: Core Backend Application Module.
Architecture: FastAPI backend module.
Inputs: standard API requests or internal service calls.
Outputs: structured responses/models.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""Firebase Admin, App Check, and Firestore integration for Cloud Run.

The module is deliberately lazy so the SQL-backed local test suite does not
need Google credentials. In Cloud Run, Application Default Credentials are
used; no service-account JSON is stored in this repository or image.
"""

import asyncio
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceException, UnauthorizedException

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_firebase_app():
    """Return the initialized Firebase Admin app when Firebase is enabled."""
    if not settings.FIREBASE_AUTH_ENABLED:
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials

        try:
            return firebase_admin.get_app()
        except ValueError:
            return firebase_admin.initialize_app(
                credentials.ApplicationDefault(),
                {"projectId": settings.FIREBASE_PROJECT_ID},
            )
    except Exception as exc:
        logger.error("Firebase Admin initialization failed: %s", exc)
        raise ExternalServiceException("Firebase", "Firebase authentication is unavailable")


def _normalise(value: Any) -> Any:
    """Convert values into Firestore-safe audit event fields."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _normalise(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalise(item) for item in value]
    return value


async def verify_firebase_id_token(token: str) -> Dict[str, Any]:
    """Verify an end-user Firebase ID token using Admin SDK credentials."""
    if not settings.FIREBASE_AUTH_ENABLED:
        raise UnauthorizedException("Firebase authentication is not enabled")

    try:
        from firebase_admin import auth

        app = _get_firebase_app()
        return await asyncio.to_thread(auth.verify_id_token, token, app)
    except ExternalServiceException:
        raise
    except Exception as exc:
        logger.warning("Firebase ID token verification failed: %s", exc)
        raise UnauthorizedException("Invalid or expired Firebase token")


async def verify_app_check_token(token: str) -> None:
    """Verify Firebase App Check when enforcement is enabled."""
    if not settings.FIREBASE_APP_CHECK_ENFORCED:
        return
    if not token:
        raise UnauthorizedException("Missing Firebase App Check token")

    try:
        from firebase_admin import app_check

        app = _get_firebase_app()
        await asyncio.to_thread(app_check.verify_token, token, app)
    except ExternalServiceException:
        raise
    except Exception as exc:
        logger.warning("Firebase App Check verification failed: %s", exc)
        raise UnauthorizedException("Invalid Firebase App Check token")


async def create_firebase_custom_token(
    ticket_id: str,
    match_id: str,
    needs_accessibility: bool,
) -> str:
    """Create a Firebase custom token after server-side QR validation."""
    if not settings.FIREBASE_AUTH_ENABLED:
        return ""

    try:
        from firebase_admin import auth

        app = _get_firebase_app()
        claims = {
            "role": "fan",
            "ticket_id": ticket_id,
            "match_id": match_id,
            "needs_accessibility": needs_accessibility,
        }
        token = await asyncio.to_thread(
            auth.create_custom_token, f"ticket:{ticket_id}", claims, app
        )
        return token.decode("utf-8") if isinstance(token, bytes) else token
    except ExternalServiceException:
        raise
    except Exception as exc:
        logger.error("Firebase custom token generation failed: %s", exc)
        raise ExternalServiceException("Firebase", "Could not create fan session")


async def write_operational_event(event_type: str, payload: Dict[str, Any]) -> None:
    """Persist a non-sensitive operational audit event to Cloud Firestore."""
    if not settings.FIRESTORE_EVENT_MIRROR_ENABLED:
        return

    try:
        from firebase_admin import firestore

        app = _get_firebase_app()
        event = {
            "event_type": event_type,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "payload": _normalise(payload),
        }
        client = firestore.client(app)
        await asyncio.to_thread(client.collection("operationalEvents").add, event)
    except ExternalServiceException:
        raise
    except Exception as exc:
        # Operational audit mirroring must not stop a time-critical incident flow.
        logger.error("Firestore audit event write failed: %s", exc)
