"""Neo4j graph repository for dependency operations."""
from __future__ import annotations

import logging
from typing import Any

from . import queries

logger = logging.getLogger(__name__)


class GraphRepository:
    """Repository for Neo4j graph operations — the core of dependency resolution."""

    def __init__(self, driver: Any):
        """Initialize graph repository.

        Args:
            driver: Neo4jDriver instance
        """
        self._driver = driver

    # --- Node Operations ---

    async def upsert_service(
        self,
        id: str,
        name: str,
        status: str = "active",
        service_type: str = "rest",
        criticality: str = "medium",
        owner: str = "",
        health_status: str = "healthy",
    ) -> dict[str, Any]:
        """Create or update a Service node.

        Args:
            id: Service ID
            name: Service name
            status: Service status (active, inactive, etc.)
            service_type: Type of service (rest, grpc, etc.)
            criticality: Criticality level (low, medium, high, critical)
            owner: Service owner
            health_status: Health status (healthy, degraded, unhealthy)

        Returns:
            Result dictionary
        """
        results = await self._driver.execute_write(
            queries.UPSERT_SERVICE_NODE,
            {
                "id": id,
                "name": name,
                "status": status,
                "service_type": service_type,
                "criticality": criticality,
                "owner": owner,
                "health_status": health_status,
            },
        )
        return results[0] if results else {}

    async def upsert_platform(
        self,
        id: str,
        name: str,
        status: str = "active",
        category: str = "",
        owner: str = "",
    ) -> dict[str, Any]:
        """Create or update a Platform node.

        Args:
            id: Platform ID
            name: Platform name
            status: Platform status
            category: Platform category (kubernetes, cloud, etc.)
            owner: Platform owner

        Returns:
            Result dictionary
        """
        results = await self._driver.execute_write(
            queries.UPSERT_PLATFORM_NODE,
            {
                "id": id,
                "name": name,
                "status": status,
                "category": category,
                "owner": owner,
            },
        )
        return results[0] if results else {}

    async def upsert_microservice(
        self,
        id: str,
        name: str,
        service_id: str,
        language: str = "",
        framework: str = "",
        status: str = "active",
    ) -> dict[str, Any]:
        """Create or update a Microservice node.

        Args:
            id: Microservice ID
            name: Microservice name
            service_id: Parent service ID
            language: Programming language
            framework: Framework used
            status: Microservice status

        Returns:
            Result dictionary
        """
        results = await self._driver.execute_write(
            queries.UPSERT_MICROSERVICE_NODE,
            {
                "id": id,
                "name": name,
                "service_id": service_id,
                "language": language,
                "framework": framework,
                "status": status,
            },
        )
        return results[0] if results else {}

    async def upsert_datastore(
        self,
        id: str,
        name: str,
        store_type: str = "",
        technology: str = "",
        status: str = "active",
    ) -> dict[str, Any]:
        """Create or update a DataStore node.

        Args:
            id: DataStore ID
            name: DataStore name
            store_type: Type of store (database, cache, etc.)
            technology: Technology (postgres, redis, etc.)
            status: DataStore status

        Returns:
            Result dictionary
        """
        results = await self._driver.execute_write(
            queries.UPSERT_DATASTORE_NODE,
            {
                "id": id,
                "name": name,
                "store_type": store_type,
                "technology": technology,
                "status": status,
            },
        )
        return results[0] if results else {}

    async def upsert_capability(
        self,
        id: str,
        name: str,
        platform_id: str,
        capability_type: str = "",
        status: str = "active",
    ) -> dict[str, Any]:
        """Create or update a Capability node.

        Args:
            id: Capability ID
            name: Capability name
            platform_id: Parent platform ID
            capability_type: Type of capability
            status: Capability status

        Returns:
            Result dictionary
        """
        results = await self._driver.execute_write(
            queries.UPSERT_CAPABILITY_NODE,
            {
                "id": id,
                "name": name,
                "platform_id": platform_id,
                "capability_type": capability_type,
                "status": status,
            },
        )
        return results[0] if results else {}

    async def upsert_flow(
        self,
        id: str,
        name: str,
        flow_type: str = "",
        status: str = "active",
    ) -> dict[str, Any]:
        """Create or update a Flow node.

        Args:
            id: Flow ID
            name: Flow name
            flow_type: Type of flow
            status: Flow status

        Returns:
            Result dictionary
        """
        results = await self._driver.execute_write(
            queries.UPSERT_FLOW_NODE,
            {"id": id, "name": name, "flow_type": flow_type, "status": status},
        )
        return results[0] if results else {}

    # --- Relationship Operations ---

    async def create_dependency(
        self,
        source_id: str,
        target_id: str,
        dep_type: str = "runtime",
        severity: str = "medium",
        is_circular: bool = False,
    ) -> dict[str, Any]:
        """Create a DEPENDS_ON relationship.

        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            dep_type: Type of dependency (runtime, build, etc.)
            severity: Severity of dependency (low, medium, high, critical)
            is_circular: Whether this creates a circular dependency

        Returns:
            Result dictionary
        """
        results = await self._driver.execute_write(
            queries.CREATE_DEPENDENCY,
            {
                "source_id": source_id,
                "target_id": target_id,
                "dep_type": dep_type,
                "severity": severity,
                "is_circular": is_circular,
            },
        )
        return results[0] if results else {}

    async def create_hosted_by(
        self, service_id: str, platform_id: str
    ) -> dict[str, Any]:
        """Create a HOSTED_BY relationship.

        Args:
            service_id: Service ID
            platform_id: Platform ID

        Returns:
            Result dictionary
        """
        results = await self._driver.execute_write(
            queries.CREATE_HOSTED_BY,
            {"service_id": service_id, "platform_id": platform_id},
        )
        return results[0] if results else {}

    async def create_implements(
        self, service_id: str, capability_id: str
    ) -> dict[str, Any]:
        """Create an IMPLEMENTS relationship.

        Args:
            service_id: Service ID
            capability_id: Capability ID

        Returns:
            Result dictionary
        """
        results = await self._driver.execute_write(
            queries.CREATE_IMPLEMENTS,
            {"service_id": service_id, "capability_id": capability_id},
        )
        return results[0] if results else {}

    async def create_uses_datastore(
        self,
        service_id: str,
        datastore_id: str,
        access_pattern: str = "read-write",
        criticality: str = "medium",
    ) -> dict[str, Any]:
        """Create a USES relationship to a DataStore.

        Args:
            service_id: Service ID
            datastore_id: DataStore ID
            access_pattern: Access pattern (read-only, write-only, read-write)
            criticality: Criticality of this dependency

        Returns:
            Result dictionary
        """
        results = await self._driver.execute_write(
            queries.CREATE_USES_DATASTORE,
            {
                "service_id": service_id,
                "datastore_id": datastore_id,
                "access_pattern": access_pattern,
                "criticality": criticality,
            },
        )
        return results[0] if results else {}

    async def create_flow_traversal(
        self, flow_id: str, service_id: str, step_number: int
    ) -> dict[str, Any]:
        """Create a TRAVERSES relationship from Flow to Service.

        Args:
            flow_id: Flow ID
            service_id: Service ID
            step_number: Step number in the flow

        Returns:
            Result dictionary
        """
        results = await self._driver.execute_write(
            queries.CREATE_FLOW_TRAVERSAL,
            {"flow_id": flow_id, "service_id": service_id, "step_number": step_number},
        )
        return results[0] if results else {}

    async def create_calls(
        self,
        from_service_id: str,
        to_service_id: str,
        interface_type: str = "rest",
        latency_ms: int = 50,
    ) -> dict[str, Any]:
        """Create a CALLS relationship between services.

        Args:
            from_service_id: Calling service ID
            to_service_id: Called service ID
            interface_type: Interface type (rest, grpc, graphql, etc.)
            latency_ms: Expected latency in milliseconds

        Returns:
            Result dictionary
        """
        results = await self._driver.execute_write(
            queries.CREATE_CALLS,
            {
                "from_service_id": from_service_id,
                "to_service_id": to_service_id,
                "interface_type": interface_type,
                "latency_ms": latency_ms,
            },
        )
        return results[0] if results else {}

    # --- Analysis Queries (Agentic Core) ---

    async def get_direct_dependencies(self, service_id: str) -> dict[str, Any]:
        """Get direct upstream and downstream dependencies.

        Args:
            service_id: Service ID

        Returns:
            Dictionary containing direct dependencies
        """
        results = await self._driver.execute_query(
            queries.GET_DIRECT_DEPENDENCIES, {"service_id": service_id}
        )
        return results[0]["result"] if results else {}

    async def get_transitive_dependencies(
        self, service_id: str
    ) -> list[dict[str, Any]]:
        """Get all transitive (indirect) dependencies.

        Args:
            service_id: Service ID

        Returns:
            List of transitive dependencies with path information
        """
        return await self._driver.execute_query(
            queries.GET_TRANSITIVE_DEPENDENCIES, {"service_id": service_id}
        )

    async def calculate_blast_radius(self, service_id: str) -> dict[str, Any]:
        """Calculate blast radius if this service fails.

        Args:
            service_id: Service ID

        Returns:
            Dictionary containing blast radius analysis
        """
        results = await self._driver.execute_query(
            queries.CALCULATE_BLAST_RADIUS, {"service_id": service_id}
        )
        return results[0]["result"] if results else {}

    async def detect_circular_dependencies(self) -> list[dict[str, Any]]:
        """Detect all circular dependencies in the graph.

        Returns:
            List of circular dependency cycles
        """
        return await self._driver.execute_query(queries.DETECT_CIRCULAR_DEPENDENCIES)

    async def find_critical_paths(self) -> list[dict[str, Any]]:
        """Find critical paths between critical services.

        Returns:
            List of critical paths
        """
        return await self._driver.execute_query(queries.FIND_CRITICAL_PATHS)

    async def get_full_service_context(self, service_id: str) -> dict[str, Any]:
        """Get complete context for a service including all relationships.

        Args:
            service_id: Service ID

        Returns:
            Dictionary containing full service context
        """
        results = await self._driver.execute_query(
            queries.GET_FULL_SERVICE_CONTEXT, {"service_id": service_id}
        )
        return results[0]["context"] if results else {}

    async def get_shared_resource_correlation(
        self, datastore_id: str
    ) -> dict[str, Any]:
        """Get all services sharing a datastore.

        Args:
            datastore_id: DataStore ID

        Returns:
            Dictionary containing shared resource correlation
        """
        results = await self._driver.execute_query(
            queries.SHARED_RESOURCE_CORRELATION, {"datastore_id": datastore_id}
        )
        return results[0]["correlation"] if results else {}

    async def get_health_cascade(self) -> list[dict[str, Any]]:
        """Get health cascade analysis for unhealthy services.

        Returns:
            List of health cascade events ordered by action priority
        """
        return await self._driver.execute_query(queries.HEALTH_CASCADE)

    async def get_ecosystem_overview(self) -> dict[str, Any]:
        """Get high-level ecosystem statistics.

        Returns:
            Dictionary containing ecosystem overview
        """
        results = await self._driver.execute_query(queries.GET_ECOSYSTEM_OVERVIEW)
        return results[0]["overview"] if results else {}

    async def simulate_failure(self, service_id: str) -> dict[str, Any]:
        """Simulate failure of a service and analyze impact.

        Args:
            service_id: Service ID to simulate failure

        Returns:
            Dictionary containing failure simulation results
        """
        results = await self._driver.execute_write(
            queries.SIMULATE_FAILURE, {"service_id": service_id}
        )
        return results[0]["simulation"] if results else {}
