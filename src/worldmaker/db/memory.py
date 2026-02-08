"""In-memory data store for development and testing.

Provides a complete persistence layer using Python dicts, lists, and sets.
Supports all CRUD operations, dependency graph queries, and audit logging
without requiring any external databases.

This is the default store used when no database connections are configured.
"""
from __future__ import annotations
import copy
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class InMemoryStore:
    """Complete in-memory persistence layer.

    Stores all WorldMaker entities with:
    - CRUD operations for all entity types
    - Dependency graph with traversal
    - Audit log
    - Flow trace storage
    - Full-text-ish search on name fields
    """

    def __init__(self):
        # Entity storage: {entity_type: {id_str: entity_dict}}
        self._entities: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)

        # Dependency graph: adjacency lists
        self._dependencies: list[dict[str, Any]] = []
        self._dep_index_source: dict[str, list[int]] = defaultdict(list)  # source_id -> dep indices
        self._dep_index_target: dict[str, list[int]] = defaultdict(list)  # target_id -> dep indices

        # Audit log
        self._audit_log: list[dict[str, Any]] = []

        # Flow traces
        self._traces: list[dict[str, Any]] = []

        # OTel spans
        self._spans: list[dict[str, Any]] = []

        # Counters
        self._stats: dict[str, int] = defaultdict(int)

    # ---- Generic CRUD ----

    def create(self, entity_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Create an entity. Auto-generates id and timestamps if missing."""
        entity = dict(data)
        if "id" not in entity:
            entity["id"] = str(uuid4())
        entity_id = str(entity["id"])
        entity.setdefault("created_at", datetime.utcnow().isoformat())
        entity.setdefault("updated_at", entity["created_at"])
        entity.setdefault("metadata", {})

        self._entities[entity_type][entity_id] = entity
        self._stats[f"{entity_type}_created"] += 1

        self._audit(entity_id, entity_type, "created", new_state=entity)
        return entity

    def get(self, entity_type: str, entity_id: str) -> dict[str, Any] | None:
        """Get entity by type and ID."""
        return copy.deepcopy(self._entities.get(entity_type, {}).get(str(entity_id)))

    def get_all(self, entity_type: str, limit: int = 100, offset: int = 0,
                filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Get all entities of a type with optional filtering."""
        entities = list(self._entities.get(entity_type, {}).values())

        if filters:
            for key, value in filters.items():
                entities = [e for e in entities if e.get(key) == value]

        return [copy.deepcopy(e) for e in entities[offset:offset + limit]]

    def update(self, entity_type: str, entity_id: str,
               updates: dict[str, Any]) -> dict[str, Any] | None:
        """Update an entity. Returns updated entity or None if not found."""
        entity_id = str(entity_id)
        entity = self._entities.get(entity_type, {}).get(entity_id)
        if not entity:
            return None

        previous = copy.deepcopy(entity)
        entity.update(updates)
        entity["updated_at"] = datetime.utcnow().isoformat()

        self._audit(entity_id, entity_type, "modified",
                    previous_state=previous, new_state=entity)
        return copy.deepcopy(entity)

    def delete(self, entity_type: str, entity_id: str) -> bool:
        """Delete an entity. Returns True if found and deleted."""
        entity_id = str(entity_id)
        if entity_id in self._entities.get(entity_type, {}):
            entity = self._entities[entity_type].pop(entity_id)
            self._audit(entity_id, entity_type, "deleted", previous_state=entity)
            return True
        return False

    def count(self, entity_type: str, filters: dict[str, Any] | None = None) -> int:
        """Count entities of a type."""
        if not filters:
            return len(self._entities.get(entity_type, {}))
        return len(self.get_all(entity_type, limit=999999, filters=filters))

    def search(self, entity_type: str, query: str, fields: list[str] | None = None) -> list[dict[str, Any]]:
        """Search entities by text match on specified fields."""
        search_fields = fields or ["name", "description"]
        query_lower = query.lower()
        results = []
        for entity in self._entities.get(entity_type, {}).values():
            for field in search_fields:
                val = entity.get(field, "")
                if val and query_lower in str(val).lower():
                    results.append(copy.deepcopy(entity))
                    break
        return results

    # ---- Dependency Graph ----

    def add_dependency(self, source_id: str, target_id: str,
                       source_type: str = "service", target_type: str = "service",
                       dep_type: str = "runtime", severity: str = "medium",
                       **kwargs: Any) -> dict[str, Any]:
        """Add a dependency relationship."""
        dep = {
            "id": str(uuid4()),
            "source_id": str(source_id),
            "target_id": str(target_id),
            "source_type": source_type,
            "target_type": target_type,
            "dependency_type": dep_type,
            "severity": severity,
            "is_circular": False,
            "created_at": datetime.utcnow().isoformat(),
            **kwargs,
        }

        idx = len(self._dependencies)
        self._dependencies.append(dep)
        self._dep_index_source[str(source_id)].append(idx)
        self._dep_index_target[str(target_id)].append(idx)

        # Check for circular dependency
        if self._has_path(str(target_id), str(source_id)):
            dep["is_circular"] = True

        return dep

    def get_dependencies_of(self, source_id: str) -> list[dict[str, Any]]:
        """Get all dependencies where source_id is the source (what I depend on)."""
        indices = self._dep_index_source.get(str(source_id), [])
        return [copy.deepcopy(self._dependencies[i]) for i in indices]

    def get_dependents_of(self, target_id: str) -> list[dict[str, Any]]:
        """Get all dependencies where target_id is the target (who depends on me)."""
        indices = self._dep_index_target.get(str(target_id), [])
        return [copy.deepcopy(self._dependencies[i]) for i in indices]

    def get_transitive_dependencies(self, source_id: str, max_depth: int = 10) -> list[dict[str, Any]]:
        """Get all transitive dependencies (BFS)."""
        visited: set[str] = set()
        queue: list[tuple[str, int]] = [(str(source_id), 0)]
        result: list[dict[str, Any]] = []

        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth > max_depth:
                continue
            visited.add(current)

            for dep in self.get_dependencies_of(current):
                target = dep["target_id"]
                dep_with_depth = {**dep, "hops_from_source": depth + 1}
                result.append(dep_with_depth)
                if target not in visited:
                    queue.append((target, depth + 1))

        return result

    def calculate_blast_radius(self, service_id: str) -> dict[str, Any]:
        """Calculate blast radius — who is affected if this service goes down."""
        service_id = str(service_id)

        # BFS upstream: who depends on me (directly or transitively)
        affected: list[dict[str, Any]] = []
        visited: set[str] = set()
        queue: list[tuple[str, int]] = [(service_id, 0)]

        while queue:
            current, depth = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            for dep in self.get_dependents_of(current):
                src = dep["source_id"]
                if src not in visited:
                    entity = self.get(dep["source_type"], src)
                    affected.append({
                        "id": src,
                        "type": dep["source_type"],
                        "name": entity.get("name", "unknown") if entity else "unknown",
                        "severity": dep["severity"],
                        "hops_away": depth + 1,
                    })
                    queue.append((src, depth + 1))

        root = self.get("service", service_id)
        return {
            "root_service": {
                "id": service_id,
                "name": root.get("name", "unknown") if root else "unknown",
            },
            "blast_radius": len(affected),
            "affected_services": affected,
            "max_depth": max((a["hops_away"] for a in affected), default=0),
        }

    def detect_circular_dependencies(self) -> list[dict[str, Any]]:
        """Detect all circular dependencies in the graph."""
        circular = [d for d in self._dependencies if d.get("is_circular")]
        return circular

    def _has_path(self, from_id: str, to_id: str, max_depth: int = 20) -> bool:
        """Check if there's a path from from_id to to_id in the dependency graph."""
        visited: set[str] = set()
        queue: list[tuple[str, int]] = [(from_id, 0)]
        while queue:
            current, depth = queue.pop(0)
            if current == to_id:
                return True
            if current in visited or depth > max_depth:
                continue
            visited.add(current)
            for dep in self.get_dependencies_of(current):
                queue.append((dep["target_id"], depth + 1))
        return False

    # ---- Audit Log ----

    def _audit(self, entity_id: str, entity_type: str, action: str,
               actor: str = "system", previous_state: dict | None = None,
               new_state: dict | None = None) -> None:
        self._audit_log.append({
            "id": str(uuid4()),
            "entity_id": entity_id,
            "entity_type": entity_type,
            "action": action,
            "actor": actor,
            "timestamp": datetime.utcnow().isoformat(),
            "previous_state": previous_state,
            "new_state": new_state,
        })

    def get_audit_log(self, entity_id: str | None = None,
                      entity_type: str | None = None,
                      limit: int = 100) -> list[dict[str, Any]]:
        """Get audit log entries, optionally filtered."""
        entries = self._audit_log
        if entity_id:
            entries = [e for e in entries if e["entity_id"] == str(entity_id)]
        if entity_type:
            entries = [e for e in entries if e["entity_type"] == entity_type]
        return entries[-limit:]

    # ---- Trace Storage ----

    def store_trace(self, trace: dict[str, Any]) -> None:
        self._traces.append(trace)

    def get_traces(self, flow_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        traces = self._traces
        if flow_id:
            traces = [t for t in traces if t.get("flow_id") == str(flow_id)]
        return traces[-limit:]

    # ---- Span Storage ----

    def store_span(self, span: dict[str, Any]) -> None:
        self._spans.append(span)

    def store_spans(self, spans: list[dict[str, Any]]) -> None:
        self._spans.extend(spans)

    def get_spans(self, trace_id: str | None = None, limit: int = 1000) -> list[dict[str, Any]]:
        spans = self._spans
        if trace_id:
            spans = [s for s in spans if s.get("traceId") == str(trace_id)]
        return spans[-limit:]

    # ---- Bulk Load ----

    def load_ecosystem(self, ecosystem: dict[str, Any]) -> dict[str, int]:
        """Load a complete generated ecosystem into the store."""
        loaded: dict[str, int] = {}

        entity_types = [
            ("products", "product"),
            ("features", "feature"),
            ("platforms", "platform"),
            ("capabilities", "capability"),
            ("services", "service"),
            ("microservices", "microservice"),
            ("interfaces", "interface"),
            ("flows", "flow"),
            ("flow_steps", "flow_step"),
            ("environments", "environment"),
            ("deployments", "deployment"),
            ("data_stores", "data_store"),
            ("event_types", "event_type"),
            ("criticality_ratings", "criticality_rating"),
            ("slo_definitions", "slo_definition"),
            ("failure_modes", "failure_mode"),
            ("recovery_patterns", "recovery_pattern"),
        ]

        for plural_key, entity_type in entity_types:
            items = ecosystem.get(plural_key, [])
            for item in items:
                self.create(entity_type, item)
            loaded[entity_type] = len(items)

        # Load dependencies into the graph
        for dep in ecosystem.get("dependencies", []):
            self.add_dependency(
                source_id=dep["source_id"],
                target_id=dep["target_id"],
                source_type=dep.get("source_type", "service"),
                target_type=dep.get("target_type", "service"),
                dep_type=dep.get("dependency_type", "runtime"),
                severity=dep.get("severity", "medium"),
            )
        loaded["dependencies"] = len(ecosystem.get("dependencies", []))

        return loaded

    # ---- Layer Operations ----

    def clear_layer(self, layer: str) -> dict[str, int]:
        """Remove all entities matching the given layer. Returns deletion counts.

        Also clears dependencies whose source or target was deleted, and
        removes traces, spans, and audit log (execution artifacts).
        """
        counts: dict[str, int] = {}

        for entity_type in list(self._entities.keys()):
            to_delete = [
                eid for eid, entity in self._entities[entity_type].items()
                if entity.get("layer") == layer
            ]
            counts[entity_type] = len(to_delete)
            for eid in to_delete:
                del self._entities[entity_type][eid]

        # Filter dependencies — remove edges where source OR target was deleted
        surviving_ids: set[str] = set()
        for entities in self._entities.values():
            surviving_ids.update(entities.keys())

        original_dep_count = len(self._dependencies)
        self._dependencies = [
            d for d in self._dependencies
            if d["source_id"] in surviving_ids and d["target_id"] in surviving_ids
        ]
        counts["dependencies"] = original_dep_count - len(self._dependencies)

        self._rebuild_dep_indexes()

        # Clear traces, spans, audit log (execution artifacts)
        counts["traces"] = len(self._traces)
        counts["spans"] = len(self._spans)
        self._traces.clear()
        self._spans.clear()
        self._audit_log.clear()

        return counts

    def _rebuild_dep_indexes(self) -> None:
        """Rebuild dependency source/target indexes after bulk operations."""
        self._dep_index_source = defaultdict(list)
        self._dep_index_target = defaultdict(list)
        for idx, dep in enumerate(self._dependencies):
            self._dep_index_source[dep["source_id"]].append(idx)
            self._dep_index_target[dep["target_id"]].append(idx)

    # ---- Stats ----

    def get_overview(self) -> dict[str, Any]:
        """Get overview of everything in the store."""
        return {
            "entity_counts": {
                entity_type: len(entities)
                for entity_type, entities in self._entities.items()
            },
            "total_entities": sum(len(e) for e in self._entities.values()),
            "total_dependencies": len(self._dependencies),
            "circular_dependencies": len(self.detect_circular_dependencies()),
            "audit_log_entries": len(self._audit_log),
            "traces": len(self._traces),
            "spans": len(self._spans),
        }


# Singleton for the default store
_default_store: InMemoryStore | None = None

def get_store() -> InMemoryStore:
    """Get or create the default in-memory store."""
    global _default_store
    if _default_store is None:
        _default_store = InMemoryStore()
    return _default_store

def reset_store() -> InMemoryStore:
    """Reset the default store (for testing)."""
    global _default_store
    _default_store = InMemoryStore()
    return _default_store
