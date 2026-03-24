"""
Pydantic schemas for session tool I/O.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CreateSessionRequest(BaseModel):
    """Input schema for create_session tool."""

    name: str = Field(..., description="Human-readable session name")
    metadata: Optional[dict] = Field(None, description="Optional metadata")


class SessionResponse(BaseModel):
    """Output schema for session operations."""

    id: str = Field(..., description="Session ID")
    name: str = Field(..., description="Session name")
    created_at: datetime = Field(..., description="Creation timestamp")
    metadata: Optional[dict] = None
