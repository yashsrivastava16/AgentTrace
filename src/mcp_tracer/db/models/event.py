"""
Event ORM model.

Represents a notable event within a span.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from mcp_tracer.db.models import Base


class Event(Base):
    """
    Event model: a notable event logged within a span.

    Event types: error, warning, info, debug

    Attributes:
        id: Unique event identifier (UUID)
        span_id: Parent span ID
        type: Event type
        message: Event message
        metadata: Optional JSON metadata
        created_at: Event creation timestamp
        span: Relationship to Span object
    """

    __tablename__ = "events"

    id = Column(String, primary_key=True)
    span_id = Column(String, ForeignKey("spans.id"), nullable=False)
    type = Column(String, nullable=False)  # error, warning, info, debug
    message = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    span = relationship("Span", back_populates="events")
