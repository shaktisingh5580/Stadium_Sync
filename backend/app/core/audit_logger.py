"""
===============================================================================
File: backend/app/core/audit_logger.py
Purpose: Operational event audit logging.
Architecture: FastAPI backend module.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""Operational event audit logger.

In a production Render deployment, this module would pipe audit events to
Cloud Logging or BigQuery. For the hackathon demo, events are logged
at INFO level for observability.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def write_operational_event(event_type: str, payload: Dict[str, Any]) -> None:
    """Log a non-sensitive operational audit event.

    In production, this would persist to Cloud Logging or BigQuery.
    Currently logs at INFO level for full observability.
    """
    logger.info("Operational event: %s | %s", event_type, payload)
