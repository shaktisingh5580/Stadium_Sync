"""
===============================================================================
File: backend/app/models/base.py
Purpose: SQLAlchemy Declarative Base - parent class for all ORM models with 
         common columns (id, created_at, updated_at) and table configuration.
Architecture: Provides Base class that all models inherit from. Automatically 
             adds UUID primary key, created_at timestamp (UTC), updated_at 
             timestamp (UTC) to every table.
Inputs: None (base class definition)
Outputs: Base class for model definition, automatic audit timestamps on all 
         entities.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """Mixin that adds a UUID primary key column."""

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
