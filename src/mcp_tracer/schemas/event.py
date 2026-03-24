"""
Pydantic schemas for event tool I/O.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


class LogEventRequest(BaseModel):
    """Input schema for log_event tool."""

    span_id: str = Field(..., description="Span ID")
    event_type: Literal["error", "warning", "info", "debug"] = Field(..., description="Event type")
    message: str = Field(..., description="Event message")
    metadata: Optional[dict] = Field(None, description="Optional metadata")


class EventResponse(BaseModel):
    """Output schema for event operations."""

    id: str = Field(..., description="Event ID")
    span_id: str = Field(..., description="Span ID")
    type: str = Field(..., description="Event type")
    message: str = Field(..., description="Event message")
    created_at: datetime = Field(..., description="Creation timestamp")
