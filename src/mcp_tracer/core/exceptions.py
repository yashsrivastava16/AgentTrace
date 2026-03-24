"""
Custom exception classes for AgentTrace.
"""


class AgentTraceException(Exception):
    """Base exception for AgentTrace."""

    pass


class SessionNotFoundError(AgentTraceException):
    """Session ID not found in database."""

    pass


class SpanNotFoundError(AgentTraceException):
    """Span ID not found in database."""

    pass


class InvalidSpanTypeError(AgentTraceException):
    """Invalid span type."""

    pass


class ParentSpanNotFoundError(AgentTraceException):
    """Parent span ID does not exist."""

    pass


class SpanAlreadyEndedError(AgentTraceException):
    """Cannot end an already-ended span."""

    pass


class DatabaseError(AgentTraceException):
    """Database operation error."""

    pass
