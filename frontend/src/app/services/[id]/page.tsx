"use client";

import { useParams } from "next/navigation";
import { useServiceContext, useServiceDependencies } from "@/hooks/use-services";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageLoader, ErrorState } from "@/components/ui/loading";
import {
  statusColor,
  severityColor,
  shortId,
  formatDate,
  formatDuration,
} from "@/lib/utils";
import {
  Server,
  GitBranch,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  Boxes,
  Clock,
  Shield,
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";

export default function ServiceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [depthMode, setDepthMode] = useState<
    "direct" | "transitive" | "blast-radius"
  >("direct");

  const context = useServiceContext(id);
  const deps = useServiceDependencies(id, depthMode);

  if (context.isLoading) return <PageLoader />;
  if (context.isError)
    return <ErrorState onRetry={() => context.refetch()} />;
  if (!context.data) return <ErrorState message="Service not found" />;

  const { entity, dependencies, health, microservices, audit } = context.data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center">
            <Server className="w-6 h-6 text-accent" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">{entity.name}</h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge className={statusColor(entity.status)}>
                {entity.status}
              </Badge>
              <span className="text-sm text-muted-fg">{entity.service_type}</span>
              <span className="text-xs font-mono text-muted-fg">
                {shortId(entity.id)}
              </span>
            </div>
          </div>
        </div>
        <Link href="/dependencies">
          <Button variant="outline" size="sm">
            <GitBranch className="w-4 h-4" />
            View in Graph
          </Button>
        </Link>
      </div>

      {entity.description && (
        <p className="text-sm text-muted-fg">{entity.description}</p>
      )}

      {/* Overview grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Health */}
        <Card>
          <CardTitle>
            <span className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-muted-fg" />
              Health
            </span>
          </CardTitle>
          <CardContent className="mt-3 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-fg">Status</span>
              <span className="capitalize">{health.service_status}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-fg">Owner</span>
              <span>{entity.owner}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-fg">API Version</span>
              <span className="font-mono">{entity.api_version}</span>
            </div>
          </CardContent>
        </Card>

        {/* Dependencies summary */}
        <Card>
          <CardTitle>
            <span className="flex items-center gap-2">
              <GitBranch className="w-4 h-4 text-muted-fg" />
              Dependencies
            </span>
          </CardTitle>
          <CardContent className="mt-3 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-fg flex items-center gap-1">
                <ArrowUpRight className="w-3 h-3" /> Upstream
              </span>
              <span className="font-medium">
                {dependencies.upstream.length}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-fg flex items-center gap-1">
                <ArrowDownRight className="w-3 h-3" /> Downstream
              </span>
              <span className="font-medium">
                {dependencies.downstream.length}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-fg">Blast radius</span>
              <span className="font-medium">
                {dependencies.blast_radius.blast_radius}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Microservices */}
        <Card>
          <CardTitle>
            <span className="flex items-center gap-2">
              <Boxes className="w-4 h-4 text-muted-fg" />
              Microservices ({microservices.length})
            </span>
          </CardTitle>
          <CardContent className="mt-3 space-y-2">
            {microservices.length === 0 ? (
              <p className="text-sm text-muted-fg">No microservices</p>
            ) : (
              microservices.slice(0, 5).map((ms) => (
                <div
                  key={ms.id}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="truncate">{ms.name}</span>
                  <Badge variant="outline" className="text-xs">
                    {ms.language}
                  </Badge>
                </div>
              ))
            )}
            {microservices.length > 5 && (
              <p className="text-xs text-muted-fg">
                +{microservices.length - 5} more
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Dependency detail with depth toggle */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <CardTitle>Dependency Analysis</CardTitle>
          <div className="flex gap-1">
            {(["direct", "transitive", "blast-radius"] as const).map((d) => (
              <Button
                key={d}
                variant={depthMode === d ? "primary" : "ghost"}
                size="sm"
                onClick={() => setDepthMode(d)}
              >
                {d === "blast-radius" ? "Blast Radius" : d.charAt(0).toUpperCase() + d.slice(1)}
              </Button>
            ))}
          </div>
        </div>
        <CardContent>
          {deps.isLoading ? (
            <p className="text-sm text-muted-fg">Loading...</p>
          ) : deps.data ? (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4 text-center text-sm">
                <div>
                  <p className="text-2xl font-bold">
                    {deps.data.statistics.direct_dependency_count}
                  </p>
                  <p className="text-muted-fg">Depends On</p>
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {deps.data.statistics.direct_dependent_count}
                  </p>
                  <p className="text-muted-fg">Depended By</p>
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {deps.data.statistics.total_count}
                  </p>
                  <p className="text-muted-fg">Total</p>
                </div>
              </div>

              {deps.data.blast_radius && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium mb-2">
                    Affected Services (blast radius:{" "}
                    {deps.data.blast_radius.blast_radius}, max depth:{" "}
                    {deps.data.blast_radius.max_cascade_depth})
                  </h4>
                  <div className="space-y-1">
                    {deps.data.blast_radius.affected_services
                      .slice(0, 10)
                      .map((svc) => (
                        <div
                          key={svc.id}
                          className="flex items-center justify-between text-sm py-1 border-b border-card-border last:border-0"
                        >
                          <Link
                            href={`/services/${svc.id}`}
                            className="text-accent hover:underline"
                          >
                            {svc.name}
                          </Link>
                          <div className="flex items-center gap-2">
                            <Badge className={severityColor(svc.severity)}>
                              {svc.severity}
                            </Badge>
                            <span className="text-xs text-muted-fg">
                              {svc.hops_away} hop{svc.hops_away !== 1 ? "s" : ""}
                            </span>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </CardContent>
      </Card>

      {/* Audit trail */}
      <Card>
        <CardTitle>
          <span className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-muted-fg" />
            Recent Activity ({audit.recent_changes})
          </span>
        </CardTitle>
        <CardContent className="mt-3">
          {audit.entries.length === 0 ? (
            <p className="text-sm text-muted-fg">No recent activity</p>
          ) : (
            <div className="space-y-1">
              {(audit.entries as Array<{ action: string; timestamp: string; entity_id: string }>)
                .slice(0, 10)
                .map((entry, i) => (
                  <div
                    key={`${entry.entity_id}-${entry.action}-${i}`}
                    className="flex items-center justify-between text-sm py-1.5 border-b border-card-border last:border-0"
                  >
                    <span className="capitalize">{entry.action}</span>
                    <span className="text-xs text-muted-fg font-mono">
                      {formatDate(entry.timestamp)}
                    </span>
                  </div>
                ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
