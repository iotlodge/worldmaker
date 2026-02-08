import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import type { EntityStatus, HealthStatus, Severity } from "./types";

/** Merge Tailwind classes safely */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Format ISO timestamp to readable string */
export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/** Format ISO timestamp to relative time */
export function formatRelativeTime(iso: string): string {
  const now = Date.now();
  const then = new Date(iso).getTime();
  const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffSec < 60) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay < 30) return `${diffDay}d ago`;
  return formatDate(iso);
}

/** Format milliseconds to human-readable duration */
export function formatDuration(ms: number): string {
  if (ms < 1) return `${(ms * 1000).toFixed(0)}µs`;
  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

/** Format microseconds to human-readable duration */
export function formatDurationUs(us: number): string {
  if (us < 1000) return `${us.toFixed(0)}µs`;
  return formatDuration(us / 1000);
}

/** Status → color mapping for badges */
export function statusColor(status: EntityStatus): string {
  const map: Record<EntityStatus, string> = {
    active: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400",
    planned: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
    deprecated: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400",
    decommissioned: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
    sunset: "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400",
  };
  return map[status] ?? "bg-gray-100 text-gray-800";
}

/** Health → color mapping */
export function healthColor(health: HealthStatus | "empty"): string {
  const map: Record<string, string> = {
    healthy: "text-emerald-500",
    degraded: "text-amber-500",
    unhealthy: "text-red-500",
    unknown: "text-gray-400",
    empty: "text-gray-300",
  };
  return map[health] ?? "text-gray-400";
}

/** Severity → color mapping */
export function severityColor(severity: Severity): string {
  const map: Record<Severity, string> = {
    critical: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
    high: "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400",
    medium: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400",
    low: "bg-slate-100 text-slate-800 dark:bg-slate-900/30 dark:text-slate-400",
  };
  return map[severity] ?? "bg-gray-100 text-gray-800";
}

/** Truncate a UUID for display */
export function shortId(id: string): string {
  return id.slice(0, 8);
}

/** Capitalize first letter */
export function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

/** Format entity type for display */
export function formatEntityType(type: string): string {
  return type
    .split("_")
    .map((w) => capitalize(w))
    .join(" ");
}

/** Build query string from params, omitting undefined/null */
export function buildQueryString(params: Record<string, unknown>): string {
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      qs.set(key, String(value));
    }
  }
  const str = qs.toString();
  return str ? `?${str}` : "";
}
