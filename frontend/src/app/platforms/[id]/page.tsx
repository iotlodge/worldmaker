"use client";

import { useParams } from "next/navigation";
import { usePlatform, useCapabilities } from "@/hooks/use-platforms";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader, ErrorState } from "@/components/ui/loading";
import { statusColor, shortId, formatDate } from "@/lib/utils";
import { Layers, Database } from "lucide-react";

export default function PlatformDetailPage() {
  const { id } = useParams<{ id: string }>();
  const platform = usePlatform(id);
  const caps = useCapabilities({ platform_id: id });

  if (platform.isLoading) return <PageLoader />;
  if (platform.isError)
    return <ErrorState onRetry={() => platform.refetch()} />;
  if (!platform.data) return <ErrorState message="Platform not found" />;

  const p = platform.data;
  const capabilities = caps.data?.capabilities ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-cyan-500/10 flex items-center justify-center">
          <Layers className="w-6 h-6 text-cyan-500" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">{p.name}</h1>
          <div className="flex items-center gap-2 mt-1">
            <Badge className={statusColor(p.status)}>{p.status}</Badge>
            <span className="text-sm text-muted-fg">{p.category}</span>
            <span className="text-xs font-mono text-muted-fg">
              {shortId(p.id)}
            </span>
          </div>
        </div>
      </div>

      {p.description && (
        <p className="text-sm text-muted-fg">{p.description}</p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardTitle>Details</CardTitle>
          <CardContent className="mt-3 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-fg">Owner</span>
              <span>{p.owner}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-fg">Category</span>
              <span>{p.category}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-fg">Created</span>
              <span>{formatDate(p.created_at)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardTitle>Tech Stack</CardTitle>
          <CardContent className="mt-3">
            {p.tech_stack.length === 0 ? (
              <p className="text-sm text-muted-fg">No tech stack defined</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {p.tech_stack.map((t) => (
                  <Badge key={t} variant="outline">
                    {t}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Capabilities */}
      <Card>
        <CardTitle>
          <span className="flex items-center gap-2">
            <Database className="w-4 h-4 text-muted-fg" />
            Capabilities ({capabilities.length})
          </span>
        </CardTitle>
        <CardContent className="mt-3">
          {capabilities.length === 0 ? (
            <p className="text-sm text-muted-fg">No capabilities</p>
          ) : (
            <div className="space-y-2">
              {capabilities.map((cap) => (
                <div
                  key={cap.id}
                  className="flex items-center justify-between text-sm py-2 border-b border-card-border last:border-0"
                >
                  <div>
                    <span className="font-medium">{cap.name}</span>
                    {cap.description && (
                      <p className="text-xs text-muted-fg mt-0.5">
                        {cap.description}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={statusColor(cap.status)}>
                      {cap.status}
                    </Badge>
                    <Badge variant="outline">{cap.capability_type}</Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
