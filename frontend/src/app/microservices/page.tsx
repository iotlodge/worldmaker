"use client";

import { useMicroservices } from "@/hooks/use-microservices";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader, ErrorState, EmptyState } from "@/components/ui/loading";
import { statusColor, shortId } from "@/lib/utils";
import { Container, ChevronRight, Server } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

export default function MicroservicesPage() {
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const { data, isLoading, isError, refetch } = useMicroservices({
    limit: 200,
  });

  if (isLoading) return <PageLoader />;
  if (isError) return <ErrorState onRetry={() => refetch()} />;

  const all = data?.microservices ?? [];
  const microservices = statusFilter
    ? all.filter((ms) => ms.status === statusFilter)
    : all;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Microservices</h1>
          <p className="text-sm text-muted-fg mt-1">
            {data?.total ?? 0} microservice{(data?.total ?? 0) !== 1 ? "s" : ""} in the ecosystem
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            className="h-9 px-3 text-sm rounded-lg border border-card-border bg-card-bg text-foreground"
            value={statusFilter ?? ""}
            onChange={(e) => setStatusFilter(e.target.value || undefined)}
          >
            <option value="">All statuses</option>
            <option value="active">Active</option>
            <option value="planned">Planned</option>
            <option value="deprecated">Deprecated</option>
          </select>
        </div>
      </div>

      {microservices.length === 0 ? (
        <EmptyState
          icon={Container}
          title="No microservices"
          description={
            statusFilter
              ? `No microservices with status "${statusFilter}". Try clearing the filter.`
              : "Microservices are created when an ecosystem is generated, or can be onboarded through the Enterprise platform workflows."
          }
        />
      ) : (
        <div className="grid gap-3">
          {microservices.map((ms) => (
            <Card key={ms.id} className="hover:border-accent/30 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-teal-500/10 flex items-center justify-center">
                    <Container className="w-5 h-5 text-teal-500" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold">{ms.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className={statusColor(ms.status)}>
                        {ms.status}
                      </Badge>
                      <span className="text-xs text-muted-fg">
                        {ms.language}
                      </span>
                      {ms.framework && (
                        <span className="text-xs text-muted-fg">
                          · {ms.framework}
                        </span>
                      )}
                      <span className="text-xs text-muted-fg font-mono">
                        {shortId(ms.id)}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right text-xs text-muted-fg space-y-0.5">
                    {ms.container_image && (
                      <p className="font-mono truncate max-w-[200px]">
                        {ms.container_image}
                      </p>
                    )}
                    {ms.service_id && (
                      <Link
                        href={`/services/${ms.service_id}`}
                        className="flex items-center gap-1 text-accent hover:underline justify-end"
                      >
                        <Server className="w-3 h-3" />
                        <span>Parent service</span>
                      </Link>
                    )}
                  </div>
                  {ms.repo_url && (
                    <a
                      href={ms.repo_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-accent hover:underline"
                    >
                      repo
                    </a>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
