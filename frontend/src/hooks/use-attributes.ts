"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import type { AttributeDefinition } from "@/lib/types";

export function useAttributes(params?: {
  tier?: string;
  category?: string;
  applies_to?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery({
    queryKey: ["attributes", params],
    queryFn: () => api.attributes.list(params),
  });
}

export function useAttribute(id: string) {
  return useQuery({
    queryKey: ["attributes", id],
    queryFn: () => api.attributes.get(id),
    enabled: !!id,
  });
}

export function useAttributeGaps(params?: {
  entity_type?: string;
  tier?: string;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["attributes", "gaps", params],
    queryFn: () => api.attributes.gaps(params),
  });
}

export function useEntityAttributes(entityType: string, entityId: string) {
  return useQuery({
    queryKey: ["attributes", "entity", entityType, entityId],
    queryFn: () => api.attributes.forEntity(entityType, entityId),
    enabled: !!entityType && !!entityId,
  });
}

export function useCreateAttribute() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<AttributeDefinition>) =>
      api.attributes.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["attributes"] });
    },
  });
}

export function useStampAttribute() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      entity_type: string;
      entity_id: string;
      attribute_name: string;
      value: unknown;
      stamped_by?: string;
    }) => api.attributes.stamp(data),
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({
        queryKey: ["attributes", "entity", variables.entity_type, variables.entity_id],
      });
      qc.invalidateQueries({ queryKey: ["attributes", "gaps"] });
    },
  });
}

export function useDeleteAttribute() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.attributes.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["attributes"] });
    },
  });
}
