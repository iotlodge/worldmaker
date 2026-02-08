"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import type { Flow } from "@/lib/types";

export function useFlows(params?: {
  status?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery({
    queryKey: ["flows", params],
    queryFn: () => api.flows.list(params),
  });
}

export function useFlow(id: string) {
  return useQuery({
    queryKey: ["flows", id],
    queryFn: () => api.flows.get(id),
    enabled: !!id,
  });
}

export function useFlowTraces(flowId: string) {
  return useQuery({
    queryKey: ["flows", flowId, "traces"],
    queryFn: () => api.flows.traces(flowId),
    select: (data) => data.traces,
    enabled: !!flowId,
  });
}

export function useExecuteFlow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      params,
    }: {
      id: string;
      params?: { environment?: string; inject_failure?: boolean };
    }) => api.flows.execute(id, params),
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: ["flows", variables.id, "traces"] });
      qc.invalidateQueries({ queryKey: ["traces"] });
      qc.invalidateQueries({ queryKey: ["ecosystem"] });
    },
  });
}

export function useCreateFlow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Flow>) => api.flows.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["flows"] });
      qc.invalidateQueries({ queryKey: ["ecosystem"] });
    },
  });
}
