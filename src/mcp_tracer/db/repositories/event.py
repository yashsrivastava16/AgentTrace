"""
Event repository.

Handles all database queries for Event model.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from mcp_tracer.db.models.event import Event


class EventRepository:
    """Repository for Event operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, id: str, span_id: str, event_type: str, message: str, metadata: dict | None = None
    ) -> Event:
        """Create a new event."""
        pass

    async def get_by_span(self, span_id: str) -> list[Event]:
        """Get all events for a span."""
        pass

    async def get_by_session(self, session_id: str) -> list[Event]:
        """Get all events for a session."""
        pass
