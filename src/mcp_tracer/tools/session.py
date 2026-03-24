"""
Session tools — MCP tool handlers for session lifecycle.
"""
from fastmcp import FastMCP
from mcp_tracer.db.engine import get_db
from mcp_tracer.services.session import SessionService


def register_session_tools(app: FastMCP) -> None:

    @app.tool
    async def create_session(name: str, metadata: dict | None = None) -> dict:
        """
        Create a new trace session.

        Args:
            name: Human readable name for this session e.g. 'summarize-report-run-1'
            metadata: Optional key-value pairs e.g. {"env": "prod", "version": "1.0"}

        Returns:
            session_id, name, status, started_at
        """
        async with get_db() as db:
            service = SessionService(db)
            return await service.create_session(name=name, metadata=metadata)

    @app.tool
    async def complete_session(session_id: str) -> dict:
        """
        Mark a session as completed.

        Args:
            session_id: UUID of the session to complete

        Returns:
            session_id, status, ended_at
        """
        async with get_db() as db:
            service = SessionService(db)
            return await service.complete_session(session_id=session_id)

    @app.tool
    async def fail_session(session_id: str) -> dict:
        """
        Mark a session as failed.

        Args:
            session_id: UUID of the session to fail

        Returns:
            session_id, status, ended_at
        """
        async with get_db() as db:
            service = SessionService(db)
            return await service.fail_session(session_id=session_id)