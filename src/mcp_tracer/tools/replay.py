"""
Session replay tool handlers.

Tool: replay_session
"""


async def replay_session(session_id: str, start_from_span_id: str | None = None) -> dict:
    """
    Replay a session's inputs into a new run.

    Soft replay: re-inject original inputs, optionally starting from mid-trace.

    Args:
        session_id: Session ID to replay
        start_from_span_id: Optional span ID to start from (for mid-trace replay)

    Returns:
        New session ID and replay metadata
    """
    pass
