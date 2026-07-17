import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.core.database import get_db_context
from app.models.volunteer import Volunteer

REAL_NAMES = [
    "Alex Johnson", "Sam Rivera", "Jordan Smith", "Taylor Lee",
    "Morgan Chen", "Casey Kim", "Riley Patel", "Avery Brooks"
]

async def main():
    async with get_db_context() as db:
        vol_res = await db.execute(select(Volunteer))
        vols = vol_res.scalars().all()
        for i, vol in enumerate(vols):
            vol.name = REAL_NAMES[i % len(REAL_NAMES)] + f" (Team {chr(65 + (i % 5))})"
            db.add(vol)
        await db.commit()
        print("Updated volunteer names.")

if __name__ == "__main__":
    asyncio.run(main())
