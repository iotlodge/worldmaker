"use client";

import { useMemo } from "react";
import { useFeatures } from "@/hooks/use-features";
import { useCapabilities } from "@/hooks/use-platforms";
import { useProducts, useProduct } from "@/hooks/use-products";
import { usePlatforms } from "@/hooks/use-platforms";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader, ErrorState, EmptyState } from "@/components/ui/loading";
import { statusColor, shortId, capitalize } from "@/lib/utils";
import {
  Package,
  Layers,
  Zap,
  ShieldAlert,
  ArrowRight,
  Info,
} from "lucide-react";
import Link from "next/link";
import type { Feature, Capability, Product, Platform } from "@/lib/types";

// ── Helper: group items by a key ──────────────────────────────────────

function groupBy<T>(items: T[], key: (item: T) => string): Map<string, T[]> {
  const map = new Map<string, T[]>();
  for (const item of items) {
    const k = key(item);
    if (!map.has(k)) map.set(k, []);
    map.get(k)!.push(item);
  }
  return map;
}

// ── Status summary bar ────────────────────────────────────────────────

function StatusBar({ items }: { items: { status: string }[] }) {
  const counts: Record<string, number> = {};
  for (const item of items) {
    counts[item.status] = (counts[item.status] || 0) + 1;
  }
  const total = items.length || 1;

  return (
    <div className="flex h-2 rounded-full overflow-hidden bg-muted/30 mt-2">
      {Object.entries(counts).map(([status, count]) => {
        const pct = (count / total) * 100;
        const color =
          status === "active"
            ? "bg-emerald-500"
            : status === "planned"
              ? "bg-blue-400"
              : status === "deprecated"
                ? "bg-amber-500"
                : status === "experimental"
                  ? "bg-violet-400"
                  : "bg-gray-400";
        return (
          <div
            key={status}
            className={`${color} transition-all`}
            style={{ width: `${pct}%` }}
            title={`${status}: ${count}`}
          />
        );
      })}
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────

export default function RiskSurfacePage() {
  const featuresQuery = useFeatures({ limit: 1000 });
  const capsQuery = useCapabilities({ limit: 1000 });
  const productsQuery = useProducts({ limit: 200 });
  const platformsQuery = usePlatforms({ limit: 200 });

  const isLoading =
    featuresQuery.isLoading ||
    capsQuery.isLoading ||
    productsQuery.isLoading ||
    platformsQuery.isLoading;

  if (isLoading) return <PageLoader />;

  const features: Feature[] = featuresQuery.data ?? [];
  const capabilities: Capability[] = capsQuery.data?.capabilities ?? [];
  const products: Product[] = productsQuery.data?.products ?? [];
  const platforms: Platform[] = platformsQuery.data?.platforms ?? [];

  const isEmpty = features.length === 0 && capabilities.length === 0;

  if (isEmpty) {
    return (
      <EmptyState
        icon={ShieldAlert}
        title="No risk surface data"
        description="Generate an ecosystem to view features and capabilities."
        action={
          <Link
            href="/generator"
            className="text-sm text-accent hover:underline"
          >
            Go to Generator →
          </Link>
        }
      />
    );
  }

  // Index parents by ID for lookups
  const productMap = new Map(products.map((p) => [p.id, p]));
  const platformMap = new Map(platforms.map((p) => [p.id, p]));

  // Group children by parent
  const featuresByProduct = groupBy(features, (f) => f.product_id);
  const capsByPlatform = groupBy(capabilities, (c) => c.platform_id);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Risk Surface</h1>
        <p className="text-sm text-muted-fg mt-1">
          Where risk materializes — Features define transaction experience, Capabilities
          define infrastructure interop
        </p>
      </div>

      {/* Educational context banner */}
      <div className="rounded-lg border border-card-border bg-card-bg/50 p-4 flex gap-4 items-start">
        <Info className="w-5 h-5 text-muted-fg shrink-0 mt-0.5" />
        <div className="text-sm text-muted-fg space-y-1">
          <p>
            <span className="font-medium text-amber-500">Product → Features</span>{" "}
            represent consumer-facing transaction experiences — what end users
            interact with. Risk here is measured by business outcome impact.
          </p>
          <p>
            <span className="font-medium text-cyan-500">Platform → Capabilities</span>{" "}
            represent infrastructure interoperability patterns — what services
            compose. Risk here is measured by operational resilience and blast radius.
          </p>
          <p className="text-xs italic mt-2">
            Different domains, different threat landscapes, different measurement profiles.
          </p>
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-amber-500">
          <div className="flex items-center gap-3">
            <Package className="w-5 h-5 text-amber-500" />
            <div>
              <p className="text-2xl font-bold">{features.length}</p>
              <p className="text-xs text-muted-fg">
                Features across {featuresByProduct.size} products
              </p>
            </div>
          </div>
        </Card>
        <Card className="border-l-4 border-l-amber-500/50">
          <div className="text-center">
            <p className="text-2xl font-bold">
              {features.filter((f) => f.status === "active").length}
            </p>
            <p className="text-xs text-muted-fg">Active Features</p>
          </div>
        </Card>
        <Card className="border-l-4 border-l-cyan-500">
          <div className="flex items-center gap-3">
            <Layers className="w-5 h-5 text-cyan-500" />
            <div>
              <p className="text-2xl font-bold">{capabilities.length}</p>
              <p className="text-xs text-muted-fg">
                Capabilities across {capsByPlatform.size} platforms
              </p>
            </div>
          </div>
        </Card>
        <Card className="border-l-4 border-l-cyan-500/50">
          <div className="text-center">
            <p className="text-2xl font-bold">
              {capabilities.filter((c) => c.status === "active").length}
            </p>
            <p className="text-xs text-muted-fg">Active Capabilities</p>
          </div>
        </Card>
      </div>

      {/* Dual panel layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ── Product Domain (warm) ──────────────────────────────────── */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
              <Package className="w-4 h-4 text-amber-500" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">Product Domain</h2>
              <p className="text-xs text-muted-fg">
                Transaction Experience · Consumer Risk
              </p>
            </div>
          </div>

          {products.map((product) => {
            const pFeatures = featuresByProduct.get(product.id) ?? [];
            if (pFeatures.length === 0) return null;

            return (
              <Card key={product.id} className="border-l-4 border-l-amber-500/40">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Link
                      href={`/products/${product.id}`}
                      className="text-sm font-semibold hover:text-accent transition-colors"
                    >
                      {product.name}
                    </Link>
                    <Badge className={statusColor(product.status)}>
                      {product.status}
                    </Badge>
                  </div>
                  <span className="text-xs text-muted-fg font-mono">
                    {pFeatures.length} feature{pFeatures.length !== 1 ? "s" : ""}
                  </span>
                </div>
                <StatusBar items={pFeatures} />
                <CardContent className="mt-3 space-y-1.5">
                  {pFeatures.map((feat) => (
                    <div
                      key={feat.id}
                      className="flex items-center justify-between text-sm py-1.5 border-b border-card-border/50 last:border-0"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <Zap className="w-3 h-3 text-amber-400 shrink-0" />
                        <span className="truncate">{feat.name}</span>
                      </div>
                      <div className="flex items-center gap-2 shrink-0 ml-2">
                        <Badge
                          variant="outline"
                          className={`text-xs ${statusColor(feat.status)}`}
                        >
                          {feat.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            );
          })}

          {/* Orphan check */}
          {featuresByProduct.size === 0 && (
            <Card className="border-dashed">
              <p className="text-sm text-muted-fg text-center py-6">
                No features generated. Re-generate ecosystem to populate.
              </p>
            </Card>
          )}
        </div>

        {/* ── Platform Domain (cool) ─────────────────────────────────── */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center">
              <Layers className="w-4 h-4 text-cyan-500" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">Platform Domain</h2>
              <p className="text-xs text-muted-fg">
                Infrastructure Interop · Operational Risk
              </p>
            </div>
          </div>

          {platforms.map((platform) => {
            const pCaps = capsByPlatform.get(platform.id) ?? [];
            if (pCaps.length === 0) return null;

            return (
              <Card key={platform.id} className="border-l-4 border-l-cyan-500/40">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Link
                      href={`/platforms/${platform.id}`}
                      className="text-sm font-semibold hover:text-accent transition-colors"
                    >
                      {platform.name}
                    </Link>
                    <Badge className={statusColor(platform.status)}>
                      {platform.status}
                    </Badge>
                  </div>
                  <span className="text-xs text-muted-fg font-mono">
                    {pCaps.length} cap{pCaps.length !== 1 ? "s" : ""}
                  </span>
                </div>
                <StatusBar items={pCaps} />
                <CardContent className="mt-3 space-y-1.5">
                  {pCaps.map((cap) => (
                    <div
                      key={cap.id}
                      className="flex items-center justify-between text-sm py-1.5 border-b border-card-border/50 last:border-0"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <Zap className="w-3 h-3 text-cyan-400 shrink-0" />
                        <span className="truncate">{cap.name}</span>
                      </div>
                      <div className="flex items-center gap-2 shrink-0 ml-2">
                        <Badge variant="outline" className="text-xs">
                          {cap.capability_type}
                        </Badge>
                        <Badge
                          variant="outline"
                          className={`text-xs ${statusColor(cap.status)}`}
                        >
                          {cap.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            );
          })}

          {capsByPlatform.size === 0 && (
            <Card className="border-dashed">
              <p className="text-sm text-muted-fg text-center py-6">
                No capabilities generated. Re-generate ecosystem to populate.
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
