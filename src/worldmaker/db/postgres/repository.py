"""Generic async repository for PostgreSQL CRUD operations."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar

if TYPE_CHECKING:
    from sqlalchemy import delete, select, update
    from sqlalchemy.ext.asyncio import AsyncSession

    from .tables import Base

T = TypeVar("T")


class PostgresRepository(Generic[T]):
    """Generic CRUD repository for SQLAlchemy models."""

    def __init__(self, model_class: type[T], session: AsyncSession) -> None:
        """Initialize repository with model class and session.

        Args:
            model_class: SQLAlchemy model class
            session: Async database session
        """
        self._model_class = model_class
        self._session = session

    async def create(self, **kwargs: Any) -> T:
        """Create a new entity.

        Args:
            **kwargs: Fields to set on the new entity

        Returns:
            T: The created entity instance
        """
        instance = self._model_class(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def get_by_id(self, entity_id: uuid.UUID) -> T | None:
        """Get entity by ID.

        Args:
            entity_id: The entity's UUID

        Returns:
            T | None: The entity or None if not found
        """
        from sqlalchemy import select

        stmt = select(self._model_class).where(self._model_class.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        """Get all entities with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            list[T]: List of entities
        """
        from sqlalchemy import select

        stmt = select(self._model_class).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, entity_id: uuid.UUID, **kwargs: Any) -> T | None:
        """Update entity by ID.

        Args:
            entity_id: The entity's UUID
            **kwargs: Fields to update

        Returns:
            T | None: The updated entity or None if not found
        """
        from sqlalchemy import update

        kwargs["updated_at"] = datetime.utcnow()
        stmt = (
            update(self._model_class)
            .where(self._model_class.id == entity_id)
            .values(**kwargs)
            .returning(self._model_class)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, entity_id: uuid.UUID) -> bool:
        """Delete entity by ID.

        Args:
            entity_id: The entity's UUID

        Returns:
            bool: True if entity was deleted, False if not found
        """
        from sqlalchemy import delete

        stmt = delete(self._model_class).where(self._model_class.id == entity_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def find_by(self, **filters: Any) -> list[T]:
        """Find entities matching filters.

        Args:
            **filters: Field=value pairs to filter on

        Returns:
            list[T]: List of matching entities
        """
        from sqlalchemy import and_, select

        conditions = [
            getattr(self._model_class, key) == value
            for key, value in filters.items()
            if hasattr(self._model_class, key)
        ]
        stmt = (
            select(self._model_class).where(and_(*conditions))
            if conditions
            else select(self._model_class)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, **filters: Any) -> int:
        """Count entities matching filters.

        Args:
            **filters: Field=value pairs to filter on

        Returns:
            int: Count of matching entities
        """
        from sqlalchemy import and_, func, select

        conditions = [
            getattr(self._model_class, key) == value
            for key, value in filters.items()
            if hasattr(self._model_class, key)
        ]
        stmt = select(func.count()).select_from(self._model_class)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def exists(self, entity_id: uuid.UUID) -> bool:
        """Check if entity exists.

        Args:
            entity_id: The entity's UUID

        Returns:
            bool: True if entity exists
        """
        from sqlalchemy import exists, select

        stmt = select(exists().where(self._model_class.id == entity_id))
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def bulk_create(self, items: list[dict[str, Any]]) -> list[T]:
        """Bulk create entities.

        Args:
            items: List of dictionaries with entity data

        Returns:
            list[T]: List of created entity instances
        """
        instances = [self._model_class(**item) for item in items]
        self._session.add_all(instances)
        await self._session.flush()
        return instances


class ServiceRepository(PostgresRepository):
    """Service-specific query methods."""

    async def find_by_platform(self, platform_id: uuid.UUID) -> list:
        """Find services by platform.

        Args:
            platform_id: The platform's UUID

        Returns:
            list: Services on the platform
        """
        from sqlalchemy import select

        stmt = select(self._model_class).where(
            self._model_class.platform_id == platform_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_status(self, status: str) -> list:
        """Find services by status.

        Args:
            status: The status to filter on

        Returns:
            list: Services with the given status
        """
        from sqlalchemy import select

        stmt = select(self._model_class).where(self._model_class.status == status)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_service_type(self, service_type: str) -> list:
        """Find services by type.

        Args:
            service_type: The service type to filter on

        Returns:
            list: Services of the given type
        """
        from sqlalchemy import select

        stmt = select(self._model_class).where(
            self._model_class.service_type == service_type
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class DependencyRepository(PostgresRepository):
    """Dependency-specific query methods."""

    async def find_dependencies_of(self, source_id: uuid.UUID) -> list:
        """Find all dependencies originating from a source entity.

        Args:
            source_id: The source entity's UUID

        Returns:
            list: Dependencies originating from source
        """
        from sqlalchemy import select

        stmt = select(self._model_class).where(
            self._model_class.source_id == source_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_dependents_of(self, target_id: uuid.UUID) -> list:
        """Find all entities that depend on a target entity.

        Args:
            target_id: The target entity's UUID

        Returns:
            list: Dependencies targeting the target
        """
        from sqlalchemy import select

        stmt = select(self._model_class).where(
            self._model_class.target_id == target_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_circular(self) -> list:
        """Find all circular dependencies.

        Returns:
            list: Dependencies marked as circular
        """
        from sqlalchemy import select

        stmt = select(self._model_class).where(self._model_class.is_circular == True)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_type(self, dependency_type: str) -> list:
        """Find dependencies by type.

        Args:
            dependency_type: The dependency type to filter on

        Returns:
            list: Dependencies of the given type
        """
        from sqlalchemy import select

        stmt = select(self._model_class).where(
            self._model_class.dependency_type == dependency_type
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_source_type(self, source_type: str) -> list:
        """Find dependencies by source entity type.

        Args:
            source_type: The source entity type

        Returns:
            list: Dependencies with given source type
        """
        from sqlalchemy import select

        stmt = select(self._model_class).where(
            self._model_class.source_type == source_type
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_target_type(self, target_type: str) -> list:
        """Find dependencies by target entity type.

        Args:
            target_type: The target entity type

        Returns:
            list: Dependencies with given target type
        """
        from sqlalchemy import select

        stmt = select(self._model_class).where(
            self._model_class.target_type == target_type
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_strength(self, strength: str) -> list:
        """Find dependencies by strength.

        Args:
            strength: The strength level to filter on (e.g., 'high', 'medium', 'low')

        Returns:
            list: Dependencies with given strength
        """
        from sqlalchemy import select

        stmt = select(self._model_class).where(
            self._model_class.strength == strength
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
