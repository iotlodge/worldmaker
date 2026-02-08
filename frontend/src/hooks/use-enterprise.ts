"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

export function useCorePlatforms() {
  return useQuery({
    queryKey: ["platforms", { layer: "core" }],
    queryFn: () => api.platforms.list({ layer: "core", limit: 100 }),
  });
}

export function useGeneratedPlatforms() {
  return useQuery({
    queryKey: ["platforms", { layer: "generated" }],
    queryFn: () => api.platforms.list({ layer: "generated", limit: 100 }),
  });
}
