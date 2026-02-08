"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

export function useCodeManifest(msId: string) {
  return useQuery({
    queryKey: ["codegen", msId, "manifest"],
    queryFn: () => api.codegen.manifest(msId),
    enabled: !!msId,
  });
}

export function useCodeFile(msId: string, filename: string) {
  return useQuery({
    queryKey: ["codegen", msId, "file", filename],
    queryFn: () => api.codegen.file(msId, filename),
    enabled: !!msId && !!filename,
  });
}

export function useScaffoldCode() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (msId: string) => api.codegen.scaffold(msId),
    onSuccess: (_data, msId) => {
      qc.invalidateQueries({ queryKey: ["codegen", msId] });
    },
  });
}
