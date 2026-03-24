"""
SQLAlchemy ORM models.

Core domain models: Session, Span, Event.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
