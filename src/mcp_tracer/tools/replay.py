"""
Replay tools — MCP tool handlers for session replay.
"""
from fastmcp import FastMCP

from mcp_tracer.services.replay import ReplayService


def register_replay_tools(app: FastMCP, get_db) -> None:

    @app.tool
    async def replay_session(
        session_id: str,
        from_span_id: str | None = None,
    ) -> dict:
        """
        Replay a session's inputs into a new run.
        Creates a new session and returns all original inputs
        so agents can re-execute them fresh.

        Args:
            session_id: UUID of the session to replay
            from_span_id: Optional UUID to start replay from mid-trace.
                          Useful when you only want to re-run from the failure point.

        Returns:
            new_session_id, replayed_from_session_id, spans_to_replay
        """
        async for db in get_db():
            service = ReplayService(db)
            return await service.replay_session(
                session_id=session_id,
                from_span_id=from_span_id,
            )