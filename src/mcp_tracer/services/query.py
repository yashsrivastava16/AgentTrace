"""
Query service — trace tree retrieval and cross-session querying.
"""
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from mcp_tracer.db.repositories.query import QueryRepository


class QueryService:

    def __init__(self, db: AsyncSession):
        self.repo = QueryRepository(db)

    async def get_session_trace(self, session_id: str) -> dict:
        trace = await self.repo.get_session_trace(uuid.UUID(session_id))
        if not trace:
            raise ValueError(f"Session {session_id} not found")
        return trace

    async def cross_session_query(
        self,
        actor: str | None = None,
        span_type: str | None = None,
        status: str | None = None,
        event_type: str | None = None,
        started_after: str | None = None,   # ISO string from MCP tool input
        started_before: str | None = None,
    ) -> list[dict]:
        # Parse ISO strings to datetime if provided
        after_dt = datetime.fromisoformat(started_after) if started_after else None
        before_dt = datetime.fromisoformat(started_before) if started_before else None

        return await self.repo.cross_session_query(
            actor=actor,
            span_type=span_type,
            status=status,
            event_type=event_type,
            started_after=after_dt,
            started_before=before_dt,
        )