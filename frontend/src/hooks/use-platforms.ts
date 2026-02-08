"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import type { Platform, Capability } from "@/lib/types";

export function usePlatforms(params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ["platforms", params],
    queryFn: () => api.platforms.list(params),
  });
}

export function usePlatform(id: string) {
  return useQuery({
    queryKey: ["platforms", id],
    queryFn: () => api.platforms.get(id),
    enabled: !!id,
  });
}

export function useCreatePlatform() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Platform>) => api.platforms.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["platforms"] });
      qc.invalidateQueries({ queryKey: ["ecosystem"] });
    },
  });
}

export function useCapabilities(params?: {
  platform_id?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery({
    queryKey: ["capabilities", params],
    queryFn: () => api.capabilities.list(params),
  });
}

export function useCapability(id: string) {
  return useQuery({
    queryKey: ["capabilities", id],
    queryFn: () => api.capabilities.get(id),
    enabled: !!id,
  });
}

export function useCreateCapability() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Capability>) => api.capabilities.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["capabilities"] });
      qc.invalidateQueries({ queryKey: ["ecosystem"] });
    },
  });
}
