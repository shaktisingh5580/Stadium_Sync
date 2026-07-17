import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.core.database import get_db_context
from app.models.volunteer import Volunteer, VolunteerStatus
from app.models.incident import Incident, IncidentStatus

async def main():
    async with get_db_context() as db:
        # Get open incidents
        res = await db.execute(select(Incident).where(Incident.status == IncidentStatus.OPEN))
        incidents = res.scalars().all()
        
        # Get available volunteers
        vol_res = await db.execute(select(Volunteer).where(Volunteer.status == VolunteerStatus.AVAILABLE))
        vols = vol_res.scalars().all()
        
        for inc in incidents:
            if not vols: break
            vol = vols.pop(0)
            inc.assigned_volunteer_id = vol.id
            inc.status = IncidentStatus.ASSIGNED
            vol.status = VolunteerStatus.BUSY
            db.add(inc)
            db.add(vol)
        
        await db.commit()
        print(f"Fixed {len(incidents)} open incidents.")

if __name__ == "__main__":
    asyncio.run(main())
