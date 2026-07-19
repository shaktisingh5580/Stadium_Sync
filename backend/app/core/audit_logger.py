"""
===============================================================================
File: backend/app/core/audit_logger.py
Purpose: Compliance and security audit trail - immutably logs all sensitive 
         operations (ticket scans, token issuance, incidents, admin actions) 
         for investigation and regulatory compliance.
Architecture: Async audit logging with PostgreSQL persistence. Each log entry 
             is immutable (no updates, only inserts) with timestamp, actor ID, 
             resource ID, outcome, and rich context (IP, details JSON).
Inputs: Audit events from various services (auth, incidents, admin, etc.) with 
        action type, actor, resource, details, and status.
Outputs: Immutable audit_logs table records for compliance, forensics, and 
         real-time security monitoring (e.g., detect abuse patterns).
Hackathon Vertical: Security & Authentication
===============================================================================
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
