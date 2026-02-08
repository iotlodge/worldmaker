"use client";

import { useEcosystemOverview, useEcosystemHealth } from "@/hooks/use-ecosystem";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader, ErrorState, EmptyState } from "@/components/ui/loading";
import { cn, healthColor, formatEntityType } from "@/lib/utils";
import {
  Package,
  Layers,
  Server,
  Workflow,
  GitBranch,
  Activity,
  AlertTriangle,
  Heart,
  Sparkles,
  Database,
  Building2,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const ENTITY_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  products: Package,
  platforms: Layers,
  services: Server,
  flows: Workflow,
  dependencies: GitBranch,
  capabilities: Database,
  microservices: Activity,
};

const ENTITY_LINKS: Record<string, string> = {
  products: "/products",
  platforms: "/platforms",
  services: "/services",
  flows: "/flows",
  dependencies: "/dependencies",
  capabilities: "/enterprise",
  microservices: "/microservices",
};

const BAR_COLORS = [
  "#3b82f6",
  "#8b5cf6",
  "#06b6d4",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#ec4899",
  "#64748b",
];

export default function DashboardPage() {
  const overview = useEcosystemOverview();
  const health = useEcosystemHealth();

  if (overview.isLoading) return <PageLoader />;
  if (overview.isError)
    return (
      <ErrorState
        message="Could not load ecosystem overview. Is the API running?"
        onRetry={() => overview.refetch()}
      />
    );

  const data = overview.data;
  if (!data || data.total_entities === 0)
    return (
      <EmptyState
        icon={Sparkles}
        title="No ecosystem data"
        description="Generate a synthetic ecosystem to get started."
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

  const eco = data.ecosystem;
  const stats = data.statistics;

  // Build chart data from ecosystem counts
  const chartData = Object.entries(eco)
    .filter(([, v]) => typeof v === "object" && "total" in v)
    .map(([key, v]) => ({
      name: key.charAt(0).toUpperCase() + key.slice(1),
      count: (v as { total: number }).total,
    }))
    .sort((a, b) => b.count - a.count);

  const healthData = health.data;

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
          <p className="text-sm text-muted-fg mt-1">
            Ecosystem overview — {data.total_entities} total entities
          </p>
        </div>
        {healthData && (
          <div className="flex items-center gap-3">
            <Heart
              className={cn("w-5 h-5", healthColor(healthData.overall_health))}
            />
            <div className="text-right">
              <p className="text-sm font-medium">
                Health: {healthData.health_score}%
              </p>
              <p className="text-xs text-muted-fg capitalize">
                {healthData.overall_health}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Entity count cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {Object.entries(eco).map(([key, val]) => {
          if (typeof val !== "object" || !("total" in val)) return null;
          const Icon = ENTITY_ICONS[key] ?? Database;
          const link = ENTITY_LINKS[key];
          const total = (val as { total: number }).total;
          const Wrapper = link ? Link : "div";
          const wrapperProps = link ? { href: link } : {};

          return (
            <Wrapper key={key} {...(wrapperProps as any)}>
              <Card className="hover:border-accent/30 transition-colors cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-accent/10 flex items-center justify-center">
                    <Icon className="w-4.5 h-4.5 text-accent" />
                  </div>
                  <div>
                    <p className="text-xl font-bold">{total}</p>
                    <p className="text-xs text-muted-fg capitalize">{key}</p>
                  </div>
                </div>
              </Card>
            </Wrapper>
          );
        })}
      </div>

      {/* Enterprise quick link */}
      <Link href="/enterprise">
        <Card className="border-violet-500/20 bg-violet-500/5 hover:border-violet-500/40 transition-colors cursor-pointer group">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
              <Building2 className="w-5 h-5 text-violet-500" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold">Enterprise Business View</p>
              <p className="text-xs text-muted-fg">
                9 core management platforms — the operational backbone of the enterprise
              </p>
            </div>
            <ChevronRight className="w-4 h-4 text-muted-fg group-hover:text-violet-500 transition-colors" />
          </div>
        </Card>
      </Link>

      {/* Charts + Health row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar chart */}
        <Card>
          <CardTitle>Entity Distribution</CardTitle>
          <CardContent className="mt-4">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
                  <XAxis type="number" tick={{ fontSize: 12 }} />
                  <YAxis
                    type="category"
                    dataKey="name"
                    tick={{ fontSize: 12 }}
                    width={100}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "var(--card-bg)",
                      border: "1px solid var(--card-border)",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {chartData.map((_entry, i) => (
                      <Cell
                        key={i}
                        fill={BAR_COLORS[i % BAR_COLORS.length]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Statistics + health */}
        <div className="space-y-4">
          <Card>
            <CardTitle>Statistics</CardTitle>
            <CardContent className="mt-3 space-y-3">
              <StatRow
                label="Avg dependencies per service"
                value={stats.avg_dependencies_per_service.toFixed(1)}
              />
              <Link
                href="/issues"
                className="block hover:bg-accent/5 -mx-2 px-2 rounded transition-colors"
              >
                <StatRow
                  label="Circular dependencies"
                  value={stats.circular_dependency_count}
                  warn={stats.circular_dependency_count > 0}
                />
              </Link>
              <StatRow
                label="Traces generated"
                value={stats.traces_generated}
              />
              <StatRow label="Total spans" value={stats.spans_generated} />
              <StatRow
                label="Audit log entries"
                value={stats.audit_log_entries}
              />
            </CardContent>
          </Card>

          {healthData && healthData.critical_issues.length > 0 && (
            <Link href="/issues">
              <Card className="border-red-200 dark:border-red-900/50 hover:border-red-400 transition-colors cursor-pointer group">
                <CardTitle>
                  <span className="flex items-center gap-2 text-red-500">
                    <AlertTriangle className="w-4 h-4" />
                    Critical Issues
                    <span className="ml-auto text-xs text-muted-fg opacity-0 group-hover:opacity-100 transition-opacity">
                      View details →
                    </span>
                  </span>
                </CardTitle>
                <CardContent className="mt-2 space-y-1.5">
                  {healthData.critical_issues.map((issue, i) => (
                    <p key={`crit-${i}-${issue.slice(0, 30)}`} className="text-sm text-red-400">
                      {issue}
                    </p>
                  ))}
                </CardContent>
              </Card>
            </Link>
          )}

          {healthData && healthData.warnings.length > 0 && (
            <Link href="/issues">
              <Card className="border-amber-200 dark:border-amber-900/50 hover:border-amber-400 transition-colors cursor-pointer group">
                <CardTitle>
                  <span className="flex items-center gap-2 text-amber-500">
                    <AlertTriangle className="w-4 h-4" />
                    Warnings ({healthData.warnings.length})
                    <span className="ml-auto text-xs text-muted-fg opacity-0 group-hover:opacity-100 transition-opacity">
                      View details →
                    </span>
                  </span>
                </CardTitle>
                <CardContent className="mt-2 space-y-1.5">
                  {healthData.warnings.slice(0, 5).map((w, i) => (
                    <p key={`warn-${i}-${w.slice(0, 30)}`} className="text-sm text-amber-400">
                      {w}
                    </p>
                  ))}
                  {healthData.warnings.length > 5 && (
                    <p className="text-xs text-muted-fg">
                      +{healthData.warnings.length - 5} more
                    </p>
                  )}
                </CardContent>
              </Card>
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}

function StatRow({
  label,
  value,
  warn,
}: {
  label: string;
  value: string | number;
  warn?: boolean;
}) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-muted-fg">{label}</span>
      <span
        className={cn(
          "font-medium font-mono",
          warn ? "text-amber-500" : "text-foreground"
        )}
      >
        {value}
      </span>
    </div>
  );
}
