"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

export function useFeatures(params?: {
  product_id?: string;
  status?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery({
    queryKey: ["features", params],
    queryFn: () => api.features.list(params),
    select: (data) => data.features,
  });
}

export function useFeature(id: string) {
  return useQuery({
    queryKey: ["features", id],
    queryFn: () => api.features.get(id),
    enabled: !!id,
  });
}
