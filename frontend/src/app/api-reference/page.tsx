"use client";

import { useState } from "react";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import {
  BookOpen,
  ChevronDown,
  ChevronRight,
  Heart,
  Globe,
  Package,
  Layers,
  Server,
  Workflow,
  Activity,
  GitBranch,
  Sparkles,
  Search,
  Zap,
  Copy,
  Check,
} from "lucide-react";

// ── Types ────────────────────────────────────────────────────────────────

interface Endpoint {
  method: "GET" | "POST" | "PUT" | "DELETE";
  path: string;
  description: string;
  params?: { name: string; type: string; required: boolean; description: string }[];
  notes?: string;
}

interface EndpointGroup {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  endpoints: Endpoint[];
}

// ── Method badge colors ──────────────────────────────────────────────────

function methodColor(method: string): string {
  switch (method) {
    case "GET":
      return "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400";
    case "POST":
      return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400";
    case "PUT":
      return "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400";
    case "DELETE":
      return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400";
    default:
      return "bg-gray-100 text-gray-800";
  }
}

// ── API Reference Data ───────────────────────────────────────────────────

const BASE_URL = "http://localhost:8000/api/v1";

const API_GROUPS: EndpointGroup[] = [
  {
    title: "Health & Status",
    icon: Heart,
    description: "System health checks, store status, and connectivity verification.",
    endpoints: [
      {
        method: "GET",
        path: "/health",
        description: "Check API health and version. Returns status and server info.",
      },
      {
        method: "GET",
        path: "/health/stores",
        description:
          "Data store status with entity counts, dependency count, trace/span counts.",
      },
    ],
  },
  {
    title: "Ecosystem Management",
    icon: Globe,
    description:
      "High-level ecosystem operations — overview, health scoring, search, and audit trail.",
    endpoints: [
      {
        method: "GET",
        path: "/ecosystem/overview",
        description:
          "Complete ecosystem summary: entity counts by type, dependency stats, circular dependency count, trace/span totals.",
        params: [
          {
            name: "include_stats",
            type: "bool",
            required: false,
            description: "Include statistics (default: true)",
          },
        ],
      },
      {
        method: "GET",
        path: "/ecosystem/health",
        description:
          "Health assessment with score (0-100), overall status, critical issues array, and warnings.",
        notes:
          "Health score: ≥95% active services = healthy, 80-94% = degraded, <80% = critical. Circular dependencies always generate a critical issue.",
      },
      {
        method: "GET",
        path: "/ecosystem/search",
        description: "Full-text search across all entity types.",
        params: [
          {
            name: "q",
            type: "string",
            required: true,
            description: "Search query (min 1 character)",
          },
          {
            name: "entity_type",
            type: "string",
            required: false,
            description: 'Filter by entity type (default: "service")',
          },
        ],
      },
      {
        method: "GET",
        path: "/ecosystem/audit",
        description: "Audit log of all entity changes with timestamps and actions.",
        params: [
          {
            name: "entity_id",
            type: "string",
            required: false,
            description: "Filter by specific entity",
          },
          {
            name: "entity_type",
            type: "string",
            required: false,
            description: "Filter by entity type",
          },
          {
            name: "limit",
            type: "int",
            required: false,
            description: "Max results (1-1000, default: 100)",
          },
        ],
      },
      {
        method: "GET",
        path: "/ecosystem/entities/{entity_type}",
        description: "List entities of any type with pagination.",
        params: [
          {
            name: "limit",
            type: "int",
            required: false,
            description: "Max results (1-1000, default: 100)",
          },
          {
            name: "offset",
            type: "int",
            required: false,
            description: "Pagination offset (default: 0)",
          },
        ],
      },
    ],
  },
  {
    title: "Products",
    icon: Package,
    description:
      "Product lifecycle management. Products own Features and define the consumer transaction experience domain.",
    endpoints: [
      {
        method: "GET",
        path: "/products",
        description: "List all products with status filtering and pagination.",
        params: [
          { name: "status", type: "string", required: false, description: "Filter by status" },
          { name: "limit", type: "int", required: false, description: "Max results (default: 100)" },
          { name: "offset", type: "int", required: false, description: "Pagination offset" },
        ],
      },
      { method: "GET", path: "/products/{product_id}", description: "Get product by ID." },
      { method: "POST", path: "/products", description: "Create a new product." },
      { method: "PUT", path: "/products/{product_id}", description: "Update a product." },
      { method: "DELETE", path: "/products/{product_id}", description: "Delete a product." },
    ],
  },
  {
    title: "Features",
    icon: Zap,
    description:
      "Features belong to Products and represent consumer-facing transaction experiences. Features are the primary risk surface for business outcome impact.",
    endpoints: [
      {
        method: "GET",
        path: "/features",
        description: "List features, optionally filtered by product or status.",
        params: [
          { name: "product_id", type: "string", required: false, description: "Filter by product" },
          { name: "status", type: "string", required: false, description: "Filter by status" },
          { name: "limit", type: "int", required: false, description: "Max results (default: 100)" },
          { name: "offset", type: "int", required: false, description: "Pagination offset" },
        ],
      },
      { method: "GET", path: "/features/{feature_id}", description: "Get feature by ID." },
      { method: "POST", path: "/features", description: "Create a new feature." },
      { method: "PUT", path: "/features/{feature_id}", description: "Update a feature." },
      { method: "DELETE", path: "/features/{feature_id}", description: "Delete a feature." },
    ],
  },
  {
    title: "Platforms",
    icon: Layers,
    description:
      "Platform management. Platforms own Capabilities and define the infrastructure interoperability domain.",
    endpoints: [
      {
        method: "GET",
        path: "/platforms",
        description: "List all platforms with optional status filter.",
        params: [
          { name: "status", type: "string", required: false, description: "Filter by status" },
          { name: "limit", type: "int", required: false, description: "Max results (default: 100)" },
          { name: "offset", type: "int", required: false, description: "Pagination offset" },
        ],
      },
      {
        method: "GET",
        path: "/platforms/{platform_id}",
        description: "Get platform with nested capabilities.",
      },
      { method: "POST", path: "/platforms", description: "Create a new platform." },
      { method: "PUT", path: "/platforms/{platform_id}", description: "Update a platform." },
      { method: "DELETE", path: "/platforms/{platform_id}", description: "Delete a platform." },
    ],
  },
  {
    title: "Capabilities",
    icon: Layers,
    description:
      "Capabilities belong to Platforms and represent infrastructure interop patterns. Risk here is measured by operational resilience and blast radius.",
    endpoints: [
      {
        method: "GET",
        path: "/capabilities",
        description: "List capabilities with optional platform filter.",
        params: [
          {
            name: "platform_id",
            type: "string",
            required: false,
            description: "Filter by platform",
          },
          { name: "limit", type: "int", required: false, description: "Max results (default: 100)" },
          { name: "offset", type: "int", required: false, description: "Pagination offset" },
        ],
      },
      {
        method: "POST",
        path: "/capabilities",
        description: "Create a new capability linked to a platform.",
      },
    ],
  },
  {
    title: "Services",
    icon: Server,
    description:
      "Service registry — the backbone of the ecosystem. Each service belongs to a platform and exposes APIs consumed through flows.",
    endpoints: [
      {
        method: "GET",
        path: "/services",
        description: "List services with multi-dimensional filtering.",
        params: [
          { name: "status", type: "string", required: false, description: "Filter by status" },
          {
            name: "platform_id",
            type: "string",
            required: false,
            description: "Filter by platform",
          },
          {
            name: "capability_id",
            type: "string",
            required: false,
            description: "Filter by capability",
          },
          { name: "limit", type: "int", required: false, description: "Max results (default: 100)" },
          { name: "offset", type: "int", required: false, description: "Pagination offset" },
        ],
      },
      {
        method: "GET",
        path: "/services/{service_id}",
        description: "Get service detail with nested microservices.",
      },
      { method: "POST", path: "/services", description: "Create a new service." },
      { method: "PUT", path: "/services/{service_id}", description: "Update a service." },
      { method: "DELETE", path: "/services/{service_id}", description: "Delete a service." },
      {
        method: "GET",
        path: "/services/{service_id}/context",
        description:
          "Agentic context — complete service intelligence: dependencies (upstream/downstream), health, blast radius, audit trail, microservices.",
        params: [
          {
            name: "include_dependencies",
            type: "bool",
            required: false,
            description: "Include dependency graph (default: true)",
          },
          {
            name: "include_health",
            type: "bool",
            required: false,
            description: "Include health data (default: true)",
          },
        ],
        notes:
          "This is the primary endpoint for AI agent consumption. It consolidates all service intelligence into a single call.",
      },
    ],
  },
  {
    title: "Microservices",
    icon: Server,
    description:
      "Container-level decomposition of services. Microservices track language, framework, container image, and repository details.",
    endpoints: [
      {
        method: "GET",
        path: "/microservices",
        description: "List microservices with optional service filter.",
        params: [
          {
            name: "service_id",
            type: "string",
            required: false,
            description: "Filter by parent service",
          },
          { name: "limit", type: "int", required: false, description: "Max results (default: 100)" },
        ],
      },
      {
        method: "GET",
        path: "/microservices/{ms_id}",
        description: "Get microservice by ID.",
      },
      { method: "POST", path: "/microservices", description: "Create a new microservice." },
    ],
  },
  {
    title: "Flows & Execution",
    icon: Workflow,
    description:
      "Flow definitions, step management, and execution. Executing a flow generates OpenTelemetry-compatible traces with full span telemetry.",
    endpoints: [
      {
        method: "GET",
        path: "/flows",
        description: "List flows with optional status/type filtering.",
        params: [
          { name: "status", type: "string", required: false, description: "Filter by status" },
          { name: "flow_type", type: "string", required: false, description: "Filter by type" },
          { name: "limit", type: "int", required: false, description: "Max results (default: 100)" },
        ],
      },
      {
        method: "GET",
        path: "/flows/{flow_id}",
        description: "Get flow with detailed steps and resolved service names.",
      },
      { method: "POST", path: "/flows", description: "Create a new flow." },
      { method: "PUT", path: "/flows/{flow_id}", description: "Update a flow." },
      { method: "DELETE", path: "/flows/{flow_id}", description: "Delete a flow." },
      {
        method: "POST",
        path: "/flows/{flow_id}/steps",
        description: "Add a step to a flow (from_service → to_service).",
      },
      {
        method: "POST",
        path: "/flows/{flow_id}/execute",
        description:
          "Execute a flow — generates OTel trace with spans for each step. Supports failure injection.",
        params: [
          {
            name: "environment",
            type: "string",
            required: false,
            description: 'Target environment (default: "prod")',
          },
          {
            name: "inject_failure",
            type: "bool",
            required: false,
            description: "Inject a random failure (default: false)",
          },
          {
            name: "failure_step",
            type: "int",
            required: false,
            description: "Specific step to fail (if inject_failure=true)",
          },
        ],
        notes:
          "Returns trace_id, duration_ms, span_count, and status. Navigate to /traces/{trace_id}/spans for full span tree.",
      },
      {
        method: "POST",
        path: "/flows/execute-all",
        description: "Execute all active flows and generate traces.",
        params: [
          {
            name: "environment",
            type: "string",
            required: false,
            description: 'Target environment (default: "prod")',
          },
        ],
      },
      {
        method: "GET",
        path: "/flows/{flow_id}/traces",
        description: "Get execution traces for a specific flow.",
        params: [
          { name: "limit", type: "int", required: false, description: "Max results (default: 100)" },
        ],
      },
    ],
  },
  {
    title: "Traces & Observability",
    icon: Activity,
    description:
      "OpenTelemetry-compatible trace and span data. Traces are generated by flow execution and include full span trees with timing, status, and attributes.",
    endpoints: [
      {
        method: "GET",
        path: "/traces",
        description: "List all execution traces with summary data.",
        params: [
          { name: "limit", type: "int", required: false, description: "Max results (default: 100)" },
        ],
      },
      {
        method: "GET",
        path: "/traces/{trace_id}/spans",
        description: "Get full span tree for a trace in OTel or Jaeger format.",
        params: [
          {
            name: "format",
            type: "string",
            required: false,
            description: 'Output format: "otel" or "jaeger" (default: "otel")',
          },
        ],
        notes:
          "OTel format includes: spanId, operationName, startTimeUnixNano, durationMs, status.code, kind, attributes, events, links.",
      },
    ],
  },
  {
    title: "Dependencies & Impact Analysis",
    icon: GitBranch,
    description:
      "Dependency graph queries, circular detection, blast radius analysis, and failure simulation. This is where risk measurement lives.",
    endpoints: [
      {
        method: "GET",
        path: "/services/{service_id}/dependencies",
        description:
          "Resolve service dependencies at three depth levels: direct, transitive (full BFS), or blast-radius (impact analysis).",
        params: [
          {
            name: "depth",
            type: "string",
            required: false,
            description:
              '"direct" | "transitive" | "blast-radius" (default: "direct")',
          },
        ],
        notes:
          "blast-radius depth includes affected_services with severity and hops_away for each. This is the primary impact analysis endpoint.",
      },
      {
        method: "GET",
        path: "/dependencies/circular",
        description:
          "All detected circular dependencies with source/target service names, dependency type, and severity.",
        params: [
          { name: "limit", type: "int", required: false, description: "Max results (default: 100)" },
        ],
        notes:
          "Circular deps are detected at creation time via BFS pathfinding. Each record includes source_name and target_name for human-readable display.",
      },
      {
        method: "POST",
        path: "/dependencies",
        description:
          "Create a dependency relationship. Automatically detects if it creates a circular dependency.",
      },
      {
        method: "POST",
        path: "/simulate/failure/{service_id}",
        description:
          "Simulate service failure — cascading impact analysis with severity breakdown, depth mapping, failure modes, recovery patterns, and recommendations.",
        notes:
          "Returns impact_by_severity, impact_by_depth, and actionable recommendations (circuit breakers, failover, architecture flattening).",
      },
    ],
  },
  {
    title: "Generator",
    icon: Sparkles,
    description:
      "Synthetic ecosystem generation for testing, demos, and stress testing. Generates deterministic ecosystems with configurable size and optional trace execution.",
    endpoints: [
      {
        method: "POST",
        path: "/generate",
        description: "Generate a synthetic ecosystem and load into store.",
        params: [
          {
            name: "seed",
            type: "int",
            required: false,
            description: "Random seed for deterministic output (default: 42)",
          },
          {
            name: "size",
            type: "string",
            required: false,
            description:
              '"small" | "medium" | "large" (default: "small")',
          },
          {
            name: "execute_flows",
            type: "bool",
            required: false,
            description: "Execute all flows and generate OTel traces (default: false)",
          },
        ],
        notes:
          "Small: ~100 entities. Medium: ~1,000 entities. Large: ~20,000 entities. Response includes summary breakdown by entity type.",
      },
      {
        method: "GET",
        path: "/generate/preview",
        description: "Preview generation without loading — shows entity count breakdown.",
        params: [
          { name: "seed", type: "int", required: false, description: "Random seed (default: 42)" },
          {
            name: "size",
            type: "string",
            required: false,
            description:
              '"small" | "medium" | "large" (default: "small")',
          },
        ],
      },
      {
        method: "POST",
        path: "/generate/reset",
        description: "Clear all data from the store.",
      },
    ],
  },
];

// ── Main page ────────────────────────────────────────────────────────────

export default function ApiReferencePage() {
  const [openSections, setOpenSections] = useState<Set<string>>(
    new Set(API_GROUPS.map((g) => g.title))
  );

  const toggleSection = (title: string) => {
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(title)) next.delete(title);
      else next.add(title);
      return next;
    });
  };

  const totalEndpoints = API_GROUPS.reduce(
    (sum, g) => sum + g.endpoints.length,
    0
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">API Reference</h1>
        <p className="text-sm text-muted-fg mt-1">
          {totalEndpoints} endpoints across {API_GROUPS.length} domains — the
          complete interface for ecosystem intelligence
        </p>
      </div>

      {/* Base URL card */}
      <Card className="border-accent/20 bg-accent/5">
        <div className="flex items-start gap-4">
          <BookOpen className="w-5 h-5 text-accent shrink-0 mt-0.5" />
          <div className="space-y-2 flex-1">
            <p className="text-sm font-medium">Base URL</p>
            <CopyableCode code={BASE_URL} />
            <p className="text-xs text-muted-fg mt-2">
              All endpoints are prefixed with <code className="text-xs bg-muted/20 px-1 rounded">/api/v1</code>.
              Interactive docs available at{" "}
              <code className="text-xs bg-muted/20 px-1 rounded">/api/docs</code>{" "}
              (Swagger) and{" "}
              <code className="text-xs bg-muted/20 px-1 rounded">/api/redoc</code>{" "}
              (ReDoc). All responses are JSON.
            </p>
          </div>
        </div>
      </Card>

      {/* Entity hierarchy context */}
      <Card>
        <CardTitle>Entity Hierarchy</CardTitle>
        <CardContent className="mt-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="space-y-1">
              <p className="font-medium text-amber-500">Product Domain</p>
              <p className="text-muted-fg">
                Product → Features → User Flows
              </p>
              <p className="text-xs text-muted-fg">
                Consumer transaction experience. Risk measured by business outcome impact.
              </p>
            </div>
            <div className="space-y-1">
              <p className="font-medium text-cyan-500">Platform Domain</p>
              <p className="text-muted-fg">
                Platform → Capabilities → Services → Microservices
              </p>
              <p className="text-xs text-muted-fg">
                Infrastructure interop. Risk measured by operational resilience and blast radius.
              </p>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-card-border/50 text-xs text-muted-fg space-y-1">
            <p>
              <span className="font-medium text-foreground">Flows</span> connect
              services through steps, generating OTel traces when executed.
            </p>
            <p>
              <span className="font-medium text-foreground">Dependencies</span>{" "}
              link services directionally. Circular dependencies are auto-detected
              and flagged as critical risk.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* AI agent usage note */}
      <Card className="border-violet-500/20 bg-violet-500/5">
        <div className="flex items-start gap-4">
          <Search className="w-5 h-5 text-violet-500 shrink-0 mt-0.5" />
          <div className="text-sm space-y-1">
            <p className="font-medium text-violet-500">
              For AI Ecosystem Agents
            </p>
            <p className="text-muted-fg">
              Start with{" "}
              <code className="text-xs bg-muted/20 px-1 rounded">
                GET /ecosystem/overview
              </code>{" "}
              for full entity counts and statistics. Use{" "}
              <code className="text-xs bg-muted/20 px-1 rounded">
                GET /services/&#123;id&#125;/context
              </code>{" "}
              for complete service intelligence in a single call. Query{" "}
              <code className="text-xs bg-muted/20 px-1 rounded">
                GET /dependencies/circular
              </code>{" "}
              and{" "}
              <code className="text-xs bg-muted/20 px-1 rounded">
                POST /simulate/failure/&#123;id&#125;
              </code>{" "}
              for risk assessment. All endpoints support pagination via limit/offset.
            </p>
          </div>
        </div>
      </Card>

      {/* Endpoint groups */}
      <div className="space-y-2">
        {API_GROUPS.map((group) => {
          const isOpen = openSections.has(group.title);
          const Icon = group.icon;

          return (
            <Card key={group.title} className="overflow-hidden">
              <button
                onClick={() => toggleSection(group.title)}
                className="w-full flex items-center gap-3 text-left"
              >
                <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
                  <Icon className="w-4 h-4 text-accent" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm">{group.title}</span>
                    <Badge variant="outline" className="text-[10px]">
                      {group.endpoints.length}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-fg truncate">
                    {group.description}
                  </p>
                </div>
                {isOpen ? (
                  <ChevronDown className="w-4 h-4 text-muted-fg shrink-0" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-muted-fg shrink-0" />
                )}
              </button>

              {isOpen && (
                <CardContent className="mt-3 pt-3 border-t border-card-border/50 space-y-3">
                  {group.endpoints.map((ep) => (
                    <EndpointRow key={`${ep.method}-${ep.path}`} endpoint={ep} />
                  ))}
                </CardContent>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────

function EndpointRow({ endpoint: ep }: { endpoint: Endpoint }) {
  return (
    <div className="border border-card-border/50 rounded-lg p-3 space-y-2">
      <div className="flex items-center gap-2 flex-wrap">
        <Badge className={cn("text-xs font-mono font-bold", methodColor(ep.method))}>
          {ep.method}
        </Badge>
        <code className="text-sm font-mono text-foreground">{ep.path}</code>
      </div>
      <p className="text-sm text-muted-fg">{ep.description}</p>

      {ep.params && ep.params.length > 0 && (
        <div className="mt-2">
          <p className="text-xs font-medium text-muted-fg mb-1">Parameters:</p>
          <div className="space-y-1">
            {ep.params.map((p) => (
              <div
                key={p.name}
                className="flex items-baseline gap-2 text-xs"
              >
                <code className="text-xs font-mono text-accent bg-accent/5 px-1 rounded">
                  {p.name}
                </code>
                <span className="text-muted-fg">
                  ({p.type}{p.required ? ", required" : ""})
                </span>
                <span className="text-muted-fg">— {p.description}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {ep.notes && (
        <p className="text-xs text-muted-fg italic border-l-2 border-accent/20 pl-2 mt-2">
          {ep.notes}
        </p>
      )}
    </div>
  );
}

function CopyableCode({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API may not be available
    }
  };

  return (
    <div className="flex items-center gap-2 bg-muted/10 border border-card-border rounded-md px-3 py-1.5 font-mono text-sm">
      <code className="flex-1">{code}</code>
      <button
        onClick={handleCopy}
        className="text-muted-fg hover:text-foreground transition-colors"
        title="Copy to clipboard"
      >
        {copied ? (
          <Check className="w-3.5 h-3.5 text-emerald-500" />
        ) : (
          <Copy className="w-3.5 h-3.5" />
        )}
      </button>
    </div>
  );
}
