"""
Span service: business logic for span lifecycle management.
"""

from mcp_tracer.db.repositories.span import SpanRepository


class SpanService:
    """Service for span operations."""

    def __init__(self, repo: SpanRepository):
        self.repo = repo

    async def start_span(
        self,
        session_id: str,
        span_type: str,
        parent_span_id: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """
        Start a new span within a session.

        Generates UUID, validates parent_span_id, stores in DB.
        """
        pass

    async def end_span(self, span_id: str, output: dict | None = None, status: str = "success") -> dict:
        """
        End a span and record output.

        Updates span status, output, and timestamps.
        """
        pass
