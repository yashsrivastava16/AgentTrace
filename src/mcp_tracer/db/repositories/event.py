"""
Event repository — all DB operations for Event model.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_tracer.db.models.event import Event


class EventRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        span_id: uuid.UUID,
        event_type: str,
        message: str,
        metadata: dict | None = None,
    ) -> Event:
        event = Event(
            event_id=uuid.uuid4(),
            span_id=span_id,
            event_type=event_type,
            message=message,
            metadata_=metadata,
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def get_by_span(self, span_id: uuid.UUID) -> list[Event]:
        result = await self.db.execute(
            select(Event)
            .where(Event.span_id == span_id)
            .order_by(Event.created_at.asc())
        )
        return list(result.scalars().all())