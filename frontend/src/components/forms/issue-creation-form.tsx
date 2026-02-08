"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { useOnboardWorkflow } from "@/hooks/use-onboarding";
import { useProducts } from "@/hooks/use-products";
import { useToast } from "@/components/ui/toast";

const PRIORITY_OPTIONS = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" },
];

interface Props {
  onSuccess?: () => void;
}

export function IssueCreationForm({ onSuccess }: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [productId, setProductId] = useState("");
  const [priority, setPriority] = useState("medium");
  const [assignee, setAssignee] = useState("");
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
    if (!title.trim()) errs.title = "Issue title is required";
    if (!description.trim()) errs.description = "Description is required";
    if (!productId) errs.productId = "Select a product";
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
        status: "active",
        owner: assignee.trim() || "issues-management-team",
        user_flows: [],
        depends_on_features: [],
        metadata: {
          workflow_type: "issue",
          priority,
          assignee: assignee.trim() || undefined,
        },
      },
      {
        onSuccess: () => {
          success(`Issue "${title}" created — priority: ${priority}`);
          onSuccess?.();
        },
        onError: (err) => {
          showError(`Failed to create issue: ${err.message}`);
        },
      }
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Issue Title"
        placeholder="e.g., Login form validation not working on mobile"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        error={errors.title}
        required
      />

      <Textarea
        label="Description"
        placeholder="Steps to reproduce, expected vs. actual behavior"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        error={errors.description}
        rows={4}
        required
      />

      <Select
        label="Product"
        options={productOptions}
        placeholder="Select a product..."
        value={productId}
        onChange={(e) => setProductId(e.target.value)}
        error={errors.productId}
        required
      />

      <div className="grid grid-cols-2 gap-4">
        <Select
          label="Priority"
          options={PRIORITY_OPTIONS}
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
        />

        <Input
          label="Assignee"
          placeholder="e.g., dev-team or john@company.com"
          value={assignee}
          onChange={(e) => setAssignee(e.target.value)}
        />
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Creating..." : "Create Issue"}
        </Button>
      </div>
    </form>
  );
}
