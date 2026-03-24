"""
Span model — a single unit of work inside a session.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mcp_tracer.db.engine import Base


class Span(Base):
    __tablename__ = "spans"

    span_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False
    )
    parent_span_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("spans.span_id", ondelete="SET NULL"), nullable=True
    )
    span_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # human_input | agent_call | tool_call | hitl
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    target: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="running"
    )  # running | success | failed
    input_: Mapped[dict | None] = mapped_column(
        "input", JSONB, nullable=True
    )
    output_: Mapped[dict | None] = mapped_column(
        "output", JSONB, nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="spans")
    events: Mapped[list["Event"]] = relationship(
        "Event", back_populates="span", cascade="all, delete-orphan"
    )
    children: Mapped[list["Span"]] = relationship(
        "Span", back_populates="parent",
        foreign_keys="Span.parent_span_id"
    )
    parent: Mapped["Span | None"] = relationship(
        "Span", back_populates="children",
        remote_side="Span.span_id",
        foreign_keys="Span.parent_span_id"
    )

    def __repr__(self) -> str:
        return f"<Span id={self.span_id} type={self.span_type} status={self.status}>"