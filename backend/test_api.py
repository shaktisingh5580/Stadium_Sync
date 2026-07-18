import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post("https://stadium-sync.onrender.com/api/v1/auth/scan-ticket", json={"qr_payload": "{\"ticket_id\":\"ticket-001\",\"match_id\":\"M2026-QF1\",\"checksum\":\"642f90c0d004\"}"})
            print(res.status_code)
            print(res.text)
        except Exception as e:
            print("Error:", e)
            
if __name__ == "__main__":
    asyncio.run(main())
