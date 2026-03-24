"""
Span lifecycle tool handlers.

Tools: start_span, end_span
"""


async def start_span(
    session_id: str,
    span_type: str,
    parent_span_id: str | None = None,
    metadata: dict | None = None,
) -> dict:
    """
    Start a new span within a session.

    Args:
        session_id: Session ID
        span_type: Type of span (human_input, agent_call, tool_call, hitl)
        parent_span_id: Optional parent span ID for nested spans
        metadata: Optional metadata dictionary

    Returns:
        Span ID and start timestamp
    """
    pass


async def end_span(span_id: str, output: dict | None = None, status: str = "success") -> dict:
    """
    End a span and record its output.

    Args:
        span_id: Span ID to end
        output: Optional output data
        status: Span status (success, error, pending)

    Returns:
        End timestamp and final span state
    """
    pass
