import asyncio
import random
import sys
import os
from datetime import datetime, timedelta

# Add parent dir to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.core.database import get_db_context
from app.models.ticket import Stadium, Section
from app.services.crowd_service import ingest_crowd_data, get_stadium_crowd_map
from app.api.v1.websocket import manager

async def live_crowd_simulation():
    print("🏟️  Starting Live Crowd Simulation...")
    
    async with get_db_context() as db:
        # Get stadium and sections
        stmt = select(Stadium).limit(1)
        result = await db.execute(stmt)
        stadium = result.unique().scalar_one_or_none()
        
        if not stadium:
            print("❌ No stadium found in database. Exiting.")
            return

        stmt = select(Section).where(Section.stadium_id == stadium.id)
        result = await db.execute(stmt)
        sections = result.unique().scalars().all()
        
        if not sections:
            print("❌ No sections found in database. Exiting.")
            return

        print(f"✅ Found Stadium: {stadium.name} with {len(sections)} sections.")
        print("📈 Seeding initial baseline crowd...")
        
        # Initial baseline density for each section (e.g. some are full, some are empty)
        baselines = {}
        for section in sections:
            baselines[section.id] = random.randint(20, 85)
            await ingest_crowd_data(db, section.id, baselines[section.id], source="iot_sensor")
            
        print("🔄 Running live fluctuation loop...")
        
        iteration = 0
        while True:
            # Fluctuate each section by -5 to +5
            for section in sections:
                current = baselines[section.id]
                change = random.randint(-5, 5)
                new_density = max(5, min(98, current + change))
                baselines[section.id] = new_density
                
                await ingest_crowd_data(db, section.id, new_density, source="iot_sensor")
            
            # Clean up old data (keep only last 10 mins to prevent DB bloat)
            if iteration % 10 == 0:
                from app.models.crowd import CrowdSnapshot
                cutoff = datetime.utcnow() - timedelta(minutes=10)
                del_stmt = delete(CrowdSnapshot).where(CrowdSnapshot.created_at < cutoff)
                await db.execute(del_stmt)
                await db.commit()
                
            iteration += 1
            
            # Optionally broadcast crowd map if needed by websocket (the UI currently fetches on mount, 
            # but we can push updates if we want to, though the task didn't strictly ask to push crowd WS, 
            # only to make the DB look live. If UI supports it, we could push `manager.broadcast_all`)
            
            crowd_map = await get_stadium_crowd_map(db, stadium.id)
            await manager.broadcast_all({
                "type": "crowd_update",
                "heatmapData": {s.section_id: s.density_pct for s in crowd_map.sections}
            })
            
            # Wait 2 seconds for a realistic "live" feel
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(live_crowd_simulation())
