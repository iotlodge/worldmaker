"""Async Neo4j driver management."""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from neo4j import AsyncGraphDatabase, AsyncDriver

    HAS_NEO4J = True
except ImportError:
    HAS_NEO4J = False


class Neo4jDriver:
    """Manages async Neo4j connections."""

    def __init__(
        self, uri: str, user: str = "neo4j", password: str = "worldmaker"
    ):
        """Initialize Neo4j driver.

        Args:
            uri: Neo4j connection URI (e.g., "bolt://localhost:7687")
            user: Username for authentication
            password: Password for authentication
        """
        self._uri = uri
        self._user = user
        self._password = password
        self._driver: Any = None  # AsyncDriver

    async def initialize(self) -> None:
        """Initialize Neo4j connection and create constraints/indexes."""
        if not HAS_NEO4J:
            raise RuntimeError("neo4j package not installed")
        self._driver = AsyncGraphDatabase.driver(
            self._uri, auth=(self._user, self._password)
        )
        # Verify connectivity
        await self._driver.verify_connectivity()
        logger.info("Neo4j connected: %s", self._uri)
        await self._ensure_constraints()

    async def dispose(self) -> None:
        """Close Neo4j driver connection."""
        if self._driver:
            await self._driver.close()
            logger.info("Neo4j driver closed")

    @property
    def driver(self) -> Any:
        """Get the Neo4j driver instance."""
        if not self._driver:
            raise RuntimeError("Neo4j not initialized")
        return self._driver

    async def execute_query(
        self, query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a Cypher read query and return results as dicts.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result dictionaries
        """
        async with self._driver.session() as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records

    async def execute_write(
        self, query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a Cypher write query.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result dictionaries
        """
        async with self._driver.session() as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records

    async def _ensure_constraints(self) -> None:
        """Create uniqueness constraints and indexes."""
        constraints = [
            "CREATE CONSTRAINT unique_service_id IF NOT EXISTS FOR (s:Service) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT unique_platform_id IF NOT EXISTS FOR (p:Platform) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT unique_microservice_id IF NOT EXISTS FOR (m:Microservice) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT unique_interface_id IF NOT EXISTS FOR (i:Interface) REQUIRE i.id IS UNIQUE",
            "CREATE CONSTRAINT unique_datastore_id IF NOT EXISTS FOR (d:DataStore) REQUIRE d.id IS UNIQUE",
            "CREATE CONSTRAINT unique_capability_id IF NOT EXISTS FOR (c:Capability) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT unique_product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT unique_feature_id IF NOT EXISTS FOR (f:Feature) REQUIRE f.id IS UNIQUE",
            "CREATE CONSTRAINT unique_flow_id IF NOT EXISTS FOR (f:Flow) REQUIRE f.id IS UNIQUE",
        ]
        indexes = [
            "CREATE INDEX service_name_idx IF NOT EXISTS FOR (s:Service) ON (s.name)",
            "CREATE INDEX platform_name_idx IF NOT EXISTS FOR (p:Platform) ON (p.name)",
            "CREATE INDEX service_status_idx IF NOT EXISTS FOR (s:Service) ON (s.status)",
            "CREATE INDEX service_criticality_idx IF NOT EXISTS FOR (s:Service) ON (s.criticality)",
        ]
        for stmt in constraints + indexes:
            try:
                await self.execute_write(stmt)
            except Exception as e:
                logger.warning(
                    "Failed to create constraint/index: %s - %s", stmt[:60], e
                )
        logger.info("Neo4j constraints and indexes ensured")
