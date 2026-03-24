"""
Event logging tool handlers.

Tool: log_event
"""


async def log_event(
    span_id: str, event_type: str, message: str, metadata: dict | None = None
) -> dict:
    """
    Log a notable event within a span.

    Args:
        span_id: Span ID
        event_type: Type of event (error, warning, info, debug)
        message: Event message
        metadata: Optional metadata dictionary

    Returns:
        Event ID and creation timestamp
    """
    pass
