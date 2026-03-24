"""
Event model — a notable occurrence inside a span.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mcp_tracer.db.engine import Base


class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    span_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("spans.span_id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # log | error | warning
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    span: Mapped["Span"] = relationship("Span", back_populates="events")

    def __repr__(self) -> str:
        return f"<Event id={self.event_id} type={self.event_type}>"