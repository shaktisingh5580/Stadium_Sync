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
        vols = (await db.execute(select(Volunteer))).scalars().all()
        for v in vols[:5]:
            print(f"Volunteer: {v.name}")
        
        incs = (await db.execute(select(Incident))).scalars().all()
        for inc in incs:
            print(f"Incident {inc.id}: status={inc.status.value}, assigned={inc.assigned_volunteer_id}")

if __name__ == "__main__":
    asyncio.run(main())
