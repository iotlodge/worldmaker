"""Flow management and trace execution endpoints."""
from __future__ import annotations

try:
    from fastapi import APIRouter, Depends, Path, Query, HTTPException, Body
    from typing import Any, Optional

    from worldmaker.api.deps import get_memory_store, get_trace_engine
    from worldmaker.db.memory import InMemoryStore
    from worldmaker.engine.trace import TraceEngine

    router = APIRouter()

    # ── Flow CRUD ──────────────────────────────────────────────────────

    @router.get("/flows")
    async def list_flows(
        status: Optional[str] = Query(None, description="Filter by status"),
        flow_type: Optional[str] = Query(None, description="Filter by flow type"),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """List all flows with optional filtering."""
        filters: dict[str, Any] = {}
        if status:
            filters["status"] = status
        if flow_type:
            filters["flow_type"] = flow_type
        filt = filters if filters else None

        flows = store.get_all("flow", limit=limit, offset=offset, filters=filt)
        total = store.count("flow", filters=filt)
        return {"total": total, "limit": limit, "offset": offset, "flows": flows}

    @router.get("/flows/{flow_id}")
    async def get_flow(
        flow_id: str = Path(..., description="Flow ID"),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get detailed information about a flow including its steps."""
        flow = store.get("flow", flow_id)
        if not flow:
            raise HTTPException(404, f"Flow {flow_id} not found")

        steps = store.get_all("flow_step", limit=1000,
                               filters={"flow_id": flow_id})
        sorted_steps = sorted(steps, key=lambda s: s.get("step_number", 0))

        for step in sorted_steps:
            from_svc = store.get("service", step.get("from_service_id", ""))
            to_svc = store.get("service", step.get("to_service_id", ""))
            step["from_service_name"] = from_svc.get("name", "unknown") if from_svc else "unknown"
            step["to_service_name"] = to_svc.get("name", "unknown") if to_svc else "unknown"

        flow["steps_detail"] = sorted_steps
        flow["step_count"] = len(sorted_steps)
        return flow

    @router.post("/flows", status_code=201)
    async def create_flow(
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Create a new flow."""
        return store.create("flow", data)

    @router.put("/flows/{flow_id}")
    async def update_flow(
        flow_id: str = Path(...),
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Update a flow."""
        result = store.update("flow", flow_id, data)
        if not result:
            raise HTTPException(404, f"Flow {flow_id} not found")
        return result

    @router.delete("/flows/{flow_id}")
    async def delete_flow(
        flow_id: str = Path(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Delete a flow."""
        if not store.delete("flow", flow_id):
            raise HTTPException(404, f"Flow {flow_id} not found")
        return {"deleted": True, "id": flow_id}

    # ── Flow Steps ─────────────────────────────────────────────────────

    @router.post("/flows/{flow_id}/steps", status_code=201)
    async def add_flow_step(
        flow_id: str = Path(...),
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Add a step to a flow."""
        flow = store.get("flow", flow_id)
        if not flow:
            raise HTTPException(404, f"Flow {flow_id} not found")
        data["flow_id"] = flow_id
        return store.create("flow_step", data)

    # ── Trace Execution ────────────────────────────────────────────────

    @router.post("/flows/{flow_id}/execute")
    async def execute_flow(
        flow_id: str = Path(..., description="Flow ID to execute"),
        environment: str = Query("prod", description="Deployment environment"),
        inject_failure: bool = Query(False, description="Inject a failure"),
        failure_step: Optional[int] = Query(None, description="Step to fail at"),
        store: InMemoryStore = Depends(get_memory_store),
        engine: TraceEngine = Depends(get_trace_engine),
    ) -> dict[str, Any]:
        """Execute a flow and generate an OpenTelemetry-compatible trace.

        Creates a full distributed trace with client/server span pairs
        for every hop in the flow. The trace is stored and can be
        retrieved via GET /flows/{flow_id}/traces.
        """
        flow = store.get("flow", flow_id)
        if not flow:
            raise HTTPException(404, f"Flow {flow_id} not found")

        all_steps = store.get_all("flow_step", limit=10000,
                                   filters={"flow_id": flow_id})
        if not all_steps:
            raise HTTPException(400, f"Flow {flow_id} has no steps")

        services: dict[str, dict[str, Any]] = {}
        for step in all_steps:
            for key in ("from_service_id", "to_service_id"):
                svc_id = step.get(key, "")
                if svc_id and svc_id not in services:
                    svc = store.get("service", svc_id)
                    if svc:
                        services[svc_id] = svc

        trace = engine.execute_flow(
            flow=flow,
            flow_steps=all_steps,
            services=services,
            environment=environment,
            inject_failure=inject_failure,
            failure_step=failure_step,
        )

        return {
            "trace_id": trace["trace_id"],
            "execution_id": trace["execution_id"],
            "flow_id": trace["flow_id"],
            "flow_name": trace["flow_name"],
            "environment": trace["environment"],
            "duration_ms": trace["duration_ms"],
            "status": trace["status"],
            "span_count": trace["span_count"],
            "error": trace["error"],
        }

    @router.post("/flows/execute-all")
    async def execute_all_flows(
        environment: str = Query("prod"),
        store: InMemoryStore = Depends(get_memory_store),
        engine: TraceEngine = Depends(get_trace_engine),
    ) -> dict[str, Any]:
        """Execute all flows and generate traces."""
        traces = engine.execute_all_flows(environment=environment)
        return {
            "total_flows_executed": len(traces),
            "environment": environment,
            "traces": [
                {
                    "trace_id": t["trace_id"],
                    "flow_name": t["flow_name"],
                    "duration_ms": t["duration_ms"],
                    "status": t["status"],
                    "span_count": t["span_count"],
                }
                for t in traces
            ],
        }

    # ── Trace & Span Retrieval ─────────────────────────────────────────

    @router.get("/flows/{flow_id}/traces")
    async def get_flow_traces(
        flow_id: str = Path(..., description="Flow ID"),
        limit: int = Query(100, ge=1, le=1000),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get execution traces for a specific flow."""
        traces = store.get_traces(flow_id=flow_id, limit=limit)
        return {
            "flow_id": flow_id,
            "total": len(traces),
            "traces": [
                {
                    "trace_id": t["trace_id"],
                    "execution_id": t.get("execution_id"),
                    "flow_name": t.get("flow_name"),
                    "duration_ms": t.get("duration_ms"),
                    "status": t.get("status"),
                    "span_count": t.get("span_count"),
                    "start_time": t.get("start_time"),
                    "end_time": t.get("end_time"),
                    "error": t.get("error"),
                }
                for t in traces
            ],
        }

    @router.get("/traces")
    async def list_all_traces(
        limit: int = Query(100, ge=1, le=1000),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """List all execution traces."""
        traces = store.get_traces(limit=limit)
        return {
            "total": len(traces),
            "traces": [
                {
                    "trace_id": t["trace_id"],
                    "flow_id": t.get("flow_id"),
                    "flow_name": t.get("flow_name"),
                    "duration_ms": t.get("duration_ms"),
                    "status": t.get("status"),
                    "span_count": t.get("span_count"),
                }
                for t in traces
            ],
        }

    @router.get("/traces/{trace_id}/spans")
    async def get_trace_spans(
        trace_id: str = Path(..., description="Trace ID"),
        format: str = Query("otel", pattern="^(otel|jaeger)$",
                            description="Span format"),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get all spans for a specific trace. Supports OTel and Jaeger formats."""
        all_traces = store.get_traces(limit=10000)
        trace = next((t for t in all_traces if t["trace_id"] == trace_id), None)
        if not trace:
            raise HTTPException(404, f"Trace {trace_id} not found")

        if format == "jaeger":
            spans = trace.get("spans_jaeger", [])
        else:
            spans = trace.get("spans", [])

        return {
            "trace_id": trace_id,
            "format": format,
            "span_count": len(spans),
            "spans": spans,
        }

except ImportError:
    router = None
