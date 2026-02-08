"""Task scheduling for WorldMaker background jobs.

Uses Celery when available, falls back to asyncio for development.
"""
from __future__ import annotations
import asyncio
import logging
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)

try:
    from celery import Celery
    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False


class AsyncScheduler:
    """Simple async task scheduler for development (no Celery needed)."""

    def __init__(self):
        self._tasks: dict[str, Callable] = {}
        self._running_tasks: dict[str, asyncio.Task] = {}
        self._periodic_tasks: dict[str, dict[str, Any]] = {}
        self._running = False

    def register(self, name: str, fn: Callable[..., Awaitable[Any]]) -> None:
        self._tasks[name] = fn
        logger.debug("Task registered: %s", name)

    async def submit(self, name: str, **kwargs: Any) -> Any:
        fn = self._tasks.get(name)
        if not fn:
            raise ValueError(f"Unknown task: {name}")
        return await fn(**kwargs)

    async def submit_background(self, name: str, **kwargs: Any) -> str:
        fn = self._tasks.get(name)
        if not fn:
            raise ValueError(f"Unknown task: {name}")

        task_id = f"{name}-{id(kwargs)}"
        task = asyncio.create_task(fn(**kwargs))
        self._running_tasks[task_id] = task
        return task_id

    def register_periodic(
        self, name: str, fn: Callable[..., Awaitable[Any]], interval_seconds: int
    ) -> None:
        self._periodic_tasks[name] = {
            "fn": fn,
            "interval": interval_seconds,
        }

    async def start(self) -> None:
        self._running = True
        for name, config in self._periodic_tasks.items():
            task = asyncio.create_task(
                self._run_periodic(name, config["fn"], config["interval"])
            )
            self._running_tasks[f"periodic-{name}"] = task
        logger.info("Scheduler started with %d periodic tasks", len(self._periodic_tasks))

    async def stop(self) -> None:
        self._running = False
        for task_id, task in self._running_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._running_tasks.clear()
        logger.info("Scheduler stopped")

    async def _run_periodic(
        self, name: str, fn: Callable, interval: int
    ) -> None:
        while self._running:
            try:
                await fn()
            except Exception as e:
                logger.error("Periodic task '%s' failed: %s", name, e)
            await asyncio.sleep(interval)

    @property
    def task_count(self) -> int:
        return len(self._tasks)

    @property
    def running_count(self) -> int:
        return len(self._running_tasks)


def create_celery_app(
    broker_url: str = "redis://localhost:6379/0",
    result_backend: str = "redis://localhost:6379/1",
) -> Any:
    """Create Celery app if available."""
    if not HAS_CELERY:
        logger.warning("Celery not installed. Use AsyncScheduler for development.")
        return None

    app = Celery(
        "worldmaker",
        broker=broker_url,
        backend=result_backend,
    )
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_default_queue="worldmaker",
    )
    return app
