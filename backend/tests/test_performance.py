"""
===============================================================================
FILE: backend/tests/test_performance.py
PURPOSE: Provides core functionality and logic for this module.
ARCHITECTURE: Python/FastAPI module
INPUTS: Standard application requests
OUTPUTS: Structured models and responses
HACKATHON VERTICAL: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
import pytest
import asyncio
from httpx import AsyncClient

# We will need the pytest-benchmark plugin.
# Run with: pytest backend/tests/test_performance.py

@pytest.mark.asyncio
async def test_qr_scan_latency_under_100ms(benchmark, test_client: AsyncClient):
    """
    Ensure QR scan endpoint responds in < 100ms for rapid stadium entry.
    """
    valid_payload = {
        "qr_payload": '{"ticket_id":"test-123","match_id":"match-1","checksum":"fake-checksum"}'
    }

    async def run_scan():
        # Ideally this would hit a mock or local DB
        # For demonstration of the benchmark structure:
        response = await test_client.post("/api/v1/auth/scan-ticket", json=valid_payload)
        return response

    # Wrap the async function to run synchronously for the benchmark
    def sync_run():
        return asyncio.run(run_scan())

    result = benchmark(sync_run)
    # The benchmark framework will record execution times.
    # We can assert that the average time is < 0.1s (100ms)
    assert benchmark.stats.stats.mean < 0.1

@pytest.mark.asyncio
async def test_gemini_response_under_3s(benchmark):
    """
    Ensure AI response completes within 3 seconds.
    """
    from app.services.gemini_client import agentic_chat

    async def run_chat():
        return await agentic_chat("Where is the restroom?")

    def sync_run():
        return asyncio.run(run_chat())

    result = benchmark(sync_run)
    # 3.0 seconds max average
    assert benchmark.stats.stats.mean < 3.0
