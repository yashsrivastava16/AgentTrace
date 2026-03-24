"""
Query service: business logic for querying and trace tree reconstruction.
"""

from mcp_tracer.db.repositories.query import QueryRepository


class QueryService:
    """Service for querying and trace construction."""

    def __init__(self, repo: QueryRepository):
        self.repo = repo

    async def query_session(self, session_id: str) -> dict:
        """
        Get full trace tree for a session.

        Uses QueryRepository to reconstruct tree from parent_span_id relationships.
        """
        pass

    async def query_cross_session(self, filters: dict | None = None) -> list[dict]:
        """
        Query spans/events across all sessions.

        Builds filter predicates and executes cross-session query.
        """
        pass
