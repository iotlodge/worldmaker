"""Pytest configuration and fixtures for WorldMaker tests."""
from __future__ import annotations

import pytest
from typing import Any

from worldmaker.db.memory import InMemoryStore, reset_store
from worldmaker.engine.trace import TraceEngine
from worldmaker.generators.ecosystem import generate_ecosystem


@pytest.fixture
def store() -> InMemoryStore:
    """Provide a clean in-memory store for each test."""
    return reset_store()


@pytest.fixture
def seeded_store(store: InMemoryStore) -> InMemoryStore:
    """Provide a store pre-loaded with a small generated ecosystem."""
    eco = generate_ecosystem(seed=42, size="small")
    store.load_ecosystem(eco)
    return store


@pytest.fixture
def trace_engine(store: InMemoryStore) -> TraceEngine:
    """Provide a TraceEngine backed by the test store."""
    return TraceEngine(store=store, rng_seed=42)


@pytest.fixture
def seeded_engine(seeded_store: InMemoryStore) -> TraceEngine:
    """Provide a TraceEngine with a pre-loaded ecosystem."""
    return TraceEngine(store=seeded_store, rng_seed=42)


@pytest.fixture
def small_ecosystem() -> dict[str, Any]:
    """Generate and return a small ecosystem dict."""
    return generate_ecosystem(seed=42, size="small")


@pytest.fixture
def medium_ecosystem() -> dict[str, Any]:
    """Generate and return a medium ecosystem dict."""
    return generate_ecosystem(seed=42, size="medium")
