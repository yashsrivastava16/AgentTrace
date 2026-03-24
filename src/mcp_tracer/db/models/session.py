"""
Session ORM model.

Represents a top-level trace session.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.orm import relationship
from mcp_tracer.db.models import Base


class Session(Base):
    """
    Session model: top-level container for a trace.

    Attributes:
        id: Unique session identifier (UUID)
        name: Human-readable session name
        metadata: Optional JSON metadata
        created_at: Session creation timestamp
        updated_at: Last update timestamp
        spans: Relationship to Span objects
    """

    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    spans = relationship("Span", back_populates="session")
