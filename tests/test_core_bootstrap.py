"""Tests for core management platform bootstrap.

Verifies:
- 9 core platforms are created with correct names
- Capabilities and services are created per platform
- All core entities have layer="core"
- Bootstrap is idempotent
- clear_layer("generated") preserves core
- clear_layer("generated") removes generated
- Generator creates additional platforms on top of core
"""
from __future__ import annotations

import pytest

from worldmaker.db.memory import InMemoryStore
from worldmaker.generators.core_platforms import bootstrap_core, CORE_PLATFORMS
from worldmaker.generators.ecosystem import generate_ecosystem


EXPECTED_PLATFORM_NAMES = [
    "Product Management",
    "Change Management",
    "Incident Management",
    "Problem Management",
    "Issues Management",
    "Risk Management",
    "Operations Management",
    "Business Continuity Management",
    "Security Management",
]

EXPECTED_CAPABILITY_COUNT = sum(len(p["capabilities"]) for p in CORE_PLATFORMS)  # 45
# Each capability gets one service
EXPECTED_SERVICE_COUNT = EXPECTED_CAPABILITY_COUNT


@pytest.fixture
def core_store() -> InMemoryStore:
    """Provide a store with core platforms bootstrapped."""
    store = InMemoryStore()
    bootstrap_core(store)
    return store


class TestBootstrapCreation:
    """Tests for initial core bootstrap."""

    def test_bootstrap_creates_nine_platforms(self, core_store: InMemoryStore):
        platforms = core_store.get_all("platform", limit=100, filters={"layer": "core"})
        assert len(platforms) == 9

    def test_bootstrap_correct_names(self, core_store: InMemoryStore):
        platforms = core_store.get_all("platform", limit=100, filters={"layer": "core"})
        names = sorted(p["name"] for p in platforms)
        assert names == sorted(EXPECTED_PLATFORM_NAMES)

    def test_bootstrap_creates_capabilities(self, core_store: InMemoryStore):
        capabilities = core_store.get_all("capability", limit=200, filters={"layer": "core"})
        assert len(capabilities) == EXPECTED_CAPABILITY_COUNT

    def test_bootstrap_creates_services(self, core_store: InMemoryStore):
        services = core_store.get_all("service", limit=200, filters={"layer": "core"})
        assert len(services) == EXPECTED_SERVICE_COUNT

    def test_all_core_platforms_active(self, core_store: InMemoryStore):
        platforms = core_store.get_all("platform", limit=100, filters={"layer": "core"})
        for p in platforms:
            assert p["status"] == "active"

    def test_all_core_capabilities_have_layer(self, core_store: InMemoryStore):
        capabilities = core_store.get_all("capability", limit=200, filters={"layer": "core"})
        for cap in capabilities:
            assert cap["layer"] == "core"

    def test_all_core_services_have_layer(self, core_store: InMemoryStore):
        services = core_store.get_all("service", limit=200, filters={"layer": "core"})
        for svc in services:
            assert svc["layer"] == "core"

    def test_capability_has_platform_reference(self, core_store: InMemoryStore):
        capabilities = core_store.get_all("capability", limit=200, filters={"layer": "core"})
        platform_ids = {p["id"] for p in core_store.get_all("platform", limit=100)}
        for cap in capabilities:
            assert cap["platform_id"] in platform_ids

    def test_service_has_capability_reference(self, core_store: InMemoryStore):
        services = core_store.get_all("service", limit=200, filters={"layer": "core"})
        cap_ids = {c["id"] for c in core_store.get_all("capability", limit=200)}
        for svc in services:
            assert svc["capability_id"] in cap_ids

    def test_platform_metadata_has_counts(self, core_store: InMemoryStore):
        platforms = core_store.get_all("platform", limit=100, filters={"layer": "core"})
        for p in platforms:
            metadata = p.get("metadata", {})
            assert "capability_count" in metadata
            assert "service_count" in metadata
            assert metadata["capability_count"] == metadata["service_count"]
            assert metadata["capability_count"] > 0

    def test_bootstrap_returns_correct_counts(self):
        store = InMemoryStore()
        result = bootstrap_core(store)
        assert result["platforms"] == 9
        assert result["capabilities"] == EXPECTED_CAPABILITY_COUNT
        assert result["services"] == EXPECTED_SERVICE_COUNT


class TestBootstrapIdempotency:
    """Bootstrap must be safely callable multiple times."""

    def test_bootstrap_idempotency(self, core_store: InMemoryStore):
        # Call bootstrap again
        result = bootstrap_core(core_store)
        assert result.get("skipped") is True

        # Still exactly 9 platforms
        platforms = core_store.get_all("platform", limit=100, filters={"layer": "core"})
        assert len(platforms) == 9

    def test_idempotency_no_duplicate_capabilities(self, core_store: InMemoryStore):
        bootstrap_core(core_store)
        capabilities = core_store.get_all("capability", limit=500, filters={"layer": "core"})
        assert len(capabilities) == EXPECTED_CAPABILITY_COUNT

    def test_idempotency_no_duplicate_services(self, core_store: InMemoryStore):
        bootstrap_core(core_store)
        services = core_store.get_all("service", limit=500, filters={"layer": "core"})
        assert len(services) == EXPECTED_SERVICE_COUNT


class TestLayerOperations:
    """Tests for layer-aware store operations."""

    def test_clear_generated_preserves_core(self, core_store: InMemoryStore):
        # Add some generated entities
        eco = generate_ecosystem(seed=42, size="small")
        core_store.load_ecosystem(eco)

        # Verify we have both layers
        all_platforms = core_store.get_all("platform", limit=500)
        assert len(all_platforms) > 9

        # Clear generated
        core_store.clear_layer("generated")

        # Core platforms still exist
        core_platforms = core_store.get_all("platform", limit=100, filters={"layer": "core"})
        assert len(core_platforms) == 9

    def test_clear_generated_removes_generated(self, core_store: InMemoryStore):
        eco = generate_ecosystem(seed=42, size="small")
        core_store.load_ecosystem(eco)

        core_store.clear_layer("generated")

        gen_platforms = core_store.get_all("platform", limit=100, filters={"layer": "generated"})
        assert len(gen_platforms) == 0

        gen_services = core_store.get_all("service", limit=500, filters={"layer": "generated"})
        assert len(gen_services) == 0

    def test_clear_generated_returns_counts(self, core_store: InMemoryStore):
        eco = generate_ecosystem(seed=42, size="small")
        core_store.load_ecosystem(eco)

        counts = core_store.clear_layer("generated")
        # Should have deleted some platforms
        assert counts.get("platform", 0) > 0
        # Traces/spans should be cleared too
        assert "traces" in counts
        assert "spans" in counts

    def test_clear_core_removes_core(self):
        """Clearing 'core' should remove core entities (edge case test)."""
        store = InMemoryStore()
        bootstrap_core(store)

        store.clear_layer("core")

        platforms = store.get_all("platform", limit=100, filters={"layer": "core"})
        assert len(platforms) == 0

    def test_generate_on_top_of_core(self, core_store: InMemoryStore):
        """Generator should augment core, not replace it."""
        eco = generate_ecosystem(seed=42, size="small")
        core_store.load_ecosystem(eco)

        all_platforms = core_store.get_all("platform", limit=500)
        core_platforms = [p for p in all_platforms if p.get("layer") == "core"]
        gen_platforms = [p for p in all_platforms if p.get("layer") == "generated"]

        assert len(core_platforms) == 9
        assert len(gen_platforms) > 0
        assert len(all_platforms) == len(core_platforms) + len(gen_platforms)


class TestGeneratedEntitiesHaveLayer:
    """All generated entities must have layer='generated'."""

    def test_generated_platforms_have_layer(self):
        eco = generate_ecosystem(seed=42, size="small")
        for p in eco.get("platforms", []):
            assert p.get("layer") == "generated", f"Platform {p.get('name')} missing layer"

    def test_generated_services_have_layer(self):
        eco = generate_ecosystem(seed=42, size="small")
        for s in eco.get("services", []):
            assert s.get("layer") == "generated", f"Service {s.get('name')} missing layer"

    def test_generated_capabilities_have_layer(self):
        eco = generate_ecosystem(seed=42, size="small")
        for c in eco.get("capabilities", []):
            assert c.get("layer") == "generated"

    def test_generated_products_have_layer(self):
        eco = generate_ecosystem(seed=42, size="small")
        for p in eco.get("products", []):
            assert p.get("layer") == "generated"

    def test_generated_flows_have_layer(self):
        eco = generate_ecosystem(seed=42, size="small")
        for f in eco.get("flows", []):
            assert f.get("layer") == "generated"


class TestDependencyIndexRebuild:
    """Tests for _rebuild_dep_indexes after clear_layer."""

    def test_dependency_indexes_valid_after_clear(self, core_store: InMemoryStore):
        eco = generate_ecosystem(seed=42, size="small")
        core_store.load_ecosystem(eco)

        core_store.clear_layer("generated")

        # Dep indexes should be consistent
        for idx_list in core_store._dep_index_source.values():
            for idx in idx_list:
                assert idx < len(core_store._dependencies)

        for idx_list in core_store._dep_index_target.values():
            for idx in idx_list:
                assert idx < len(core_store._dependencies)

    def test_dep_count_consistent_after_clear(self, core_store: InMemoryStore):
        eco = generate_ecosystem(seed=42, size="small")
        core_store.load_ecosystem(eco)

        original_dep_count = len(core_store._dependencies)
        counts = core_store.clear_layer("generated")
        remaining = len(core_store._dependencies)

        assert remaining == original_dep_count - counts.get("dependencies", 0)
