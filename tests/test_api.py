"""Tests for the FastAPI API endpoints using TestClient."""
from __future__ import annotations

import pytest
from worldmaker.db.memory import InMemoryStore

try:
    from fastapi.testclient import TestClient
    from worldmaker.api.app import create_app
    from worldmaker.api.deps import get_memory_store, get_trace_engine, reset_all
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

pytestmark = pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")


@pytest.fixture
def client():
    """Create a test client with a clean store."""
    reset_all()
    app = create_app()

    from worldmaker.engine.trace import TraceEngine

    # Override dependencies to use a fresh store and engine sharing the same store
    store = InMemoryStore()
    engine = TraceEngine(store=store, rng_seed=42)
    app.dependency_overrides[get_memory_store] = lambda: store
    app.dependency_overrides[get_trace_engine] = lambda: engine

    with TestClient(app) as c:
        yield c

    # Clean up
    app.dependency_overrides.clear()
    reset_all()


@pytest.fixture
def seeded_client():
    """Create a test client with a pre-loaded ecosystem."""
    reset_all()
    app = create_app()

    from worldmaker.generators.ecosystem import generate_ecosystem
    from worldmaker.engine.trace import TraceEngine

    store = InMemoryStore()
    eco = generate_ecosystem(seed=42, size="small")
    store.load_ecosystem(eco)

    engine = TraceEngine(store=store, rng_seed=42)

    app.dependency_overrides[get_memory_store] = lambda: store
    app.dependency_overrides[get_trace_engine] = lambda: engine

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    reset_all()


class TestHealthEndpoints:
    def test_health(self, client):
        r = client.get("/api/v1/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_store_health_empty(self, client):
        r = client.get("/api/v1/health/stores")
        assert r.status_code == 200
        data = r.json()
        assert data["store_type"] == "in_memory"
        assert data["total_entities"] == 0

    def test_store_health_with_data(self, seeded_client):
        r = seeded_client.get("/api/v1/health/stores")
        data = r.json()
        assert data["total_entities"] > 0
        assert data["total_dependencies"] > 0


class TestEcosystemEndpoints:
    def test_overview_empty(self, client):
        r = client.get("/api/v1/ecosystem/overview")
        assert r.status_code == 200
        data = r.json()
        assert data["total_entities"] == 0

    def test_overview_with_data(self, seeded_client):
        r = seeded_client.get("/api/v1/ecosystem/overview")
        data = r.json()
        assert data["total_entities"] > 0
        assert data["ecosystem"]["services"]["total"] > 0
        assert "statistics" in data

    def test_health_check(self, seeded_client):
        r = seeded_client.get("/api/v1/ecosystem/health")
        data = r.json()
        assert "overall_health" in data
        assert "health_score" in data

    def test_search(self, seeded_client):
        r = seeded_client.get("/api/v1/ecosystem/search?q=Service&entity_type=service")
        data = r.json()
        assert data["total"] > 0

    def test_audit_log(self, seeded_client):
        r = seeded_client.get("/api/v1/ecosystem/audit?limit=10")
        data = r.json()
        assert data["total"] > 0


class TestServiceEndpoints:
    def test_list_services(self, seeded_client):
        r = seeded_client.get("/api/v1/services")
        data = r.json()
        assert data["total"] > 0
        assert len(data["services"]) > 0

    def test_get_service(self, seeded_client):
        # First get a service ID
        r = seeded_client.get("/api/v1/services?limit=1")
        svc = r.json()["services"][0]
        svc_id = svc["id"]

        r = seeded_client.get(f"/api/v1/services/{svc_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == svc_id
        assert "microservices" in data

    def test_get_service_not_found(self, seeded_client):
        r = seeded_client.get("/api/v1/services/nonexistent")
        assert r.status_code == 404

    def test_create_service(self, client):
        r = client.post("/api/v1/services", json={
            "name": "new-service",
            "status": "active",
            "service_type": "rest",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "new-service"
        assert "id" in data

    def test_update_service(self, seeded_client):
        r = seeded_client.get("/api/v1/services?limit=1")
        svc_id = r.json()["services"][0]["id"]

        r = seeded_client.put(f"/api/v1/services/{svc_id}",
                              json={"status": "degraded"})
        assert r.status_code == 200
        assert r.json()["status"] == "degraded"

    def test_delete_service(self, client):
        r = client.post("/api/v1/services", json={"name": "temp"})
        svc_id = r.json()["id"]

        r = client.delete(f"/api/v1/services/{svc_id}")
        assert r.status_code == 200
        assert r.json()["deleted"] is True

        r = client.get(f"/api/v1/services/{svc_id}")
        assert r.status_code == 404

    def test_service_context(self, seeded_client):
        r = seeded_client.get("/api/v1/services?limit=1")
        svc_id = r.json()["services"][0]["id"]

        r = seeded_client.get(f"/api/v1/services/{svc_id}/context")
        assert r.status_code == 200
        data = r.json()
        assert "entity" in data
        assert "dependencies" in data
        assert "health" in data
        assert "microservices" in data
        assert "audit" in data


class TestProductEndpoints:
    def test_list_products(self, seeded_client):
        r = seeded_client.get("/api/v1/products")
        assert r.status_code == 200
        assert r.json()["total"] > 0

    def test_create_product(self, client):
        r = client.post("/api/v1/products", json={
            "name": "Digital Banking",
            "status": "active",
        })
        assert r.status_code == 201
        assert r.json()["name"] == "Digital Banking"


class TestPlatformEndpoints:
    def test_list_platforms(self, seeded_client):
        r = seeded_client.get("/api/v1/platforms")
        assert r.status_code == 200
        assert r.json()["total"] > 0

    def test_get_platform_with_capabilities(self, seeded_client):
        r = seeded_client.get("/api/v1/platforms?limit=1")
        plat_id = r.json()["platforms"][0]["id"]

        r = seeded_client.get(f"/api/v1/platforms/{plat_id}")
        assert r.status_code == 200
        assert "capabilities" in r.json()


class TestFlowEndpoints:
    def test_list_flows(self, seeded_client):
        r = seeded_client.get("/api/v1/flows")
        assert r.status_code == 200
        assert r.json()["total"] > 0

    def test_get_flow_with_steps(self, seeded_client):
        r = seeded_client.get("/api/v1/flows?limit=1")
        flow_id = r.json()["flows"][0]["id"]

        r = seeded_client.get(f"/api/v1/flows/{flow_id}")
        assert r.status_code == 200
        data = r.json()
        assert "steps_detail" in data
        assert "step_count" in data

    def test_execute_flow(self, seeded_client):
        r = seeded_client.get("/api/v1/flows?limit=1")
        flow_id = r.json()["flows"][0]["id"]

        r = seeded_client.post(f"/api/v1/flows/{flow_id}/execute")
        assert r.status_code == 200
        data = r.json()
        assert "trace_id" in data
        assert data["span_count"] > 0

    def test_execute_flow_with_failure(self, seeded_client):
        r = seeded_client.get("/api/v1/flows?limit=1")
        flow_id = r.json()["flows"][0]["id"]

        r = seeded_client.post(
            f"/api/v1/flows/{flow_id}/execute?inject_failure=true&failure_step=0"
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "STATUS_CODE_ERROR"

    def test_get_flow_traces(self, seeded_client):
        # Execute a flow first
        r = seeded_client.get("/api/v1/flows?limit=1")
        flow_id = r.json()["flows"][0]["id"]
        seeded_client.post(f"/api/v1/flows/{flow_id}/execute")

        r = seeded_client.get(f"/api/v1/flows/{flow_id}/traces")
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_get_trace_spans(self, seeded_client):
        r = seeded_client.get("/api/v1/flows?limit=1")
        flow_id = r.json()["flows"][0]["id"]
        exec_r = seeded_client.post(f"/api/v1/flows/{flow_id}/execute")
        trace_id = exec_r.json()["trace_id"]

        r = seeded_client.get(f"/api/v1/traces/{trace_id}/spans")
        assert r.status_code == 200
        data = r.json()
        assert data["span_count"] > 0
        assert len(data["spans"]) > 0

    def test_get_trace_spans_jaeger(self, seeded_client):
        r = seeded_client.get("/api/v1/flows?limit=1")
        flow_id = r.json()["flows"][0]["id"]
        exec_r = seeded_client.post(f"/api/v1/flows/{flow_id}/execute")
        trace_id = exec_r.json()["trace_id"]

        r = seeded_client.get(f"/api/v1/traces/{trace_id}/spans?format=jaeger")
        assert r.status_code == 200
        data = r.json()
        assert data["format"] == "jaeger"
        assert data["span_count"] > 0


class TestDependencyEndpoints:
    def test_get_direct_dependencies(self, seeded_client):
        r = seeded_client.get("/api/v1/services?limit=1")
        svc_id = r.json()["services"][0]["id"]

        r = seeded_client.get(f"/api/v1/services/{svc_id}/dependencies")
        assert r.status_code == 200
        data = r.json()
        assert "depends_on" in data
        assert "depended_on_by" in data
        assert "statistics" in data

    def test_get_transitive_dependencies(self, seeded_client):
        r = seeded_client.get("/api/v1/services?limit=1")
        svc_id = r.json()["services"][0]["id"]

        r = seeded_client.get(
            f"/api/v1/services/{svc_id}/dependencies?depth=transitive"
        )
        assert r.status_code == 200
        assert "transitive_dependencies" in r.json()

    def test_get_blast_radius(self, seeded_client):
        r = seeded_client.get("/api/v1/services?limit=1")
        svc_id = r.json()["services"][0]["id"]

        r = seeded_client.get(
            f"/api/v1/services/{svc_id}/dependencies?depth=blast-radius"
        )
        assert r.status_code == 200
        assert "blast_radius" in r.json()

    def test_circular_dependencies(self, seeded_client):
        r = seeded_client.get("/api/v1/dependencies/circular")
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "circular_dependencies" in data

    def test_simulate_failure(self, seeded_client):
        r = seeded_client.get("/api/v1/services?limit=1")
        svc_id = r.json()["services"][0]["id"]

        r = seeded_client.post(f"/api/v1/simulate/failure/{svc_id}")
        assert r.status_code == 200
        data = r.json()
        assert "blast_radius" in data
        assert "severity" in data
        assert "recommendations" in data
        assert "impact_by_severity" in data

    def test_create_dependency(self, client):
        s1 = client.post("/api/v1/services", json={"name": "a"}).json()
        s2 = client.post("/api/v1/services", json={"name": "b"}).json()

        r = client.post("/api/v1/dependencies", json={
            "source_id": s1["id"],
            "target_id": s2["id"],
            "dependency_type": "runtime",
            "severity": "high",
        })
        assert r.status_code == 201
        dep = r.json()
        assert dep["source_id"] == s1["id"]
        assert dep["target_id"] == s2["id"]


class TestGeneratorEndpoints:
    def test_generate_ecosystem(self, client):
        r = client.post("/api/v1/generate?seed=42&size=small")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "completed"
        assert data["summary"]["services"] > 0
        assert data["loaded"]["service"] > 0

    def test_generate_with_traces(self, client):
        r = client.post("/api/v1/generate?seed=42&size=small&execute_flows=true")
        assert r.status_code == 200
        data = r.json()
        assert "traces_generated" in data
        assert data["traces_generated"] > 0

    def test_preview(self, client):
        r = client.get("/api/v1/generate/preview?seed=42&size=small")
        assert r.status_code == 200
        data = r.json()
        assert data["preview"]["total_entities"] > 0

    def test_reset(self, client):
        # Generate first
        client.post("/api/v1/generate?seed=42&size=small")
        # Reset
        r = client.post("/api/v1/generate/reset")
        assert r.status_code == 200
        assert r.json()["status"] == "reset"
