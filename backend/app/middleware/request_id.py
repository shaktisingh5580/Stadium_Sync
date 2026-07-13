"""
Stadium Sync — Request ID Middleware.

Generates a unique UUID for each request, attaches it to
request.state and adds it as X-Request-ID response header.
Used by error handlers for tracing.
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
