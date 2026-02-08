"""Alembic environment configuration for WorldMaker.

Supports both online (async) and offline migration modes.
Uses the same database URL as the application via Settings,
with optional override from alembic.ini or environment variables.
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config, create_async_engine

# Ensure the project root is on sys.path so we can import worldmaker modules.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import the declarative Base that holds all table metadata.
# This import triggers table class registration on Base.metadata.
from worldmaker.db.postgres.tables import Base  # noqa: E402

# Import application settings for the default database URL.
from worldmaker.config import Settings  # noqa: E402

logger = logging.getLogger("alembic.env")

# Alembic Config object — provides access to alembic.ini values.
config = context.config

# Interpret the config file for Python logging (unless we're testing).
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The target metadata that Alembic uses for autogenerate.
target_metadata = Base.metadata


def get_database_url() -> str:
    """Resolve the database URL with fallback chain.

    Priority:
        1. WM_POSTGRES_URL environment variable
        2. sqlalchemy.url from alembic.ini (if not the placeholder)
        3. Application Settings default

    For Alembic migrations we need a *sync* driver (psycopg2) because
    Alembic's offline mode and some operations need synchronous access.
    We also support asyncpg via the run_async wrapper for online mode.
    """
    # Check environment variable first
    env_url = os.environ.get("WM_POSTGRES_URL")
    if env_url:
        return env_url

    # Check alembic.ini setting
    ini_url = config.get_main_option("sqlalchemy.url", "")
    if ini_url and "driver://user:password" not in ini_url:
        return ini_url

    # Fall back to application defaults
    settings = Settings()
    return settings.POSTGRES_URL


def _make_sync_url(url: str) -> str:
    """Convert an async URL to a sync URL for offline migrations.

    asyncpg:// -> psycopg2:// (or plain postgresql://)
    """
    return (
        url.replace("postgresql+asyncpg://", "postgresql://")
        .replace("+asyncpg", "")
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates SQL scripts without connecting to the database.
    Uses a synchronous URL since we don't need a real connection.
    """
    url = _make_sync_url(get_database_url())

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations within a provided connection context."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        # Render JSONB, UUID, ARRAY types correctly in autogenerate
        render_as_batch=False,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with an async engine.

    Creates an async engine, then runs migrations synchronously
    within the engine's connection context using run_sync().
    """
    db_url = get_database_url()

    connectable = create_async_engine(
        db_url,
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode — async wrapper."""
    asyncio.run(run_async_migrations())


# Dispatch based on whether we're online or offline.
if context.is_offline_mode():
    logger.info("Running migrations offline")
    run_migrations_offline()
else:
    logger.info("Running migrations online (async)")
    run_migrations_online()
