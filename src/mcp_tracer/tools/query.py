"""
Query tools — MCP tool handlers for session and cross-session querying.
"""
from fastmcp import FastMCP

from mcp_tracer.services.query import QueryService


def register_query_tools(app: FastMCP, get_db) -> None:

    @app.tool
    async def query_session(session_id: str) -> dict:
        """
        Retrieve the full trace tree for a session.
        Returns all spans and events nested by parent-child relationships.

        Args:
            session_id: UUID of the session to retrieve

        Returns:
            Full nested trace tree with all spans and events
        """
        async for db in get_db():
            service = QueryService(db)
            return await service.get_session_trace(session_id=session_id)

    @app.tool
    async def query_cross_session(
        actor: str | None = None,
        span_type: str | None = None,
        status: str | None = None,
        event_type: str | None = None,
        started_after: str | None = None,
        started_before: str | None = None,
    ) -> list[dict]:
        """
        Query spans and events across all sessions with filters.

        Args:
            actor: Filter by actor name e.g. 'research_agent'
            span_type: Filter by type — 'human_input', 'agent_call', 'tool_call', 'hitl'
            status: Filter by status — 'running', 'success', 'failed'
            event_type: Filter spans that contain this event type — 'log', 'error', 'warning'
            started_after: ISO datetime string e.g. '2026-01-01T00:00:00'
            started_before: ISO datetime string e.g. '2026-12-31T23:59:59'

        Returns:
            List of matching spans with session context and events
        """
        async for db in get_db():
            service = QueryService(db)
            return await service.cross_session_query(
                actor=actor,
                span_type=span_type,
                status=status,
                event_type=event_type,
                started_after=started_after,
                started_before=started_before,
            )