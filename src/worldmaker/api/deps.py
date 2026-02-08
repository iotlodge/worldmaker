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
_code_repo_mgr: Any = None


def get_memory_store() -> InMemoryStore:
    """Get the shared InMemoryStore instance."""
    return get_store()


def get_trace_engine() -> TraceEngine:
    """Get the shared TraceEngine instance (backed by the store)."""
    global _trace_engine
    if _trace_engine is None:
        _trace_engine = TraceEngine(store=get_store(), rng_seed=42)
    return _trace_engine


def get_code_repo_manager():
    """Get the shared CodeRepoManager singleton (ensures consistent path)."""
    global _code_repo_mgr
    if _code_repo_mgr is None:
        from worldmaker.codegen import CodeRepoManager
        from worldmaker.config import settings
        _code_repo_mgr = CodeRepoManager(base_path=settings.CODE_REPO_PATH)
    return _code_repo_mgr


def reset_all() -> None:
    """Reset generated entities and code repos; core platforms persist."""
    global _trace_engine
    store = get_store()
    store.clear_layer("generated")
    _trace_engine = TraceEngine(store=store, rng_seed=42)

    # Clear generated code repos
    try:
        mgr = get_code_repo_manager()
        mgr.clear_all()
    except Exception:
        pass  # Non-fatal if repos dir doesn't exist
