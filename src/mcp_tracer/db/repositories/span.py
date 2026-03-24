"""
Span repository — all DB operations for Span model.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_tracer.db.models.span import Span


class SpanRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        session_id: uuid.UUID,
        span_type: str,
        actor: str,
        target: str,
        input_: dict | None = None,
        parent_span_id: uuid.UUID | None = None,
    ) -> Span:
        span = Span(
            span_id=uuid.uuid4(),
            session_id=session_id,
            parent_span_id=parent_span_id,
            span_type=span_type,
            actor=actor,
            target=target,
            status="running",
            input_=input_,
        )
        self.db.add(span)
        await self.db.flush()
        return span

    async def get_by_id(self, span_id: uuid.UUID) -> Span | None:
        result = await self.db.execute(
            select(Span).where(Span.span_id == span_id)
        )
        return result.scalar_one_or_none()

    async def get_by_session(self, session_id: uuid.UUID) -> list[Span]:
        result = await self.db.execute(
            select(Span)
            .where(Span.session_id == session_id)
            .order_by(Span.started_at.asc())
        )
        return list(result.scalars().all())

    async def end(
        self,
        span_id: uuid.UUID,
        status: str,
        output_: dict | None = None,
    ) -> Span | None:
        await self.db.execute(
            update(Span)
            .where(Span.span_id == span_id)
            .values(
                status=status,
                output_=output_,
                ended_at=datetime.now(timezone.utc),
            )
        )
        await self.db.flush()
        return await self.get_by_id(span_id)

    async def get_by_filters(
        self,
        actor: str | None = None,
        span_type: str | None = None,
        status: str | None = None,
        started_after: datetime | None = None,
        started_before: datetime | None = None,
    ) -> list[Span]:
        query = select(Span)

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

        query = query.order_by(Span.started_at.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())