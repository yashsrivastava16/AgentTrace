"""
Query repository — trace tree reconstruction and cross-session querying.
"""
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mcp_tracer.db.models.session import Session
from mcp_tracer.db.models.span import Span
from mcp_tracer.db.models.event import Event


class QueryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_session_trace(self, session_id: uuid.UUID) -> dict | None:
        """
        Fetch a full session with all spans and events,
        then reconstruct it as a nested trace tree.
        """
        # Fetch session
        session_result = await self.db.execute(
            select(Session).where(Session.session_id == session_id)
        )
        session = session_result.scalar_one_or_none()

        if not session:
            return None

        # Fetch all spans for session with their events eagerly loaded
        spans_result = await self.db.execute(
            select(Span)
            .where(Span.session_id == session_id)
            .options(selectinload(Span.events))
            .order_by(Span.started_at.asc())
        )
        spans = list(spans_result.scalars().all())

        # Build trace tree
        tree = self._build_tree(spans)

        return {
            "session_id": str(session.session_id),
            "name": session.name,
            "status": session.status,
            "metadata": session.metadata_,
            "started_at": session.started_at.isoformat(),
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "spans": tree,
        }

    def _build_tree(self, spans: list[Span]) -> list[dict]:
        """
        Convert flat list of spans into a nested tree
        using parent_span_id references.
        """
        # Index all spans by their id
        span_map: dict[uuid.UUID, dict] = {}
        for span in spans:
            span_map[span.span_id] = {
                "span_id": str(span.span_id),
                "parent_span_id": str(span.parent_span_id) if span.parent_span_id else None,
                "span_type": span.span_type,
                "actor": span.actor,
                "target": span.target,
                "status": span.status,
                "input": span.input_,
                "output": span.output_,
                "started_at": span.started_at.isoformat(),
                "ended_at": span.ended_at.isoformat() if span.ended_at else None,
                "events": [
                    {
                        "event_id": str(e.event_id),
                        "event_type": e.event_type,
                        "message": e.message,
                        "metadata": e.metadata_,
                        "created_at": e.created_at.isoformat(),
                    }
                    for e in sorted(span.events, key=lambda x: x.created_at)
                ],
                "children": [],  # will be populated below
            }

        # Wire children to parents
        roots = []
        for span in spans:
            node = span_map[span.span_id]
            if span.parent_span_id and span.parent_span_id in span_map:
                span_map[span.parent_span_id]["children"].append(node)
            else:
                roots.append(node)

        return roots

    async def cross_session_query(
        self,
        actor: str | None = None,
        span_type: str | None = None,
        status: str | None = None,
        event_type: str | None = None,
        started_after: datetime | None = None,
        started_before: datetime | None = None,
    ) -> list[dict]:
        """
        Query spans across all sessions with optional filters.
        Returns spans with their parent session context.
        """
        query = (
            select(Span)
            .options(selectinload(Span.events))
            .join(Session, Span.session_id == Session.session_id)
        )

        if actor:
            query = query.where(Span.actor == actor)
        if span_type:
            query = query.where(Span.span_type == span_type)
        if status:
            query = query.where(Span.status == status)
        if started_after:
            query = query.where(Span.started_at >= started_after)
        if started_before:
            query = query.where(Span.started_at <= started_before)
        if event_type:
            query = query.where(
                Span.span_id.in_(
                    select(Event.span_id).where(Event.event_type == event_type)
                )
            )

        query = query.order_by(Span.started_at.desc())
        result = await self.db.execute(query)
        spans = list(result.scalars().all())

        # Include session context with each span
        return [
            {
                "span_id": str(s.span_id),
                "session_id": str(s.session_id),
                "span_type": s.span_type,
                "actor": s.actor,
                "target": s.target,
                "status": s.status,
                "started_at": s.started_at.isoformat(),
                "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                "events": [
                    {
                        "event_id": str(e.event_id),
                        "event_type": e.event_type,
                        "message": e.message,
                        "created_at": e.created_at.isoformat(),
                    }
                    for e in sorted(s.events, key=lambda x: x.created_at)
                ],
            }
            for s in spans
        ]