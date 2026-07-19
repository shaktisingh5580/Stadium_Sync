"""
===============================================================================
FILE: backend/scripts/generate_test_tickets.py
PURPOSE: Stadium Sync — Test Ticket Seeder Script. Seeds the database with: - 1 Stadium (MetLife Stadium) - 8 Sections (N101-N104, S201-S204) - 4 Gates (North, South, East, West) - 100 Seats (distributed across sections) - 20 Test Tickets with valid QR payloads - Amenity points and waste bins per section Run: python -m scripts.generate_test_tickets or: .venv/Scripts/python -m scripts.generate_test_tickets
ARCHITECTURE: Python/FastAPI module
INPUTS: Standard application requests
OUTPUTS: Structured models and responses
HACKATHON VERTICAL: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
import asyncio
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db_context, create_tables
from app.models.ticket import (
    Gate, GateType, Seat, Section, SectionType, Stadium, Ticket,
)
from app.models.stadium import (
    AmenityPoint, AmenityType, WasteBin, BinType,
)
from app.services.ticket_service import generate_qr_payload
from sqlalchemy import select


# ── Stadium Data ──

STADIUM = {
    "id": "stadium-metlife-001",
    "name": "MetLife Stadium",
    "city": "East Rutherford",
    "country": "USA",
    "capacity": 82500,
}

SECTIONS = [
    {"id": "section-n101", "name": "N101", "type": SectionType.GENERAL, "cap": 1200, "svg_x": 100, "svg_y": 50, "svg_w": 150, "svg_h": 100},
    {"id": "section-n102", "name": "N102", "type": SectionType.GENERAL, "cap": 1200, "svg_x": 260, "svg_y": 50, "svg_w": 150, "svg_h": 100},
    {"id": "section-n103", "name": "N103", "type": SectionType.VIP, "cap": 500, "svg_x": 420, "svg_y": 50, "svg_w": 150, "svg_h": 100},
    {"id": "section-n104", "name": "N104", "type": SectionType.GENERAL, "cap": 1200, "svg_x": 580, "svg_y": 50, "svg_w": 150, "svg_h": 100},
    {"id": "section-s201", "name": "S201", "type": SectionType.GENERAL, "cap": 1200, "svg_x": 100, "svg_y": 450, "svg_w": 150, "svg_h": 100},
    {"id": "section-s202", "name": "S202", "type": SectionType.PREMIUM, "cap": 800, "svg_x": 260, "svg_y": 450, "svg_w": 150, "svg_h": 100},
    {"id": "section-s203", "name": "S203", "type": SectionType.GENERAL, "cap": 1200, "svg_x": 420, "svg_y": 450, "svg_w": 150, "svg_h": 100},
    {"id": "section-s204", "name": "S204", "type": SectionType.GENERAL, "cap": 1200, "svg_x": 580, "svg_y": 450, "svg_w": 150, "svg_h": 100},
]

GATES = [
    {"id": "gate-north", "name": "Gate North", "type": GateType.ENTRY_EXIT, "cap": 3000, "svg_x": 400, "svg_y": 10, "lat": 40.8135, "lng": -74.0745, "transit": "metro"},
    {"id": "gate-south", "name": "Gate South", "type": GateType.ENTRY_EXIT, "cap": 3000, "svg_x": 400, "svg_y": 590, "lat": 40.8115, "lng": -74.0745, "transit": "bus"},
    {"id": "gate-east", "name": "Gate East", "type": GateType.ENTRY_EXIT, "cap": 2500, "svg_x": 790, "svg_y": 300, "lat": 40.8125, "lng": -74.0725, "transit": "rideshare"},
    {"id": "gate-west", "name": "Gate West", "type": GateType.ENTRY_EXIT, "cap": 2500, "svg_x": 10, "svg_y": 300, "lat": 40.8125, "lng": -74.0765, "transit": "parking"},
]

MATCH_ID = "M2026-QF1"
FAN_NAMES = [
    "Carlos Rivera", "Aisha Okafor", "Yuki Tanaka", "Emma Wilson",
    "Lucas Schmidt", "Fatima Al-Rashid", "Chen Wei", "Maria Santos",
    "James O'Connor", "Priya Sharma", "David Kim", "Sarah Johnson",
    "Mohammed Ali", "Anna Petrova", "Luis Mendoza", "Grace Nakamura",
    "Omar Hassan", "Sofia Costa", "Ryan Mitchell", "Elena Volkov",
]


async def seed_database():
    """Seed the database with test stadium data."""
    print("\n🏟️  Stadium Sync — Test Data Seeder")
    print("=" * 50)

    async with get_db_context() as db:
        # Check if already seeded
        existing = await db.execute(select(Stadium).where(Stadium.id == STADIUM["id"]))
        if existing.scalar_one_or_none():
            print("✅ Database is already seeded. Run this on a fresh database to re-seed.")
            return

        # ── 1. Create Stadium ──
        stadium = Stadium(
            id=STADIUM["id"],
            name=STADIUM["name"],
            city=STADIUM["city"],
            country=STADIUM["country"],
            capacity=STADIUM["capacity"],
        )
        db.add(stadium)
        await db.flush()
        print(f"✅ Stadium: {stadium.name} ({stadium.capacity:,} capacity)")

        # ── 2. Create Sections ──
        section_objs = []
        for s in SECTIONS:
            section = Section(
                id=s["id"],
                stadium_id=STADIUM["id"],
                name=s["name"],
                section_type=s["type"],
                capacity=s["cap"],
                svg_x=s["svg_x"],
                svg_y=s["svg_y"],
                svg_width=s["svg_w"],
                svg_height=s["svg_h"],
            )
            db.add(section)
            section_objs.append(section)
        await db.flush()
        print(f"✅ Sections: {len(section_objs)} created ({', '.join(s['name'] for s in SECTIONS)})")

        # ── 3. Create Gates ──
        for g in GATES:
            gate = Gate(
                id=g["id"],
                stadium_id=STADIUM["id"],
                name=g["name"],
                gate_type=g["type"],
                capacity=g["cap"],
                svg_x=g["svg_x"],
                svg_y=g["svg_y"],
                lat=g["lat"],
                lng=g["lng"],
                nearest_transit=g["transit"],
            )
            db.add(gate)
        await db.flush()
        print(f"✅ Gates: {len(GATES)} created ({', '.join(g['name'] for g in GATES)})")

        # ── 4. Create Seats (100 across 8 sections) ──
        seats = []
        seat_idx = 0
        for section_data, section_obj in zip(SECTIONS, section_objs):
            rows_per_section = 3
            seats_per_row = 4
            for row_num in range(1, rows_per_section + 1):
                for seat_num in range(1, seats_per_row + 1):
                    seat_idx += 1
                    seat = Seat(
                        id=f"seat-{seat_idx:03d}",
                        section_id=section_data["id"],
                        row=str(row_num),
                        number=seat_num,
                        svg_x=section_data["svg_x"] + 20 + (seat_num * 25),
                        svg_y=section_data["svg_y"] + 20 + (row_num * 20),
                    )
                    db.add(seat)
                    seats.append(seat)
        await db.flush()
        print(f"✅ Seats: {len(seats)} created across {len(SECTIONS)} sections")

        # ── 5. Create Tickets (20 fans) ──
        tickets = []
        print(f"\n📱 Test QR Payloads:")
        print("-" * 50)
        for i, name in enumerate(FAN_NAMES):
            ticket_id = f"ticket-{i+1:03d}"
            seat = seats[i % len(seats)]
            qr_payload = generate_qr_payload(ticket_id, MATCH_ID)

            ticket = Ticket(
                id=ticket_id,
                match_id=MATCH_ID,
                seat_id=seat.id,
                qr_payload=qr_payload,
                holder_name=name,
                holder_email=f"{name.lower().replace(' ', '.')}@example.com",
                is_active=True,
                needs_accessibility=(i == 0),
            )
            db.add(ticket)
            tickets.append(ticket)

            if i < 5:  # Print first 5 QR payloads for testing
                print(f"  Fan: {name:<20} | Seat: {seat.id:<12} | QR: {qr_payload}")

        # Make one inactive ticket for testing
        tickets[-1].is_active = False

        await db.flush()
        print(f"  ... and {len(tickets) - 5} more")
        print(f"\n✅ Tickets: {len(tickets)} created ({len(tickets)-1} active, 1 inactive)")

        # ── 6. Create Amenities ──
        amenity_count = 0
        for section_data in SECTIONS:
            for amenity_type, name_suffix in [
                (AmenityType.RESTROOM, "Restroom"),
                (AmenityType.FOOD, "Food Court"),
                (AmenityType.WATER, "Water Station"),
            ]:
                amenity = AmenityPoint(
                    stadium_id=STADIUM["id"],
                    section_id=section_data["id"],
                    amenity_type=amenity_type,
                    name=f"{section_data['name']} {name_suffix}",
                    svg_x=section_data["svg_x"] + 75,
                    svg_y=section_data["svg_y"] - 15 + (amenity_count % 3) * 10,
                )
                db.add(amenity)
                amenity_count += 1
        # Add first aid stations near each gate
        for g in GATES:
            amenity = AmenityPoint(
                stadium_id=STADIUM["id"],
                amenity_type=AmenityType.FIRST_AID,
                name=f"First Aid - {g['name']}",
                svg_x=g["svg_x"],
                svg_y=g["svg_y"] + 20,
            )
            db.add(amenity)
            amenity_count += 1
        await db.flush()
        print(f"✅ Amenities: {amenity_count} created")

        # ── 7. Create Waste Bins ──
        bin_count = 0
        for section_data in SECTIONS:
            for bin_type in [BinType.COMPOST, BinType.RECYCLE, BinType.LANDFILL]:
                waste_bin = WasteBin(
                    stadium_id=STADIUM["id"],
                    section_id=section_data["id"],
                    bin_type=bin_type,
                    svg_x=section_data["svg_x"] + 50 + bin_count % 3 * 30,
                    svg_y=section_data["svg_y"] + 110,
                )
                db.add(waste_bin)
                bin_count += 1
        await db.flush()
        print(f"✅ Waste Bins: {bin_count} created")

    print(f"\n{'=' * 50}")
    print("🎉 Seeding complete! Database is ready for testing.")
    print(f"\nTo test, use any QR payload above with POST /api/v1/auth/scan-ticket")


async def main():
    """Main entry point: create tables then seed."""
    await create_tables()
    await seed_database()


if __name__ == "__main__":
    asyncio.run(main())
