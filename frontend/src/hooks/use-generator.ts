"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

export function useGenerate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (params: {
      size?: string;
      seed?: number;
      with_traces?: boolean;
    }) => {
      // Auto-reset the store before generating so each size gives clean results
      await api.generator.reset();
      return api.generator.generate(params);
    },
    onSuccess: () => {
      // Invalidate everything — generation repopulates the store
      qc.invalidateQueries();
    },
  });
}

export function useGeneratePreview() {
  return useMutation({
    mutationFn: (params: { size?: string; seed?: number }) =>
      api.generator.preview(params),
  });
}

export function useReset() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.generator.reset(),
    onSuccess: () => {
      qc.invalidateQueries();
    },
  });
}
