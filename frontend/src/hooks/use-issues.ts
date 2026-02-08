"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

export function useCircularDependencies(params?: { limit?: number }) {
  return useQuery({
    queryKey: ["dependencies", "circular", params],
    queryFn: () => api.dependencies.circular(params),
  });
}

export function useDependencies(params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ["dependencies", "list", params],
    queryFn: () => api.dependencies.list(params),
  });
}
