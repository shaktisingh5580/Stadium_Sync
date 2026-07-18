import httpx
import asyncio

async def test_webhook():
    payload = {
        "type": "FIRE_SMOKE",
        "location": "South Block",
        "confidence": 0.98,
        "description": "Dense smoke and thermal anomaly detected in concourse.",
        "image_url": "https://images.unsplash.com/photo-1542282088-fe8426682b8f?auto=format&fit=crop&w=800&q=80"
    }

    url = "http://localhost:8000/api/v1/admin/cv-webhook"
    
    print(f"Sending webhook to {url}...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.json())

if __name__ == "__main__":
    asyncio.run(test_webhook())
