"""
Alembic migration environment file.

Configures Alembic to support async SQLAlchemy operations.
"""

from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import asyncio
import os
import sys
from pathlib import Path

# Add src to path for importing models
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_tracer.db.models import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def get_database_url() -> str:
    """Determine the SQLAlchemy DSN used for migrations."""
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    file_url = config.get_main_option("sqlalchemy.url")
    if file_url and file_url != "driver://user:password@localhost/dbname":
        return file_url

    raise ValueError("DATABASE_URL is not set in environment and sqlalchemy.url is invalid in alembic.ini")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = get_database_url()
    connectable = create_async_engine(url, poolclass=pool.NullPool, future=True)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection):
    """Execute migration scripts."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
