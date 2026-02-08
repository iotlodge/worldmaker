"""Event handlers for WorldMaker ecosystem management.

These handlers react to events and perform cross-cutting operations:
- DependencyAnalyzerHandler: Validates deps, detects cycles, updates graph
- ImpactChainHandler: Calculates blast radius on dependency changes
- LifecycleHandler: Tracks state transitions, emits audit logs
- FlowTracerHandler: Stores execution traces, updates metrics
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from .types import (
    BaseEvent,
    EntityCreatedEvent,
    EntityModifiedEvent,
    DependencyDiscoveredEvent,
    DependencyRemovedEvent,
    CircularDependencyDetectedEvent,
    FlowExecutionCompletedEvent,
    FailureDetectedEvent,
    ImpactChainCalculatedEvent,
    LifecycleTransitionEvent,
)

logger = logging.getLogger(__name__)


class DependencyAnalyzerHandler:
    """Analyzes dependency events: validates, detects cycles, updates graph.

    Listens for:
    - DependencyDiscoveredEvent: Creates edge in dependency graph
    - DependencyRemovedEvent: Removes edge from dependency graph

    Performs:
    - Circular dependency detection
    - Publishes CircularDependencyDetectedEvent if cycle found
    """

    def __init__(self, graph_repo: Any = None, event_bus: Any = None):
        """Initialize the dependency analyzer.

        Args:
            graph_repo: Repository for dependency graph operations
            event_bus: Event bus for publishing detected events
        """
        self._graph_repo = graph_repo
        self._event_bus = event_bus

    async def handle(self, event: BaseEvent) -> None:
        """Route event to appropriate handler.

        Args:
            event: The event to handle
        """
        if isinstance(event, DependencyDiscoveredEvent):
            await self._handle_dependency_discovered(event)
        elif isinstance(event, DependencyRemovedEvent):
            await self._handle_dependency_removed(event)

    async def _handle_dependency_discovered(
        self, event: DependencyDiscoveredEvent
    ) -> None:
        """Process a newly discovered dependency.

        Args:
            event: DependencyDiscoveredEvent to process
        """
        logger.info(
            "Dependency discovered: %s (%s) -> %s (%s), type=%s, severity=%s",
            event.source_id,
            event.source_type,
            event.target_id,
            event.target_type,
            event.dependency_type,
            event.severity,
        )

        if self._graph_repo:
            # Create dependency in graph
            await self._graph_repo.create_dependency(
                source_id=event.source_id,
                target_id=event.target_id,
                dep_type=event.dependency_type,
                severity=event.severity,
            )

            # Check for circular dependencies
            circular = await self._graph_repo.detect_circular_dependencies()
            if circular and self._event_bus:
                for cycle_info in circular:
                    cycle_nodes = cycle_info.get("circular_dependency", {}).get(
                        "cycle_nodes", []
                    )
                    cycle_ids = [str(n.get("id", "")) for n in cycle_nodes]
                    cycle_event = CircularDependencyDetectedEvent(
                        source_id=event.source_id,
                        source_type=event.source_type,
                        cycle=cycle_ids,
                        correlation_id=event.correlation_id,
                    )
                    await self._event_bus.publish(cycle_event)

    async def _handle_dependency_removed(
        self, event: DependencyRemovedEvent
    ) -> None:
        """Process a removed dependency.

        Args:
            event: DependencyRemovedEvent to process
        """
        logger.info(
            "Dependency removed: %s -> %s, reason=%s",
            event.source_id,
            event.target_id,
            event.reason,
        )


class ImpactChainHandler:
    """Calculates blast radius when dependencies change.

    Listens for:
    - DependencyDiscoveredEvent: Recalculates impact for source
    - FailureDetectedEvent: Calculates failure propagation

    Performs:
    - Blast radius calculation
    - Publishes ImpactChainCalculatedEvent
    """

    def __init__(self, graph_repo: Any = None, event_bus: Any = None):
        """Initialize the impact chain calculator.

        Args:
            graph_repo: Repository for dependency graph operations
            event_bus: Event bus for publishing impact events
        """
        self._graph_repo = graph_repo
        self._event_bus = event_bus

    async def handle(self, event: BaseEvent) -> None:
        """Route event to appropriate handler.

        Args:
            event: The event to handle
        """
        if isinstance(event, DependencyDiscoveredEvent):
            await self._recalculate_impact(event.source_id)
        elif isinstance(event, FailureDetectedEvent):
            await self._calculate_failure_impact(event)

    async def _recalculate_impact(self, service_id: str) -> None:
        """Recalculate blast radius for a service.

        Args:
            service_id: ID of the service to analyze
        """
        if not self._graph_repo:
            return

        result = await self._graph_repo.calculate_blast_radius(service_id)
        if result and self._event_bus:
            impact_event = ImpactChainCalculatedEvent(
                source_id=service_id,
                root_cause_id=service_id,
                blast_radius=result.get("blast_radius", 0),
                affected_services=result.get("affected_services", []),
            )
            await self._event_bus.publish(impact_event)

    async def _calculate_failure_impact(self, event: FailureDetectedEvent) -> None:
        """Calculate impact of a detected failure.

        Args:
            event: FailureDetectedEvent to analyze
        """
        if not self._graph_repo:
            return

        result = await self._graph_repo.simulate_failure(event.source_id)
        logger.warning(
            "Failure impact calculated: service=%s, total_impact=%d",
            event.source_id,
            result.get("total_impact", 0),
        )


class LifecycleHandler:
    """Tracks lifecycle state transitions and emits audit logs.

    Listens for:
    - EntityCreatedEvent: Logs entity creation
    - EntityModifiedEvent: Logs entity modification
    - LifecycleTransitionEvent: Logs state transitions

    Performs:
    - Persists audit log entries to repository
    """

    def __init__(self, mongo_repo: Any = None):
        """Initialize the lifecycle handler.

        Args:
            mongo_repo: Repository for persisting audit logs
        """
        self._mongo_repo = mongo_repo

    async def handle(self, event: BaseEvent) -> None:
        """Route event to appropriate handler.

        Args:
            event: The event to handle
        """
        if isinstance(event, EntityCreatedEvent):
            await self._handle_entity_created(event)
        elif isinstance(event, EntityModifiedEvent):
            await self._handle_entity_modified(event)
        elif isinstance(event, LifecycleTransitionEvent):
            await self._handle_lifecycle_transition(event)

    async def _handle_entity_created(self, event: EntityCreatedEvent) -> None:
        """Log entity creation.

        Args:
            event: EntityCreatedEvent to process
        """
        logger.info("Entity created: %s (%s)", event.source_id, event.source_type)
        if self._mongo_repo:
            await self._mongo_repo.log_entity_change(
                entity_id=event.source_id,
                entity_type=event.source_type,
                action="created",
                actor=event.metadata.get("author", "system"),
                new_state=event.entity_data,
            )

    async def _handle_entity_modified(self, event: EntityModifiedEvent) -> None:
        """Log entity modification.

        Args:
            event: EntityModifiedEvent to process
        """
        logger.info("Entity modified: %s (%s)", event.source_id, event.source_type)
        if self._mongo_repo:
            await self._mongo_repo.log_entity_change(
                entity_id=event.source_id,
                entity_type=event.source_type,
                action="modified",
                actor=event.metadata.get("author", "system"),
                previous_state=event.previous_state,
                new_state=event.changes,
            )

    async def _handle_lifecycle_transition(
        self, event: LifecycleTransitionEvent
    ) -> None:
        """Log lifecycle state transition.

        Args:
            event: LifecycleTransitionEvent to process
        """
        logger.info(
            "Lifecycle transition: %s (%s) %s -> %s, reason=%s",
            event.source_id,
            event.source_type,
            event.from_state,
            event.to_state,
            event.reason,
        )
        if self._mongo_repo:
            await self._mongo_repo.log_entity_change(
                entity_id=event.source_id,
                entity_type=event.source_type,
                action=f"lifecycle_{event.to_state}",
                actor=event.author,
                metadata={"from_state": event.from_state, "reason": event.reason},
            )


class FlowTracerHandler:
    """Stores flow execution traces and updates performance metrics.

    Listens for:
    - FlowExecutionCompletedEvent: Records execution trace

    Performs:
    - Persists execution trace to repository
    - Updates performance metrics
    """

    def __init__(self, mongo_repo: Any = None):
        """Initialize the flow tracer.

        Args:
            mongo_repo: Repository for persisting execution traces
        """
        self._mongo_repo = mongo_repo

    async def handle(self, event: BaseEvent) -> None:
        """Route event to appropriate handler.

        Args:
            event: The event to handle
        """
        if isinstance(event, FlowExecutionCompletedEvent):
            await self._handle_flow_completed(event)

    async def _handle_flow_completed(self, event: FlowExecutionCompletedEvent) -> None:
        """Record a completed flow execution.

        Args:
            event: FlowExecutionCompletedEvent to process
        """
        logger.info(
            "Flow execution completed: flow=%s, execution=%s, status=%s, duration=%dms",
            event.flow_id,
            event.execution_id,
            event.status,
            event.total_duration_ms,
        )
        if self._mongo_repo:
            await self._mongo_repo.record_execution(
                flow_id=event.flow_id,
                execution_id=event.execution_id,
                steps=event.steps,
                status=event.status,
                total_duration_ms=event.total_duration_ms,
            )


class EventHandlerRegistry:
    """Central registry that wires handlers to the event bus.

    Manages subscription of all event handlers and provides
    a single point for handler lifecycle management.
    """

    def __init__(self, event_bus: Any):
        """Initialize the event handler registry.

        Args:
            event_bus: The event bus to subscribe handlers to
        """
        self._event_bus = event_bus
        self._handlers: list[Any] = []

    async def register_all(
        self,
        graph_repo: Any = None,
        audit_repo: Any = None,
        trace_repo: Any = None,
    ) -> None:
        """Register all handlers with the event bus.

        Args:
            graph_repo: Repository for dependency graph operations
            audit_repo: Repository for audit logs
            trace_repo: Repository for execution traces
        """
        # Dependency analyzer
        dep_handler = DependencyAnalyzerHandler(graph_repo, self._event_bus)
        await self._event_bus.subscribe("dependency.discovered", dep_handler.handle)
        await self._event_bus.subscribe("dependency.removed", dep_handler.handle)
        self._handlers.append(dep_handler)

        # Impact chain calculator
        impact_handler = ImpactChainHandler(graph_repo, self._event_bus)
        await self._event_bus.subscribe("dependency.discovered", impact_handler.handle)
        await self._event_bus.subscribe("failure.detected", impact_handler.handle)
        self._handlers.append(impact_handler)

        # Lifecycle tracker
        lifecycle_handler = LifecycleHandler(audit_repo)
        await self._event_bus.subscribe("entity.created", lifecycle_handler.handle)
        await self._event_bus.subscribe("entity.modified", lifecycle_handler.handle)
        await self._event_bus.subscribe("lifecycle.transition", lifecycle_handler.handle)
        self._handlers.append(lifecycle_handler)

        # Flow tracer
        flow_handler = FlowTracerHandler(trace_repo)
        await self._event_bus.subscribe("flow.execution_completed", flow_handler.handle)
        self._handlers.append(flow_handler)

        logger.info("All event handlers registered (%d handlers)", len(self._handlers))
