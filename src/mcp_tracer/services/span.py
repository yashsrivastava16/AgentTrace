"""
Span service — business logic for span lifecycle.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from mcp_tracer.db.repositories.span import SpanRepository
from mcp_tracer.db.repositories.session import SessionRepository


class SpanService:

    def __init__(self, db: AsyncSession):
        self.repo = SpanRepository(db)
        self.session_repo = SessionRepository(db)

    async def start_span(
        self,
        session_id: str,
        span_type: str,
        actor: str,
        target: str,
        input_: dict | None = None,
        parent_span_id: str | None = None,
    ) -> dict:
        # Validate session exists and is active
        session = await self.session_repo.get_by_id(uuid.UUID(session_id))
        if not session:
            raise ValueError(f"Session {session_id} not found")
        if session.status != "active":
            raise ValueError(
                f"Session {session_id} is {session.status}, only active sessions accept new spans"
            )

        # Validate parent span exists if provided
        parent_id = None
        if parent_span_id:
            parent = await self.repo.get_by_id(uuid.UUID(parent_span_id))
            if not parent:
                raise ValueError(f"Parent span {parent_span_id} not found")
            parent_id = uuid.UUID(parent_span_id)

        span = await self.repo.create(
            session_id=uuid.UUID(session_id),
            span_type=span_type,
            actor=actor,
            target=target,
            input_=input_,
            parent_span_id=parent_id,
        )
        return {
            "span_id": str(span.span_id),
            "session_id": str(span.session_id),
            "parent_span_id": str(span.parent_span_id) if span.parent_span_id else None,
            "span_type": span.span_type,
            "actor": span.actor,
            "target": span.target,
            "status": span.status,
            "started_at": span.started_at.isoformat(),
        }

    async def end_span(
        self,
        span_id: str,
        status: str,
        output_: dict | None = None,
    ) -> dict:
        # Validate span exists and is still running
        span = await self.repo.get_by_id(uuid.UUID(span_id))
        if not span:
            raise ValueError(f"Span {span_id} not found")
        if span.status != "running":
            raise ValueError(
                f"Span {span_id} is already {span.status}"
            )
        if status not in ("success", "failed"):
            raise ValueError("status must be 'success' or 'failed'")

        span = await self.repo.end(
            span_id=uuid.UUID(span_id),
            status=status,
            output_=output_,
        )
        return {
            "span_id": str(span.span_id),
            "status": span.status,
            "ended_at": span.ended_at.isoformat() if span.ended_at else None,
            "output": span.output_,
        }