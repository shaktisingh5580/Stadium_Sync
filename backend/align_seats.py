import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os

DB_URL = "sqlite+aiosqlite:///stadium_sync.db"
engine = create_async_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

section_centers = {
    'section-n101': (273, 168),
    'section-n102': (527, 168),
    'section-n103': (632, 293),
    'section-n104': (632, 507),
    'section-s201': (527, 632),
    'section-s202': (273, 632),
    'section-s203': (168, 507),
    'section-s204': (168, 293),
}

async def main():
    async with SessionLocal() as db:
        for sec_id, (cx, cy) in section_centers.items():
            result = await db.execute(text("SELECT id FROM seats WHERE section_id = :sec_id"), {"sec_id": sec_id})
            seats = result.fetchall()
            
            # distribute seats nicely around the center in a grid
            grid_size = 4
            offset = 12
            for i, seat in enumerate(seats):
                row = i // grid_size
                col = i % grid_size
                # calculate simple offset
                dx = (col - (grid_size - 1) / 2) * offset
                dy = (row - (grid_size - 1) / 2) * offset
                
                new_x = cx + dx
                new_y = cy + dy
                
                await db.execute(
                    text("UPDATE seats SET svg_x = :x, svg_y = :y WHERE id = :seat_id"),
                    {"x": new_x, "y": new_y, "seat_id": seat[0]}
                )
        await db.commit()
        print("✅ Seats beautifully aligned to SVG sections!")

if __name__ == "__main__":
    asyncio.run(main())
