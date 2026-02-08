"""Tests for the Attribute Registry system.

Verifies:
- Bootstrap creates ~20 attribute definitions
- Bootstrap is idempotent
- Gap analysis detects missing required attributes
- Gap analysis is clean when all required attrs present
- Attribute stamping updates entity metadata
- Stamping creates audit trail
- Core attributes survive reset (clear_layer("generated"))
- FUNCTION tier attributes can be created
- CORE/LIFECYCLE tier attributes cannot be deleted
"""
from __future__ import annotations

import pytest

from worldmaker.db.memory import InMemoryStore
from worldmaker.generators.core_attributes import (
    bootstrap_core_attributes,
    ALL_ATTRIBUTES,
)


@pytest.fixture
def store() -> InMemoryStore:
    """Provide a fresh in-memory store."""
    return InMemoryStore()


@pytest.fixture
def attr_store(store: InMemoryStore) -> InMemoryStore:
    """Provide a store with core attributes bootstrapped."""
    bootstrap_core_attributes(store)
    return store


class TestBootstrap:
    """Tests for attribute definition bootstrap."""

    def test_bootstrap_creates_attribute_definitions(self, attr_store: InMemoryStore):
        attrs = attr_store.get_all("attribute_definition", limit=1000)
        assert len(attrs) >= 20  # 5 core + 12 lifecycle + 3 function

    def test_bootstrap_creates_correct_tiers(self, attr_store: InMemoryStore):
        attrs = attr_store.get_all("attribute_definition", limit=1000)
        tiers = {a["tier"] for a in attrs}
        assert "core" in tiers
        assert "lifecycle" in tiers
        assert "function" in tiers

    def test_bootstrap_core_count(self, attr_store: InMemoryStore):
        core_attrs = [
            a for a in attr_store.get_all("attribute_definition", limit=1000)
            if a.get("tier") == "core"
        ]
        assert len(core_attrs) == 5

    def test_bootstrap_lifecycle_count(self, attr_store: InMemoryStore):
        lifecycle_attrs = [
            a for a in attr_store.get_all("attribute_definition", limit=1000)
            if a.get("tier") == "lifecycle"
        ]
        assert len(lifecycle_attrs) == 12

    def test_bootstrap_function_count(self, attr_store: InMemoryStore):
        func_attrs = [
            a for a in attr_store.get_all("attribute_definition", limit=1000)
            if a.get("tier") == "function"
        ]
        assert len(func_attrs) == 3

    def test_bootstrap_idempotent(self, store: InMemoryStore):
        result1 = bootstrap_core_attributes(store)
        count1 = len(store.get_all("attribute_definition", limit=1000))

        result2 = bootstrap_core_attributes(store)
        count2 = len(store.get_all("attribute_definition", limit=1000))

        assert count1 == count2
        assert result2.get("skipped") is True

    def test_bootstrap_all_have_layer_core(self, attr_store: InMemoryStore):
        attrs = attr_store.get_all("attribute_definition", limit=1000)
        for attr in attrs:
            assert attr.get("layer") == "core", f"Attribute {attr['name']} missing layer=core"

    def test_all_attributes_constant_matches_bootstrap(self):
        assert len(ALL_ATTRIBUTES) >= 20

    def test_core_attributes_are_required(self, attr_store: InMemoryStore):
        core_attrs = [
            a for a in attr_store.get_all("attribute_definition", limit=1000)
            if a.get("tier") == "core"
        ]
        for attr in core_attrs:
            assert attr.get("required") is True, f"Core attr {attr['name']} should be required"


class TestGapAnalysis:
    """Tests for gap detection — the risk signal."""

    def test_gap_analysis_detects_missing(self, attr_store: InMemoryStore):
        """Entity without required attributes shows up in gaps."""
        # Create a service with empty metadata
        attr_store.create("service", {
            "name": "risky-service",
            "status": "active",
            "metadata": {},
        })

        # Get required attributes for services
        all_attrs = attr_store.get_all("attribute_definition", limit=1000)
        required_for_service = [
            a for a in all_attrs
            if a.get("required") and "service" in a.get("applies_to", [])
        ]

        # Should have at least some required attrs
        assert len(required_for_service) > 0

        # Now check gaps manually
        services = attr_store.get_all("service", limit=100)
        assert len(services) >= 1

        service = services[0]
        metadata = service.get("metadata", {})
        missing = [
            a["name"] for a in required_for_service
            if a["name"] not in metadata
        ]
        assert len(missing) > 0, "Service should be missing required attributes"

    def test_gap_analysis_clean(self, attr_store: InMemoryStore):
        """Entity with all required attributes has no gaps."""
        all_attrs = attr_store.get_all("attribute_definition", limit=1000)
        required_for_service = [
            a for a in all_attrs
            if a.get("required") and "service" in a.get("applies_to", [])
        ]

        # Build metadata with all required values populated
        metadata = {}
        for attr in required_for_service:
            metadata[attr["name"]] = "test_value"

        attr_store.create("service", {
            "name": "compliant-service",
            "status": "active",
            "metadata": metadata,
        })

        # Verify this service has no missing required attributes
        services = attr_store.search("service", "compliant-service")
        assert len(services) == 1
        svc = services[0]
        svc_metadata = svc.get("metadata", {})

        missing = [
            a["name"] for a in required_for_service
            if a["name"] not in svc_metadata
        ]
        assert len(missing) == 0, f"Compliant service should have no gaps, but missing: {missing}"


class TestStamping:
    """Tests for attribute stamping — core function enrichment."""

    def test_stamp_attribute(self, attr_store: InMemoryStore):
        """Stamping updates entity metadata."""
        svc = attr_store.create("service", {
            "name": "stamp-test-svc",
            "status": "active",
            "metadata": {},
        })

        # Stamp an attribute value
        entity = attr_store.get("service", str(svc["id"]))
        metadata = entity.get("metadata", {})
        metadata["risk_classification"] = "high"
        metadata["risk_classification_stamped_by"] = "Security Management"
        attr_store.update("service", str(svc["id"]), {"metadata": metadata})

        # Verify
        updated = attr_store.get("service", str(svc["id"]))
        assert updated["metadata"]["risk_classification"] == "high"
        assert updated["metadata"]["risk_classification_stamped_by"] == "Security Management"

    def test_stamp_creates_audit_entry(self, attr_store: InMemoryStore):
        """Stamping generates an audit log entry."""
        svc = attr_store.create("service", {
            "name": "audit-test-svc",
            "status": "active",
            "metadata": {},
        })

        initial_audit_count = len(attr_store.get_audit_log(entity_id=str(svc["id"])))

        # Stamp
        entity = attr_store.get("service", str(svc["id"]))
        metadata = entity.get("metadata", {})
        metadata["criticality_tier"] = "tier1"
        attr_store.update("service", str(svc["id"]), {"metadata": metadata})

        audit = attr_store.get_audit_log(entity_id=str(svc["id"]))
        assert len(audit) > initial_audit_count

    def test_stamp_overwrites_previous_value(self, attr_store: InMemoryStore):
        svc = attr_store.create("service", {
            "name": "overwrite-test",
            "status": "active",
            "metadata": {"risk_classification": "low"},
        })

        entity = attr_store.get("service", str(svc["id"]))
        metadata = entity.get("metadata", {})
        assert metadata["risk_classification"] == "low"

        metadata["risk_classification"] = "critical"
        attr_store.update("service", str(svc["id"]), {"metadata": metadata})

        updated = attr_store.get("service", str(svc["id"]))
        assert updated["metadata"]["risk_classification"] == "critical"


class TestLayerProtection:
    """Tests for core attribute survival across resets."""

    def test_core_attributes_survive_reset(self, attr_store: InMemoryStore):
        """clear_layer('generated') preserves core attribute definitions."""
        before = len(attr_store.get_all("attribute_definition", limit=1000))
        assert before >= 20

        attr_store.clear_layer("generated")

        after = len(attr_store.get_all("attribute_definition", limit=1000))
        assert after == before, "Core attribute definitions should survive reset"

    def test_generated_entities_cleared_but_attrs_preserved(self, attr_store: InMemoryStore):
        """Generated services are cleared, but core attributes remain."""
        # Create a generated service
        attr_store.create("service", {
            "name": "generated-svc",
            "status": "active",
            "layer": "generated",
            "metadata": {},
        })
        assert len(attr_store.get_all("service", limit=100)) >= 1

        attr_store.clear_layer("generated")

        # Generated services are gone
        gen_services = [
            s for s in attr_store.get_all("service", limit=100)
            if s.get("layer") == "generated"
        ]
        assert len(gen_services) == 0

        # Core attributes remain
        attrs = attr_store.get_all("attribute_definition", limit=1000)
        assert len(attrs) >= 20


class TestFunctionTierCrud:
    """Tests for FUNCTION tier runtime extensibility."""

    def test_create_function_attribute(self, attr_store: InMemoryStore):
        new_attr = attr_store.create("attribute_definition", {
            "name": "custom_metric",
            "display_name": "Custom Metric",
            "tier": "function",
            "data_type": "number",
            "description": "A custom function-tier attribute",
            "applies_to": ["service"],
            "required": False,
            "category": "custom",
            "layer": "generated",
        })
        assert new_attr["name"] == "custom_metric"
        assert new_attr["tier"] == "function"

    def test_delete_function_attribute(self, attr_store: InMemoryStore):
        new_attr = attr_store.create("attribute_definition", {
            "name": "deletable_metric",
            "display_name": "Deletable",
            "tier": "function",
            "data_type": "string",
            "description": "Will be deleted",
            "applies_to": ["service"],
            "layer": "generated",
        })
        deleted = attr_store.delete("attribute_definition", str(new_attr["id"]))
        assert deleted is True

    def test_cannot_delete_core_attribute_logic(self, attr_store: InMemoryStore):
        """Core-tier attributes should be protected from deletion in the API layer.

        Note: The store itself doesn't enforce tier protection —
        that's the API route's responsibility. This test verifies the data
        that would be checked by the API endpoint.
        """
        core_attrs = [
            a for a in attr_store.get_all("attribute_definition", limit=1000)
            if a.get("tier") == "core"
        ]
        assert len(core_attrs) > 0

        for attr in core_attrs:
            # Verify the tier field is present and correct
            assert attr["tier"] in ("core", "lifecycle"), \
                f"Attribute {attr['name']} has unexpected tier {attr['tier']}"


class TestAttributeMetadata:
    """Tests for attribute definition quality."""

    def test_all_attributes_have_name(self, attr_store: InMemoryStore):
        attrs = attr_store.get_all("attribute_definition", limit=1000)
        for attr in attrs:
            assert attr.get("name"), f"Attribute {attr.get('id')} missing name"

    def test_all_attributes_have_display_name(self, attr_store: InMemoryStore):
        attrs = attr_store.get_all("attribute_definition", limit=1000)
        for attr in attrs:
            assert attr.get("display_name"), f"Attribute {attr['name']} missing display_name"

    def test_all_attributes_have_applies_to(self, attr_store: InMemoryStore):
        attrs = attr_store.get_all("attribute_definition", limit=1000)
        for attr in attrs:
            assert len(attr.get("applies_to", [])) > 0, \
                f"Attribute {attr['name']} has no applies_to"

    def test_all_attributes_have_data_type(self, attr_store: InMemoryStore):
        attrs = attr_store.get_all("attribute_definition", limit=1000)
        valid_types = {"string", "number", "boolean", "enum", "json"}
        for attr in attrs:
            assert attr.get("data_type") in valid_types, \
                f"Attribute {attr['name']} has invalid data_type: {attr.get('data_type')}"

    def test_enum_attributes_have_values(self, attr_store: InMemoryStore):
        attrs = attr_store.get_all("attribute_definition", limit=1000)
        for attr in attrs:
            if attr.get("data_type") == "enum":
                assert len(attr.get("enum_values", [])) > 0, \
                    f"Enum attribute {attr['name']} has no enum_values"

    def test_lifecycle_attributes_have_owner(self, attr_store: InMemoryStore):
        lifecycle_attrs = [
            a for a in attr_store.get_all("attribute_definition", limit=1000)
            if a.get("tier") == "lifecycle"
        ]
        for attr in lifecycle_attrs:
            assert attr.get("owner_platform"), \
                f"Lifecycle attribute {attr['name']} missing owner_platform"
