"""
Pytest configuration and fixtures for AgentTrace tests.

Provides test database setup, async session fixtures, and common test utilities.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from mcp_tracer.db.models import Base


@pytest.fixture
async def test_db():
    """Create a test database session."""
    # Use in-memory SQLite or test PostgreSQL
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with TestSessionLocal() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def anyio_backend():
    """Configure pytest-anyio backend."""
    return "asyncio"
