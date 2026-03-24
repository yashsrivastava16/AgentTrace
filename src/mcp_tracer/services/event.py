"""
Event service — business logic for event logging.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from mcp_tracer.db.repositories.event import EventRepository
from mcp_tracer.db.repositories.span import SpanRepository


class EventService:

    def __init__(self, db: AsyncSession):
        self.repo = EventRepository(db)
        self.span_repo = SpanRepository(db)

    async def log_event(
        self,
        span_id: str,
        event_type: str,
        message: str,
        metadata: dict | None = None,
    ) -> dict:
        if event_type not in ("log", "error", "warning"):
            raise ValueError("event_type must be 'log', 'error', or 'warning'")

        # Validate span exists
        span = await self.span_repo.get_by_id(uuid.UUID(span_id))
        if not span:
            raise ValueError(f"Span {span_id} not found")

        event = await self.repo.create(
            span_id=uuid.UUID(span_id),
            event_type=event_type,
            message=message,
            metadata=metadata,
        )
        return {
            "event_id": str(event.event_id),
            "span_id": str(event.span_id),
            "event_type": event.event_type,
            "message": event.message,
            "created_at": event.created_at.isoformat(),
        }