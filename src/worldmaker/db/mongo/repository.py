"""Async MongoDB repository for document operations."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class MongoRepository:
    """Base MongoDB repository for document CRUD."""

    def __init__(self, client: Any, collection_name: str):
        """Initialize repository.

        Args:
            client: MongoClient instance from client.py
            collection_name: Name of the collection
        """
        self._client = client
        self._collection_name = collection_name

    @property
    def collection(self) -> Any:
        """Get the collection instance."""
        return self._client.collection(self._collection_name)

    async def insert_one(self, document: dict[str, Any]) -> str:
        """Insert a single document.

        Args:
            document: Document to insert

        Returns:
            Inserted document ID as string
        """
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def insert_many(self, documents: list[dict[str, Any]]) -> list[str]:
        """Insert multiple documents.

        Args:
            documents: List of documents to insert

        Returns:
            List of inserted document IDs as strings
        """
        result = await self.collection.insert_many(documents)
        return [str(id_) for id_ in result.inserted_ids]

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        """Find a single document.

        Args:
            query: MongoDB query filter

        Returns:
            Document or None if not found
        """
        return await self.collection.find_one(query)

    async def find_many(
        self,
        query: dict[str, Any],
        sort: list[tuple[str, int]] | None = None,
        limit: int = 100,
        skip: int = 0,
    ) -> list[dict[str, Any]]:
        """Find multiple documents.

        Args:
            query: MongoDB query filter
            sort: List of (field, direction) tuples
            limit: Maximum documents to return
            skip: Documents to skip

        Returns:
            List of documents
        """
        cursor = self.collection.find(query).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        return await cursor.to_list(length=limit)

    async def count(self, query: dict[str, Any] | None = None) -> int:
        """Count documents matching query.

        Args:
            query: MongoDB query filter

        Returns:
            Document count
        """
        return await self.collection.count_documents(query or {})

    async def update_one(self, query: dict[str, Any], update: dict[str, Any]) -> bool:
        """Update a single document.

        Args:
            query: MongoDB query filter
            update: Update document

        Returns:
            True if document was modified
        """
        result = await self.collection.update_one(query, {"$set": update})
        return result.modified_count > 0

    async def delete_one(self, query: dict[str, Any]) -> bool:
        """Delete a single document.

        Args:
            query: MongoDB query filter

        Returns:
            True if document was deleted
        """
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0

    async def aggregate(
        self, pipeline: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Execute aggregation pipeline.

        Args:
            pipeline: MongoDB aggregation pipeline

        Returns:
            Aggregation results
        """
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)


class AuditLogRepository(MongoRepository):
    """Specialized repository for audit logs."""

    def __init__(self, client: Any):
        """Initialize audit log repository."""
        super().__init__(client, "audit_logs")

    async def log_entity_change(
        self,
        entity_id: str,
        entity_type: str,
        action: str,
        actor: str,
        previous_state: dict[str, Any] | None = None,
        new_state: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Log an entity change.

        Args:
            entity_id: ID of entity that changed
            entity_type: Type of entity
            action: Action performed (create, update, delete, etc.)
            actor: User or system that performed the action
            previous_state: Previous entity state
            new_state: New entity state
            metadata: Additional metadata

        Returns:
            Inserted log ID
        """
        document = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "action": action,
            "actor": actor,
            "timestamp": datetime.utcnow(),
            "previous_state": previous_state or {},
            "new_state": new_state or {},
            "metadata": metadata or {},
        }
        return await self.insert_one(document)

    async def get_entity_history(
        self, entity_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get change history for an entity.

        Args:
            entity_id: Entity ID
            limit: Maximum records to return

        Returns:
            List of audit log entries
        """
        return await self.find_many(
            {"entity_id": entity_id},
            sort=[("timestamp", -1)],
            limit=limit,
        )

    async def get_actor_activity(
        self, actor: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get activity for a specific actor.

        Args:
            actor: Actor name or ID
            limit: Maximum records to return

        Returns:
            List of audit log entries
        """
        return await self.find_many(
            {"actor": actor},
            sort=[("timestamp", -1)],
            limit=limit,
        )


class FlowTraceRepository(MongoRepository):
    """Specialized repository for flow execution traces."""

    def __init__(self, client: Any):
        """Initialize flow trace repository."""
        super().__init__(client, "flow_execution_traces")

    async def record_execution(
        self,
        flow_id: str,
        execution_id: str,
        steps: list[dict[str, Any]],
        status: str = "completed",
        total_duration_ms: int = 0,
    ) -> str:
        """Record a flow execution.

        Args:
            flow_id: Flow ID
            execution_id: Unique execution ID
            steps: List of execution steps
            status: Execution status (completed, failed, etc.)
            total_duration_ms: Total execution time in milliseconds

        Returns:
            Inserted trace ID
        """
        now = datetime.utcnow()
        document = {
            "flow_id": flow_id,
            "execution_id": execution_id,
            "start_time": now,
            "end_time": now,
            "status": status,
            "total_duration_ms": total_duration_ms,
            "steps": steps,
            "errors": [s for s in steps if s.get("status") == "failure"],
            "performance_metrics": {},
        }
        return await self.insert_one(document)

    async def get_flow_history(
        self, flow_id: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Get execution history for a flow.

        Args:
            flow_id: Flow ID
            limit: Maximum records to return

        Returns:
            List of execution traces
        """
        return await self.find_many(
            {"flow_id": flow_id},
            sort=[("start_time", -1)],
            limit=limit,
        )

    async def get_failed_executions(
        self, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get failed executions.

        Args:
            limit: Maximum records to return

        Returns:
            List of failed execution traces
        """
        return await self.find_many(
            {"status": "failed"},
            sort=[("start_time", -1)],
            limit=limit,
        )


class DependencySnapshotRepository(MongoRepository):
    """Specialized repository for dependency graph snapshots."""

    def __init__(self, client: Any):
        """Initialize dependency snapshot repository."""
        super().__init__(client, "dependency_snapshots")

    async def save_snapshot(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        circular_deps: list[list[str]] | None = None,
        blast_radii: dict[str, int] | None = None,
    ) -> str:
        """Save a dependency graph snapshot.

        Args:
            nodes: Graph nodes
            edges: Graph edges
            circular_deps: Detected circular dependencies
            blast_radii: Blast radius for each service

        Returns:
            Inserted snapshot ID
        """
        document = {
            "snapshot_id": str(uuid4()),
            "timestamp": datetime.utcnow(),
            "nodes": nodes,
            "edges": edges,
            "circular_dependencies": circular_deps or [],
            "blast_radii": blast_radii or {},
        }
        return await self.insert_one(document)

    async def get_latest_snapshot(self) -> dict[str, Any] | None:
        """Get the most recent snapshot.

        Returns:
            Latest snapshot document or None
        """
        results = await self.find_many(
            {},
            sort=[("timestamp", -1)],
            limit=1,
        )
        return results[0] if results else None


class EventStreamRepository(MongoRepository):
    """Specialized repository for event stream CDC."""

    def __init__(self, client: Any):
        """Initialize event stream repository."""
        super().__init__(client, "event_stream")

    async def emit_event(
        self,
        event_type: str,
        source_id: str,
        source_type: str,
        data: dict[str, Any],
        correlation_id: str | None = None,
    ) -> str:
        """Emit an event to the stream.

        Args:
            event_type: Type of event
            source_id: ID of event source
            source_type: Type of source entity
            data: Event data
            correlation_id: Correlation ID for tracing

        Returns:
            Inserted event ID
        """
        document = {
            "event_type": event_type,
            "source_id": source_id,
            "source_type": source_type,
            "timestamp": datetime.utcnow(),
            "data": data,
            "correlation_id": correlation_id or str(uuid4()),
        }
        return await self.insert_one(document)

    async def get_events_since(
        self,
        since: datetime,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get events since a specific time.

        Args:
            since: Start timestamp
            event_type: Filter by event type (optional)
            limit: Maximum records to return

        Returns:
            List of events
        """
        query: dict[str, Any] = {"timestamp": {"$gte": since}}
        if event_type:
            query["event_type"] = event_type
        return await self.find_many(query, sort=[("timestamp", 1)], limit=limit)
