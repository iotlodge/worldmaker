"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

export function useMicroservices(params?: {
  service_id?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery({
    queryKey: ["microservices", params],
    queryFn: () => api.microservices.list(params),
  });
}

export function useMicroservice(id: string) {
  return useQuery({
    queryKey: ["microservices", id],
    queryFn: () => api.microservices.get(id),
    enabled: !!id,
  });
}
