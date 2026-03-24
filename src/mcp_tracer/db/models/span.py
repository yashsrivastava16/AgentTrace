"""
Span ORM model.

Represents a traced operation within a session.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from mcp_tracer.db.models import Base


class Span(Base):
    """
    Span model: a traced operation within a session.

    Span types: human_input, agent_call, tool_call, hitl

    Attributes:
        id: Unique span identifier (UUID)
        session_id: Parent session ID
        type: Span type
        input_data: Input data (JSON)
        output_data: Output data (JSON)
        status: Span status (success, error, pending)
        parent_span_id: Optional parent span ID for nested spans
        metadata: Optional JSON metadata
        created_at: Span creation timestamp
        started_at: Span start timestamp
        ended_at: Span end timestamp
        events: Relationship to Event objects
    """

    __tablename__ = "spans"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    type = Column(String, nullable=False)  # human_input, agent_call, tool_call, hitl
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    status = Column(String, default="pending")  # success, error, pending
    parent_span_id = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    session = relationship("Session", back_populates="spans")
    events = relationship("Event", back_populates="span")
