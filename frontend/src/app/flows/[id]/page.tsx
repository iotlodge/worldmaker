"use client";

import { useParams } from "next/navigation";
import { useFlow, useFlowTraces, useExecuteFlow } from "@/hooks/use-flows";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageLoader, ErrorState } from "@/components/ui/loading";
import { statusColor, shortId, formatDuration, formatDate } from "@/lib/utils";
import { Workflow, Play, Activity } from "lucide-react";
import Link from "next/link";

export default function FlowDetailPage() {
  const { id } = useParams<{ id: string }>();
  const flow = useFlow(id);
  const traces = useFlowTraces(id);
  const execute = useExecuteFlow();

  if (flow.isLoading) return <PageLoader />;
  if (flow.isError) return <ErrorState onRetry={() => flow.refetch()} />;
  if (!flow.data) return <ErrorState message="Flow not found" />;

  const f = flow.data;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
            <Workflow className="w-6 h-6 text-purple-500" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">{f.name}</h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge className={statusColor(f.status)}>{f.status}</Badge>
              <span className="text-sm text-muted-fg">{f.flow_type}</span>
              <span className="text-xs font-mono text-muted-fg">
                {shortId(f.id)}
              </span>
            </div>
          </div>
        </div>
        <Button
          onClick={() => execute.mutate({ id: f.id })}
          disabled={execute.isPending}
        >
          <Play className="w-4 h-4" />
          {execute.isPending ? "Executing..." : "Execute Flow"}
        </Button>
      </div>

      {f.description && (
        <p className="text-sm text-muted-fg">{f.description}</p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="text-center">
          <p className="text-3xl font-bold">{f.steps?.length ?? 0}</p>
          <p className="text-xs text-muted-fg mt-1">Steps</p>
        </Card>
        <Card className="text-center">
          <p className="text-3xl font-bold">
            {f.average_duration_ms ? formatDuration(f.average_duration_ms) : "—"}
          </p>
          <p className="text-xs text-muted-fg mt-1">Avg Duration</p>
        </Card>
        <Card className="text-center">
          <p className="text-3xl font-bold">{traces.data?.length ?? 0}</p>
          <p className="text-xs text-muted-fg mt-1">Traces</p>
        </Card>
      </div>

      {/* Execution history */}
      <Card>
        <CardTitle>
          <span className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-muted-fg" />
            Execution History
          </span>
        </CardTitle>
        <CardContent className="mt-3">
          {!traces.data || traces.data.length === 0 ? (
            <p className="text-sm text-muted-fg py-4 text-center">
              No traces yet. Execute the flow to generate traces.
            </p>
          ) : (
            <div className="space-y-1">
              {traces.data.slice(0, 20).map((t) => (
                <Link
                  key={t.trace_id}
                  href={`/observability/${t.trace_id}`}
                  className="flex items-center justify-between py-2 px-2 rounded hover:bg-muted text-sm transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-muted-fg">
                      {shortId(t.trace_id)}
                    </span>
                    <Badge
                      className={
                        t.status === "ok" || t.status === "OK"
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-red-100 text-red-800"
                      }
                    >
                      {t.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-muted-fg">
                    <span>{t.span_count} spans</span>
                    <span>{formatDuration(t.duration_ms)}</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Last execution result */}
      {execute.data && (
        <Card className="border-emerald-200 dark:border-emerald-900/50">
          <CardTitle>
            <span className="text-emerald-500">Latest Execution Result</span>
          </CardTitle>
          <CardContent className="mt-3 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-fg">Trace ID</span>
              <Link
                href={`/observability/${execute.data.trace_id}`}
                className="font-mono text-accent hover:underline"
              >
                {shortId(execute.data.trace_id)}
              </Link>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-fg">Duration</span>
              <span>{formatDuration(execute.data.duration_ms)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-fg">Spans</span>
              <span>{execute.data.span_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-fg">Status</span>
              <Badge
                className={
                  execute.data.status === "ok" || execute.data.status === "OK"
                    ? "bg-emerald-100 text-emerald-800"
                    : "bg-red-100 text-red-800"
                }
              >
                {execute.data.status}
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
