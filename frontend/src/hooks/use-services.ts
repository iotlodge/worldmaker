"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import type { Service } from "@/lib/types";

export function useServices(params?: {
  platform_id?: string;
  status?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery({
    queryKey: ["services", params],
    queryFn: () => api.services.list(params),
  });
}

export function useService(id: string) {
  return useQuery({
    queryKey: ["services", id],
    queryFn: () => api.services.get(id),
    enabled: !!id,
  });
}

export function useServiceContext(id: string) {
  return useQuery({
    queryKey: ["services", id, "context"],
    queryFn: () => api.services.context(id),
    enabled: !!id,
  });
}

export function useServiceDependencies(
  id: string,
  depth?: "direct" | "transitive" | "blast-radius"
) {
  return useQuery({
    queryKey: ["services", id, "dependencies", depth],
    queryFn: () => api.services.dependencies(id, depth),
    enabled: !!id,
  });
}

export function useCreateService() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Service>) => api.services.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["services"] });
      qc.invalidateQueries({ queryKey: ["ecosystem"] });
    },
  });
}

export function useUpdateService() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Service> }) =>
      api.services.update(id, data),
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: ["services", variables.id] });
      qc.invalidateQueries({ queryKey: ["services"] });
    },
  });
}

export function useDeleteService() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.services.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["services"] });
      qc.invalidateQueries({ queryKey: ["ecosystem"] });
    },
  });
}
