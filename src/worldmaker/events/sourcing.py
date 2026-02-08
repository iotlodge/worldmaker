"""Event sourcing patterns for WorldMaker.

Provides event replay, state reconstruction, and event store abstractions
that work across both in-memory and Kafka backends.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable
from uuid import UUID

from .types import BaseEvent, EVENT_REGISTRY

logger = logging.getLogger(__name__)


class EventStore:
    """In-memory event store for event sourcing patterns.

    Stores events per aggregate (entity) and supports replaying
    events to reconstruct state at any point in time.

    Attributes:
        _events: Dict mapping aggregate_id -> list of events
        _global_sequence: Complete timeline of all events
        _projections: Named projection reducers
    """

    def __init__(self):
        """Initialize an empty event store."""
        self._events: dict[str, list[BaseEvent]] = defaultdict(list)
        self._global_sequence: list[BaseEvent] = []
        self._projections: dict[str, Callable[[dict[str, Any], BaseEvent], dict[str, Any]]] = {}

    async def append(self, aggregate_id: str, event: BaseEvent) -> None:
        """Append an event to an aggregate's event stream.

        Args:
            aggregate_id: ID of the aggregate (entity) receiving the event
            event: The event to append
        """
        self._events[aggregate_id].append(event)
        self._global_sequence.append(event)

    async def get_events(
        self,
        aggregate_id: str,
        since: datetime | None = None,
        event_type: str | None = None,
    ) -> list[BaseEvent]:
        """Get events for an aggregate, optionally filtered.

        Args:
            aggregate_id: ID of the aggregate to retrieve events for
            since: Only return events at or after this timestamp
            event_type: Only return events of this type

        Returns:
            List of matching BaseEvent instances
        """
        events = self._events.get(aggregate_id, [])
        if since:
            events = [e for e in events if e.timestamp >= since]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events

    async def replay(
        self,
        aggregate_id: str,
        initial_state: dict[str, Any] | None = None,
        reducer: Callable[[dict[str, Any], BaseEvent], dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Replay all events for an aggregate to reconstruct state.

        Applies events in order starting from initial_state using the reducer
        function to compute the new state after each event.

        Args:
            aggregate_id: The entity to reconstruct.
            initial_state: Starting state (empty dict if None).
            reducer: Function(state, event) -> new_state.
                     Uses default reducer if not provided.

        Returns:
            The reconstructed state after applying all events
        """
        state = dict(initial_state or {})
        events = self._events.get(aggregate_id, [])
        reduce_fn = reducer or self._default_reducer

        for event in events:
            state = reduce_fn(state, event)

        return state

    def register_projection(
        self, name: str, reducer: Callable[[dict[str, Any], BaseEvent], dict[str, Any]]
    ) -> None:
        """Register a named projection (materialized view) reducer.

        Projections are reducers that compute aggregate state across
        multiple aggregates by processing the global event stream.

        Args:
            name: Name of the projection
            reducer: Async function(state, event) -> new_state
        """
        self._projections[name] = reducer

    async def project(self, name: str) -> dict[str, Any]:
        """Run a projection across all events.

        Args:
            name: Name of the registered projection to run

        Returns:
            The computed projection state

        Raises:
            ValueError: If projection name is not registered
        """
        reducer = self._projections.get(name)
        if not reducer:
            raise ValueError(f"Unknown projection: {name}")

        state: dict[str, Any] = {}
        for event in self._global_sequence:
            state = reducer(state, event)
        return state

    @property
    def total_events(self) -> int:
        """Total number of events in the store."""
        return len(self._global_sequence)

    @property
    def aggregate_count(self) -> int:
        """Number of distinct aggregates with events."""
        return len(self._events)

    @staticmethod
    def _default_reducer(
        state: dict[str, Any], event: BaseEvent
    ) -> dict[str, Any]:
        """Default state reducer — merges event data into state.

        This is a simple reducer that:
        - Tracks the last event type
        - Updates timestamp
        - Increments event count
        - Merges entity data from creation/modification events
        - Updates status from lifecycle transitions

        Args:
            state: Current aggregate state
            event: Event to apply

        Returns:
            New state after applying the event
        """
        new_state = dict(state)
        new_state["last_event_type"] = event.event_type
        new_state["last_updated"] = event.timestamp.isoformat()
        new_state["event_count"] = state.get("event_count", 0) + 1

        # Merge entity data from creation events
        if hasattr(event, "entity_data") and event.entity_data:
            new_state.update(event.entity_data)

        # Apply changes from modification events
        if hasattr(event, "changes") and event.changes:
            new_state.update(event.changes)

        # Track lifecycle transitions
        if hasattr(event, "to_state") and event.to_state:
            new_state["status"] = event.to_state

        return new_state
