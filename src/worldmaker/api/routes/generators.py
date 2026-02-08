"""Synthetic ecosystem generation endpoints."""
from __future__ import annotations

try:
    from fastapi import APIRouter, Depends, Query
    from typing import Any

    from worldmaker.api.deps import get_memory_store, get_trace_engine
    from worldmaker.db.memory import InMemoryStore
    from worldmaker.engine.trace import TraceEngine
    from worldmaker.generators.ecosystem import generate_ecosystem

    router = APIRouter()

    @router.post("/generate")
    async def generate_and_load_ecosystem(
        seed: int = Query(42, description="Random seed for reproducibility"),
        size: str = Query("small", pattern="^(small|medium|large)$"),
        execute_flows: bool = Query(False,
            description="Execute all flows and generate traces after generation"),
        store: InMemoryStore = Depends(get_memory_store),
        engine: TraceEngine = Depends(get_trace_engine),
    ) -> dict[str, Any]:
        """Generate a synthetic ecosystem and load it into the store.

        Creates a complete enterprise digital ecosystem with all entity types,
        dependencies, flows, and risk metadata. Optionally executes all flows
        to generate OTel traces.
        """
        ecosystem = generate_ecosystem(seed=seed, size=size)
        loaded = store.load_ecosystem(ecosystem)

        result: dict[str, Any] = {
            "status": "completed",
            "seed": seed,
            "size": size,
            "summary": ecosystem.get("summary", {}),
            "loaded": loaded,
        }

        if execute_flows:
            traces = engine.execute_all_flows(environment="prod")
            result["traces_generated"] = len(traces)
            result["total_spans"] = sum(t.get("span_count", 0) for t in traces)

        return result

    @router.get("/generate/preview")
    async def preview_ecosystem(
        seed: int = Query(42, description="Random seed"),
        size: str = Query("small", pattern="^(small|medium|large)$"),
    ) -> dict[str, Any]:
        """Preview what would be generated without loading into the store."""
        ecosystem = generate_ecosystem(seed=seed, size=size)
        summary = ecosystem.get("summary", {})
        total = sum(summary.values()) if summary else 0

        return {
            "seed": seed,
            "size": size,
            "preview": {
                "total_entities": total,
                "breakdown": summary,
            },
        }

    @router.post("/generate/reset")
    async def reset_store_endpoint(
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Clear generated data; core platforms persist."""
        from worldmaker.api.deps import reset_all
        reset_all()
        return {
            "status": "reset",
            "message": "Generated entities cleared; core platforms preserved",
            "core_preserved": True,
        }

except ImportError:
    router = None
