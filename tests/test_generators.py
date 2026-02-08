"""Tests for the ecosystem generator."""
from __future__ import annotations

import pytest
from worldmaker.generators.ecosystem import generate_ecosystem, EcosystemGenerator
from worldmaker.generators.base import GeneratorConfig


class TestEcosystemGeneration:
    """Test synthetic ecosystem generation."""

    def test_small_ecosystem(self, small_ecosystem):
        s = small_ecosystem["summary"]
        assert s["products"] > 0
        assert s["platforms"] > 0
        assert s["services"] > 0
        assert s["microservices"] > 0
        assert s["flows"] > 0
        assert s["dependencies"] > 0

    def test_medium_ecosystem(self, medium_ecosystem):
        s = medium_ecosystem["summary"]
        assert s["services"] > small_count(s)
        assert s["platforms"] >= 5

    def test_reproducibility(self):
        eco1 = generate_ecosystem(seed=42, size="small")
        eco2 = generate_ecosystem(seed=42, size="small")
        assert eco1["summary"] == eco2["summary"]
        assert len(eco1["services"]) == len(eco2["services"])
        # Same names with same seed
        names1 = sorted(s["name"] for s in eco1["services"])
        names2 = sorted(s["name"] for s in eco2["services"])
        assert names1 == names2

    def test_different_seeds_produce_different_data(self):
        eco1 = generate_ecosystem(seed=42, size="small")
        eco2 = generate_ecosystem(seed=99, size="small")
        names1 = set(s["name"] for s in eco1["services"])
        names2 = set(s["name"] for s in eco2["services"])
        # Should have some differences
        assert names1 != names2

    def test_all_entity_types_present(self, small_ecosystem):
        expected_keys = [
            "products", "platforms", "capabilities", "services",
            "microservices", "interfaces", "flows", "flow_steps",
            "dependencies", "environments", "deployments",
            "criticality_ratings", "slo_definitions", "failure_modes",
            "recovery_patterns", "event_types",
        ]
        for key in expected_keys:
            assert key in small_ecosystem, f"Missing key: {key}"

    def test_services_have_required_fields(self, small_ecosystem):
        for svc in small_ecosystem["services"]:
            assert "id" in svc
            assert "name" in svc
            assert "status" in svc
            assert "service_type" in svc
            assert "capability_id" in svc
            assert "platform_id" in svc

    def test_flow_steps_reference_valid_services(self, small_ecosystem):
        service_ids = {s["id"] for s in small_ecosystem["services"]}
        for step in small_ecosystem["flow_steps"]:
            assert step["from_service_id"] in service_ids
            assert step["to_service_id"] in service_ids

    def test_dependencies_reference_valid_services(self, small_ecosystem):
        service_ids = {s["id"] for s in small_ecosystem["services"]}
        for dep in small_ecosystem["dependencies"]:
            assert dep["source_id"] in service_ids
            assert dep["target_id"] in service_ids

    def test_microservices_reference_valid_services(self, small_ecosystem):
        service_ids = {s["id"] for s in small_ecosystem["services"]}
        for ms in small_ecosystem["microservices"]:
            assert ms["service_id"] in service_ids

    def test_capabilities_reference_valid_platforms(self, small_ecosystem):
        platform_ids = {p["id"] for p in small_ecosystem["platforms"]}
        for cap in small_ecosystem["capabilities"]:
            assert cap["platform_id"] in platform_ids

    def test_flow_steps_ordered(self, small_ecosystem):
        flow_ids = {f["id"] for f in small_ecosystem["flows"]}
        for flow_id in flow_ids:
            steps = [s for s in small_ecosystem["flow_steps"]
                     if s["flow_id"] == flow_id]
            if len(steps) > 1:
                step_numbers = [s["step_number"] for s in steps]
                assert step_numbers == sorted(step_numbers)


class TestGeneratorConfig:
    """Test generator configuration."""

    def test_small_config(self):
        config = GeneratorConfig("small")
        # products and platforms are range tuples like (2, 4)
        products = config.get("products")
        platforms = config.get("platforms")
        assert products is not None
        assert isinstance(products, tuple)
        assert products[0] > 0  # lower bound > 0
        assert products[1] >= products[0]  # upper >= lower

        assert platforms is not None
        assert isinstance(platforms, tuple)
        assert platforms[0] > 0

    def test_config_range(self):
        config = GeneratorConfig("small")
        lo, hi = config.range("products")
        assert lo > 0
        assert hi >= lo

    def test_large_produces_more(self):
        small = generate_ecosystem(seed=1, size="small")
        large = generate_ecosystem(seed=1, size="large")
        assert large["summary"]["services"] > small["summary"]["services"]
        assert large["summary"]["platforms"] > small["summary"]["platforms"]


def small_count(summary: dict) -> int:
    """Helper to get a reference small count for comparison."""
    small = generate_ecosystem(seed=42, size="small")
    return small["summary"]["services"]
