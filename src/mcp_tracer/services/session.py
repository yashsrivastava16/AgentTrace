"""
Session service — business logic for session lifecycle.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from mcp_tracer.db.repositories.session import SessionRepository


class SessionService:

    def __init__(self, db: AsyncSession):
        self.repo = SessionRepository(db)

    async def create_session(
        self, name: str, metadata: dict | None = None
    ) -> dict:
        session = await self.repo.create(name=name, metadata=metadata)
        return {
            "session_id": str(session.session_id),
            "name": session.name,
            "status": session.status,
            "started_at": session.started_at.isoformat(),
            "metadata": session.metadata_,
        }

    async def complete_session(self, session_id: str) -> dict:
        session = await self.repo.update_status(
            session_id=uuid.UUID(session_id),
            status="completed",
        )
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return {
            "session_id": str(session.session_id),
            "status": session.status,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
        }

    async def fail_session(self, session_id: str) -> dict:
        session = await self.repo.update_status(
            session_id=uuid.UUID(session_id),
            status="failed",
        )
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return {
            "session_id": str(session.session_id),
            "status": session.status,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
        }