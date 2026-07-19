"""
===============================================================================
File: backend/app/schemas/__init__.py
Purpose: Core Backend Application Module.
Architecture: FastAPI backend module.
Inputs: standard API requests or internal service calls.
Outputs: structured responses/models.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""
Stadium Sync — Shared Response Schemas.

Standard wrappers for all API responses ensuring consistency.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Error detail inside error responses."""
    code: str
    message: str
    request_id: str = ""
    details: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response wrapper."""
    success: bool = True
    data: T
    request_id: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""
    success: bool = False
    error: ErrorDetail


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""
    success: bool = True
    data: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    request_id: str = ""


class MessageResponse(BaseModel):
    """Simple message response."""
    success: bool = True
    message: str
    request_id: str = ""


# ── Pagination Parameters ──

class PaginationParams(BaseModel):
    """Common pagination query parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page
