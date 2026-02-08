"use client";

import { useCorePlatforms } from "@/hooks/use-enterprise";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader, ErrorState, EmptyState } from "@/components/ui/loading";
import { statusColor } from "@/lib/utils";
import {
  Building2,
  Package,
  RefreshCw,
  AlertTriangle,
  Bug,
  AlertCircle,
  ShieldAlert,
  Settings,
  Shield,
  Lock,
  ChevronRight,
  Puzzle,
  Server,
} from "lucide-react";
import Link from "next/link";
import type { Platform } from "@/lib/types";

// ── Icon map for core platforms ──────────────────────────────────────────

const PLATFORM_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  "Product Management": Package,
  "Change Management": RefreshCw,
  "Incident Management": AlertTriangle,
  "Problem Management": Bug,
  "Issues Management": AlertCircle,
  "Risk Management": ShieldAlert,
  "Operations Management": Settings,
  "Business Continuity Management": Shield,
  "Security Management": Lock,
};

const PLATFORM_COLORS: Record<string, string> = {
  "Product Management": "bg-blue-500/10 text-blue-500",
  "Change Management": "bg-amber-500/10 text-amber-500",
  "Incident Management": "bg-red-500/10 text-red-500",
  "Problem Management": "bg-orange-500/10 text-orange-500",
  "Issues Management": "bg-yellow-500/10 text-yellow-500",
  "Risk Management": "bg-purple-500/10 text-purple-500",
  "Operations Management": "bg-cyan-500/10 text-cyan-500",
  "Business Continuity Management": "bg-emerald-500/10 text-emerald-500",
  "Security Management": "bg-rose-500/10 text-rose-500",
};

// ── Platform Card ────────────────────────────────────────────────────────

function PlatformCard({ platform }: { platform: Platform }) {
  const Icon = PLATFORM_ICONS[platform.name] ?? Building2;
  const colorClass = PLATFORM_COLORS[platform.name] ?? "bg-gray-500/10 text-gray-500";
  const capCount = (platform.metadata as Record<string, number>)?.capability_count ?? 0;
  const svcCount = (platform.metadata as Record<string, number>)?.service_count ?? 0;

  return (
    <Link href={`/enterprise/${platform.id}`}>
      <Card className="hover:border-accent/30 hover:shadow-md transition-all cursor-pointer h-full">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div className={`w-11 h-11 rounded-lg ${colorClass} flex items-center justify-center`}>
              <Icon className="w-5 h-5" />
            </div>
            <Badge className={statusColor(platform.status)}>
              {platform.status}
            </Badge>
          </div>

          {/* Name + Description */}
          <h3 className="text-sm font-semibold mb-1">{platform.name}</h3>
          <p className="text-xs text-muted-fg mb-4 line-clamp-2 flex-1">
            {platform.description}
          </p>

          {/* Stats footer */}
          <div className="flex items-center gap-4 pt-3 border-t border-card-border">
            <div className="flex items-center gap-1.5 text-xs text-muted-fg">
              <Puzzle className="w-3.5 h-3.5" />
              <span>{capCount} capabilities</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-muted-fg">
              <Server className="w-3.5 h-3.5" />
              <span>{svcCount} services</span>
            </div>
            <ChevronRight className="w-3.5 h-3.5 text-muted-fg ml-auto" />
          </div>
        </div>
      </Card>
    </Link>
  );
}

// ── Page ─────────────────────────────────────────────────────────────────

export default function EnterprisePage() {
  const { data, isLoading, isError, refetch } = useCorePlatforms();

  if (isLoading) return <PageLoader />;
  if (isError) return <ErrorState onRetry={() => refetch()} />;

  const platforms = data?.platforms ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Business View</h1>
        <p className="text-sm text-muted-fg mt-1">
          {platforms.length} core management platform{platforms.length !== 1 ? "s" : ""} — the operational backbone of the enterprise
        </p>
      </div>

      {platforms.length === 0 ? (
        <EmptyState
          icon={Building2}
          title="No core platforms"
          description="Core platforms are bootstrapped at startup. Restart the server to create them."
        />
      ) : (
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {platforms.map((p) => (
            <PlatformCard key={p.id} platform={p} />
          ))}
        </div>
      )}
    </div>
  );
}
