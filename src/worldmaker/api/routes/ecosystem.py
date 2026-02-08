"""Ecosystem management endpoints."""
from __future__ import annotations

try:
    from fastapi import APIRouter, Depends, Query
    from typing import Any, Optional

    from worldmaker.api.deps import get_memory_store
    from worldmaker.db.memory import InMemoryStore

    router = APIRouter()

    @router.get("/ecosystem/overview")
    async def get_ecosystem_overview(
        include_stats: bool = Query(True, description="Include statistics"),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get high-level overview of the ecosystem.

        Returns summary statistics about all entity types, dependencies, and flows.
        """
        overview = store.get_overview()
        counts = overview["entity_counts"]

        services_total = counts.get("service", 0)
        active_services = store.count("service", {"status": "active"})
        degraded_services = store.count("service", {"status": "degraded"})

        flows_total = counts.get("flow", 0)
        active_flows = store.count("flow", {"status": "active"})

        result: dict[str, Any] = {
            "status": "ok",
            "ecosystem": {
                "products": {"total": counts.get("product", 0)},
                "platforms": {"total": counts.get("platform", 0)},
                "capabilities": {"total": counts.get("capability", 0)},
                "services": {
                    "total": services_total,
                    "active": active_services,
                    "degraded": degraded_services,
                },
                "microservices": {"total": counts.get("microservice", 0)},
                "flows": {"total": flows_total, "active": active_flows},
                "dependencies": {
                    "total": overview["total_dependencies"],
                    "circular": overview["circular_dependencies"],
                },
                "environments": {"total": counts.get("environment", 0)},
            },
            "total_entities": overview["total_entities"],
        }

        if include_stats:
            avg_deps = 0.0
            if services_total > 0:
                avg_deps = round(overview["total_dependencies"] / services_total, 2)

            result["statistics"] = {
                "avg_dependencies_per_service": avg_deps,
                "circular_dependency_count": overview["circular_dependencies"],
                "audit_log_entries": overview["audit_log_entries"],
                "traces_generated": overview["traces"],
                "spans_generated": overview["spans"],
            }

        return result

    @router.get("/ecosystem/health")
    async def get_ecosystem_health(
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get ecosystem health status with real data."""
        overview = store.get_overview()
        counts = overview["entity_counts"]

        total_services = counts.get("service", 0)
        degraded = store.count("service", {"status": "degraded"})
        offline = store.count("service", {"status": "offline"})

        if total_services == 0:
            health_score = 100
            overall = "empty"
        else:
            healthy_pct = ((total_services - degraded - offline) / total_services) * 100
            health_score = round(healthy_pct, 1)
            if health_score >= 95:
                overall = "healthy"
            elif health_score >= 80:
                overall = "degraded"
            else:
                overall = "critical"

        critical_issues: list[str] = []
        if overview["circular_dependencies"] > 0:
            critical_issues.append(
                f"{overview['circular_dependencies']} circular dependencies detected"
            )
        if offline > 0:
            critical_issues.append(f"{offline} services offline")

        warnings: list[str] = []
        if degraded > 0:
            warnings.append(f"{degraded} services in degraded state")

        return {
            "overall_health": overall,
            "health_score": health_score,
            "total_services": total_services,
            "critical_issues": critical_issues,
            "warnings": warnings,
        }

    @router.get("/ecosystem/entities/{entity_type}")
    async def list_entities_by_type(
        entity_type: str,
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """List entities of any type. Useful for browsing the full data model."""
        entities = store.get_all(entity_type, limit=limit, offset=offset)
        total = store.count(entity_type)
        return {
            "entity_type": entity_type,
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": entities,
        }

    @router.get("/ecosystem/search")
    async def search_ecosystem(
        q: str = Query(..., min_length=1, description="Search query"),
        entity_type: str = Query("service", description="Entity type to search"),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Full-text search across entities."""
        results = store.search(entity_type, q)
        return {
            "query": q,
            "entity_type": entity_type,
            "total": len(results),
            "results": results,
        }

    @router.get("/ecosystem/audit")
    async def get_audit_log(
        entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
        entity_type: Optional[str] = Query(None, description="Filter by entity type"),
        limit: int = Query(100, ge=1, le=1000),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get the audit log for entity changes."""
        entries = store.get_audit_log(
            entity_id=entity_id,
            entity_type=entity_type,
            limit=limit,
        )
        return {
            "total": len(entries),
            "limit": limit,
            "entries": entries,
        }

except ImportError:
    router = None
