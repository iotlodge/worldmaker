"use client";

import { useFlows, useExecuteFlow } from "@/hooks/use-flows";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageLoader, ErrorState, EmptyState } from "@/components/ui/loading";
import { statusColor, shortId, formatDuration } from "@/lib/utils";
import { Workflow, Play, ChevronRight } from "lucide-react";
import Link from "next/link";

export default function FlowsPage() {
  const { data, isLoading, isError, refetch } = useFlows({ limit: 100 });
  const execute = useExecuteFlow();

  if (isLoading) return <PageLoader />;
  if (isError) return <ErrorState onRetry={() => refetch()} />;

  const flows = data?.flows ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Flows</h1>
        <p className="text-sm text-muted-fg mt-1">
          {data?.total ?? 0} flows — request paths through the ecosystem
        </p>
      </div>

      {flows.length === 0 ? (
        <EmptyState
          icon={Workflow}
          title="No flows"
          description="Generate an ecosystem to create flows."
        />
      ) : (
        <div className="grid gap-3">
          {flows.map((flow) => (
            <Card
              key={flow.id}
              className="hover:border-accent/30 transition-colors"
            >
              <div className="flex items-center justify-between">
                <Link
                  href={`/flows/${flow.id}`}
                  className="flex items-center gap-4 flex-1"
                >
                  <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                    <Workflow className="w-5 h-5 text-purple-500" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold">{flow.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className={statusColor(flow.status)}>
                        {flow.status}
                      </Badge>
                      <span className="text-xs text-muted-fg">
                        {flow.flow_type}
                      </span>
                      {flow.average_duration_ms && (
                        <span className="text-xs text-muted-fg">
                          ~{formatDuration(flow.average_duration_ms)}
                        </span>
                      )}
                      <span className="text-xs text-muted-fg">
                        {flow.steps?.length ?? 0} steps
                      </span>
                    </div>
                  </div>
                </Link>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={(e) => {
                      e.preventDefault();
                      execute.mutate({ id: flow.id });
                    }}
                    disabled={execute.isPending}
                  >
                    <Play className="w-3.5 h-3.5" />
                    Execute
                  </Button>
                  <Link href={`/flows/${flow.id}`}>
                    <ChevronRight className="w-4 h-4 text-muted-fg" />
                  </Link>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
