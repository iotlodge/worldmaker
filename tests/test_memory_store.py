"""Tests for the InMemoryStore — CRUD, dependencies, audit, search."""
from __future__ import annotations

import pytest
from worldmaker.db.memory import InMemoryStore


class TestCRUD:
    """Test basic Create/Read/Update/Delete operations."""

    def test_create_entity(self, store: InMemoryStore):
        entity = store.create("service", {"name": "auth-service", "status": "active"})
        assert entity["name"] == "auth-service"
        assert "id" in entity
        assert "created_at" in entity
        assert "updated_at" in entity

    def test_get_entity(self, store: InMemoryStore):
        created = store.create("service", {"name": "auth-service"})
        fetched = store.get("service", created["id"])
        assert fetched is not None
        assert fetched["name"] == "auth-service"

    def test_get_returns_deep_copy(self, store: InMemoryStore):
        created = store.create("service", {"name": "svc", "tags": ["a"]})
        fetched = store.get("service", created["id"])
        fetched["tags"].append("b")
        original = store.get("service", created["id"])
        assert "b" not in original["tags"]

    def test_get_nonexistent_returns_none(self, store: InMemoryStore):
        assert store.get("service", "nonexistent") is None

    def test_get_all(self, store: InMemoryStore):
        store.create("service", {"name": "svc-1", "status": "active"})
        store.create("service", {"name": "svc-2", "status": "active"})
        store.create("service", {"name": "svc-3", "status": "degraded"})
        all_svcs = store.get_all("service")
        assert len(all_svcs) == 3

    def test_get_all_with_filter(self, store: InMemoryStore):
        store.create("service", {"name": "svc-1", "status": "active"})
        store.create("service", {"name": "svc-2", "status": "degraded"})
        active = store.get_all("service", filters={"status": "active"})
        assert len(active) == 1
        assert active[0]["name"] == "svc-1"

    def test_get_all_with_limit_offset(self, store: InMemoryStore):
        for i in range(10):
            store.create("service", {"name": f"svc-{i}"})
        page = store.get_all("service", limit=3, offset=2)
        assert len(page) == 3

    def test_update_entity(self, store: InMemoryStore):
        created = store.create("service", {"name": "old-name", "status": "active"})
        updated = store.update("service", created["id"], {"name": "new-name"})
        assert updated is not None
        assert updated["name"] == "new-name"
        assert updated["status"] == "active"

    def test_update_nonexistent_returns_none(self, store: InMemoryStore):
        assert store.update("service", "nonexistent", {"name": "x"}) is None

    def test_delete_entity(self, store: InMemoryStore):
        created = store.create("service", {"name": "temp"})
        assert store.delete("service", created["id"]) is True
        assert store.get("service", created["id"]) is None

    def test_delete_nonexistent_returns_false(self, store: InMemoryStore):
        assert store.delete("service", "nonexistent") is False

    def test_count(self, store: InMemoryStore):
        store.create("product", {"name": "p1"})
        store.create("product", {"name": "p2"})
        assert store.count("product") == 2

    def test_count_with_filter(self, store: InMemoryStore):
        store.create("product", {"name": "p1", "status": "active"})
        store.create("product", {"name": "p2", "status": "planned"})
        assert store.count("product", {"status": "active"}) == 1

    def test_search(self, store: InMemoryStore):
        store.create("service", {"name": "payment-gateway"})
        store.create("service", {"name": "auth-service"})
        store.create("service", {"name": "payment-processor"})
        results = store.search("service", "payment")
        assert len(results) == 2


class TestDependencyGraph:
    """Test dependency graph operations."""

    def test_add_dependency(self, store: InMemoryStore):
        s1 = store.create("service", {"name": "svc-a"})
        s2 = store.create("service", {"name": "svc-b"})
        dep = store.add_dependency(s1["id"], s2["id"])
        assert dep["source_id"] == s1["id"]
        assert dep["target_id"] == s2["id"]

    def test_get_dependencies_of(self, store: InMemoryStore):
        s1 = store.create("service", {"name": "consumer"})
        s2 = store.create("service", {"name": "provider-1"})
        s3 = store.create("service", {"name": "provider-2"})
        store.add_dependency(s1["id"], s2["id"])
        store.add_dependency(s1["id"], s3["id"])
        deps = store.get_dependencies_of(s1["id"])
        assert len(deps) == 2

    def test_get_dependents_of(self, store: InMemoryStore):
        s1 = store.create("service", {"name": "provider"})
        s2 = store.create("service", {"name": "consumer-1"})
        s3 = store.create("service", {"name": "consumer-2"})
        store.add_dependency(s2["id"], s1["id"])
        store.add_dependency(s3["id"], s1["id"])
        dependents = store.get_dependents_of(s1["id"])
        assert len(dependents) == 2

    def test_transitive_dependencies(self, store: InMemoryStore):
        s1 = store.create("service", {"name": "a"})
        s2 = store.create("service", {"name": "b"})
        s3 = store.create("service", {"name": "c"})
        store.add_dependency(s1["id"], s2["id"])
        store.add_dependency(s2["id"], s3["id"])
        trans = store.get_transitive_dependencies(s1["id"])
        target_ids = {d["target_id"] for d in trans}
        assert s2["id"] in target_ids
        assert s3["id"] in target_ids

    def test_blast_radius(self, store: InMemoryStore):
        hub = store.create("service", {"name": "auth-hub"})
        c1 = store.create("service", {"name": "consumer-1"})
        c2 = store.create("service", {"name": "consumer-2"})
        c3 = store.create("service", {"name": "consumer-3"})
        store.add_dependency(c1["id"], hub["id"])
        store.add_dependency(c2["id"], hub["id"])
        store.add_dependency(c3["id"], c1["id"])
        blast = store.calculate_blast_radius(hub["id"])
        assert blast["blast_radius"] >= 2
        assert blast["root_service"]["id"] == hub["id"]

    def test_circular_dependency_detection(self, store: InMemoryStore):
        s1 = store.create("service", {"name": "a"})
        s2 = store.create("service", {"name": "b"})
        store.add_dependency(s1["id"], s2["id"])
        dep = store.add_dependency(s2["id"], s1["id"])
        assert dep["is_circular"] is True
        circular = store.detect_circular_dependencies()
        assert len(circular) >= 1


class TestAuditLog:
    """Test audit logging."""

    def test_create_generates_audit(self, store: InMemoryStore):
        entity = store.create("service", {"name": "test"})
        log = store.get_audit_log(entity_id=entity["id"])
        assert len(log) == 1
        assert log[0]["action"] == "created"

    def test_update_generates_audit(self, store: InMemoryStore):
        entity = store.create("service", {"name": "old"})
        store.update("service", entity["id"], {"name": "new"})
        log = store.get_audit_log(entity_id=entity["id"])
        assert len(log) == 2
        assert log[1]["action"] == "modified"

    def test_delete_generates_audit(self, store: InMemoryStore):
        entity = store.create("service", {"name": "temp"})
        entity_id = entity["id"]
        store.delete("service", entity_id)
        log = store.get_audit_log(entity_id=entity_id)
        assert len(log) == 2
        assert log[1]["action"] == "deleted"

    def test_filter_by_entity_type(self, store: InMemoryStore):
        store.create("service", {"name": "svc"})
        store.create("product", {"name": "prod"})
        svc_log = store.get_audit_log(entity_type="service")
        prod_log = store.get_audit_log(entity_type="product")
        assert len(svc_log) == 1
        assert len(prod_log) == 1


class TestBulkLoad:
    """Test ecosystem loading."""

    def test_load_ecosystem(self, store: InMemoryStore, small_ecosystem):
        loaded = store.load_ecosystem(small_ecosystem)
        assert loaded.get("service", 0) > 0
        assert loaded.get("product", 0) > 0
        assert loaded.get("platform", 0) > 0
        assert loaded.get("dependencies", 0) > 0

    def test_overview_after_load(self, seeded_store: InMemoryStore):
        overview = seeded_store.get_overview()
        assert overview["total_entities"] > 0
        assert overview["total_dependencies"] > 0


class TestTraceStorage:
    """Test trace and span storage."""

    def test_store_and_retrieve_trace(self, store: InMemoryStore):
        trace = {"trace_id": "abc123", "flow_id": "flow-1", "spans": []}
        store.store_trace(trace)
        traces = store.get_traces()
        assert len(traces) == 1
        assert traces[0]["trace_id"] == "abc123"

    def test_filter_traces_by_flow_id(self, store: InMemoryStore):
        store.store_trace({"trace_id": "t1", "flow_id": "f1"})
        store.store_trace({"trace_id": "t2", "flow_id": "f2"})
        store.store_trace({"trace_id": "t3", "flow_id": "f1"})
        f1_traces = store.get_traces(flow_id="f1")
        assert len(f1_traces) == 2

    def test_store_and_retrieve_spans(self, store: InMemoryStore):
        spans = [
            {"traceId": "t1", "spanId": "s1"},
            {"traceId": "t1", "spanId": "s2"},
            {"traceId": "t2", "spanId": "s3"},
        ]
        store.store_spans(spans)
        t1_spans = store.get_spans(trace_id="t1")
        assert len(t1_spans) == 2
