"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import type { Span, SpanEvent, SpanLink } from "@/lib/types";

// ── OTel → Normalized Span mapper ──────────────────────────────────────────
// The backend emits OTel-format spans (camelCase, nanosecond timestamps,
// prefixed enums).  The frontend Span type uses snake_case, ISO dates, and
// clean enum values.  This mapper handles both formats defensively.

/* eslint-disable @typescript-eslint/no-explicit-any */
function normalizeSpan(raw: any): Span {
  // Timestamps — OTel uses nanoseconds, fall back to ISO strings if present
  const startNano = raw.startTimeUnixNano;
  const endNano = raw.endTimeUnixNano;
  const startMs = startNano ? startNano / 1_000_000 : 0;
  const endMs = endNano ? endNano / 1_000_000 : 0;

  const startTime =
    raw.start_time ?? (startMs ? new Date(startMs).toISOString() : "");
  const endTime =
    raw.end_time ?? (endMs ? new Date(endMs).toISOString() : "");

  // Duration — prefer durationNano → microseconds, fall back to durationMs
  const durationUs =
    raw.duration_us ??
    ((raw.durationNano ? raw.durationNano / 1_000 : 0) ||
    (raw.durationMs ? raw.durationMs * 1_000 : 0));

  // Kind — strip "SPAN_KIND_" prefix
  const rawKind: string = raw.kind ?? "";
  const kind = rawKind.replace("SPAN_KIND_", "") || "INTERNAL";

  // Status — backend nests it as { code, message }
  const statusObj = raw.status ?? {};
  const rawCode: string =
    raw.status_code ??
    (typeof statusObj === "string" ? statusObj : statusObj.code ?? "");
  const statusCode = rawCode.replace("STATUS_CODE_", "") || "UNSET";

  // Events
  const events: SpanEvent[] = (raw.events ?? []).map((e: any) => ({
    name: e.name ?? "",
    timestamp: e.timestamp ?? "",
    attributes: e.attributes ?? {},
  }));

  // Links
  const links: SpanLink[] = (raw.links ?? []).map((l: any) => ({
    trace_id: l.traceId ?? l.trace_id ?? "",
    span_id: l.spanId ?? l.span_id ?? "",
    attributes: l.attributes ?? {},
  }));

  return {
    span_id: raw.spanId ?? raw.span_id ?? "",
    trace_id: raw.traceId ?? raw.trace_id ?? "",
    parent_span_id: raw.parentSpanId ?? raw.parent_span_id ?? undefined,
    operation_name: raw.operationName ?? raw.operation_name ?? "",
    service_name: raw.serviceName ?? raw.service_name ?? "",
    kind: kind as Span["kind"],
    start_time: startTime,
    end_time: endTime,
    duration_us: durationUs,
    status_code: statusCode,
    attributes: raw.attributes ?? {},
    events,
    links,
  };
}
/* eslint-enable @typescript-eslint/no-explicit-any */

// ── Hooks ──────────────────────────────────────────────────────────────────

export function useTraces(params?: { limit?: number }) {
  return useQuery({
    queryKey: ["traces", params],
    queryFn: () => api.traces.list(params),
    select: (data) => data.traces,
  });
}

export function useTrace(traceId: string) {
  return useQuery({
    queryKey: ["traces", traceId],
    queryFn: () => api.traces.get(traceId),
    select: (data) => ({
      ...data,
      spans: Array.isArray(data.spans)
        ? data.spans.map(normalizeSpan)
        : [],
    }),
    enabled: !!traceId,
  });
}
