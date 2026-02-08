"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import type { Product, Feature } from "@/lib/types";

/**
 * Onboard a new product through Product Management.
 * Posts to /products with layer="generated".
 */
export function useOnboardProduct() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Product> & { name: string; owner: string }) =>
      api.products.create({ ...data, layer: "generated" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["products"] });
      qc.invalidateQueries({ queryKey: ["ecosystem"] });
    },
  });
}

/**
 * Create a workflow entity (change request, incident, issue) through
 * a management platform capability. Models as a Feature with
 * metadata.workflow_type discriminator.
 */
export function useOnboardWorkflow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (
      data: Partial<Feature> & {
        name: string;
        metadata: { workflow_type: string; [key: string]: unknown };
      }
    ) => api.features.create({ ...data, layer: "generated" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["features"] });
      qc.invalidateQueries({ queryKey: ["products"] });
      qc.invalidateQueries({ queryKey: ["ecosystem"] });
    },
  });
}
