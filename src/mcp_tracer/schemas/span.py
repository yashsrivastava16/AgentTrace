"""
Pydantic schemas for span tool I/O.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


class StartSpanRequest(BaseModel):
    """Input schema for start_span tool."""

    session_id: str = Field(..., description="Session ID")
    span_type: Literal["human_input", "agent_call", "tool_call", "hitl"] = Field(
        ..., description="Type of span"
    )
    parent_span_id: Optional[str] = Field(None, description="Optional parent span ID")
    metadata: Optional[dict] = Field(None, description="Optional metadata")


class EndSpanRequest(BaseModel):
    """Input schema for end_span tool."""

    span_id: str = Field(..., description="Span ID to end")
    output: Optional[dict] = Field(None, description="Output data")
    status: Literal["success", "error", "pending"] = Field("success", description="Span status")


class SpanResponse(BaseModel):
    """Output schema for span operations."""

    id: str = Field(..., description="Span ID")
    session_id: str = Field(..., description="Session ID")
    type: str = Field(..., description="Span type")
    status: str = Field(..., description="Span status")
    created_at: datetime = Field(..., description="Creation timestamp")
