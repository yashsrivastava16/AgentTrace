"""
Replay service — soft session replay logic.
Re-injects original inputs from a session into a new session.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from mcp_tracer.db.repositories.session import SessionRepository
from mcp_tracer.db.repositories.span import SpanRepository


class ReplayService:

    def __init__(self, db: AsyncSession):
        self.session_repo = SessionRepository(db)
        self.span_repo = SpanRepository(db)

    async def replay_session(
        self,
        session_id: str,
        from_span_id: str | None = None,
    ) -> dict:
        original_session = await self.session_repo.get_by_id(uuid.UUID(session_id))
        if not original_session:
            raise ValueError(f"Session {session_id} not found")

        # Fetch all spans ordered by start time
        spans = await self.span_repo.get_by_session(uuid.UUID(session_id))
        if not spans:
            raise ValueError(f"Session {session_id} has no spans to replay")

        # If from_span_id provided, slice spans from that point
        if from_span_id:
            from_id = uuid.UUID(from_span_id)
            ids = [s.span_id for s in spans]
            if from_id not in ids:
                raise ValueError(f"Span {from_span_id} not found in session {session_id}")
            start_index = ids.index(from_id)
            spans = spans[start_index:]

        # Create new replay session
        new_session = await self.session_repo.create(
            name=f"[Replay] {original_session.name}",
            metadata={
                "replayed_from_session": session_id,
                "replayed_from_span": from_span_id,
                "original_session_name": original_session.name,
            },
        )

        # Return replay context — actual re-execution is done by the agent
        # using these inputs. This is soft replay — we hand back the inputs,
        # agents run fresh against them.
        return {
            "new_session_id": str(new_session.session_id),
            "replayed_from_session_id": session_id,
            "replayed_from_span_id": from_span_id,
            "spans_to_replay": [
                {
                    "span_id": str(s.span_id),
                    "span_type": s.span_type,
                    "actor": s.actor,
                    "target": s.target,
                    "input": s.input_,
                    "parent_span_id": str(s.parent_span_id) if s.parent_span_id else None,
                }
                for s in spans
            ],
        }