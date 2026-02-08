"""Tests for the OpenTelemetry trace engine."""
from __future__ import annotations

import pytest
from worldmaker.db.memory import InMemoryStore
from worldmaker.engine.trace import TraceEngine, Span, SpanEvent


class TestTraceExecution:
    """Test flow execution and trace generation."""

    def test_execute_flow_generates_trace(self, seeded_store: InMemoryStore):
        engine = TraceEngine(store=seeded_store, rng_seed=42)
        flows = seeded_store.get_all("flow", limit=1)
        assert len(flows) > 0, "Expected at least one flow in seeded store"

        flow = flows[0]
        trace = engine.execute_flow_by_id(flow["id"])

        assert "trace_id" in trace
        assert len(trace["trace_id"]) == 32  # 128-bit hex
        assert trace["span_count"] > 0
        assert trace["status"] in ("STATUS_CODE_OK", "STATUS_CODE_ERROR")

    def test_trace_has_root_span(self, seeded_store: InMemoryStore):
        engine = TraceEngine(store=seeded_store, rng_seed=42)
        flows = seeded_store.get_all("flow", limit=1)
        trace = engine.execute_flow_by_id(flows[0]["id"])

        spans = trace["spans"]
        root_spans = [s for s in spans if s.get("parentSpanId") == ""]
        assert len(root_spans) == 1
        assert root_spans[0]["operationName"].startswith("FLOW ")

    def test_spans_have_required_fields(self, seeded_store: InMemoryStore):
        engine = TraceEngine(store=seeded_store, rng_seed=42)
        flows = seeded_store.get_all("flow", limit=1)
        trace = engine.execute_flow_by_id(flows[0]["id"])

        for span in trace["spans"]:
            assert "traceId" in span
            assert "spanId" in span
            assert "operationName" in span
            assert "serviceName" in span
            assert "kind" in span
            assert "status" in span
            assert "attributes" in span
            assert "resource" in span

    def test_client_server_span_pairs(self, seeded_store: InMemoryStore):
        engine = TraceEngine(store=seeded_store, rng_seed=42)
        flows = seeded_store.get_all("flow", limit=1)
        trace = engine.execute_flow_by_id(flows[0]["id"])

        spans = trace["spans"]
        non_root = [s for s in spans if s.get("parentSpanId") != ""]
        client_spans = [s for s in non_root if s["kind"] == "SPAN_KIND_CLIENT"]
        server_spans = [s for s in non_root if s["kind"] == "SPAN_KIND_SERVER"]

        # Every client span should have a corresponding server span
        assert len(client_spans) == len(server_spans)

    def test_inject_failure(self, seeded_store: InMemoryStore):
        engine = TraceEngine(store=seeded_store, rng_seed=42)
        flows = seeded_store.get_all("flow", limit=1)
        trace = engine.execute_flow_by_id(
            flows[0]["id"], inject_failure=True, failure_step=0
        )
        assert trace["status"] == "STATUS_CODE_ERROR"
        assert trace["error"] is not None
        assert "step" in trace["error"]

    def test_failure_at_specific_step(self, seeded_store: InMemoryStore):
        engine = TraceEngine(store=seeded_store, rng_seed=42)
        flows = seeded_store.get_all("flow", limit=10)

        # Find a flow with multiple steps
        for flow in flows:
            steps = seeded_store.get_all("flow_step", limit=100,
                                          filters={"flow_id": flow["id"]})
            if len(steps) >= 2:
                trace = engine.execute_flow_by_id(
                    flow["id"], inject_failure=True, failure_step=1
                )
                assert trace["status"] == "STATUS_CODE_ERROR"
                assert trace["error"]["step"] == 1
                break

    def test_trace_stored_in_memory(self, seeded_store: InMemoryStore):
        engine = TraceEngine(store=seeded_store, rng_seed=42)
        flows = seeded_store.get_all("flow", limit=1)
        trace = engine.execute_flow_by_id(flows[0]["id"])

        stored_traces = seeded_store.get_traces(flow_id=flows[0]["id"])
        assert len(stored_traces) >= 1
        assert stored_traces[0]["trace_id"] == trace["trace_id"]

    def test_spans_stored_in_memory(self, seeded_store: InMemoryStore):
        engine = TraceEngine(store=seeded_store, rng_seed=42)
        flows = seeded_store.get_all("flow", limit=1)
        trace = engine.execute_flow_by_id(flows[0]["id"])

        stored_spans = seeded_store.get_spans(trace_id=trace["trace_id"])
        assert len(stored_spans) == trace["span_count"]

    def test_execute_all_flows(self, seeded_store: InMemoryStore):
        engine = TraceEngine(store=seeded_store, rng_seed=42)
        all_flows = seeded_store.get_all("flow", limit=10000)
        traces = engine.execute_all_flows()

        # Should have at least some traces
        assert len(traces) > 0

    def test_execution_count_increments(self, seeded_store: InMemoryStore):
        engine = TraceEngine(store=seeded_store, rng_seed=42)
        assert engine.execution_count == 0
        flows = seeded_store.get_all("flow", limit=1)
        engine.execute_flow_by_id(flows[0]["id"])
        assert engine.execution_count == 1


class TestJaegerFormat:
    """Test Jaeger-compatible span output."""

    def test_jaeger_format_present(self, seeded_store: InMemoryStore):
        engine = TraceEngine(store=seeded_store, rng_seed=42)
        flows = seeded_store.get_all("flow", limit=1)
        trace = engine.execute_flow_by_id(flows[0]["id"])
        assert "spans_jaeger" in trace
        assert len(trace["spans_jaeger"]) == len(trace["spans"])

    def test_jaeger_span_fields(self, seeded_store: InMemoryStore):
        engine = TraceEngine(store=seeded_store, rng_seed=42)
        flows = seeded_store.get_all("flow", limit=1)
        trace = engine.execute_flow_by_id(flows[0]["id"])

        for span in trace["spans_jaeger"]:
            assert "traceID" in span
            assert "spanID" in span
            assert "operationName" in span
            assert "startTime" in span
            assert "duration" in span
            assert "process" in span
            assert "serviceName" in span["process"]


class TestSpanDataclass:
    """Test Span, SpanEvent, SpanLink dataclasses."""

    def test_span_to_dict(self):
        from datetime import datetime
        span = Span(
            trace_id="a" * 32,
            span_id="b" * 16,
            parent_span_id=None,
            operation_name="test-op",
            service_name="test-service",
            start_time=datetime(2025, 1, 1),
            end_time=datetime(2025, 1, 1, 0, 0, 1),
            duration_ns=1_000_000_000,
        )
        d = span.to_dict()
        assert d["traceId"] == "a" * 32
        assert d["spanId"] == "b" * 16
        assert d["operationName"] == "test-op"
        assert d["durationMs"] == 1000.0

    def test_span_event_to_dict(self):
        from datetime import datetime
        event = SpanEvent(
            name="test-event",
            timestamp=datetime(2025, 1, 1),
            attributes={"key": "value"},
        )
        d = event.to_dict()
        assert d["name"] == "test-event"
        assert d["attributes"]["key"] == "value"

    def test_span_jaeger_format(self):
        from datetime import datetime
        span = Span(
            trace_id="a" * 32,
            span_id="b" * 16,
            parent_span_id="c" * 16,
            operation_name="test-op",
            service_name="test-svc",
            start_time=datetime(2025, 1, 1),
            end_time=datetime(2025, 1, 1, 0, 0, 1),
            duration_ns=1_000_000_000,
        )
        j = span.to_jaeger_format()
        assert j["traceID"] == "a" * 32
        assert j["process"]["serviceName"] == "test-svc"
        assert len(j["references"]) == 1
