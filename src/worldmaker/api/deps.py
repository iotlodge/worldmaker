"""FastAPI dependency injection for WorldMaker API.

Provides shared instances of InMemoryStore and TraceEngine
to all route handlers via FastAPI's Depends() system.
"""
from __future__ import annotations
from typing import Any

from worldmaker.db.memory import InMemoryStore, get_store, reset_store
from worldmaker.engine.trace import TraceEngine


# Singletons
_trace_engine: TraceEngine | None = None


def get_memory_store() -> InMemoryStore:
    """Get the shared InMemoryStore instance."""
    return get_store()


def get_trace_engine() -> TraceEngine:
    """Get the shared TraceEngine instance (backed by the store)."""
    global _trace_engine
    if _trace_engine is None:
        _trace_engine = TraceEngine(store=get_store(), rng_seed=42)
    return _trace_engine


def reset_all() -> None:
    """Reset all singletons (for testing)."""
    global _trace_engine
    reset_store()
    _trace_engine = None
