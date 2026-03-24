"""
Session model — the top-level unit of a trace.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mcp_tracer.db.engine import Base


class Session(Base):
    __tablename__ = "sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )  # active | completed | failed
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSONB, nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    spans: Mapped[list["Span"]] = relationship(
        "Span", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Session id={self.session_id} name={self.name} status={self.status}>"