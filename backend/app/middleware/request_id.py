"""
===============================================================================
File: backend/app/middleware/request_id.py
Purpose: X-Request-ID injection - assigns unique UUID to every request for 
         end-to-end tracing through logs, database, and external APIs.
Architecture: Middleware generates UUID (if not present in header) and stores 
             in request.state.request_id. All downstream operations can access 
             and log this ID for correlation.
Inputs: HTTP requests (with optional existing X-Request-ID header).
Outputs: UUID stored in request state and included in X-Request-ID response 
         header for client-side bug reporting.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Inject a unique request ID into every request/response cycle."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate or use existing request ID
        request_id = request.headers.get(
            "X-Request-ID", str(uuid.uuid4())
        )

        # Attach to request state for downstream use
        request.state.request_id = request_id

        # Process the request
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Request-ID"] = request_id

        return response
