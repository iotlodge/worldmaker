"use client";

import { useParams } from "next/navigation";
import { useProduct } from "@/hooks/use-products";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader, ErrorState } from "@/components/ui/loading";
import { statusColor, shortId, formatDate } from "@/lib/utils";
import { Package } from "lucide-react";

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading, isError, refetch } = useProduct(id);

  if (isLoading) return <PageLoader />;
  if (isError) return <ErrorState onRetry={() => refetch()} />;
  if (!data) return <ErrorState message="Product not found" />;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center">
          <Package className="w-6 h-6 text-indigo-500" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">{data.name}</h1>
          <div className="flex items-center gap-2 mt-1">
            <Badge className={statusColor(data.status)}>{data.status}</Badge>
            <span className="text-sm text-muted-fg">v{data.version}</span>
            <span className="text-xs font-mono text-muted-fg">
              {shortId(data.id)}
            </span>
          </div>
        </div>
      </div>

      {data.description && (
        <p className="text-sm text-muted-fg">{data.description}</p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardTitle>Details</CardTitle>
          <CardContent className="mt-3 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-fg">Owner</span>
              <span>{data.owner}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-fg">Version</span>
              <span>{data.version}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-fg">Features</span>
              <span>{data.features?.length ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-fg">Created</span>
              <span>{formatDate(data.created_at)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardTitle>Tags</CardTitle>
          <CardContent className="mt-3">
            {data.tags.length === 0 ? (
              <p className="text-sm text-muted-fg">No tags</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {data.tags.map((t) => (
                  <Badge key={t} variant="outline">
                    {t}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
