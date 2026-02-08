"""WorldMaker persistence layer.

Provides InMemoryStore for lightweight operation, plus optional MongoDB (Motor)
and Neo4j backends when the corresponding drivers are available.

Imports of mongo/graph sub-packages are lazy so that environments without
those drivers (or with driver-level incompatibilities) can still use the
InMemoryStore without errors.
"""
from __future__ import annotations

# Always-available in-memory store
from .memory import InMemoryStore, get_store, reset_store

# Lazy accessors for optional backends — import only when explicitly requested.
def _import_mongo():
    from .mongo import (
        HAS_MOTOR,
        AUDIT_LOGS,
        CONFIG_CHANGE_HISTORY,
        DEPENDENCY_SNAPSHOTS,
        EVENT_STREAM,
        FLOW_EXECUTION_TRACES,
        SERVICE_CONFIGS,
        AuditLogDocument,
        AuditLogRepository,
        ConfigChangeEntry,
        DependencySnapshot,
        DependencySnapshotRepository,
        EventStreamEntry,
        EventStreamRepository,
        FlowExecutionTrace,
        FlowTraceRepository,
        MongoClient,
        MongoRepository,
    )
    return locals()


def _import_graph():
    from .graph import HAS_NEO4J, GraphRepository, Neo4jDriver
    return locals()


__all__ = [
    # Always available
    "InMemoryStore",
    "get_store",
    "reset_store",
    # MongoDB (lazy)
    "HAS_MOTOR",
    "MongoClient",
    "MongoRepository",
    "AuditLogRepository",
    "FlowTraceRepository",
    "DependencySnapshotRepository",
    "EventStreamRepository",
    "AUDIT_LOGS",
    "SERVICE_CONFIGS",
    "FLOW_EXECUTION_TRACES",
    "EVENT_STREAM",
    "DEPENDENCY_SNAPSHOTS",
    "CONFIG_CHANGE_HISTORY",
    "AuditLogDocument",
    "FlowExecutionTrace",
    "DependencySnapshot",
    "EventStreamEntry",
    "ConfigChangeEntry",
    # Neo4j (lazy)
    "HAS_NEO4J",
    "Neo4jDriver",
    "GraphRepository",
]
