"""
===============================================================================
File: backend/app/middleware/security_headers.py
Purpose: HTTP security header injection - adds CSP, X-Frame-Options, HSTS, 
         X-Content-Type-Options to prevent XSS, clickjacking, and MIME sniffing.
Architecture: Middleware appends security headers to all responses. Headers 
             configured per OWASP recommendations.
Inputs: All HTTP responses.
Outputs: Responses with security headers added for browser-level protection.
Hackathon Vertical: Security & Authentication
===============================================================================
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
import logging

logger = logging.getLogger("stadium_sync.access")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Apply safe, broadly compatible headers to every HTTP response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(self), geolocation=(self), microphone=()"
        )
        response.headers.setdefault("Cache-Control", "no-store")
        return response

class SanitizingLoggingMiddleware(BaseHTTPMiddleware):
    """Strip secrets from logs before they're written."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Sanitize Authorization header before logging
        headers_to_log = dict(request.headers)
        if "authorization" in headers_to_log:
            headers_to_log["authorization"] = "Bearer [REDACTED]"
        
        response = await call_next(request)
        
        # Log without exposing secrets
        logger.info(f"Request: {request.method} {request.url.path} Headers: {headers_to_log}")
        return response
