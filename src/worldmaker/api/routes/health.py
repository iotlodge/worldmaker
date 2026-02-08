"""Health check endpoints."""
from __future__ import annotations

try:
    from fastapi import APIRouter, Depends
    from typing import Any

    from worldmaker.api.deps import get_memory_store
    from worldmaker.db.memory import InMemoryStore

    router = APIRouter()

    @router.get("/health")
    async def health_check() -> dict[str, Any]:
        """Check overall API health."""
        return {"status": "healthy", "service": "worldmaker", "version": "0.1.0"}

    @router.get("/health/stores")
    async def store_health(
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Check data store status and entity counts."""
        overview = store.get_overview()
        return {
            "store_type": "in_memory",
            "status": "connected",
            "entity_counts": overview["entity_counts"],
            "total_entities": overview["total_entities"],
            "total_dependencies": overview["total_dependencies"],
            "circular_dependencies": overview["circular_dependencies"],
            "audit_log_entries": overview["audit_log_entries"],
            "traces": overview["traces"],
            "spans": overview["spans"],
        }

except ImportError:
    router = None
