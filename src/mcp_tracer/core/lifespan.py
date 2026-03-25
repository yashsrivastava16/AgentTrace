"""
Application lifespan — startup and shutdown logic.
Handles DB engine lifecycle, connection pool warmup, and cleanup.
"""
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp_tracer.db.engine import engine
from mcp_tracer.core.logging import logger


@asynccontextmanager
async def lifespan(app) -> AsyncIterator[None]:
    """
    FastMCP lifespan context manager.
    Everything before yield runs on startup.
    Everything after yield runs on shutdown.
    """
    # Startup
    logger.info("AgentTrace starting up...")

    # Warm up connection pool — verify DB is reachable
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        logger.info("Database connection pool ready")
    except Exception as e:
        logger.error(f"Database connection failed on startup: {e}")
        raise

    logger.info("AgentTrace is ready")

    yield  # app is running

    # Shutdown
    logger.info("AgentTrace shutting down...")
    await engine.dispose()
    logger.info("Database connection pool closed")