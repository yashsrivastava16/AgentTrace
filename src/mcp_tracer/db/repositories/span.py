"""
Span repository.

Handles all database queries for Span model.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from mcp_tracer.db.models.span import Span


class SpanRepository:
    """Repository for Span operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        id: str,
        session_id: str,
        span_type: str,
        parent_span_id: str | None = None,
        metadata: dict | None = None,
    ) -> Span:
        """Create a new span."""
        pass

    async def get_by_id(self, span_id: str) -> Span | None:
        """Get span by ID."""
        pass

    async def get_by_session(self, session_id: str) -> list[Span]:
        """Get all spans for a session."""
        pass

    async def update(self, span_id: str, output_data: dict, status: str) -> Span:
        """Update span with output and status."""
        pass
