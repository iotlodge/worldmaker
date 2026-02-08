"use client";

import { useParams } from "next/navigation";
import { useTrace } from "@/hooks/use-traces";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader, ErrorState } from "@/components/ui/loading";
import { shortId, formatDurationUs, cn } from "@/lib/utils";
import { Activity } from "lucide-react";
import { useState } from "react";

const KIND_COLORS: Record<string, string> = {
  CLIENT: "bg-blue-500",
  SERVER: "bg-emerald-500",
  INTERNAL: "bg-purple-500",
};

export default function TraceDetailPage() {
  const { traceId } = useParams<{ traceId: string }>();
  const { data, isLoading, isError, refetch } = useTrace(traceId);
  const [selectedSpan, setSelectedSpan] = useState<string | null>(null);

  if (isLoading) return <PageLoader />;
  if (isError) return <ErrorState onRetry={() => refetch()} />;
  if (!data) return <ErrorState message="Trace not found" />;

  // Defensive: ensure spans is always a real array of normalized Span objects
  const rawSpans = data.spans;
  const spans = Array.isArray(rawSpans) ? rawSpans : [];
  if (spans.length === 0)
    return <ErrorState message="No spans in this trace" />;

  // Sort spans by start time
  const sorted = [...spans].sort(
    (a, b) =>
      new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
  );

  // Calculate waterfall dimensions from sorted spans
  const minStart = new Date(sorted[0].start_time).getTime();
  const maxEnd = Math.max(
    ...sorted.map((s) => new Date(s.end_time).getTime())
  );
  const totalDuration = maxEnd - minStart || 1; // avoid division by zero

  const selected = selectedSpan
    ? spans.find((s) => s.span_id === selectedSpan)
    : null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-3">
          <Activity className="w-6 h-6 text-accent" />
          Trace {shortId(data.trace_id)}
        </h1>
        <p className="text-sm text-muted-fg mt-1">
          {spans.length} spans • {(totalDuration / 1000).toFixed(1)}ms total
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Waterfall */}
        <Card className="lg:col-span-2 overflow-x-auto">
          <CardTitle>Span Waterfall</CardTitle>
          <CardContent className="mt-4">
            <div className="space-y-1 min-w-[500px]">
              {sorted.map((span) => {
                const start = new Date(span.start_time).getTime() - minStart;
                const duration =
                  new Date(span.end_time).getTime() -
                  new Date(span.start_time).getTime();
                const leftPct = totalDuration > 0 ? (start / totalDuration) * 100 : 0;
                const widthPct =
                  totalDuration > 0
                    ? Math.max((duration / totalDuration) * 100, 0.5)
                    : 100;

                const isError =
                  span.status_code === "ERROR" ||
                  span.status_code === "error";

                return (
                  <button
                    key={span.span_id}
                    onClick={() => setSelectedSpan(span.span_id)}
                    className={cn(
                      "flex items-center gap-3 w-full text-left py-1.5 px-2 rounded transition-colors text-xs",
                      selectedSpan === span.span_id
                        ? "bg-accent/10"
                        : "hover:bg-muted"
                    )}
                  >
                    <span className="w-40 truncate shrink-0 text-muted-fg">
                      {span.service_name}
                    </span>
                    <div className="flex-1 relative h-5">
                      <div
                        className={cn(
                          "absolute top-0 h-full rounded-sm",
                          isError
                            ? "bg-red-500"
                            : KIND_COLORS[span.kind] ?? "bg-gray-400"
                        )}
                        style={{
                          left: `${leftPct}%`,
                          width: `${widthPct}%`,
                        }}
                      />
                    </div>
                    <span className="w-16 text-right font-mono shrink-0">
                      {formatDurationUs(span.duration_us)}
                    </span>
                  </button>
                );
              })}
            </div>

            {/* Legend */}
            <div className="flex items-center gap-4 mt-4 text-xs text-muted-fg">
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-sm bg-blue-500" /> CLIENT
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-sm bg-emerald-500" /> SERVER
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-sm bg-purple-500" /> INTERNAL
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-sm bg-red-500" /> ERROR
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Span detail panel */}
        <Card>
          <CardTitle>
            {selected ? "Span Detail" : "Select a Span"}
          </CardTitle>
          <CardContent className="mt-3">
            {!selected ? (
              <p className="text-sm text-muted-fg py-8 text-center">
                Click a span in the waterfall to view details
              </p>
            ) : (
              <div className="space-y-3 text-sm">
                <DetailRow label="Operation" value={selected.operation_name} />
                <DetailRow label="Service" value={selected.service_name} />
                <DetailRow
                  label="Kind"
                  value={
                    <Badge variant="outline">{selected.kind}</Badge>
                  }
                />
                <DetailRow
                  label="Status"
                  value={
                    <Badge
                      className={
                        selected.status_code === "ERROR"
                          ? "bg-red-100 text-red-800"
                          : "bg-emerald-100 text-emerald-800"
                      }
                    >
                      {selected.status_code}
                    </Badge>
                  }
                />
                <DetailRow
                  label="Duration"
                  value={formatDurationUs(selected.duration_us)}
                  mono
                />
                <DetailRow
                  label="Span ID"
                  value={shortId(selected.span_id)}
                  mono
                />
                {selected.parent_span_id && (
                  <DetailRow
                    label="Parent"
                    value={shortId(selected.parent_span_id)}
                    mono
                  />
                )}

                {/* Attributes */}
                {Object.keys(selected.attributes).length > 0 && (
                  <div className="pt-2 border-t border-card-border">
                    <p className="text-xs text-muted-fg font-medium mb-2">
                      Attributes
                    </p>
                    <div className="space-y-1.5">
                      {Object.entries(selected.attributes).map(
                        ([key, val]) => (
                          <div
                            key={key}
                            className="flex justify-between text-xs"
                          >
                            <span className="text-muted-fg truncate">
                              {key}
                            </span>
                            <span className="font-mono truncate ml-2">
                              {String(val)}
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

                {/* Events */}
                {selected.events.length > 0 && (
                  <div className="pt-2 border-t border-card-border">
                    <p className="text-xs text-muted-fg font-medium mb-2">
                      Events ({selected.events.length})
                    </p>
                    <div className="space-y-1">
                      {selected.events.map((evt, i) => (
                        <p key={i} className="text-xs">
                          {evt.name}
                        </p>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function DetailRow({
  label,
  value,
  mono,
}: {
  label: string;
  value: React.ReactNode;
  mono?: boolean;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted-fg">{label}</span>
      <span className={mono ? "font-mono" : ""}>{value}</span>
    </div>
  );
}
