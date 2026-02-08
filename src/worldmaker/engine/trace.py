"""OpenTelemetry-compatible trace span engine.

Generates distributed trace spans for Flow executions that are
indistinguishable from production telemetry. Each FlowStep hop
produces a span with:
- trace_id (shared across all spans in one execution)
- span_id (unique per hop)
- parent_span_id (links to calling span)
- operation_name (e.g., "POST /api/payment/process")
- service_name, service_type
- start_time, end_time, duration_ns
- status (OK, ERROR, UNSET)
- attributes (http.method, http.status_code, etc.)
- events (logs within a span)
- resource attributes (service.name, service.version, deployment.environment)
"""
from __future__ import annotations
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


def _generate_trace_id() -> str:
    """Generate a 32-char hex trace ID (128-bit, OTel standard)."""
    return uuid4().hex

def _generate_span_id() -> str:
    """Generate a 16-char hex span ID (64-bit, OTel standard)."""
    return uuid4().hex[:16]


@dataclass
class SpanEvent:
    """An event (log line) within a span."""
    name: str
    timestamp: datetime
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "timestamp": self.timestamp.isoformat() + "Z",
            "attributes": self.attributes,
        }


@dataclass
class SpanLink:
    """A link to another span (for async/batch relationships)."""
    trace_id: str
    span_id: str
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "traceId": self.trace_id,
            "spanId": self.span_id,
            "attributes": self.attributes,
        }


@dataclass
class Span:
    """OpenTelemetry-compatible span."""
    trace_id: str
    span_id: str
    parent_span_id: str | None
    operation_name: str
    service_name: str
    service_type: str = "rest"
    kind: str = "SPAN_KIND_CLIENT"
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime | None = None
    duration_ns: int = 0
    status_code: str = "STATUS_CODE_OK"
    status_message: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[SpanEvent] = field(default_factory=list)
    links: list[SpanLink] = field(default_factory=list)
    resource: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to OTel-compatible JSON format."""
        return {
            "traceId": self.trace_id,
            "spanId": self.span_id,
            "parentSpanId": self.parent_span_id or "",
            "operationName": self.operation_name,
            "serviceName": self.service_name,
            "kind": self.kind,
            "startTimeUnixNano": int(self.start_time.timestamp() * 1e9),
            "endTimeUnixNano": int(self.end_time.timestamp() * 1e9) if self.end_time else 0,
            "durationNano": self.duration_ns,
            "durationMs": round(self.duration_ns / 1e6, 2),
            "status": {
                "code": self.status_code,
                "message": self.status_message,
            },
            "attributes": self.attributes,
            "events": [e.to_dict() for e in self.events],
            "links": [l.to_dict() for l in self.links],
            "resource": {
                "attributes": self.resource,
            },
        }

    def to_jaeger_format(self) -> dict[str, Any]:
        """Serialize to Jaeger-compatible format."""
        return {
            "traceID": self.trace_id,
            "spanID": self.span_id,
            "parentSpanID": self.parent_span_id or "0" * 16,
            "operationName": self.operation_name,
            "references": [
                {"refType": "CHILD_OF", "traceID": self.trace_id, "spanID": self.parent_span_id}
            ] if self.parent_span_id else [],
            "startTime": int(self.start_time.timestamp() * 1e6),
            "duration": self.duration_ns // 1000,
            "tags": [
                {"key": k, "type": _jaeger_tag_type(v), "value": v}
                for k, v in self.attributes.items()
            ],
            "logs": [
                {
                    "timestamp": int(e.timestamp.timestamp() * 1e6),
                    "fields": [{"key": k, "type": _jaeger_tag_type(v), "value": v}
                               for k, v in e.attributes.items()],
                }
                for e in self.events
            ],
            "process": {
                "serviceName": self.service_name,
                "tags": [
                    {"key": k, "type": _jaeger_tag_type(v), "value": v}
                    for k, v in self.resource.items()
                ],
            },
        }


def _jaeger_tag_type(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int64"
    if isinstance(value, float):
        return "float64"
    return "string"


OPERATION_PATTERNS: dict[str, list[str]] = {
    "rest": [
        "POST /api/{service}/process",
        "GET /api/{service}/status",
        "PUT /api/{service}/update",
        "POST /api/{service}/validate",
        "GET /api/{service}/health",
    ],
    "grpc": [
        "{service}.{Service}Service/Process",
        "{service}.{Service}Service/Get",
        "{service}.{Service}Service/Update",
        "{service}.{Service}Service/Validate",
    ],
    "event_driven": [
        "PUBLISH {service}.event.processed",
        "CONSUME {service}.event.received",
        "PUBLISH {service}.event.completed",
    ],
    "graphql": [
        "QUERY {service}.query",
        "MUTATION {service}.mutate",
    ],
    "batch": [
        "BATCH {service}.process_batch",
        "BATCH {service}.aggregate",
    ],
}


class TraceEngine:
    """Generates OpenTelemetry-compatible traces for Flow executions.

    When a Flow is executed, the engine:
    1. Creates a root span for the entire flow
    2. Walks each FlowStep in order
    3. For each hop, creates client + server span pair
    4. Simulates realistic latency based on service type
    5. Optionally injects failures based on failure mode config
    6. Returns a complete trace with all spans
    """

    def __init__(self, store: Any = None, rng_seed: int | None = None):
        self._store = store
        self._rng = random.Random(rng_seed)
        self._execution_count = 0

    def execute_flow(
        self,
        flow: dict[str, Any],
        flow_steps: list[dict[str, Any]],
        services: dict[str, dict[str, Any]],
        environment: str = "prod",
        inject_failure: bool = False,
        failure_step: int | None = None,
    ) -> dict[str, Any]:
        """Execute a flow and generate a complete OTel trace.

        Args:
            flow: The Flow entity dict
            flow_steps: Ordered list of FlowStep dicts
            services: Dict of service_id -> service dict
            environment: Deployment environment
            inject_failure: Whether to inject a failure
            failure_step: Which step to fail at (random if None)

        Returns:
            Complete trace with all spans, metadata, and timing
        """
        self._execution_count += 1
        trace_id = _generate_trace_id()
        execution_id = str(uuid4())
        base_time = datetime.utcnow()

        # Sort steps by step_number
        sorted_steps = sorted(flow_steps, key=lambda s: s.get("step_number", 0))

        # Decide failure point
        fail_at = None
        if inject_failure:
            fail_at = failure_step if failure_step is not None else self._rng.randint(0, len(sorted_steps) - 1)

        # Root span for the entire flow
        root_span_id = _generate_span_id()
        total_start = base_time
        spans: list[Span] = []
        current_time = base_time
        total_status = "STATUS_CODE_OK"
        error_info: dict[str, Any] | None = None

        for i, step in enumerate(sorted_steps):
            from_svc = services.get(step.get("from_service_id", ""), {})
            to_svc = services.get(step.get("to_service_id", ""), {})

            from_name = from_svc.get("name", f"service-{i}")
            to_name = to_svc.get("name", f"service-{i+1}")
            svc_type = to_svc.get("service_type", "rest")

            # Determine if this step fails
            step_fails = (fail_at == i)

            # Generate realistic latency
            latency_ms = self._simulate_latency(svc_type, step_fails)
            latency_ns = int(latency_ms * 1e6)

            # Client span (from calling service)
            client_span_id = _generate_span_id()
            client_start = current_time
            client_end = client_start + timedelta(milliseconds=latency_ms)

            operation = self._generate_operation(to_name, svc_type)

            client_span = Span(
                trace_id=trace_id,
                span_id=client_span_id,
                parent_span_id=root_span_id,
                operation_name=operation,
                service_name=from_name,
                service_type=svc_type,
                kind="SPAN_KIND_CLIENT",
                start_time=client_start,
                end_time=client_end,
                duration_ns=latency_ns,
                status_code="STATUS_CODE_ERROR" if step_fails else "STATUS_CODE_OK",
                status_message=f"Error calling {to_name}" if step_fails else "",
                attributes=self._build_client_attributes(from_name, to_name, svc_type, step, step_fails),
                resource=self._build_resource(from_name, from_svc, environment),
            )

            # Server span (on receiving service)
            server_span_id = _generate_span_id()
            network_delay_ms = self._rng.uniform(0.5, 5.0)
            server_start = client_start + timedelta(milliseconds=network_delay_ms)
            processing_ms = latency_ms - network_delay_ms * 2
            server_end = server_start + timedelta(milliseconds=max(processing_ms, 1))

            server_span = Span(
                trace_id=trace_id,
                span_id=server_span_id,
                parent_span_id=client_span_id,
                operation_name=operation,
                service_name=to_name,
                service_type=svc_type,
                kind="SPAN_KIND_SERVER",
                start_time=server_start,
                end_time=server_end,
                duration_ns=int(max(processing_ms, 1) * 1e6),
                status_code="STATUS_CODE_ERROR" if step_fails else "STATUS_CODE_OK",
                status_message=self._generate_error_message(to_name) if step_fails else "",
                attributes=self._build_server_attributes(to_name, svc_type, step, step_fails),
                events=self._generate_span_events(to_name, svc_type, step_fails, server_start),
                resource=self._build_resource(to_name, to_svc, environment),
            )

            spans.extend([client_span, server_span])

            if step_fails:
                total_status = "STATUS_CODE_ERROR"
                error_info = {
                    "step": i,
                    "from_service": from_name,
                    "to_service": to_name,
                    "error": server_span.status_message,
                }
                # Don't continue after failure
                break

            # Advance time for next step
            current_time = client_end + timedelta(milliseconds=self._rng.uniform(0.1, 2.0))

        total_end = current_time
        total_duration_ns = int((total_end - total_start).total_seconds() * 1e9)

        # Root span
        root_span = Span(
            trace_id=trace_id,
            span_id=root_span_id,
            parent_span_id=None,
            operation_name=f"FLOW {flow.get('name', 'unknown')}",
            service_name="worldmaker-flow-engine",
            service_type="internal",
            kind="SPAN_KIND_INTERNAL",
            start_time=total_start,
            end_time=total_end,
            duration_ns=total_duration_ns,
            status_code=total_status,
            attributes={
                "flow.id": flow.get("id", ""),
                "flow.name": flow.get("name", ""),
                "flow.type": flow.get("flow_type", ""),
                "flow.steps_total": len(sorted_steps),
                "flow.steps_completed": len(spans) // 2,
                "execution.id": execution_id,
                "execution.environment": environment,
            },
            resource={
                "service.name": "worldmaker-flow-engine",
                "service.version": "0.1.0",
                "deployment.environment": environment,
            },
        )

        # Insert root span at the beginning
        all_spans = [root_span] + spans

        # Build the complete trace
        trace = {
            "trace_id": trace_id,
            "execution_id": execution_id,
            "flow_id": flow.get("id", ""),
            "flow_name": flow.get("name", ""),
            "environment": environment,
            "start_time": total_start.isoformat() + "Z",
            "end_time": total_end.isoformat() + "Z",
            "duration_ms": round(total_duration_ns / 1e6, 2),
            "status": total_status,
            "span_count": len(all_spans),
            "error": error_info,
            "spans": [s.to_dict() for s in all_spans],
            "spans_jaeger": [s.to_jaeger_format() for s in all_spans],
        }

        # Store in memory if store is available
        if self._store:
            self._store.store_trace(trace)
            self._store.store_spans([s.to_dict() for s in all_spans])

        return trace

    def execute_flow_by_id(self, flow_id: str, **kwargs: Any) -> dict[str, Any]:
        """Execute a flow by looking it up in the store."""
        if not self._store:
            raise RuntimeError("Store not configured")

        flow = self._store.get("flow", flow_id)
        if not flow:
            raise ValueError(f"Flow not found: {flow_id}")

        # Get flow steps
        all_steps = self._store.get_all("flow_step", limit=10000,
                                         filters={"flow_id": flow_id})

        # Build service lookup
        services: dict[str, dict[str, Any]] = {}
        for step in all_steps:
            for key in ("from_service_id", "to_service_id"):
                svc_id = step.get(key, "")
                if svc_id and svc_id not in services:
                    svc = self._store.get("service", svc_id)
                    if svc:
                        services[svc_id] = svc

        return self.execute_flow(flow, all_steps, services, **kwargs)

    def execute_all_flows(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Execute all flows in the store and return traces."""
        if not self._store:
            raise RuntimeError("Store not configured")

        flows = self._store.get_all("flow", limit=10000)
        traces = []
        for flow in flows:
            try:
                trace = self.execute_flow_by_id(flow["id"], **kwargs)
                traces.append(trace)
            except Exception as e:
                logger.warning("Failed to execute flow %s: %s", flow.get("name"), e)

        return traces

    def _simulate_latency(self, service_type: str, is_error: bool) -> float:
        """Generate realistic latency in milliseconds."""
        base_latency = {
            "rest": (5, 150),
            "grpc": (1, 50),
            "event_driven": (10, 500),
            "graphql": (10, 200),
            "batch": (100, 5000),
        }.get(service_type, (5, 100))

        latency = self._rng.uniform(*base_latency)

        if is_error:
            # Errors often come with timeout-like latency
            latency *= self._rng.uniform(2, 10)

        # Occasional latency spike (5% chance)
        if self._rng.random() < 0.05:
            latency *= self._rng.uniform(3, 8)

        return round(latency, 2)

    def _generate_operation(self, service_name: str, service_type: str) -> str:
        """Generate a realistic operation name."""
        patterns = OPERATION_PATTERNS.get(service_type, OPERATION_PATTERNS["rest"])
        pattern = self._rng.choice(patterns)

        # Clean service name for use in operation
        clean = service_name.lower().replace("service", "").replace("-", "").strip()
        capitalized = clean.capitalize() if clean else "Default"

        return pattern.format(service=clean or "default", Service=capitalized)

    def _generate_error_message(self, service_name: str) -> str:
        errors = [
            f"Connection refused: {service_name}:8080",
            f"Timeout after 30000ms calling {service_name}",
            f"HTTP 503 Service Unavailable from {service_name}",
            f"Circuit breaker OPEN for {service_name}",
            f"HTTP 500 Internal Server Error from {service_name}",
            f"gRPC UNAVAILABLE: {service_name} not responding",
            f"Connection pool exhausted for {service_name}",
        ]
        return self._rng.choice(errors)

    def _build_client_attributes(self, from_svc: str, to_svc: str,
                                  svc_type: str, step: dict, is_error: bool) -> dict[str, Any]:
        attrs: dict[str, Any] = {
            "peer.service": to_svc,
            "net.peer.name": f"{to_svc.lower().replace(' ', '-')}.internal",
            "net.peer.port": 8080 if svc_type == "rest" else 50051 if svc_type == "grpc" else 9092,
            "flow.step_number": step.get("step_number", 0),
        }

        if svc_type == "rest":
            attrs.update({
                "http.method": self._rng.choice(["POST", "GET", "PUT"]),
                "http.status_code": self._rng.choice([500, 502, 503, 504]) if is_error else 200,
                "http.url": f"http://{to_svc.lower()}.internal:8080/api/process",
            })
        elif svc_type == "grpc":
            attrs.update({
                "rpc.system": "grpc",
                "rpc.service": f"{to_svc}Service",
                "rpc.method": "Process",
                "rpc.grpc.status_code": 14 if is_error else 0,
            })
        elif svc_type == "event_driven":
            attrs.update({
                "messaging.system": "kafka",
                "messaging.destination": f"{to_svc.lower()}.events",
                "messaging.operation": "publish",
            })

        return attrs

    def _build_server_attributes(self, service_name: str, svc_type: str,
                                  step: dict, is_error: bool) -> dict[str, Any]:
        attrs: dict[str, Any] = {
            "flow.step_number": step.get("step_number", 0),
        }

        if svc_type == "rest":
            attrs.update({
                "http.method": "POST",
                "http.status_code": self._rng.choice([500, 502, 503]) if is_error else 200,
                "http.route": "/api/process",
                "http.scheme": "http",
            })
        elif svc_type == "grpc":
            attrs.update({
                "rpc.system": "grpc",
                "rpc.grpc.status_code": 14 if is_error else 0,
            })

        return attrs

    def _build_resource(self, service_name: str, service: dict,
                        environment: str) -> dict[str, Any]:
        return {
            "service.name": service_name,
            "service.version": service.get("api_version", "v1"),
            "service.namespace": "worldmaker",
            "deployment.environment": environment,
            "host.name": f"{service_name.lower().replace(' ', '-')}-{self._rng.randint(1, 5):02d}",
            "os.type": "linux",
            "process.runtime.name": service.get("metadata", {}).get("language", "python"),
            "telemetry.sdk.name": "worldmaker-synthetic",
            "telemetry.sdk.version": "0.1.0",
        }

    def _generate_span_events(self, service_name: str, svc_type: str,
                               is_error: bool, base_time: datetime) -> list[SpanEvent]:
        events: list[SpanEvent] = []

        # Request received event
        events.append(SpanEvent(
            name="request.received",
            timestamp=base_time + timedelta(milliseconds=0.1),
            attributes={"service.name": service_name},
        ))

        if is_error:
            events.append(SpanEvent(
                name="exception",
                timestamp=base_time + timedelta(milliseconds=self._rng.uniform(5, 50)),
                attributes={
                    "exception.type": self._rng.choice([
                        "ConnectionRefusedError",
                        "TimeoutError",
                        "ServiceUnavailableError",
                        "CircuitBreakerOpenError",
                    ]),
                    "exception.message": f"Failed to process request in {service_name}",
                    "exception.stacktrace": f"  File \"{service_name.lower()}/handler.py\", line 42\n    raise ServiceUnavailableError()",
                },
            ))
        else:
            events.append(SpanEvent(
                name="request.processed",
                timestamp=base_time + timedelta(milliseconds=self._rng.uniform(2, 20)),
                attributes={"service.name": service_name, "status": "ok"},
            ))

        return events

    @property
    def execution_count(self) -> int:
        return self._execution_count
