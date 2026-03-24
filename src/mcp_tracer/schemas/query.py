"""
Pydantic schemas for query tool I/O.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any


class QuerySessionRequest(BaseModel):
    """Input schema for query_session tool."""

    session_id: str = Field(..., description="Session ID to query")


class QuerySessionResponse(BaseModel):
    """Output schema for query_session tool."""

    session_id: str = Field(..., description="Session ID")
    spans: list[dict] = Field(..., description="List of spans")
    events: list[dict] = Field(..., description="List of events")
    trace_tree: dict = Field(..., description="Nested trace tree")


class QueryCrossSessionRequest(BaseModel):
    """Input schema for query_cross_session tool."""

    filters: Optional[dict] = Field(
        None,
        description="Optional filters: agent, error_type, span_type, time_range",
    )


class QueryCrossSessionResponse(BaseModel):
    """Output schema for query_cross_session tool."""

    results: list[dict] = Field(..., description="Matching spans/events")
    count: int = Field(..., description="Total count")
