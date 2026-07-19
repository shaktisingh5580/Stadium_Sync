"""
===============================================================================
File: backend/app/schemas/__init__.py
Purpose: Package initialization for Pydantic request/response schemas - 
         centralizes validation and serialization models.
Architecture: Exports all schema classes to enable clean imports like 
             'from app.schemas import QRScanRequest, ChatResponse'.
Inputs: None (package initialization)
Outputs: Centralized schema access for route handlers and documentation.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
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
