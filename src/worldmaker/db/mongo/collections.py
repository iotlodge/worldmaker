"""MongoDB collection definitions and document schemas."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# Collection names as constants
AUDIT_LOGS = "audit_logs"
SERVICE_CONFIGS = "service_configs"
FLOW_EXECUTION_TRACES = "flow_execution_traces"
EVENT_STREAM = "event_stream"
DEPENDENCY_SNAPSHOTS = "dependency_snapshots"
CONFIG_CHANGE_HISTORY = "config_change_history"

ALL_COLLECTIONS = [
    AUDIT_LOGS,
    SERVICE_CONFIGS,
    FLOW_EXECUTION_TRACES,
    EVENT_STREAM,
    DEPENDENCY_SNAPSHOTS,
    CONFIG_CHANGE_HISTORY,
]


@dataclass
class AuditLogDocument:
    """Audit log entry for entity changes."""

    entity_id: str
    entity_type: str
    action: str
    actor: str
    timestamp: datetime
    previous_state: dict[str, Any] = field(default_factory=dict)
    new_state: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_document(self) -> dict[str, Any]:
        """Convert to MongoDB document."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "action": self.action,
            "actor": self.actor,
            "timestamp": self.timestamp,
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "metadata": self.metadata,
        }


@dataclass
class FlowExecutionTrace:
    """Detailed trace of a flow execution."""

    flow_id: str
    execution_id: str
    start_time: datetime
    end_time: datetime | None = None
    status: str = "running"
    total_duration_ms: int = 0
    steps: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    performance_metrics: dict[str, Any] = field(default_factory=dict)

    def to_document(self) -> dict[str, Any]:
        """Convert to MongoDB document."""
        return {
            "flow_id": self.flow_id,
            "execution_id": self.execution_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "total_duration_ms": self.total_duration_ms,
            "steps": self.steps,
            "errors": self.errors,
            "performance_metrics": self.performance_metrics,
        }


@dataclass
class DependencySnapshot:
    """Point-in-time snapshot of the dependency graph."""

    snapshot_id: str
    timestamp: datetime
    nodes: list[dict[str, Any]] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)
    circular_dependencies: list[list[str]] = field(default_factory=list)
    blast_radii: dict[str, int] = field(default_factory=dict)

    def to_document(self) -> dict[str, Any]:
        """Convert to MongoDB document."""
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "nodes": self.nodes,
            "edges": self.edges,
            "circular_dependencies": self.circular_dependencies,
            "blast_radii": self.blast_radii,
        }


@dataclass
class EventStreamEntry:
    """Event stream CDC entry."""

    event_type: str
    source_id: str
    source_type: str
    timestamp: datetime
    data: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None

    def to_document(self) -> dict[str, Any]:
        """Convert to MongoDB document."""
        return {
            "event_type": self.event_type,
            "source_id": self.source_id,
            "source_type": self.source_type,
            "timestamp": self.timestamp,
            "data": self.data,
            "correlation_id": self.correlation_id,
        }


@dataclass
class ConfigChangeEntry:
    """Configuration change history entry."""

    entity_id: str
    entity_type: str
    change_timestamp: datetime
    change_type: str
    author: str
    description: str = ""
    diff: dict[str, Any] = field(
        default_factory=lambda: {"added": {}, "modified": {}, "removed": {}}
    )
    rollback_info: dict[str, Any] = field(default_factory=dict)
    approval_status: str = "pending"

    def to_document(self) -> dict[str, Any]:
        """Convert to MongoDB document."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "change_timestamp": self.change_timestamp,
            "change_type": self.change_type,
            "author": self.author,
            "description": self.description,
            "diff": self.diff,
            "rollback_info": self.rollback_info,
            "approval_status": self.approval_status,
        }
