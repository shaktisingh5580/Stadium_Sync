import asyncio
from app.core.database import get_db_context
from app.services.crowd_service import get_stadium_crowd_map

async def main():
    async with get_db_context() as db:
        try:
            crowd = await get_stadium_crowd_map(db, "stadium-metlife-001")
            print([(s.section_id, s.density_pct) for s in crowd.sections])
        except Exception as e:
            print("ERROR:", e)

if __name__ == "__main__":
    asyncio.run(main())
