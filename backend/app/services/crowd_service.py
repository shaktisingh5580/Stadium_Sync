"""
Stadium Sync — Crowd Density Service.

Handles ingestion of crowd density data from IoT sensors and
provides real-time stadium occupancy maps.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, BadRequestException
from app.models.crowd import (
    CrowdSnapshot,
    CrowdSource,
    DensityLevel,
)
from app.models.ticket import Section
from app.schemas.crowd import CrowdDensityResponse, StadiumCrowdMap

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

    return snapshot


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

        section_data.append(CrowdDensityResponse(
            section_id=section.id,
            section_name=section.name,
            density_pct=density_pct,
            density_level=density_level,
            timestamp=ts,
        ))

    total_pct = (total_occupancy / total_capacity * 100) if total_capacity > 0 else 0

    return StadiumCrowdMap(
        stadium_id=stadium_id,
        sections=section_data,
        timestamp=datetime.now(timezone.utc),
        total_occupancy_pct=round(total_pct, 1),
    )
