"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

export function useEcosystemOverview() {
  return useQuery({
    queryKey: ["ecosystem", "overview"],
    queryFn: () => api.ecosystem.overview(),
  });
}

export function useEcosystemHealth() {
  return useQuery({
    queryKey: ["ecosystem", "health"],
    queryFn: () => api.ecosystem.health(),
  });
}

export function useStoreStatus() {
  return useQuery({
    queryKey: ["store", "status"],
    queryFn: () => api.health.storeStatus(),
  });
}

export function useEcosystemSearch(query: string) {
  return useQuery({
    queryKey: ["ecosystem", "search", query],
    queryFn: () => api.ecosystem.search(query),
    enabled: query.length > 0,
  });
}

export function useAuditLog(params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ["ecosystem", "audit", params],
    queryFn: () => api.ecosystem.audit(params),
  });
}
