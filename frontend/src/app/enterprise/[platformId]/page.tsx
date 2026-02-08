"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { usePlatform, useCapabilities } from "@/hooks/use-platforms";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog } from "@/components/ui/dialog";
import { PageLoader, ErrorState } from "@/components/ui/loading";
import { statusColor } from "@/lib/utils";
import {
  Package,
  RefreshCw,
  AlertTriangle,
  Bug,
  AlertCircle,
  ShieldAlert,
  Settings,
  Shield,
  Lock,
  Building2,
  Puzzle,
  ArrowLeft,
  Play,
  Clock,
} from "lucide-react";
import Link from "next/link";
import type { Capability } from "@/lib/types";

// Forms
import { ProductOnboardingForm } from "@/components/forms/product-onboarding-form";
import { ChangeRequestForm } from "@/components/forms/change-request-form";
import { IncidentReportForm } from "@/components/forms/incident-report-form";
import { IssueCreationForm } from "@/components/forms/issue-creation-form";

// ── Icon + color maps ───────────────────────────────────────────────────

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

// ── Capability → Form mapping ───────────────────────────────────────────

interface FormMapping {
  component: React.ComponentType<{ onSuccess?: () => void }>;
  dialogTitle: string;
  dialogDescription: string;
}

const CAPABILITY_FORMS: Record<string, FormMapping> = {
  "Product Onboarding": {
    component: ProductOnboardingForm,
    dialogTitle: "Onboard a New Product",
    dialogDescription: "Add a new product to the enterprise lifecycle",
  },
  "Change Request": {
    component: ChangeRequestForm,
    dialogTitle: "Submit a Change Request",
    dialogDescription: "Propose a change to an existing product or service",
  },
  "Incident Detection": {
    component: IncidentReportForm,
    dialogTitle: "Open an Incident",
    dialogDescription: "Report a production incident or service degradation",
  },
  "Issue Tracking": {
    component: IssueCreationForm,
    dialogTitle: "Create an Issue",
    dialogDescription: "Track a new issue or bug for resolution",
  },
};

// ── Capability Card ─────────────────────────────────────────────────────

function CapabilityCard({
  capability,
  onAction,
}: {
  capability: Capability;
  onAction?: () => void;
}) {
  const hasForm = capability.name in CAPABILITY_FORMS;

  return (
    <Card className="h-full">
      <div className="flex flex-col h-full">
        <div className="flex items-start justify-between mb-2">
          <div className="w-9 h-9 rounded-lg bg-accent/10 flex items-center justify-center">
            <Puzzle className="w-4 h-4 text-accent" />
          </div>
          <Badge className={statusColor(capability.status)}>
            {capability.status}
          </Badge>
        </div>

        <h3 className="text-sm font-semibold mb-1">{capability.name}</h3>
        <p className="text-xs text-muted-fg mb-4 flex-1 line-clamp-2">
          {capability.description}
        </p>

        <div className="pt-3 border-t border-card-border">
          {hasForm ? (
            <Button
              size="sm"
              onClick={onAction}
              className="w-full"
            >
              <Play className="w-3.5 h-3.5 mr-1.5" />
              Open
            </Button>
          ) : (
            <div className="flex items-center justify-center gap-1.5 text-xs text-muted-fg py-1.5">
              <Clock className="w-3.5 h-3.5" />
              Coming Soon
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}

// ── Page ─────────────────────────────────────────────────────────────────

export default function EnterprisePlatformPage() {
  const params = useParams();
  const platformId = params.platformId as string;

  const platform = usePlatform(platformId);
  const capabilities = useCapabilities({ platform_id: platformId, limit: 100 });

  const [activeForm, setActiveForm] = useState<string | null>(null);

  if (platform.isLoading || capabilities.isLoading) return <PageLoader />;
  if (platform.isError)
    return <ErrorState onRetry={() => platform.refetch()} />;

  const p = platform.data;
  if (!p) return <ErrorState message="Platform not found" />;

  const caps = capabilities.data?.capabilities ?? [];
  const Icon = PLATFORM_ICONS[p.name] ?? Building2;
  const colorClass = PLATFORM_COLORS[p.name] ?? "bg-gray-500/10 text-gray-500";

  const formMapping = activeForm ? CAPABILITY_FORMS[activeForm] : null;
  const FormComponent = formMapping?.component;

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link
        href="/enterprise"
        className="inline-flex items-center gap-1.5 text-sm text-muted-fg hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        Back to Business View
      </Link>

      {/* Platform header */}
      <div className="flex items-start gap-4">
        <div className={`w-14 h-14 rounded-xl ${colorClass} flex items-center justify-center`}>
          <Icon className="w-7 h-7" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">{p.name}</h1>
            <Badge className={statusColor(p.status)}>{p.status}</Badge>
            {p.layer === "core" && (
              <Badge variant="outline" className="text-[10px] border-emerald-500/30 text-emerald-500">
                CORE
              </Badge>
            )}
          </div>
          <p className="text-sm text-muted-fg mt-1">{p.description}</p>
          <p className="text-xs text-muted-fg mt-1">
            Owner: {p.owner} · {caps.length} capabilities
          </p>
        </div>
      </div>

      {/* Capabilities grid */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Capabilities</h2>
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {caps.map((cap) => (
            <CapabilityCard
              key={cap.id}
              capability={cap}
              onAction={() => setActiveForm(cap.name)}
            />
          ))}
        </div>
      </div>

      {/* Form dialog */}
      {formMapping && FormComponent && (
        <Dialog
          open={!!activeForm}
          onClose={() => setActiveForm(null)}
          title={formMapping.dialogTitle}
          description={formMapping.dialogDescription}
        >
          <FormComponent onSuccess={() => setActiveForm(null)} />
        </Dialog>
      )}
    </div>
  );
}
