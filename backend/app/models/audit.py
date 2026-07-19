"""
===============================================================================
FILE: backend/app/models/audit.py
PURPOSE: Provides core functionality and logic for this module.
ARCHITECTURE: Python/FastAPI module
INPUTS: Standard application requests
OUTPUTS: Structured models and responses
HACKATHON VERTICAL: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, UniqueConstraint
from app.models.base import Base

class AuditLog(Base):
    """
    Immutable audit trail for compliance and security monitoring.
    Never updated or deleted after creation.
    """
    __tablename__ = "audit_logs"

    id: str = Column(String(36), primary_key=True)
    timestamp: datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    action: str = Column(String(50))  # e.g., 'ticket_scanned', 'incident_reported', 'admin_evacuation'
    actor_id: str = Column(String(36))  # Who did it (ticket_id, volunteer_id, etc.)
    actor_type: str = Column(String(20))  # 'fan', 'volunteer', 'admin', 'system'
    resource_id: str = Column(String(36))  # What was affected
    resource_type: str = Column(String(20))  # 'ticket', 'incident', 'crowd_alert'
    details: dict = Column(JSON, nullable=True)  # {"ip": "...", "outcome": "..."}

    __table_args__ = (UniqueConstraint('id'),)
