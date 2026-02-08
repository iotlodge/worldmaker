"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { useOnboardWorkflow } from "@/hooks/use-onboarding";
import { useServices } from "@/hooks/use-services";
import { useToast } from "@/components/ui/toast";

const SEVERITY_OPTIONS = [
  { value: "critical", label: "Critical — Service down" },
  { value: "high", label: "High — Major degradation" },
  { value: "medium", label: "Medium — Partial impact" },
  { value: "low", label: "Low — Minor issue" },
];

const INCIDENT_STATUS = [
  { value: "investigating", label: "Investigating" },
  { value: "acknowledged", label: "Acknowledged" },
  { value: "in_progress", label: "In Progress" },
];

interface Props {
  onSuccess?: () => void;
}

export function IncidentReportForm({ onSuccess }: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState("high");
  const [serviceId, setServiceId] = useState("");
  const [incidentStatus, setIncidentStatus] = useState("investigating");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const mutation = useOnboardWorkflow();
  const services = useServices({ limit: 200 });
  const { success, error: showError } = useToast();

  const serviceOptions = (services.data?.services ?? []).map((s) => ({
    value: s.id,
    label: s.name,
  }));

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!title.trim()) errs.title = "Incident title is required";
    if (!description.trim()) errs.description = "Description is required";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    mutation.mutate(
      {
        name: title.trim(),
        description: description.trim(),
        status: "active",
        owner: "incident-management-team",
        user_flows: [],
        depends_on_features: [],
        metadata: {
          workflow_type: "incident",
          severity,
          incident_status: incidentStatus,
          affected_service_id: serviceId || undefined,
        },
      },
      {
        onSuccess: () => {
          success(`Incident "${title}" opened — severity: ${severity}`);
          onSuccess?.();
        },
        onError: (err) => {
          showError(`Failed to open incident: ${err.message}`);
        },
      }
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Incident Title"
        placeholder="e.g., Payment service timeout errors in production"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        error={errors.title}
        required
      />

      <Textarea
        label="Description"
        placeholder="What is happening? User impact? Affected components?"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        error={errors.description}
        rows={4}
        required
      />

      <div className="grid grid-cols-2 gap-4">
        <Select
          label="Severity"
          options={SEVERITY_OPTIONS}
          value={severity}
          onChange={(e) => setSeverity(e.target.value)}
          required
        />

        <Select
          label="Status"
          options={INCIDENT_STATUS}
          value={incidentStatus}
          onChange={(e) => setIncidentStatus(e.target.value)}
        />
      </div>

      <Select
        label="Affected Service"
        options={serviceOptions}
        placeholder="Select a service (optional)..."
        value={serviceId}
        onChange={(e) => setServiceId(e.target.value)}
      />

      <div className="flex justify-end gap-3 pt-2">
        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Opening..." : "Open Incident"}
        </Button>
      </div>
    </form>
  );
}
