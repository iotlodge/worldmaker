"""Real-time dependency resolution engine.

Resolves dependency graphs for agentic consumers.
Caches hot paths for performance, invalidates on events.
"""
from __future__ import annotations
import asyncio
import logging
import time
from collections import defaultdict
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DependencyResolver:
    """Real-time dependency resolution with caching."""

    def __init__(self, graph_repo: Any = None, cache_ttl_seconds: int = 60):
        self._graph_repo = graph_repo
        self._cache: dict[str, tuple[float, Any]] = {}
        self._cache_ttl = cache_ttl_seconds
        self._resolution_count = 0
        self._cache_hits = 0

    async def resolve(
        self, service_id: str, depth: str = "direct"
    ) -> dict[str, Any]:
        """Resolve dependencies for a service.

        Args:
            service_id: The service to resolve.
            depth: 'direct', 'transitive', or 'blast-radius'
        """
        cache_key = f"{service_id}:{depth}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            self._cache_hits += 1
            return cached

        self._resolution_count += 1

        if not self._graph_repo:
            return {"service_id": service_id, "error": "graph_repo not configured"}

        if depth == "direct":
            result = await self._graph_repo.get_direct_dependencies(service_id)
        elif depth == "transitive":
            deps = await self._graph_repo.get_transitive_dependencies(service_id)
            result = {"service_id": service_id, "transitive_dependencies": deps}
        elif depth == "blast-radius":
            result = await self._graph_repo.calculate_blast_radius(service_id)
        else:
            result = await self._graph_repo.get_direct_dependencies(service_id)

        self._set_cached(cache_key, result)
        return result

    async def resolve_full_context(self, service_id: str) -> dict[str, Any]:
        """Resolve complete context for agentic consumption."""
        if not self._graph_repo:
            return {"service_id": service_id, "error": "graph_repo not configured"}

        cache_key = f"{service_id}:full"
        cached = self._get_cached(cache_key)
        if cached is not None:
            self._cache_hits += 1
            return cached

        self._resolution_count += 1
        result = await self._graph_repo.get_full_service_context(service_id)
        self._set_cached(cache_key, result)
        return result

    def invalidate(self, service_id: str) -> None:
        """Invalidate cache for a service (called on dependency changes)."""
        keys_to_remove = [k for k in self._cache if k.startswith(f"{service_id}:")]
        for key in keys_to_remove:
            del self._cache[key]
        logger.debug("Cache invalidated for service %s (%d entries)", service_id, len(keys_to_remove))

    def invalidate_all(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
        logger.info("Dependency cache fully invalidated")

    def _get_cached(self, key: str) -> Any | None:
        if key in self._cache:
            timestamp, value = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return value
            del self._cache[key]
        return None

    def _set_cached(self, key: str, value: Any) -> None:
        self._cache[key] = (time.time(), value)

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "total_resolutions": self._resolution_count,
            "cache_hits": self._cache_hits,
            "cache_size": len(self._cache),
            "hit_rate": self._cache_hits / max(self._resolution_count + self._cache_hits, 1),
        }
