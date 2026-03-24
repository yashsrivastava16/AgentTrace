"""
Event tools — MCP tool handlers for event logging.
"""
from fastmcp import FastMCP

from mcp_tracer.services.event import EventService


def register_event_tools(app: FastMCP, get_db) -> None:

    @app.tool
    async def log_event(
        span_id: str,
        event_type: str,
        message: str,
        metadata: dict | None = None,
    ) -> dict:
        """
        Log a notable event inside a span.

        Args:
            span_id: UUID of the span this event belongs to
            event_type: One of 'log', 'error', 'warning'
            message: Human readable description of what happened
            metadata: Optional additional context

        Returns:
            event_id, span_id, event_type, message, created_at
        """
        async for db in get_db():
            service = EventService(db)
            return await service.log_event(
                span_id=span_id,
                event_type=event_type,
                message=message,
                metadata=metadata,
            )