"""
Session repository — all DB operations for Session model.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_tracer.db.models.session import Session


class SessionRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, name: str, metadata: dict | None = None) -> Session:
        session = Session(
            session_id=uuid.uuid4(),
            name=name,
            status="active",
            metadata_=metadata,
        )
        self.db.add(session)
        await self.db.flush()  # flush to get session_id without full commit
        return session

    async def get_by_id(self, session_id: uuid.UUID) -> Session | None:
        result = await self.db.execute(
            select(Session).where(Session.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self, session_id: uuid.UUID, status: str
    ) -> Session | None:
        await self.db.execute(
            update(Session)
            .where(Session.session_id == session_id)
            .values(
                status=status,
                ended_at=datetime.now(timezone.utc) if status in ("completed", "failed") else None,
            )
        )
        await self.db.flush()
        return await self.get_by_id(session_id)