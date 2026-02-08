"use client";

import { useMemo } from "react";
import { useCircularDependencies } from "@/hooks/use-issues";
import { useEcosystemHealth, useEcosystemOverview } from "@/hooks/use-ecosystem";
import { useServices } from "@/hooks/use-services";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader, ErrorState, EmptyState } from "@/components/ui/loading";
import { severityColor, shortId, capitalize, formatEntityType } from "@/lib/utils";
import {
  AlertTriangle,
  AlertOctagon,
  RefreshCcw,
  ArrowRight,
  ArrowLeftRight,
  Server,
  ShieldX,
  CircleAlert,
  Check,
} from "lucide-react";
import Link from "next/link";
import type {
  CircularDependency,
  Service,
  Severity,
} from "@/lib/types";

// ── Severity ordering for sort ──────────────────────────────────────────

const SEV_ORDER: Record<string, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
};

// ── Main page ───────────────────────────────────────────────────────────

export default function IssueDiscoveryPage() {
  const healthQuery = useEcosystemHealth();
  const overviewQuery = useEcosystemOverview();
  const circularQuery = useCircularDependencies({ limit: 500 });
  const servicesQuery = useServices({ limit: 1000 });

  const isLoading =
    healthQuery.isLoading ||
    overviewQuery.isLoading ||
    circularQuery.isLoading ||
    servicesQuery.isLoading;

  // All hooks MUST be above conditional returns (Rules of Hooks)
  const circularDeps: CircularDependency[] =
    circularQuery.data?.circular_dependencies ?? [];

  const criticalIssues: string[] = healthQuery.data?.critical_issues ?? [];
  const warnings: string[] = healthQuery.data?.warnings ?? [];

  const allServices: Service[] = servicesQuery.data?.services ?? [];

  const degradedServices = useMemo(
    () =>
      allServices.filter(
        (s) => s.status !== "active" && s.status !== "planned"
      ),
    [allServices]
  );

  const sortedCircular = useMemo(
    () =>
      [...circularDeps].sort(
        (a, b) =>
          (SEV_ORDER[a.severity] ?? 9) - (SEV_ORDER[b.severity] ?? 9)
      ),
    [circularDeps]
  );

  const circularBySeverity = useMemo(() => {
    const acc: Record<string, number> = {};
    for (const d of circularDeps) {
      acc[d.severity] = (acc[d.severity] || 0) + 1;
    }
    return acc;
  }, [circularDeps]);

  const totalFindings =
    circularDeps.length +
    criticalIssues.length +
    warnings.length +
    degradedServices.length;

  const allClear = totalFindings === 0;

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Issue Discovery</h1>
        <p className="text-sm text-muted-fg mt-1">
          Consolidated negative findings — circular dependencies, critical
          issues, and service degradation
        </p>
      </div>

      {/* All-clear state */}
      {allClear && (
        <Card className="border-emerald-500/30 bg-emerald-500/5">
          <div className="flex items-center gap-4 py-4">
            <div className="w-12 h-12 rounded-full bg-emerald-500/10 flex items-center justify-center">
              <Check className="w-6 h-6 text-emerald-500" />
            </div>
            <div>
              <p className="font-semibold text-emerald-500">
                No issues detected
              </p>
              <p className="text-sm text-muted-fg">
                Ecosystem health is clean. Generate a larger ecosystem to stress
                test dependency patterns.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Summary cards */}
      {!allClear && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <SummaryCard
            icon={RefreshCcw}
            label="Circular Dependencies"
            count={circularDeps.length}
            severity={circularDeps.length > 0 ? "critical" : undefined}
          />
          <SummaryCard
            icon={AlertOctagon}
            label="Critical Issues"
            count={criticalIssues.length}
            severity={criticalIssues.length > 0 ? "critical" : undefined}
          />
          <SummaryCard
            icon={AlertTriangle}
            label="Warnings"
            count={warnings.length}
            severity={warnings.length > 0 ? "high" : undefined}
          />
          <SummaryCard
            icon={Server}
            label="Degraded Services"
            count={degradedServices.length}
            severity={degradedServices.length > 0 ? "medium" : undefined}
          />
        </div>
      )}

      {/* ── Section 1: Circular Dependencies ───────────────────────────── */}
      {circularDeps.length > 0 && (
        <div className="space-y-3">
          <SectionHeader
            icon={RefreshCcw}
            title="Circular Dependencies"
            subtitle="Bidirectional coupling creates tight failure domains — one failure cascades both directions"
            colorClass="text-red-500"
          />

          {/* Severity breakdown */}
          <div className="flex gap-2 flex-wrap">
            {Object.entries(circularBySeverity)
              .sort(
                ([a], [b]) =>
                  (SEV_ORDER[a] ?? 9) - (SEV_ORDER[b] ?? 9)
              )
              .map(([sev, count]) => (
                <Badge
                  key={sev}
                  className={severityColor(sev as Severity)}
                >
                  {count} {sev}
                </Badge>
              ))}
          </div>

          {/* Individual circular dep cards */}
          <div className="space-y-2">
            {sortedCircular.map((dep) => (
              <CircularDepCard key={dep.id} dep={dep} />
            ))}
          </div>
        </div>
      )}

      {/* ── Section 2: Critical Issues ─────────────────────────────────── */}
      {criticalIssues.length > 0 && (
        <div className="space-y-3">
          <SectionHeader
            icon={AlertOctagon}
            title="Critical Issues"
            subtitle="Conditions requiring immediate attention"
            colorClass="text-red-500"
          />
          <Card className="border-red-500/20">
            <CardContent className="space-y-2">
              {criticalIssues.map((issue, i) => (
                <div
                  key={`crit-${i}-${issue.slice(0, 30)}`}
                  className="flex items-start gap-3 py-2 border-b border-card-border/50 last:border-0"
                >
                  <ShieldX className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                  <p className="text-sm">{issue}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ── Section 3: Warnings ────────────────────────────────────────── */}
      {warnings.length > 0 && (
        <div className="space-y-3">
          <SectionHeader
            icon={AlertTriangle}
            title="Warnings"
            subtitle="Conditions that may escalate without remediation"
            colorClass="text-amber-500"
          />
          <Card className="border-amber-500/20">
            <CardContent className="space-y-2">
              {warnings.map((w, i) => (
                <div
                  key={`warn-${i}-${w.slice(0, 30)}`}
                  className="flex items-start gap-3 py-2 border-b border-card-border/50 last:border-0"
                >
                  <CircleAlert className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                  <p className="text-sm">{w}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ── Section 4: Degraded Services ───────────────────────────────── */}
      {degradedServices.length > 0 && (
        <div className="space-y-3">
          <SectionHeader
            icon={Server}
            title="Degraded Services"
            subtitle="Services not in active state — potential operational risk"
            colorClass="text-orange-500"
          />
          <Card className="border-orange-500/20">
            <CardContent className="space-y-1.5">
              {degradedServices.map((svc) => (
                <div
                  key={svc.id}
                  className="flex items-center justify-between py-2 border-b border-card-border/50 last:border-0"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <Server className="w-4 h-4 text-orange-400 shrink-0" />
                    <Link
                      href={`/services/${svc.id}`}
                      className="text-sm font-medium hover:text-accent transition-colors truncate"
                    >
                      {svc.name}
                    </Link>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 ml-2">
                    <Badge variant="outline" className="text-xs">
                      {svc.service_type}
                    </Badge>
                    <Badge
                      className={`text-xs ${
                        svc.status === "deprecated"
                          ? "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400"
                          : svc.status === "decommissioned"
                            ? "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400"
                            : "bg-slate-100 text-slate-800 dark:bg-slate-900/30 dark:text-slate-400"
                      }`}
                    >
                      {svc.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ── Educational footer ─────────────────────────────────────────── */}
      {!allClear && (
        <Card className="border-card-border/50 bg-card-bg/50">
          <CardContent>
            <p className="text-xs text-muted-fg leading-relaxed">
              <span className="font-medium text-foreground">
                Why circular dependencies matter:
              </span>{" "}
              A circular dependency between Service A and Service B means both
              must be available for either to function. This eliminates
              independent deployability, creates tight failure domains, and makes
              rollback dangerous. In enterprise ecosystems, circular deps are the
              #1 indicator of architectural debt and are the primary target for
              decoupling initiatives. The dependency type (runtime, data, event)
              determines the blast radius and remediation strategy.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────

function SummaryCard({
  icon: Icon,
  label,
  count,
  severity,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  count: number;
  severity?: "critical" | "high" | "medium";
}) {
  const borderColor =
    severity === "critical"
      ? "border-l-red-500"
      : severity === "high"
        ? "border-l-orange-500"
        : severity === "medium"
          ? "border-l-amber-500"
          : "border-l-emerald-500";

  const iconColor =
    severity === "critical"
      ? "text-red-500"
      : severity === "high"
        ? "text-orange-500"
        : severity === "medium"
          ? "text-amber-500"
          : "text-emerald-500";

  return (
    <Card className={`border-l-4 ${borderColor}`}>
      <div className="flex items-center gap-3">
        <Icon className={`w-5 h-5 ${iconColor}`} />
        <div>
          <p className="text-2xl font-bold">{count}</p>
          <p className="text-xs text-muted-fg">{label}</p>
        </div>
      </div>
    </Card>
  );
}

function SectionHeader({
  icon: Icon,
  title,
  subtitle,
  colorClass,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  subtitle: string;
  colorClass: string;
}) {
  return (
    <div className="flex items-center gap-3">
      <div
        className={`w-8 h-8 rounded-lg ${colorClass.replace("text-", "bg-").replace("500", "500/10")} flex items-center justify-center`}
      >
        <Icon className={`w-4 h-4 ${colorClass}`} />
      </div>
      <div>
        <h2 className="text-lg font-semibold">{title}</h2>
        <p className="text-xs text-muted-fg">{subtitle}</p>
      </div>
    </div>
  );
}

function CircularDepCard({ dep }: { dep: CircularDependency }) {
  const sourceName = dep.source_name ?? shortId(dep.source_id);
  const targetName = dep.target_name ?? shortId(dep.target_id);

  return (
    <Card className="border-l-4 border-l-red-500/40 hover:border-l-red-500 transition-colors">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Cycle visualization */}
        <div className="flex items-center gap-2 min-w-0">
          <div className="flex items-center gap-1.5 min-w-0">
            <Link
              href={`/services/${dep.source_id}`}
              className="text-sm font-medium hover:text-accent transition-colors truncate max-w-[180px]"
              title={sourceName}
            >
              {sourceName}
            </Link>
            <ArrowLeftRight className="w-4 h-4 text-red-400 shrink-0" />
            <Link
              href={`/services/${dep.target_id}`}
              className="text-sm font-medium hover:text-accent transition-colors truncate max-w-[180px]"
              title={targetName}
            >
              {targetName}
            </Link>
          </div>
        </div>

        {/* Metadata */}
        <div className="flex items-center gap-2 shrink-0">
          <Badge variant="outline" className="text-xs capitalize">
            {dep.dependency_type.replace("_", " ")}
          </Badge>
          <Badge className={`text-xs ${severityColor(dep.severity)}`}>
            {dep.severity}
          </Badge>
          <span className="text-[10px] text-muted-fg font-mono">
            {shortId(dep.id)}
          </span>
        </div>
      </div>

      {/* Description if available */}
      {dep.description && (
        <p className="text-xs text-muted-fg mt-2 pl-1">{dep.description}</p>
      )}
    </Card>
  );
}
