import asyncio
from app.core.database import get_db_context
from app.models.ticket import Ticket
from sqlalchemy import select

async def main():
    async with get_db_context() as db:
        res = await db.execute(select(Ticket).where(Ticket.holder_name == "Carlos Rivera"))
        ticket = res.scalar_one_or_none()
        if ticket:
            print(f"Ticket exists: {ticket.id}, Stadium: {ticket.stadium_id}")
        else:
            print("Ticket not found!")

if __name__ == "__main__":
    asyncio.run(main())
