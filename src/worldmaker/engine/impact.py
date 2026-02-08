"""Blast radius calculator for failure impact analysis.

Computes the cascade effect of service failures through the
dependency graph, incorporating criticality propagation.
"""
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ImpactCalculator:
    """Calculates blast radius and failure impact."""

    def __init__(self, graph_repo: Any = None, unified_repo: Any = None):
        self._graph_repo = graph_repo
        self._unified_repo = unified_repo

    async def calculate_blast_radius(self, service_id: str) -> dict[str, Any]:
        """Calculate complete blast radius for a service failure."""
        if not self._graph_repo:
            return {"service_id": service_id, "error": "graph_repo not configured"}

        # Get blast radius from graph
        blast = await self._graph_repo.calculate_blast_radius(service_id)

        # Get full context for richer analysis
        context = await self._graph_repo.get_full_service_context(service_id)

        return {
            "service_id": service_id,
            "blast_radius": blast.get("blast_radius", 0),
            "affected_services": blast.get("affected_services", []),
            "root_service": blast.get("root_service", {}),
            "service_context": context,
            "recommendations": self._generate_recommendations(blast, context),
        }

    async def simulate_failure(self, service_id: str) -> dict[str, Any]:
        """Simulate a service failure and return impact analysis."""
        if not self._graph_repo:
            return {"service_id": service_id, "error": "graph_repo not configured"}

        simulation = await self._graph_repo.simulate_failure(service_id)
        cascade = await self._graph_repo.get_health_cascade()

        return {
            "simulation": simulation,
            "cascade_effects": cascade,
            "severity": self._classify_severity(simulation),
        }

    def _classify_severity(self, simulation: dict[str, Any]) -> str:
        """Classify severity based on simulation impact."""
        total = simulation.get("total_impact", 0)
        if total >= 10:
            return "critical"
        elif total >= 5:
            return "high"
        elif total >= 2:
            return "medium"
        return "low"

    def _generate_recommendations(
        self, blast: dict[str, Any], context: dict[str, Any]
    ) -> list[str]:
        """Generate actionable recommendations based on impact analysis."""
        recommendations: list[str] = []
        radius = blast.get("blast_radius", 0)

        if radius > 10:
            recommendations.append("CRITICAL: High blast radius. Consider adding circuit breakers.")
        if radius > 5:
            recommendations.append("Add fallback/degraded-mode capabilities for downstream consumers.")

        # Check for missing redundancy
        upstream = context.get("upstream_dependencies", [])
        if len(upstream) > 5:
            recommendations.append("Many upstream dependents. Consider splitting into smaller services.")

        downstream = context.get("downstream_dependencies", [])
        if len(downstream) > 3:
            recommendations.append("Multiple critical dependencies. Implement bulkhead patterns.")

        if not recommendations:
            recommendations.append("No immediate concerns. Continue monitoring.")

        return recommendations
