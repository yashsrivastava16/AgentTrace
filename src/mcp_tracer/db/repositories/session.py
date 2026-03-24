"""
Session repository.

Handles all database queries for Session model.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from mcp_tracer.db.models.session import Session


class SessionRepository:
    """Repository for Session operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, id: str, name: str, metadata: dict | None = None) -> Session:
        """Create a new session."""
        pass

    async def get_by_id(self, session_id: str) -> Session | None:
        """Get session by ID."""
        pass

    async def list_all(self) -> list[Session]:
        """Get all sessions."""
        pass
