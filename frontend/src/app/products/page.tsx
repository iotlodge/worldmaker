"use client";

import { useProducts } from "@/hooks/use-products";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader, ErrorState, EmptyState } from "@/components/ui/loading";
import { statusColor, shortId } from "@/lib/utils";
import { Package, ChevronRight } from "lucide-react";
import Link from "next/link";

export default function ProductsPage() {
  const { data, isLoading, isError, refetch } = useProducts({ limit: 100 });

  if (isLoading) return <PageLoader />;
  if (isError) return <ErrorState onRetry={() => refetch()} />;

  const products = data?.products ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Products</h1>
        <p className="text-sm text-muted-fg mt-1">
          {data?.total ?? 0} products in the ecosystem
        </p>
      </div>

      {products.length === 0 ? (
        <EmptyState
          icon={Package}
          title="No products"
          description="Generate an ecosystem to populate products."
        />
      ) : (
        <div className="grid gap-3">
          {products.map((p) => (
            <Link key={p.id} href={`/products/${p.id}`}>
              <Card className="hover:border-accent/30 transition-colors cursor-pointer">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center">
                      <Package className="w-5 h-5 text-indigo-500" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold">{p.name}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge className={statusColor(p.status)}>
                          {p.status}
                        </Badge>
                        <span className="text-xs text-muted-fg">
                          v{p.version}
                        </span>
                        <span className="text-xs text-muted-fg">
                          {p.features?.length ?? 0} features
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right text-xs text-muted-fg">
                      <p>{p.owner}</p>
                      {p.tags.length > 0 && (
                        <div className="flex gap-1 mt-1 justify-end">
                          {p.tags.slice(0, 3).map((t) => (
                            <Badge key={t} variant="outline" className="text-[10px]">
                              {t}
                            </Badge>
                          ))}
                        </div>
                      )}
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
