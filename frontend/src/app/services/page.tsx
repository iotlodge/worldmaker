"use client";

import { useServices } from "@/hooks/use-services";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageLoader, ErrorState, EmptyState } from "@/components/ui/loading";
import { statusColor, shortId, capitalize } from "@/lib/utils";
import { Server, ChevronRight, Filter } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

export default function ServicesPage() {
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const { data, isLoading, isError, refetch } = useServices({
    status: statusFilter,
    limit: 100,
  });

  if (isLoading) return <PageLoader />;
  if (isError) return <ErrorState onRetry={() => refetch()} />;

  const services = data?.services ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Services</h1>
          <p className="text-sm text-muted-fg mt-1">
            {data?.total ?? 0} services in the ecosystem
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            className="h-9 px-3 text-sm rounded-lg border border-card-border bg-card-bg text-foreground"
            value={statusFilter ?? ""}
            onChange={(e) =>
              setStatusFilter(e.target.value || undefined)
            }
          >
            <option value="">All statuses</option>
            <option value="active">Active</option>
            <option value="planned">Planned</option>
            <option value="deprecated">Deprecated</option>
          </select>
        </div>
      </div>

      {services.length === 0 ? (
        <EmptyState
          icon={Server}
          title="No services"
          description="Generate an ecosystem to populate services."
        />
      ) : (
        <div className="grid gap-3">
          {services.map((svc) => (
            <Link key={svc.id} href={`/services/${svc.id}`}>
              <Card className="hover:border-accent/30 transition-colors cursor-pointer">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                      <Server className="w-5 h-5 text-accent" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold">{svc.name}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge className={statusColor(svc.status)}>
                          {svc.status}
                        </Badge>
                        <span className="text-xs text-muted-fg">
                          {svc.service_type}
                        </span>
                        <span className="text-xs text-muted-fg font-mono">
                          {shortId(svc.id)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right text-xs text-muted-fg">
                      <p>{svc.microservice_ids?.length ?? 0} microservices</p>
                      <p>v{svc.api_version}</p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-fg" />
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
