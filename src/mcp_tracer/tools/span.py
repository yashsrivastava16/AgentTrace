"""
Span tools — MCP tool handlers for span lifecycle.
"""
from fastmcp import FastMCP
from mcp_tracer.db.engine import get_db
from mcp_tracer.services.span import SpanService


def register_span_tools(app: FastMCP) -> None:

    @app.tool
    async def start_span(
        session_id: str,
        span_type: str,
        actor: str,
        target: str,
        input: dict | None = None,
        parent_span_id: str | None = None,
    ) -> dict:
        """
        Start a new span inside a session.

        Args:
            session_id: UUID of the parent session
            span_type: One of 'human_input', 'agent_call', 'tool_call', 'hitl'
            actor: Who initiated this span e.g. 'orchestrator', 'human'
            target: Who received this span e.g. 'research_agent', 'web_search'
            input: Optional payload sent to the target
            parent_span_id: UUID of parent span for nested calls

        Returns:
            span_id, session_id, span_type, actor, target, status, started_at
        """
        async with get_db() as db:
            service = SpanService(db)
            return await service.start_span(
                session_id=session_id,
                span_type=span_type,
                actor=actor,
                target=target,
                input_=input,
                parent_span_id=parent_span_id,
            )

    @app.tool
    async def end_span(
        span_id: str,
        status: str,
        output: dict | None = None,
    ) -> dict:
        """
        End a span and record its output.

        Args:
            span_id: UUID of the span to end
            status: 'success' or 'failed'
            output: Optional payload returned from the target

        Returns:
            span_id, status, ended_at, output
        """
        async with get_db() as db:
            service = SpanService(db)
            return await service.end_span(
                span_id=span_id,
                status=status,
                output_=output,
            )