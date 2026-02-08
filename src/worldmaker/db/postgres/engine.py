"""Async PostgreSQL engine and session management."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)


class PostgresEngine:
    """Manages async PostgreSQL connections via SQLAlchemy."""

    def __init__(
        self,
        database_url: str,
        echo: bool = False,
        pool_size: int = 20,
        max_overflow: int = 10,
    ) -> None:
        """Initialize PostgreSQL engine configuration.

        Args:
            database_url: PostgreSQL connection URL (async driver required)
            echo: Whether to log SQL statements
            pool_size: Number of connections to keep in the pool
            max_overflow: Maximum overflow connections beyond pool_size
        """
        self._database_url = database_url
        self._echo = echo
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def initialize(self) -> None:
        """Create engine and session factory."""
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

        self._engine = create_async_engine(
            self._database_url,
            echo=self._echo,
            pool_size=self._pool_size,
            max_overflow=self._max_overflow,
            pool_pre_ping=True,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info(
            "PostgreSQL engine initialized: %s",
            self._database_url.split("@")[-1],
        )

    async def dispose(self) -> None:
        """Close all connections."""
        if self._engine:
            await self._engine.dispose()
            logger.info("PostgreSQL engine disposed")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield an async session with transaction management.

        Automatically commits on success or rolls back on exception.

        Yields:
            AsyncSession: Active database session

        Raises:
            RuntimeError: If engine not initialized
        """
        if not self._session_factory:
            raise RuntimeError("Engine not initialized. Call initialize() first.")

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @property
    def engine(self) -> AsyncEngine:
        """Get the underlying SQLAlchemy engine.

        Returns:
            AsyncEngine: The async engine instance

        Raises:
            RuntimeError: If engine not initialized
        """
        if not self._engine:
            raise RuntimeError("Engine not initialized.")
        return self._engine
