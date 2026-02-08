"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { useOnboardProduct } from "@/hooks/use-onboarding";
import { useToast } from "@/components/ui/toast";

const STATUS_OPTIONS = [
  { value: "planned", label: "Planned" },
  { value: "active", label: "Active" },
  { value: "deprecated", label: "Deprecated" },
];

interface Props {
  onSuccess?: () => void;
}

export function ProductOnboardingForm({ onSuccess }: Props) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [owner, setOwner] = useState("");
  const [status, setStatus] = useState("active");
  const [version, setVersion] = useState("1");
  const [tags, setTags] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const mutation = useOnboardProduct();
  const { success, error: showError } = useToast();

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!name.trim()) errs.name = "Product name is required";
    if (!owner.trim()) errs.owner = "Owner is required";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    const tagList = tags
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);

    mutation.mutate(
      {
        name: name.trim(),
        description: description.trim() || undefined,
        owner: owner.trim(),
        status: status as "planned" | "active" | "deprecated",
        version: parseInt(version) || 1,
        tags: tagList,
        features: [],
      },
      {
        onSuccess: () => {
          success(`Product "${name}" onboarded successfully`);
          onSuccess?.();
        },
        onError: (err) => {
          showError(`Failed to onboard product: ${err.message}`);
        },
      }
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Product Name"
        placeholder="e.g., Customer Portal"
        value={name}
        onChange={(e) => setName(e.target.value)}
        error={errors.name}
        required
      />

      <Textarea
        label="Description"
        placeholder="What does this product do?"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        rows={3}
      />

      <Input
        label="Owner"
        placeholder="e.g., platform-team or john@company.com"
        value={owner}
        onChange={(e) => setOwner(e.target.value)}
        error={errors.owner}
        required
      />

      <div className="grid grid-cols-2 gap-4">
        <Select
          label="Status"
          options={STATUS_OPTIONS}
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        />

        <Input
          label="Version"
          type="number"
          min={1}
          value={version}
          onChange={(e) => setVersion(e.target.value)}
        />
      </div>

      <Input
        label="Tags"
        placeholder="e.g., frontend, payments, core (comma-separated)"
        value={tags}
        onChange={(e) => setTags(e.target.value)}
      />

      <div className="flex justify-end gap-3 pt-2">
        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Onboarding..." : "Onboard Product"}
        </Button>
      </div>
    </form>
  );
}
