"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { useOnboardWorkflow } from "@/hooks/use-onboarding";
import { useProducts } from "@/hooks/use-products";
import { useToast } from "@/components/ui/toast";

const CHANGE_TYPES = [
  { value: "feature_release", label: "Feature Release" },
  { value: "hotfix", label: "Hotfix" },
  { value: "security_patch", label: "Security Patch" },
  { value: "deprecation", label: "Deprecation" },
  { value: "migration", label: "Migration" },
];

const PRIORITY_OPTIONS = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" },
];

interface Props {
  onSuccess?: () => void;
}

export function ChangeRequestForm({ onSuccess }: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [productId, setProductId] = useState("");
  const [changeType, setChangeType] = useState("feature_release");
  const [priority, setPriority] = useState("medium");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const mutation = useOnboardWorkflow();
  const products = useProducts({ limit: 200 });
  const { success, error: showError } = useToast();

  const productOptions = (products.data?.products ?? []).map((p) => ({
    value: p.id,
    label: p.name,
  }));

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!title.trim()) errs.title = "Change title is required";
    if (!description.trim()) errs.description = "Description is required";
    if (!productId) errs.productId = "Select an affected product";
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
        product_id: productId,
        status: "planned",
        owner: "change-management-team",
        user_flows: [],
        depends_on_features: [],
        metadata: {
          workflow_type: "change_request",
          change_type: changeType,
          priority,
        },
      },
      {
        onSuccess: () => {
          success(`Change request "${title}" submitted`);
          onSuccess?.();
        },
        onError: (err) => {
          showError(`Failed to submit change request: ${err.message}`);
        },
      }
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Change Title"
        placeholder="e.g., Migrate payment gateway to Stripe v3"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        error={errors.title}
        required
      />

      <Textarea
        label="Description"
        placeholder="What is changing, why, and what is the expected impact?"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        error={errors.description}
        rows={4}
        required
      />

      <Select
        label="Affected Product"
        options={productOptions}
        placeholder="Select a product..."
        value={productId}
        onChange={(e) => setProductId(e.target.value)}
        error={errors.productId}
        required
      />

      <div className="grid grid-cols-2 gap-4">
        <Select
          label="Change Type"
          options={CHANGE_TYPES}
          value={changeType}
          onChange={(e) => setChangeType(e.target.value)}
        />

        <Select
          label="Priority"
          options={PRIORITY_OPTIONS}
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
        />
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Submitting..." : "Submit Change Request"}
        </Button>
      </div>
    </form>
  );
}
