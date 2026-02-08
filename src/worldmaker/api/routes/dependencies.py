"""Dependency analysis endpoints — graph queries, blast radius, circular detection."""
from __future__ import annotations

try:
    from fastapi import APIRouter, Depends, Path, Query, HTTPException, Body
    from typing import Any, Optional

    from worldmaker.api.deps import get_memory_store
    from worldmaker.db.memory import InMemoryStore

    router = APIRouter()

    @router.get("/services/{service_id}/dependencies")
    async def get_service_dependencies(
        service_id: str = Path(..., description="Service ID"),
        depth: str = Query("direct", pattern="^(direct|transitive|blast-radius)$"),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Resolve dependencies for a service.

        Depth levels:
        - direct: Only immediate dependencies
        - transitive: All reachable dependencies via BFS
        - blast-radius: Full impact analysis (who is affected if this goes down)
        """
        service = store.get("service", service_id)
        if not service:
            raise HTTPException(404, f"Service {service_id} not found")

        direct_deps = store.get_dependencies_of(service_id)
        direct_dependents = store.get_dependents_of(service_id)

        result: dict[str, Any] = {
            "service_id": service_id,
            "service_name": service.get("name", "unknown"),
            "depth": depth,
            "depends_on": direct_deps,
            "depended_on_by": direct_dependents,
        }

        if depth in ("transitive", "blast-radius"):
            transitive = store.get_transitive_dependencies(service_id)
            result["transitive_dependencies"] = transitive
            result["transitive_count"] = len(transitive)

        if depth == "blast-radius":
            blast = store.calculate_blast_radius(service_id)
            result["blast_radius"] = blast

        result["statistics"] = {
            "direct_dependency_count": len(direct_deps),
            "direct_dependent_count": len(direct_dependents),
            "total_count": (
                len(direct_deps) + len(direct_dependents) +
                (len(result.get("transitive_dependencies", [])))
            ),
        }

        return result

    @router.get("/dependencies/circular")
    async def get_circular_dependencies(
        limit: int = Query(100, ge=1, le=1000),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get all detected circular dependencies."""
        circular = store.detect_circular_dependencies()
        limited = circular[:limit]

        for dep in limited:
            src = store.get("service", dep.get("source_id", ""))
            tgt = store.get("service", dep.get("target_id", ""))
            dep["source_name"] = src.get("name", "unknown") if src else "unknown"
            dep["target_name"] = tgt.get("name", "unknown") if tgt else "unknown"

        return {
            "total": len(circular),
            "limit": limit,
            "circular_dependencies": limited,
        }

    @router.post("/dependencies", status_code=201)
    async def create_dependency(
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Create a new dependency relationship.

        Required: source_id, target_id.
        Optional: source_type, target_type, dependency_type, severity.
        """
        source_id = data.get("source_id")
        target_id = data.get("target_id")
        if not source_id or not target_id:
            raise HTTPException(400, "source_id and target_id are required")

        dep = store.add_dependency(
            source_id=source_id,
            target_id=target_id,
            source_type=data.get("source_type", "service"),
            target_type=data.get("target_type", "service"),
            dep_type=data.get("dependency_type", "runtime"),
            severity=data.get("severity", "medium"),
        )
        return dep

    @router.post("/simulate/failure/{service_id}")
    async def simulate_failure(
        service_id: str = Path(..., description="Service ID to simulate failure for"),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Simulate a service failure and analyze impact.

        Computes cascade effects through the dependency graph.
        """
        service = store.get("service", service_id)
        if not service:
            raise HTTPException(404, f"Service {service_id} not found")

        blast = store.calculate_blast_radius(service_id)
        affected = blast["affected_services"]

        critical = [a for a in affected if a.get("severity") == "critical"]
        high = [a for a in affected if a.get("severity") == "high"]
        medium = [a for a in affected if a.get("severity") == "medium"]

        by_depth: dict[int, list[dict]] = {}
        for a in affected:
            d = a.get("hops_away", 1)
            by_depth.setdefault(d, []).append(a)

        if len(critical) > 0:
            severity = "critical"
        elif len(high) > 2:
            severity = "high"
        elif len(affected) > 5:
            severity = "medium"
        else:
            severity = "low"

        failure_modes = store.get_all("failure_mode", limit=10,
                                       filters={"entity_id": service_id})
        recovery_patterns = store.get_all("recovery_pattern", limit=10)

        recommendations: list[str] = []
        if len(affected) > 10:
            recommendations.append("Consider adding circuit breakers to limit cascade")
        if len(critical) > 0:
            recommendations.append("Critical downstream services need immediate failover capability")
        if blast["max_depth"] > 3:
            recommendations.append("Deep dependency chain detected — consider flattening architecture")
        if not recommendations:
            recommendations.append("Service has limited blast radius — no immediate action needed")

        return {
            "service_id": service_id,
            "service_name": service.get("name", "unknown"),
            "blast_radius": blast["blast_radius"],
            "max_cascade_depth": blast["max_depth"],
            "severity": severity,
            "affected_services": affected,
            "impact_by_severity": {
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
                "low": len(affected) - len(critical) - len(high) - len(medium),
            },
            "impact_by_depth": {
                str(k): [a["name"] for a in v] for k, v in sorted(by_depth.items())
            },
            "failure_modes": failure_modes,
            "recovery_patterns": recovery_patterns[:3],
            "recommendations": recommendations,
        }

except ImportError:
    router = None
