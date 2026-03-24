"""
Session service: business logic for session management.
"""

from mcp_tracer.db.repositories.session import SessionRepository


class SessionService:
    """Service for session operations."""

    def __init__(self, repo: SessionRepository):
        self.repo = repo

    async def create_session(self, name: str, metadata: dict | None = None) -> dict:
        """
        Create a new session.

        Generates UUID, stores in DB, returns session ID and metadata.
        """
        pass

    async def get_session(self, session_id: str) -> dict:
        """Retrieve session by ID."""
        pass
