"""
Query tool handlers.

Tools: query_session, query_cross_session
"""


async def query_session(session_id: str) -> dict:
    """
    Retrieve the full trace tree for a session.

    Args:
        session_id: Session ID to query

    Returns:
        Complete trace tree with all spans and events
    """
    pass


async def query_cross_session(filters: dict | None = None) -> list[dict]:
    """
    Query spans and events across all sessions with filters.

    Args:
        filters: Optional filter dictionary (agent, error_type, span_type, time_range)

    Returns:
        List of matching spans/events across sessions
    """
    pass
