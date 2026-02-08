"""Processing pipelines for WorldMaker ecosystem operations.

Orchestrates multi-step workflows: generation, loading, analysis.
"""
from __future__ import annotations
import asyncio
import json
import logging
import time
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)


class Pipeline:
    """Async processing pipeline with step tracking."""

    def __init__(self, name: str):
        self.name = name
        self._steps: list[tuple[str, Callable[..., Awaitable[Any]]]] = []
        self._results: dict[str, Any] = {}
        self._timings: dict[str, float] = {}

    def add_step(self, name: str, fn: Callable[..., Awaitable[Any]]) -> "Pipeline":
        self._steps.append((name, fn))
        return self

    async def execute(self, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute all pipeline steps sequentially."""
        ctx = dict(context or {})
        total_start = time.time()

        logger.info("Pipeline '%s' starting with %d steps", self.name, len(self._steps))

        for step_name, step_fn in self._steps:
            step_start = time.time()
            logger.info("  Step '%s' starting...", step_name)

            try:
                result = await step_fn(ctx)
                self._results[step_name] = result
                if isinstance(result, dict):
                    ctx.update(result)
            except Exception as e:
                logger.error("  Step '%s' FAILED: %s", step_name, e)
                self._results[step_name] = {"error": str(e)}
                raise

            elapsed = time.time() - step_start
            self._timings[step_name] = elapsed
            logger.info("  Step '%s' completed in %.2fs", step_name, elapsed)

        total_elapsed = time.time() - total_start
        logger.info("Pipeline '%s' completed in %.2fs", self.name, total_elapsed)

        return {
            "pipeline": self.name,
            "total_time_seconds": round(total_elapsed, 3),
            "steps": self._timings,
            "results": self._results,
        }


class EcosystemPipeline:
    """Pre-built pipeline for ecosystem generation and loading."""

    def __init__(self, unified_repo: Any = None, event_bus: Any = None):
        self._unified_repo = unified_repo
        self._event_bus = event_bus

    async def generate_and_load(
        self, seed: int = 42, size: str = "small"
    ) -> dict[str, Any]:
        """Generate synthetic ecosystem and load into all stores."""
        from ..generators.ecosystem import generate_ecosystem

        pipeline = Pipeline("generate-and-load")

        # Step 1: Generate ecosystem data
        async def generate(ctx: dict) -> dict:
            ecosystem = generate_ecosystem(seed=seed, size=size)
            return {"ecosystem": ecosystem}

        # Step 2: Load into graph store (Neo4j)
        async def load_graph(ctx: dict) -> dict:
            ecosystem = ctx.get("ecosystem", {})
            loaded = {"services": 0, "dependencies": 0, "platforms": 0}

            if self._unified_repo and self._unified_repo._graph:
                graph = self._unified_repo._graph

                # Load platforms
                for p in ecosystem.get("platforms", []):
                    await graph.upsert_platform(
                        id=p["id"], name=p["name"],
                        status=p.get("status", "active"),
                        category=p.get("category", ""),
                        owner=p.get("owner", ""),
                    )
                    loaded["platforms"] += 1

                # Load services
                for s in ecosystem.get("services", []):
                    crit = "medium"
                    for cr in ecosystem.get("criticality_ratings", []):
                        if cr["entity_id"] == s["id"]:
                            crit = cr["criticality"]
                            break

                    await graph.upsert_service(
                        id=s["id"], name=s["name"],
                        status=s.get("status", "active"),
                        service_type=s.get("service_type", "rest"),
                        criticality=crit,
                        owner=s.get("owner", ""),
                    )
                    loaded["services"] += 1

                    # Link to platform
                    if s.get("platform_id"):
                        await graph.create_hosted_by(s["id"], s["platform_id"])

                # Load dependencies
                for d in ecosystem.get("dependencies", []):
                    await graph.create_dependency(
                        source_id=d["source_id"],
                        target_id=d["target_id"],
                        dep_type=d.get("dependency_type", "runtime"),
                        severity=d.get("severity", "medium"),
                        is_circular=d.get("is_circular", False),
                    )
                    loaded["dependencies"] += 1

            return {"graph_loaded": loaded}

        # Step 3: Emit events
        async def emit_events(ctx: dict) -> dict:
            ecosystem = ctx.get("ecosystem", {})
            event_count = 0

            if self._event_bus:
                from ..events.types import EntityCreatedEvent
                for s in ecosystem.get("services", []):
                    event = EntityCreatedEvent(
                        source_id=s["id"],
                        source_type="service",
                        entity_data=s,
                    )
                    await self._event_bus.publish(event)
                    event_count += 1

            return {"events_emitted": event_count}

        pipeline.add_step("generate", generate)
        pipeline.add_step("load_graph", load_graph)
        pipeline.add_step("emit_events", emit_events)

        return await pipeline.execute()
