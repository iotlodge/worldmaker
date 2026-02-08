"""WorldMaker event type definitions.

All state mutations in the ecosystem flow through these event types.
The event bus processes these asynchronously, and handlers react to derive
dependency graphs, impact chains, and lifecycle transitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4


class EventCategory(str, Enum):
    """Categories for classifying events by domain."""
    ENTITY = "entity"
    DEPENDENCY = "dependency"
    FLOW = "flow"
    LIFECYCLE = "lifecycle"
    FAILURE = "failure"
    IMPACT = "impact"


@dataclass
class BaseEvent:
    """Base event — all events carry correlation context.

    Attributes:
        event_id: Unique identifier for this event
        event_type: Semantic event type (e.g., "entity.created")
        category: Domain category for this event
        timestamp: When the event occurred
        source_id: ID of the entity that triggered the event
        source_type: Type of the source entity
        correlation_id: ID for tracing related events
        version: Event schema version
        metadata: Arbitrary event context
    """
    event_id: UUID = field(default_factory=uuid4)
    event_type: str = ""
    category: EventCategory = EventCategory.ENTITY
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_id: str = ""
    source_type: str = ""
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    version: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "category": self.category.value if isinstance(self.category, EventCategory) else self.category,
            "timestamp": self.timestamp.isoformat(),
            "source_id": self.source_id,
            "source_type": self.source_type,
            "correlation_id": self.correlation_id,
            "version": self.version,
            "metadata": self.metadata,
        }


# ============================================================================
# Entity Events
# ============================================================================


@dataclass
class EntityCreatedEvent(BaseEvent):
    """Emitted when a new entity is created.

    Attributes:
        entity_data: Dictionary of entity attributes
    """
    event_type: str = "entity.created"
    category: EventCategory = EventCategory.ENTITY
    entity_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class EntityModifiedEvent(BaseEvent):
    """Emitted when an existing entity is modified.

    Attributes:
        changes: Dictionary of changed fields
        previous_state: State before modification
    """
    event_type: str = "entity.modified"
    category: EventCategory = EventCategory.ENTITY
    changes: dict[str, Any] = field(default_factory=dict)
    previous_state: dict[str, Any] = field(default_factory=dict)


@dataclass
class EntityDeprecatedEvent(BaseEvent):
    """Emitted when an entity is marked as deprecated.

    Attributes:
        reason: Why the entity was deprecated
        replacement_id: ID of the replacement entity if any
    """
    event_type: str = "entity.deprecated"
    category: EventCategory = EventCategory.ENTITY
    reason: str = ""
    replacement_id: Optional[str] = None


# ============================================================================
# Dependency Events
# ============================================================================


@dataclass
class DependencyDiscoveredEvent(BaseEvent):
    """Emitted when a dependency is discovered or created.

    Attributes:
        target_id: ID of the target (depended-on) entity
        target_type: Type of the target entity
        dependency_type: Type of dependency (e.g., "runtime", "compile")
        severity: Severity level (e.g., "low", "medium", "high", "critical")
    """
    event_type: str = "dependency.discovered"
    category: EventCategory = EventCategory.DEPENDENCY
    target_id: str = ""
    target_type: str = ""
    dependency_type: str = "runtime"
    severity: str = "medium"


@dataclass
class DependencyRemovedEvent(BaseEvent):
    """Emitted when a dependency is removed.

    Attributes:
        target_id: ID of the target entity
        target_type: Type of the target entity
        reason: Why the dependency was removed
    """
    event_type: str = "dependency.removed"
    category: EventCategory = EventCategory.DEPENDENCY
    target_id: str = ""
    target_type: str = ""
    reason: str = ""


@dataclass
class CircularDependencyDetectedEvent(BaseEvent):
    """Emitted when a circular dependency is detected.

    Attributes:
        cycle: List of IDs forming the cycle
        cycle_services: List of service details in the cycle
        severity: Always critical
    """
    event_type: str = "dependency.circular_detected"
    category: EventCategory = EventCategory.DEPENDENCY
    cycle: list[str] = field(default_factory=list)
    cycle_services: list[dict[str, str]] = field(default_factory=list)
    severity: str = "critical"


# ============================================================================
# Flow Events
# ============================================================================


@dataclass
class FlowExecutionStartedEvent(BaseEvent):
    """Emitted when a flow execution begins.

    Attributes:
        flow_id: ID of the flow template
        execution_id: Unique ID for this execution
    """
    event_type: str = "flow.execution_started"
    category: EventCategory = EventCategory.FLOW
    flow_id: str = ""
    execution_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class FlowExecutionCompletedEvent(BaseEvent):
    """Emitted when a flow execution finishes.

    Attributes:
        flow_id: ID of the flow template
        execution_id: ID of the execution
        status: Final status (e.g., "completed", "failed")
        total_duration_ms: Total execution time
        steps: List of step execution records
        errors: List of any errors that occurred
    """
    event_type: str = "flow.execution_completed"
    category: EventCategory = EventCategory.FLOW
    flow_id: str = ""
    execution_id: str = ""
    status: str = "completed"
    total_duration_ms: int = 0
    steps: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


# ============================================================================
# Lifecycle Events
# ============================================================================


@dataclass
class LifecycleTransitionEvent(BaseEvent):
    """Emitted when an entity transitions between lifecycle states.

    Attributes:
        from_state: Previous state
        to_state: New state
        reason: Reason for the transition
        author: Who triggered the transition
    """
    event_type: str = "lifecycle.transition"
    category: EventCategory = EventCategory.LIFECYCLE
    from_state: str = ""
    to_state: str = ""
    reason: str = ""
    author: str = ""


# ============================================================================
# Failure Events
# ============================================================================


@dataclass
class FailureDetectedEvent(BaseEvent):
    """Emitted when a failure is detected in an entity.

    Attributes:
        failure_type: Type of failure
        severity: Severity level
        affected_service_ids: Services affected by this failure
        description: Human-readable description
    """
    event_type: str = "failure.detected"
    category: EventCategory = EventCategory.FAILURE
    failure_type: str = ""
    severity: str = "high"
    affected_service_ids: list[str] = field(default_factory=list)
    description: str = ""


# ============================================================================
# Impact Events
# ============================================================================


@dataclass
class ImpactChainCalculatedEvent(BaseEvent):
    """Emitted when impact analysis is performed.

    Attributes:
        root_cause_id: ID of the root cause entity
        blast_radius: Number of affected entities
        affected_services: Details of affected services
        estimated_recovery_minutes: Time to recovery
    """
    event_type: str = "impact.chain_calculated"
    category: EventCategory = EventCategory.IMPACT
    root_cause_id: str = ""
    blast_radius: int = 0
    affected_services: list[dict[str, Any]] = field(default_factory=list)
    estimated_recovery_minutes: int = 0


# ============================================================================
# Event Registry
# ============================================================================


EVENT_REGISTRY: dict[str, type[BaseEvent]] = {
    "entity.created": EntityCreatedEvent,
    "entity.modified": EntityModifiedEvent,
    "entity.deprecated": EntityDeprecatedEvent,
    "dependency.discovered": DependencyDiscoveredEvent,
    "dependency.removed": DependencyRemovedEvent,
    "dependency.circular_detected": CircularDependencyDetectedEvent,
    "flow.execution_started": FlowExecutionStartedEvent,
    "flow.execution_completed": FlowExecutionCompletedEvent,
    "lifecycle.transition": LifecycleTransitionEvent,
    "failure.detected": FailureDetectedEvent,
    "impact.chain_calculated": ImpactChainCalculatedEvent,
}
