"""Event bus module for WorldMaker.

Provides an event-driven architecture for asynchronous processing of
ecosystem state mutations, dependency changes, flow executions, and
lifecycle transitions.

Key exports:
- BaseEvent: Base class for all events
- Event types: EntityCreatedEvent, DependencyDiscoveredEvent, etc.
- EventBus: Abstract interface
- InMemoryEventBus: Development/testing backend
- KafkaEventBus: Production backend
- EventHandlerRegistry: Central handler registration
- EventStore: Event sourcing patterns
"""

from .types import (
    BaseEvent,
    EventCategory,
    EntityCreatedEvent,
    EntityModifiedEvent,
    EntityDeprecatedEvent,
    DependencyDiscoveredEvent,
    DependencyRemovedEvent,
    CircularDependencyDetectedEvent,
    FlowExecutionStartedEvent,
    FlowExecutionCompletedEvent,
    LifecycleTransitionEvent,
    FailureDetectedEvent,
    ImpactChainCalculatedEvent,
    EVENT_REGISTRY,
)

from .bus import (
    EventBus,
    InMemoryEventBus,
    KafkaEventBus,
    create_event_bus,
    EventHandler,
)

from .handlers import (
    DependencyAnalyzerHandler,
    ImpactChainHandler,
    LifecycleHandler,
    FlowTracerHandler,
    EventHandlerRegistry,
)

from .sourcing import (
    EventStore,
)

__all__ = [
    # Types
    "BaseEvent",
    "EventCategory",
    "EntityCreatedEvent",
    "EntityModifiedEvent",
    "EntityDeprecatedEvent",
    "DependencyDiscoveredEvent",
    "DependencyRemovedEvent",
    "CircularDependencyDetectedEvent",
    "FlowExecutionStartedEvent",
    "FlowExecutionCompletedEvent",
    "LifecycleTransitionEvent",
    "FailureDetectedEvent",
    "ImpactChainCalculatedEvent",
    "EVENT_REGISTRY",
    # Bus
    "EventBus",
    "InMemoryEventBus",
    "KafkaEventBus",
    "create_event_bus",
    "EventHandler",
    # Handlers
    "DependencyAnalyzerHandler",
    "ImpactChainHandler",
    "LifecycleHandler",
    "FlowTracerHandler",
    "EventHandlerRegistry",
    # Event sourcing
    "EventStore",
]
