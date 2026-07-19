"""
===============================================================================
File: backend/app/core/exceptions.py
Purpose: Core Backend Application Module.
Architecture: FastAPI backend module.
Inputs: standard API requests or internal service calls.
Outputs: structured responses/models.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""
Stadium Sync — Custom Exceptions and Error Handlers.

Provides structured JSON error responses across the entire API.
All exceptions follow the format:
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": { ... }  // optional
    }
}
"""

from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse


# ── Base Exception ──

class StadiumSyncException(Exception):
    """Base exception for all Stadium Sync errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


# ── Specific Exceptions ──

class NotFoundException(StadiumSyncException):
    """Resource not found (404)."""

    def __init__(self, resource: str = "Resource", resource_id: Any = None):
        details = {"resource": resource}
        if resource_id:
            details["id"] = str(resource_id)
        super().__init__(
            message=f"{resource} not found",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class UnauthorizedException(StadiumSyncException):
    """Authentication required or failed (401)."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(StadiumSyncException):
    """Insufficient permissions (403)."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class RateLimitExceededException(StadiumSyncException):
    """Too many requests (429)."""

    def __init__(self, limit: str = ""):
        msg = "Rate limit exceeded"
        if limit:
            msg += f" ({limit})"
        super().__init__(
            message=msg,
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"limit": limit} if limit else None,
        )


class ConflictException(StadiumSyncException):
    """Resource conflict (409)."""

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
        )


class BadRequestException(StadiumSyncException):
    """Bad request (400)."""

    def __init__(self, message: str = "Bad request", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="BAD_REQUEST",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class AIServiceException(StadiumSyncException):
    """AI service (Gemini) unavailable or failed (503)."""

    def __init__(self, message: str = "AI service temporarily unavailable"):
        super().__init__(
            message=message,
            code="AI_SERVICE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class ExternalServiceException(StadiumSyncException):
    """External service (Telegram, etc.) failed (502)."""

    def __init__(self, service: str, message: str = ""):
        super().__init__(
            message=message or f"{service} service error",
            code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={"service": service},
        )


# ── Error Response Builder ──

def _build_error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: Optional[Dict] = None,
) -> ORJSONResponse:
    """Build a consistent error response."""
    request_id = getattr(request.state, "request_id", "unknown")
    body: Dict[str, Any] = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        },
    }
    if details:
        body["error"]["details"] = details
    return ORJSONResponse(status_code=status_code, content=body)


# ── Exception Handlers ──

async def stadium_sync_exception_handler(
    request: Request, exc: StadiumSyncException
) -> ORJSONResponse:
    """Handle all StadiumSyncException subclasses."""
    return _build_error_response(
        request=request,
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> ORJSONResponse:
    """Handle Pydantic validation errors with field-level detail."""
    field_errors = []
    for error in exc.errors():
        field_errors.append({
            "field": " → ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    return _build_error_response(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"fields": field_errors},
    )


async def generic_exception_handler(
    request: Request, exc: Exception
) -> ORJSONResponse:
    """Catch-all handler. Masks internal details in production."""
    from app.core.config import get_settings

    settings = get_settings()
    message = str(exc) if settings.DEBUG else "An unexpected error occurred"
    return _build_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_ERROR",
        message=message,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app."""
    app.add_exception_handler(StadiumSyncException, stadium_sync_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
