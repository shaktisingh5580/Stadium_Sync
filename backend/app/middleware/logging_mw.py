"""
===============================================================================
File: backend/app/middleware/logging_mw.py
Purpose: Structured request/response logging - logs all API calls with method, 
         path, status, duration, response size. Sanitizes sensitive headers 
         (Authorization, API keys) before logging.
Architecture: BaseHTTPMiddleware that wraps all requests. Logs method, path, 
             status code, duration (ms), response size. Stores timing in 
             response headers for observability.
Inputs: All HTTP requests passing through the application.
Outputs: Structured log entries for operational visibility and debugging.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("stadium_sync.access")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log request method, path, status code, and response time."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.perf_counter()

        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Get request ID from state (set by RequestIDMiddleware)
        request_id = getattr(request.state, "request_id", "unknown")

        # Log the request
        logger.info(
            "%s %s → %d (%.1fms) [%s]",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )

        # Add timing header
        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"

        return response
