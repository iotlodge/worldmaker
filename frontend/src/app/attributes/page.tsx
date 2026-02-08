"use client";

import { useState } from "react";
import { useAttributes, useAttributeGaps } from "@/hooks/use-attributes";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader, ErrorState, EmptyState } from "@/components/ui/loading";
import { cn } from "@/lib/utils";
import {
  Tags,
  Shield,
  RefreshCw,
  Puzzle,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Target,
} from "lucide-react";
import type { AttributeTier, AttributeDefinition } from "@/lib/types";

const TIER_CONFIG: Record<
  AttributeTier,
  { label: string; icon: React.ComponentType<{ className?: string }>; color: string; description: string }
> = {
  core: {
    label: "Core",
    icon: Shield,
    color: "text-red-500 bg-red-500/10 border-red-500/20",
    description: "Required for AI intelligence — absence = risk signal",
  },
  lifecycle: {
    label: "Lifecycle",
    icon: RefreshCw,
    color: "text-amber-500 bg-amber-500/10 border-amber-500/20",
    description: "Stamped by core functions during workflows",
  },
  function: {
    label: "Function",
    icon: Puzzle,
    color: "text-blue-500 bg-blue-500/10 border-blue-500/20",
    description: "Extensible — added by platform owners at runtime",
  },
};

const DATA_TYPE_COLORS: Record<string, string> = {
  enum: "bg-violet-500/10 text-violet-500",
  string: "bg-emerald-500/10 text-emerald-500",
  number: "bg-cyan-500/10 text-cyan-500",
  boolean: "bg-orange-500/10 text-orange-500",
  json: "bg-pink-500/10 text-pink-500",
};

export default function AttributesPage() {
  const [activeTier, setActiveTier] = useState<AttributeTier>("core");
  const [showGaps, setShowGaps] = useState(false);

  const attrs = useAttributes({ tier: activeTier, limit: 500 });
  const gaps = useAttributeGaps();

  if (attrs.isLoading) return <PageLoader />;
  if (attrs.isError)
    return (
      <ErrorState
        message="Could not load attributes. Is the API running?"
        onRetry={() => attrs.refetch()}
      />
    );

  const definitions = attrs.data?.attribute_definitions ?? [];
  const gapData = gaps.data;

  // Group by category
  const byCategory: Record<string, AttributeDefinition[]> = {};
  for (const attr of definitions) {
    const cat = attr.category || "general";
    if (!byCategory[cat]) byCategory[cat] = [];
    byCategory[cat].push(attr);
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <Tags className="w-6 h-6 text-accent" />
          Attribute Registry
        </h1>
        <p className="text-sm text-muted-fg mt-1">
          Three-tier attribute ontology — CORE / LIFECYCLE / FUNCTION.
          Attribute gaps are risk signals.
        </p>
      </div>

      {/* Tier tabs */}
      <div className="flex gap-2">
        {(Object.keys(TIER_CONFIG) as AttributeTier[]).map((tier) => {
          const config = TIER_CONFIG[tier];
          const Icon = config.icon;
          const isActive = activeTier === tier;
          return (
            <button
              key={tier}
              onClick={() => setActiveTier(tier)}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-all",
                isActive
                  ? config.color
                  : "border-card-border bg-card-bg text-muted-fg hover:border-accent/30"
              )}
            >
              <Icon className="w-4 h-4" />
              {config.label}
            </button>
          );
        })}
      </div>

      {/* Tier description */}
      <p className="text-xs text-muted-fg italic">
        {TIER_CONFIG[activeTier].description}
      </p>

      {/* Attribute table */}
      {definitions.length === 0 ? (
        <EmptyState
          icon={Tags}
          title={`No ${activeTier} attributes`}
          description="Generate an ecosystem to bootstrap attribute definitions."
        />
      ) : (
        <div className="space-y-6">
          {Object.entries(byCategory)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([category, catAttrs]) => (
              <Card key={category}>
                <CardTitle className="capitalize">{category}</CardTitle>
                <CardContent className="mt-3">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-card-border text-left text-muted-fg">
                          <th className="pb-2 pr-4 font-medium">Name</th>
                          <th className="pb-2 pr-4 font-medium">Type</th>
                          <th className="pb-2 pr-4 font-medium">Applies To</th>
                          <th className="pb-2 pr-4 font-medium">Required</th>
                          <th className="pb-2 font-medium">Owner</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-card-border/50">
                        {catAttrs.map((attr) => (
                          <tr key={attr.id} className="hover:bg-white/[0.02]">
                            <td className="py-2.5 pr-4">
                              <div>
                                <p className="font-medium text-foreground">
                                  {attr.display_name}
                                </p>
                                <p className="text-xs text-muted-fg font-mono">
                                  {attr.name}
                                </p>
                              </div>
                            </td>
                            <td className="py-2.5 pr-4">
                              <Badge
                                className={cn(
                                  "text-xs",
                                  DATA_TYPE_COLORS[attr.data_type] ??
                                    "bg-gray-500/10 text-gray-500"
                                )}
                              >
                                {attr.data_type}
                              </Badge>
                              {attr.enum_values.length > 0 && (
                                <p className="text-[10px] text-muted-fg mt-0.5">
                                  {attr.enum_values.join(" | ")}
                                </p>
                              )}
                            </td>
                            <td className="py-2.5 pr-4">
                              <div className="flex flex-wrap gap-1">
                                {attr.applies_to.map((et) => (
                                  <Badge
                                    key={et}
                                    className="text-[10px] bg-accent/10 text-accent"
                                  >
                                    {et}
                                  </Badge>
                                ))}
                              </div>
                            </td>
                            <td className="py-2.5 pr-4">
                              {attr.required ? (
                                <span className="text-red-400 font-medium text-xs">
                                  Required
                                </span>
                              ) : (
                                <span className="text-muted-fg text-xs">
                                  Optional
                                </span>
                              )}
                            </td>
                            <td className="py-2.5 text-xs text-muted-fg">
                              {attr.owner_platform || "—"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            ))}
        </div>
      )}

      {/* Gap Analysis panel */}
      <Card className="border-amber-500/20">
        <button
          onClick={() => setShowGaps(!showGaps)}
          className="w-full flex items-center justify-between"
        >
          <CardTitle>
            <span className="flex items-center gap-2 text-amber-500">
              <AlertTriangle className="w-4 h-4" />
              Gap Analysis
              {gapData && gapData.entities_with_gaps > 0 && (
                <Badge className="ml-2 bg-amber-500/10 text-amber-500 text-xs">
                  {gapData.entities_with_gaps} entities with gaps
                </Badge>
              )}
            </span>
          </CardTitle>
          {showGaps ? (
            <ChevronDown className="w-4 h-4 text-muted-fg" />
          ) : (
            <ChevronRight className="w-4 h-4 text-muted-fg" />
          )}
        </button>

        {showGaps && (
          <CardContent className="mt-4">
            {gaps.isLoading && (
              <p className="text-sm text-muted-fg">Loading gap analysis...</p>
            )}
            {gapData && gapData.gaps.length === 0 && (
              <p className="text-sm text-emerald-500">
                No attribute gaps detected — all entities have required attributes.
              </p>
            )}
            {gapData && gapData.gaps.length > 0 && (
              <div className="space-y-3">
                <div className="flex gap-4 text-xs text-muted-fg">
                  <span>
                    Total entities scanned:{" "}
                    <strong className="text-foreground">
                      {gapData.total_entities}
                    </strong>
                  </span>
                  <span>
                    Entities with gaps:{" "}
                    <strong className="text-amber-500">
                      {gapData.entities_with_gaps}
                    </strong>
                  </span>
                  <span>
                    Total missing attributes:{" "}
                    <strong className="text-red-500">
                      {gapData.total_gaps}
                    </strong>
                  </span>
                </div>
                <div className="divide-y divide-card-border/50">
                  {gapData.gaps.slice(0, 20).map((gap) => (
                    <div key={gap.entity_id} className="py-2.5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Target className="w-3.5 h-3.5 text-amber-500" />
                          <span className="text-sm font-medium">
                            {gap.entity_name}
                          </span>
                          <Badge className="text-[10px] bg-accent/10 text-accent">
                            {gap.entity_type}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-fg">
                            {gap.gap_count} missing
                          </span>
                          <Badge
                            className={cn(
                              "text-xs",
                              gap.risk_score >= 30
                                ? "bg-red-500/10 text-red-500"
                                : gap.risk_score >= 10
                                ? "bg-amber-500/10 text-amber-500"
                                : "bg-blue-500/10 text-blue-500"
                            )}
                          >
                            Risk: {gap.risk_score}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-1 mt-1.5 ml-5">
                        {gap.missing_attributes.map((ma) => (
                          <Badge
                            key={ma.name}
                            className={cn(
                              "text-[10px]",
                              ma.required
                                ? "bg-red-500/10 text-red-400"
                                : "bg-gray-500/10 text-gray-400"
                            )}
                          >
                            {ma.display_name}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
                {gapData.gaps.length > 20 && (
                  <p className="text-xs text-muted-fg">
                    +{gapData.gaps.length - 20} more entities with gaps
                  </p>
                )}
              </div>
            )}
          </CardContent>
        )}
      </Card>
    </div>
  );
}
