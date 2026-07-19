"""
===============================================================================
File: backend/app/services/crowd_service.py
Purpose: Crowd analytics engine - ingests IoT turnstile data, computes 
         real-time density, predicts 15-min future congestion via linear 
         regression, triggers congestion alerts.
Architecture: Ingest flow: IoT count → aggregate by section → compute density % 
             → compare against thresholds → broadcast alerts. Prediction flow: 
             historical data → linear regression model → 15-min forecast.
Inputs: Turnstile counts from IoT sensors (POST /crowd/ingest).
Outputs: Real-time density heatmap, 15-min predictions, WebSocket alerts to 
         fans in congested sections.
Hackathon Vertical: Crowd Management & Real-Time Decision Support
===============================================================================
"""

import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, BadRequestException
from app.core.audit_logger import write_operational_event
from app.models.crowd import (
    CrowdSnapshot,
    CrowdSource,
    DensityLevel,
)
from app.models.ticket import Section
from app.schemas.crowd import CrowdDensityResponse, StadiumCrowdMap
from app.api.v1.websocket import manager

logger = logging.getLogger(__name__)


def classify_density(pct: float) -> DensityLevel:
    """Classify a density percentage into a level."""
    if pct < 30:
        return DensityLevel.LOW
    elif pct < 60:
        return DensityLevel.MODERATE
    elif pct < 85:
        return DensityLevel.HIGH
    else:
        return DensityLevel.CRITICAL

async def ingest_crowd_data(
    db: AsyncSession,
    section_id: str,
    density_pct: float,
    source: str = "sensor",
) -> CrowdSnapshot:
    """
    Ingest a crowd density reading for a section.

    Args:
        db: Database session.
        section_id: Section being measured.
        density_pct: Density percentage (0-100).
        source: Data source (sensor, manual, camera).

    Returns:
        The created CrowdSnapshot.
    """
    # Validate section exists
    stmt = select(Section).where(Section.id == section_id)
    result = await db.execute(stmt)
    section = result.unique().scalar_one_or_none()
    if not section:
        raise NotFoundException("Section", section_id)

    # Map source string
    source_map = {
        "sensor": CrowdSource.IOT_SENSOR,
        "manual": CrowdSource.MANUAL,
        "camera": CrowdSource.CAMERA,
    }
    crowd_source = source_map.get(source, CrowdSource.IOT_SENSOR)

    density_level = classify_density(density_pct)

    snapshot = CrowdSnapshot(
        id=str(uuid.uuid4()),
        section_id=section_id,
        stadium_id=section.stadium_id,
        density_pct=density_pct,
        density_level=density_level,
        source=crowd_source,
        occupancy_count=int((density_pct / 100) * section.capacity),
    )

    db.add(snapshot)
    await db.flush()

    logger.info(
        f"Crowd data ingested: section={section_id}, "
        f"density={density_pct:.1f}%, level={density_level.value}"
    )

    # Notify admin dashboards
    await manager.broadcast_to_admins({"type": "admin_refresh_required"})
    await write_operational_event(
        "crowd_snapshot_ingested",
        {
            "snapshot_id": snapshot.id,
            "stadium_id": snapshot.stadium_id,
            "section_id": snapshot.section_id,
            "density_pct": snapshot.density_pct,
            "density_level": snapshot.density_level,
            "source": snapshot.source,
        },
    )

    return snapshot


async def predict_crowd_congestion(
    db: AsyncSession,
    section_id: str,
    minutes_lookback: int = 30
) -> dict:
    """
    Predict how many minutes until a section hits 85% capacity (HIGH density).
    Uses linear regression on recent snapshots.
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=minutes_lookback)

    stmt = (
        select(CrowdSnapshot)
        .where(CrowdSnapshot.section_id == section_id)
        .where(CrowdSnapshot.created_at >= cutoff)
        .order_by(CrowdSnapshot.created_at.asc())
    )
    result = await db.execute(stmt)
    snapshots = result.scalars().all()

    if len(snapshots) < 2:
        return {"predicted_mins_to_85": None, "trend": "stable"}

    # time in minutes since cutoff
    t_values = [(s.created_at.replace(tzinfo=timezone.utc) - cutoff).total_seconds() / 60.0 for s in snapshots]
    d_values = [s.density_pct for s in snapshots]

    n = len(snapshots)
    sum_t = sum(t_values)
    sum_d = sum(d_values)
    sum_t_sq = sum(t * t for t in t_values)
    sum_td = sum(t * d for t, d in zip(t_values, d_values))

    denominator = (n * sum_t_sq - sum_t ** 2)
    if denominator == 0:
        return {"predicted_mins_to_85": None, "trend": "stable"}
        
    m = (n * sum_td - sum_t * sum_d) / denominator
    b = (sum_d * sum_t_sq - sum_t * sum_td) / denominator

    t_now = (now - cutoff).total_seconds() / 60.0

    if m <= 0:
        return {"predicted_mins_to_85": None, "trend": "decreasing" if m < -0.5 else "stable"}

    t_85 = (85.0 - b) / m
    mins_to_85 = t_85 - t_now

    if mins_to_85 < 0:
        return {"predicted_mins_to_85": 0, "trend": "increasing"}
        
    return {
        "predicted_mins_to_85": max(1, int(mins_to_85)),
        "trend": "increasing"
    }


async def get_stadium_crowd_map(
    db: AsyncSession,
    stadium_id: str,
) -> StadiumCrowdMap:
    """
    Get the latest crowd density for all sections in a stadium.
    Returns the most recent snapshot per section.
    """
    # Get all sections for the stadium
    sections_stmt = select(Section).where(Section.stadium_id == stadium_id)
    sections_result = await db.execute(sections_stmt)
    sections = sections_result.unique().scalars().all()

    if not sections:
        raise NotFoundException("Stadium sections", stadium_id)

    section_data = []
    total_capacity = 0
    total_occupancy = 0

    for section in sections:
        total_capacity += section.capacity

        # Get latest snapshot for this section
        snap_stmt = (
            select(CrowdSnapshot)
            .where(CrowdSnapshot.section_id == section.id)
            .order_by(desc(CrowdSnapshot.created_at))
            .limit(1)
        )
        snap_result = await db.execute(snap_stmt)
        snapshot = snap_result.unique().scalar_one_or_none()

        if snapshot:
            density_pct = snapshot.density_pct
            density_level = snapshot.density_level.value
            total_occupancy += snapshot.occupancy_count
            ts = snapshot.created_at
        else:
            density_pct = 0.0
            density_level = "low"
            ts = datetime.now(timezone.utc)

        prediction = await predict_crowd_congestion(db, section.id)
        trend = prediction.get("trend") or "stable"
        section_data.append(CrowdDensityResponse(
            section_id=section.id,
            section_name=section.name,
            density_pct=density_pct,
            density_level=density_level,
            timestamp=ts,
            predicted_mins_to_85=prediction.get("predicted_mins_to_85"),
            trend=trend,
            # Audio sentiment requires a separately authenticated source. Never
            # manufacture a crowd mood from density in a production dashboard.
            sentiment_score=None,
            acoustic_status=None,
        ))

    total_pct = (total_occupancy / total_capacity * 100) if total_capacity > 0 else 0

    return StadiumCrowdMap(
        stadium_id=stadium_id,
        sections=section_data,
        timestamp=datetime.now(timezone.utc),
        total_occupancy_pct=round(total_pct, 1),
    )
