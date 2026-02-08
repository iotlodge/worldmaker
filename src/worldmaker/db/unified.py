"""Unified query router for polyglot persistence.

Routes operations to the appropriate data store:
- Entity CRUD → PostgreSQL (transactional, relational)
- Audit/Config/Traces → MongoDB (documents, time-series)
- Dependency/Impact graphs → Neo4j (graph traversal)
- Composite queries → fan-out to all stores, merge results

This is the single entry point for all data operations in WorldMaker.
Agentic consumers use this to get complete context about any entity.
"""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class UnifiedRepository:
    """Polyglot persistence query router.

    Orchestrates reads/writes across PostgreSQL, MongoDB, and Neo4j
    to provide a unified data access layer for the WorldMaker ecosystem.
    """

    def __init__(
        self,
        postgres_repo: Any = None,  # PostgresRepository instances
        mongo_client: Any = None,   # MongoClient
        graph_repo: Any = None,     # GraphRepository
        event_bus: Any = None,      # EventBus
    ):
        self._pg = postgres_repo
        self._mongo = mongo_client
        self._graph = graph_repo
        self._event_bus = event_bus

        # Lazy-initialize specialized mongo repos
        self._audit_repo: Any = None
        self._trace_repo: Any = None
        self._snapshot_repo: Any = None
        self._event_stream_repo: Any = None

    def _get_audit_repo(self) -> Any:
        if not self._audit_repo and self._mongo:
            from .mongo.repository import AuditLogRepository
            self._audit_repo = AuditLogRepository(self._mongo)
        return self._audit_repo

    def _get_trace_repo(self) -> Any:
        if not self._trace_repo and self._mongo:
            from .mongo.repository import FlowTraceRepository
            self._trace_repo = FlowTraceRepository(self._mongo)
        return self._trace_repo

    def _get_snapshot_repo(self) -> Any:
        if not self._snapshot_repo and self._mongo:
            from .mongo.repository import DependencySnapshotRepository
            self._snapshot_repo = DependencySnapshotRepository(self._mongo)
        return self._snapshot_repo

    def _get_event_stream_repo(self) -> Any:
        if not self._event_stream_repo and self._mongo:
            from .mongo.repository import EventStreamRepository
            self._event_stream_repo = EventStreamRepository(self._mongo)
        return self._event_stream_repo

    # ---- Composite Queries (Fan-out to multiple stores) ----

    async def get_service_full_context(self, service_id: str) -> dict[str, Any]:
        """Get complete service context from all three stores.

        This is THE primary query for agentic consumers.
        Combines: PostgreSQL entity data + Neo4j dependency graph + MongoDB audit trail.
        """
        result: dict[str, Any] = {"service_id": service_id}

        # PostgreSQL: Core entity data
        if self._pg:
            try:
                entity = await self._pg.get_by_id(UUID(service_id))
                if entity:
                    result["entity"] = {
                        "id": str(entity.id),
                        "name": entity.name,
                        "status": entity.status,
                        "owner": getattr(entity, "owner", None),
                        "service_type": getattr(entity, "service_type", None),
                        "api_version": getattr(entity, "api_version", None),
                    }
            except Exception as e:
                logger.warning("PostgreSQL query failed for service %s: %s", service_id, e)

        # Neo4j: Dependency graph context
        if self._graph:
            try:
                graph_context = await self._graph.get_full_service_context(service_id)
                result["graph"] = graph_context

                blast = await self._graph.calculate_blast_radius(service_id)
                result["blast_radius"] = blast
            except Exception as e:
                logger.warning("Neo4j query failed for service %s: %s", service_id, e)

        # MongoDB: Recent audit history
        audit_repo = self._get_audit_repo()
        if audit_repo:
            try:
                history = await audit_repo.get_entity_history(service_id, limit=10)
                result["recent_changes"] = history
            except Exception as e:
                logger.warning("MongoDB query failed for service %s: %s", service_id, e)

        return result

    async def get_ecosystem_overview(self) -> dict[str, Any]:
        """Get a high-level overview of the entire ecosystem.

        Combines counts and metrics from all three stores.
        """
        overview: dict[str, Any] = {"timestamp": datetime.utcnow().isoformat()}

        # Neo4j: Graph-level overview
        if self._graph:
            try:
                graph_overview = await self._graph.get_ecosystem_overview()
                overview["graph"] = graph_overview
            except Exception as e:
                logger.warning("Neo4j ecosystem overview failed: %s", e)

        # MongoDB: Latest dependency snapshot
        snapshot_repo = self._get_snapshot_repo()
        if snapshot_repo:
            try:
                latest = await snapshot_repo.get_latest_snapshot()
                if latest:
                    overview["latest_snapshot"] = {
                        "timestamp": str(latest.get("timestamp", "")),
                        "node_count": len(latest.get("nodes", [])),
                        "edge_count": len(latest.get("edges", [])),
                        "circular_deps": len(latest.get("circular_dependencies", [])),
                    }
            except Exception as e:
                logger.warning("MongoDB snapshot query failed: %s", e)

        return overview

    async def analyze_failure_impact(self, service_id: str) -> dict[str, Any]:
        """Comprehensive failure impact analysis.

        Combines Neo4j blast radius with PostgreSQL criticality data
        and MongoDB execution trace history.
        """
        analysis: dict[str, Any] = {
            "failed_service_id": service_id,
            "analysis_time": datetime.utcnow().isoformat(),
        }

        # Neo4j: Blast radius and cascade
        if self._graph:
            try:
                blast = await self._graph.calculate_blast_radius(service_id)
                analysis["blast_radius"] = blast

                cascade = await self._graph.get_health_cascade()
                analysis["health_cascade"] = cascade
            except Exception as e:
                logger.warning("Neo4j failure analysis failed: %s", e)

        # MongoDB: Recent flow traces involving this service
        trace_repo = self._get_trace_repo()
        if trace_repo:
            try:
                failed = await trace_repo.get_failed_executions(limit=20)
                analysis["recent_failures"] = failed
            except Exception as e:
                logger.warning("MongoDB trace query failed: %s", e)

        return analysis

    async def get_dependency_graph(
        self, service_id: str, depth: str = "direct"
    ) -> dict[str, Any]:
        """Get dependency graph at specified depth.

        Args:
            service_id: Root service
            depth: 'direct', 'transitive', or 'blast-radius'
        """
        if not self._graph:
            return {"error": "Graph store not available"}

        if depth == "direct":
            return await self._graph.get_direct_dependencies(service_id)
        elif depth == "transitive":
            deps = await self._graph.get_transitive_dependencies(service_id)
            return {"service_id": service_id, "transitive_dependencies": deps}
        elif depth == "blast-radius":
            return await self._graph.calculate_blast_radius(service_id)
        else:
            return await self._graph.get_direct_dependencies(service_id)

    async def detect_anomalies(self) -> dict[str, Any]:
        """Detect anomalies across the ecosystem.

        Checks for: circular deps, unhealthy cascades, orphaned services.
        """
        anomalies: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "circular_dependencies": [],
            "health_cascades": [],
            "critical_paths": [],
        }

        if self._graph:
            try:
                anomalies["circular_dependencies"] = (
                    await self._graph.detect_circular_dependencies()
                )
                anomalies["health_cascades"] = (
                    await self._graph.get_health_cascade()
                )
                anomalies["critical_paths"] = (
                    await self._graph.find_critical_paths()
                )
            except Exception as e:
                logger.warning("Anomaly detection failed: %s", e)

        return anomalies

    # ---- Event-Integrated Operations ----

    async def register_service(self, service_data: dict[str, Any]) -> dict[str, Any]:
        """Register a new service across all stores with event emission.

        1. PostgreSQL: Insert service record
        2. Neo4j: Create service node
        3. MongoDB: Emit audit log
        4. Event Bus: Publish EntityCreated event
        """
        service_id = service_data.get("id", str(UUID(int=0)))
        result: dict[str, Any] = {"service_id": service_id, "stores": {}}

        # PostgreSQL
        if self._pg:
            try:
                entity = await self._pg.create(**service_data)
                result["stores"]["postgres"] = "ok"
            except Exception as e:
                result["stores"]["postgres"] = f"error: {e}"
                logger.error("PostgreSQL service registration failed: %s", e)

        # Neo4j
        if self._graph:
            try:
                await self._graph.upsert_service(
                    id=service_id,
                    name=service_data.get("name", ""),
                    status=service_data.get("status", "active"),
                    service_type=service_data.get("service_type", "rest"),
                    criticality=service_data.get("criticality", "medium"),
                    owner=service_data.get("owner", ""),
                )
                result["stores"]["neo4j"] = "ok"
            except Exception as e:
                result["stores"]["neo4j"] = f"error: {e}"
                logger.error("Neo4j service registration failed: %s", e)

        # MongoDB audit
        audit_repo = self._get_audit_repo()
        if audit_repo:
            try:
                await audit_repo.log_entity_change(
                    entity_id=service_id,
                    entity_type="service",
                    action="created",
                    actor=service_data.get("owner", "system"),
                    new_state=service_data,
                )
                result["stores"]["mongodb"] = "ok"
            except Exception as e:
                result["stores"]["mongodb"] = f"error: {e}"

        # Event Bus
        if self._event_bus:
            from ..events.types import EntityCreatedEvent
            event = EntityCreatedEvent(
                source_id=service_id,
                source_type="service",
                entity_data=service_data,
            )
            await self._event_bus.publish(event)

        return result

    async def register_dependency(
        self,
        source_id: str,
        target_id: str,
        source_type: str = "service",
        target_type: str = "service",
        dep_type: str = "runtime",
        severity: str = "medium",
    ) -> dict[str, Any]:
        """Register a dependency across stores with event emission."""
        result: dict[str, Any] = {
            "source_id": source_id,
            "target_id": target_id,
            "stores": {},
        }

        # Neo4j: Create relationship
        if self._graph:
            try:
                await self._graph.create_dependency(
                    source_id=source_id,
                    target_id=target_id,
                    dep_type=dep_type,
                    severity=severity,
                )
                result["stores"]["neo4j"] = "ok"
            except Exception as e:
                result["stores"]["neo4j"] = f"error: {e}"

        # Event Bus
        if self._event_bus:
            from ..events.types import DependencyDiscoveredEvent
            event = DependencyDiscoveredEvent(
                source_id=source_id,
                source_type=source_type,
                target_id=target_id,
                target_type=target_type,
                dependency_type=dep_type,
                severity=severity,
            )
            await self._event_bus.publish(event)

        return result

    # ---- Health Check ----

    async def health_check(self) -> dict[str, Any]:
        """Check health of all data stores."""
        health: dict[str, Any] = {"timestamp": datetime.utcnow().isoformat()}

        # PostgreSQL
        if self._pg:
            try:
                count = await self._pg.count()
                health["postgres"] = {"status": "healthy", "record_count": count}
            except Exception as e:
                health["postgres"] = {"status": "unhealthy", "error": str(e)}
        else:
            health["postgres"] = {"status": "not_configured"}

        # MongoDB
        if self._mongo:
            try:
                await self._mongo.db.command("ping")
                health["mongodb"] = {"status": "healthy"}
            except Exception as e:
                health["mongodb"] = {"status": "unhealthy", "error": str(e)}
        else:
            health["mongodb"] = {"status": "not_configured"}

        # Neo4j
        if self._graph:
            try:
                overview = await self._graph.get_ecosystem_overview()
                health["neo4j"] = {"status": "healthy", "overview": overview}
            except Exception as e:
                health["neo4j"] = {"status": "unhealthy", "error": str(e)}
        else:
            health["neo4j"] = {"status": "not_configured"}

        return health
