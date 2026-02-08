"use client";

import { useTraces } from "@/hooks/use-traces";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader, ErrorState, EmptyState } from "@/components/ui/loading";
import { shortId, formatDuration } from "@/lib/utils";
import { Activity } from "lucide-react";
import Link from "next/link";

export default function ObservabilityPage() {
  const { data, isLoading, isError, refetch } = useTraces({ limit: 50 });

  if (isLoading) return <PageLoader />;
  if (isError) return <ErrorState onRetry={() => refetch()} />;

  const traces = data ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Observability</h1>
        <p className="text-sm text-muted-fg mt-1">
          Distributed traces and span analysis
        </p>
      </div>

      {traces.length === 0 ? (
        <EmptyState
          icon={Activity}
          title="No traces"
          description="Execute a flow to generate traces."
        />
      ) : (
        <div className="space-y-2">
          <div className="grid grid-cols-6 gap-4 text-xs text-muted-fg uppercase font-medium px-4 py-2">
            <span className="col-span-1">Trace ID</span>
            <span className="col-span-2">Flow</span>
            <span>Status</span>
            <span className="text-right">Spans</span>
            <span className="text-right">Duration</span>
          </div>
          {traces.map((t) => (
            <Link key={t.trace_id} href={`/observability/${t.trace_id}`}>
              <Card className="hover:border-accent/30 transition-colors cursor-pointer py-3 px-4">
                <div className="grid grid-cols-6 gap-4 items-center text-sm">
                  <span className="col-span-1 font-mono text-xs text-muted-fg truncate">
                    {shortId(t.trace_id)}
                  </span>
                  <span className="col-span-2 truncate">
                    {t.flow_name}
                  </span>
                  <span>
                    <Badge
                      className={
                        t.status.includes("OK") || t.status === "ok"
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-red-100 text-red-800"
                      }
                    >
                      {t.status.replace("STATUS_CODE_", "")}
                    </Badge>
                  </span>
                  <span className="text-right font-mono">
                    {t.span_count}
                  </span>
                  <span className="text-right font-mono">
                    {formatDuration(t.duration_ms)}
                  </span>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
