"""Event bus abstraction with pluggable backends.

InMemoryEventBus: For development and testing (asyncio.Queue)
KafkaEventBus: For production (aiokafka)
"""
from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable, Awaitable

from .types import BaseEvent

logger = logging.getLogger(__name__)

# Type alias for event handlers
EventHandler = Callable[[BaseEvent], Awaitable[None]]


class EventBus(ABC):
    """Abstract event bus interface.

    Defines the contract for event publishing and subscription
    that can be implemented by various backends.
    """

    @abstractmethod
    async def publish(self, event: BaseEvent) -> None:
        """Publish an event to the bus.

        Args:
            event: The event to publish
        """
        ...

    @abstractmethod
    async def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe a handler to an event type.

        Args:
            event_type: The event type to listen for, or "*" for all
            handler: Async function to call when event is published
        """
        ...

    @abstractmethod
    async def start(self) -> None:
        """Start the event bus."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Stop the event bus."""
        ...


class InMemoryEventBus(EventBus):
    """In-memory event bus using asyncio for development/testing.

    No external dependencies. Uses asyncio.Queue for async dispatch.
    Optionally runs a background processor or dispatches immediately.

    Attributes:
        max_queue_size: Maximum events in the queue
    """

    def __init__(self, max_queue_size: int = 10000):
        """Initialize the in-memory event bus.

        Args:
            max_queue_size: Maximum events that can be queued
        """
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._wildcard_handlers: list[EventHandler] = []
        self._queue: asyncio.Queue[BaseEvent] = asyncio.Queue(maxsize=max_queue_size)
        self._running = False
        self._processor_task: asyncio.Task[None] | None = None
        self._event_log: list[BaseEvent] = []
        self._max_log_size = 10000

    async def publish(self, event: BaseEvent) -> None:
        """Publish an event, storing in log and dispatching immediately or queueing.

        Args:
            event: Event to publish
        """
        self._event_log.append(event)
        if len(self._event_log) > self._max_log_size:
            self._event_log = self._event_log[-self._max_log_size:]

        if self._running:
            await self._queue.put(event)
        else:
            # Process immediately if not running background processor
            await self._dispatch(event)

    async def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe a handler to an event type.

        Args:
            event_type: Event type to listen for, or "*" for all events
            handler: Async callable to invoke when event is published
        """
        if event_type == "*":
            self._wildcard_handlers.append(handler)
        else:
            self._handlers[event_type].append(handler)
        logger.debug("Subscribed handler to '%s'", event_type)

    async def start(self) -> None:
        """Start the event bus background processor."""
        self._running = True
        self._processor_task = asyncio.create_task(self._process_events())
        logger.info("InMemory event bus started")

    async def stop(self) -> None:
        """Stop the event bus and cancel the processor."""
        self._running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        logger.info("InMemory event bus stopped")

    async def _process_events(self) -> None:
        """Background task that processes events from the queue."""
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._dispatch(event)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error processing event: %s", e)

    async def _dispatch(self, event: BaseEvent) -> None:
        """Dispatch an event to all registered handlers.

        Args:
            event: Event to dispatch
        """
        handlers = self._handlers.get(event.event_type, []) + self._wildcard_handlers
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error("Handler error for %s: %s", event.event_type, e)

    def get_event_log(
        self, event_type: str | None = None, limit: int = 100
    ) -> list[BaseEvent]:
        """Retrieve recent events (for testing/debugging).

        Args:
            event_type: Filter by event type, or None for all
            limit: Maximum number of events to return

        Returns:
            List of BaseEvent instances
        """
        events = self._event_log
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]

    @property
    def event_count(self) -> int:
        """Total number of events published to this bus."""
        return len(self._event_log)


class KafkaEventBus(EventBus):
    """Kafka-backed event bus for production.

    Publishes events to Kafka topics and consumes them asynchronously.
    Requires aiokafka to be installed.

    Attributes:
        bootstrap_servers: Kafka broker addresses
        group_id: Consumer group ID
    """

    def __init__(
        self, bootstrap_servers: str = "localhost:9092", group_id: str = "worldmaker"
    ):
        """Initialize Kafka event bus.

        Args:
            bootstrap_servers: Kafka broker addresses (comma-separated)
            group_id: Consumer group ID for subscriptions
        """
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        self._producer: Any = None
        self._consumer: Any = None
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._wildcard_handlers: list[EventHandler] = []
        self._running = False
        self._consumer_task: asyncio.Task[None] | None = None

    async def publish(self, event: BaseEvent) -> None:
        """Publish an event to Kafka.

        Topic name is derived from event_type (dots replaced with hyphens).

        Args:
            event: Event to publish

        Raises:
            RuntimeError: If producer not started
        """
        if not self._producer:
            raise RuntimeError("Kafka producer not started")

        topic = event.event_type.replace(".", "-")
        value = json.dumps(event.to_dict()).encode("utf-8")
        key = event.source_id.encode("utf-8") if event.source_id else None

        await self._producer.send_and_wait(topic, value=value, key=key)
        logger.debug("Published event %s to topic %s", event.event_id, topic)

    async def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe a handler to an event type.

        Args:
            event_type: Event type or "*" for all events
            handler: Async handler to invoke
        """
        if event_type == "*":
            self._wildcard_handlers.append(handler)
        else:
            self._handlers[event_type].append(handler)

    async def start(self) -> None:
        """Start the Kafka producer and consumer.

        Raises:
            RuntimeError: If aiokafka is not installed
        """
        try:
            from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
        except ImportError:
            raise RuntimeError(
                "aiokafka package not installed. Use InMemoryEventBus for development."
            )

        self._producer = AIOKafkaProducer(bootstrap_servers=self._bootstrap_servers)
        await self._producer.start()

        topics = [et.replace(".", "-") for et in self._handlers.keys()]
        if topics:
            self._consumer = AIOKafkaConsumer(
                *topics,
                bootstrap_servers=self._bootstrap_servers,
                group_id=self._group_id,
                auto_offset_reset="latest",
            )
            await self._consumer.start()
            self._running = True
            self._consumer_task = asyncio.create_task(self._consume_events())

        logger.info("Kafka event bus started: %s", self._bootstrap_servers)

    async def stop(self) -> None:
        """Stop the Kafka consumer and producer."""
        self._running = False
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
        if self._consumer:
            await self._consumer.stop()
        if self._producer:
            await self._producer.stop()
        logger.info("Kafka event bus stopped")

    async def _consume_events(self) -> None:
        """Background task that consumes and dispatches Kafka messages."""
        from .types import EVENT_REGISTRY

        while self._running:
            try:
                async for message in self._consumer:
                    data = json.loads(message.value.decode("utf-8"))
                    event_type = data.get("event_type", "")
                    event_class = EVENT_REGISTRY.get(event_type, BaseEvent)

                    # Reconstruct event from dictionary
                    event_kwargs = {
                        k: v
                        for k, v in data.items()
                        if k in event_class.__dataclass_fields__
                    }
                    event = event_class(**event_kwargs)

                    handlers = self._handlers.get(event_type, []) + self._wildcard_handlers
                    for handler in handlers:
                        try:
                            await handler(event)
                        except Exception as e:
                            logger.error("Kafka handler error: %s", e)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Kafka consumer error: %s", e)
                await asyncio.sleep(1)


def create_event_bus(backend: str = "memory", **kwargs: Any) -> EventBus:
    """Factory function to create the appropriate event bus.

    Args:
        backend: "memory" for InMemoryEventBus or "kafka" for KafkaEventBus
        **kwargs: Additional arguments to pass to the bus constructor

    Returns:
        An EventBus instance
    """
    if backend == "kafka":
        return KafkaEventBus(**kwargs)
    return InMemoryEventBus(**kwargs)
