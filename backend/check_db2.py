import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sqlalchemy import select
from app.core.database import get_db_context
from app.models.volunteer import Volunteer
from app.models.incident import Incident

async def main():
    async with get_db_context() as db:
        inc = await db.get(Incident, "d4be4a9e-1699-479b-92d5-92ae827059f3")
        if inc and inc.assigned_volunteer_id:
            vol = await db.get(Volunteer, inc.assigned_volunteer_id)
            print(f"Incident {inc.id} assigned to Volunteer ID {inc.assigned_volunteer_id}")
            print(f"Volunteer name is: {vol.name if vol else 'None'}")
        else:
            print("Incident not found or not assigned")

if __name__ == "__main__":
    asyncio.run(main())
