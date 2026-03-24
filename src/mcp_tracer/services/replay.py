"""
Replay service: orchestration logic for session replay.
"""


class ReplayService:
    """Service for session replay operations."""

    async def replay_session(self, session_id: str, start_from_span_id: str | None = None) -> dict:
        """
        Soft replay: re-inject original inputs into a new run.

        Retrieves session inputs, optionally starting from a mid-trace span,
        creates new session, and prepares for re-execution.
        """
        pass
