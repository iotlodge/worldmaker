"""MongoDB persistence layer for WorldMaker."""
from __future__ import annotations

from .client import HAS_MOTOR, MongoClient
from .collections import (
    ALL_COLLECTIONS,
    AUDIT_LOGS,
    CONFIG_CHANGE_HISTORY,
    DEPENDENCY_SNAPSHOTS,
    EVENT_STREAM,
    FLOW_EXECUTION_TRACES,
    SERVICE_CONFIGS,
    AuditLogDocument,
    ConfigChangeEntry,
    DependencySnapshot,
    EventStreamEntry,
    FlowExecutionTrace,
)
from .repository import (
    AuditLogRepository,
    DependencySnapshotRepository,
    EventStreamRepository,
    FlowTraceRepository,
    MongoRepository,
)

__all__ = [
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
    "ALL_COLLECTIONS",
    "AuditLogDocument",
    "FlowExecutionTrace",
    "DependencySnapshot",
    "EventStreamEntry",
    "ConfigChangeEntry",
]
