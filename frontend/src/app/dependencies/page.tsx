"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { useServices, useServiceDependencies } from "@/hooks/use-services";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageLoader, ErrorState, EmptyState } from "@/components/ui/loading";
import { severityColor, shortId } from "@/lib/utils";
import { GitBranch, AlertTriangle, Crosshair, Zap } from "lucide-react";
import Link from "next/link";
import api from "@/lib/api";
import type { FailureSimulation, Service } from "@/lib/types";

export default function DependenciesPage() {
  const { data, isLoading, isError, refetch } = useServices({ limit: 200 });
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [simulation, setSimulation] = useState<FailureSimulation | null>(null);
  const [simLoading, setSimLoading] = useState(false);

  const deps = useServiceDependencies(selectedId ?? "", "blast-radius");

  const services = data?.services ?? [];

  const handleSimulate = async (serviceId: string) => {
    setSimLoading(true);
    try {
      const result = await api.dependencies.simulate(serviceId);
      setSimulation(result);
    } catch {
      setSimulation(null);
    }
    setSimLoading(false);
  };

  if (isLoading) return <PageLoader />;
  if (isError) return <ErrorState onRetry={() => refetch()} />;

  if (services.length === 0)
    return (
      <EmptyState
        icon={GitBranch}
        title="No services"
        description="Generate an ecosystem to view the dependency graph."
      />
    );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dependencies</h1>
        <p className="text-sm text-muted-fg mt-1">
          Dependency graph, blast radius analysis, and failure simulation
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Service selector */}
        <Card className="lg:col-span-1">
          <CardTitle>Select Service</CardTitle>
          <CardContent className="mt-3 max-h-96 overflow-y-auto space-y-1">
            {services.map((svc) => (
              <button
                key={svc.id}
                onClick={() => {
                  setSelectedId(svc.id);
                  setSimulation(null);
                }}
                className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  selectedId === svc.id
                    ? "bg-accent/10 text-accent font-medium"
                    : "text-foreground hover:bg-muted"
                }`}
              >
                <span className="block truncate">{svc.name}</span>
                <span className="text-xs text-muted-fg font-mono">
                  {shortId(svc.id)}
                </span>
              </button>
            ))}
          </CardContent>
        </Card>

        {/* Analysis panel */}
        <div className="lg:col-span-2 space-y-4">
          {!selectedId ? (
            <Card>
              <div className="flex items-center justify-center py-16 text-muted-fg text-sm">
                <Crosshair className="w-5 h-5 mr-2" />
                Select a service to analyze its dependencies
              </div>
            </Card>
          ) : deps.isLoading ? (
            <PageLoader />
          ) : deps.data ? (
            <>
              {/* Summary stats */}
              <div className="grid grid-cols-3 gap-4">
                <Card className="text-center">
                  <p className="text-3xl font-bold">
                    {deps.data.statistics.direct_dependency_count}
                  </p>
                  <p className="text-xs text-muted-fg mt-1">Depends On</p>
                </Card>
                <Card className="text-center">
                  <p className="text-3xl font-bold">
                    {deps.data.statistics.direct_dependent_count}
                  </p>
                  <p className="text-xs text-muted-fg mt-1">Depended By</p>
                </Card>
                <Card className="text-center">
                  <p className="text-3xl font-bold">
                    {deps.data.blast_radius?.blast_radius ?? 0}
                  </p>
                  <p className="text-xs text-muted-fg mt-1">Blast Radius</p>
                </Card>
              </div>

              {/* Blast radius detail */}
              {deps.data.blast_radius &&
                deps.data.blast_radius.affected_services.length > 0 && (
                  <Card>
                    <div className="flex items-center justify-between mb-3">
                      <CardTitle>
                        <span className="flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4 text-amber-500" />
                          Blast Radius (max depth:{" "}
                          {deps.data.blast_radius.max_cascade_depth})
                        </span>
                      </CardTitle>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleSimulate(selectedId)}
                        disabled={simLoading}
                      >
                        <Zap className="w-3.5 h-3.5" />
                        {simLoading ? "Simulating..." : "Simulate Failure"}
                      </Button>
                    </div>
                    <CardContent>
                      <div className="space-y-1">
                        {deps.data.blast_radius.affected_services.map((svc) => (
                          <div
                            key={svc.id}
                            className="flex items-center justify-between text-sm py-1.5 border-b border-card-border last:border-0"
                          >
                            <Link
                              href={`/services/${svc.id}`}
                              className="text-accent hover:underline truncate"
                            >
                              {svc.name}
                            </Link>
                            <div className="flex items-center gap-2 shrink-0">
                              <Badge className={severityColor(svc.severity)}>
                                {svc.severity}
                              </Badge>
                              <span className="text-xs text-muted-fg w-14 text-right">
                                {svc.hops_away} hop
                                {svc.hops_away !== 1 ? "s" : ""}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

              {/* Failure simulation results */}
              {simulation && (
                <Card className="border-red-200 dark:border-red-900/50">
                  <CardTitle>
                    <span className="flex items-center gap-2 text-red-500">
                      <Zap className="w-4 h-4" />
                      Failure Simulation: {simulation.service_name}
                    </span>
                  </CardTitle>
                  <CardContent className="mt-3 space-y-4">
                    <div className="grid grid-cols-3 gap-4 text-center text-sm">
                      <div>
                        <p className="text-xl font-bold text-red-500">
                          {simulation.blast_radius}
                        </p>
                        <p className="text-muted-fg">Affected</p>
                      </div>
                      <div>
                        <p className="text-xl font-bold">
                          {simulation.max_cascade_depth}
                        </p>
                        <p className="text-muted-fg">Max Depth</p>
                      </div>
                      <div>
                        <Badge className={severityColor(simulation.severity)}>
                          {simulation.severity}
                        </Badge>
                        <p className="text-muted-fg mt-1">Severity</p>
                      </div>
                    </div>

                    {simulation.recommendations.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium mb-2">
                          Recommendations
                        </h4>
                        <ul className="space-y-1">
                          {simulation.recommendations.map((rec, i) => (
                            <li key={`rec-${i}-${rec.slice(0, 20)}`} className="text-sm text-muted-fg">
                              • {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
