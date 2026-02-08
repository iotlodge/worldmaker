/**
 * WorldMaker API Client
 *
 * Typed fetch wrapper for all backend endpoints.
 * Base URL configurable via NEXT_PUBLIC_API_URL env var.
 */

import { buildQueryString } from "./utils";
import type {
  Product,
  ProductListResponse,
  Feature,
  FeatureListResponse,
  Platform,
  PlatformListResponse,
  Capability,
  CapabilityListResponse,
  Service,
  ServiceListResponse,
  Microservice,
  MicroserviceListResponse,
  Flow,
  FlowListResponse,
  TraceResult,
  TraceListResponse,
  FlowTracesResponse,
  TraceSpansResponse,
  EcosystemOverview,
  EcosystemHealth,
  DependencyAnalysis,
  DependencyListResponse,
  CircularDependencyResponse,
  FailureSimulation,
  GenerateResult,
  GeneratePreview,
  ServiceContext,
  AuditLogResponse,
  StoreStatus,
  SearchResult,
} from "./types";

// ── Config ───────────────────────────────────────────────────────────────

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

// ── Fetch Wrapper ────────────────────────────────────────────────────────

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public body: unknown
  ) {
    super(`API Error ${status}: ${statusText}`);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let body: unknown;
    try {
      body = await res.json();
    } catch {
      body = await res.text();
    }
    throw new ApiError(res.status, res.statusText, body);
  }

  // Handle 204 No Content
  if (res.status === 204) return undefined as T;
  return res.json();
}

function get<T>(path: string): Promise<T> {
  return request<T>(path, { method: "GET" });
}

function post<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    body: body ? JSON.stringify(body) : undefined,
  });
}

function put<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

function del<T = void>(path: string): Promise<T> {
  return request<T>(path, { method: "DELETE" });
}

// ── Health & Status ──────────────────────────────────────────────────────

export const health = {
  check: () => get<{ status: string }>("/health"),
  storeStatus: () => get<StoreStatus>("/store/status"),
};

// ── Ecosystem ────────────────────────────────────────────────────────────

export const ecosystem = {
  overview: () => get<EcosystemOverview>("/ecosystem/overview"),
  health: () => get<EcosystemHealth>("/ecosystem/health"),
  search: (query: string) =>
    get<SearchResult>(`/ecosystem/search${buildQueryString({ q: query })}`),
  audit: (params?: { limit?: number; offset?: number }) =>
    get<AuditLogResponse>(`/ecosystem/audit${buildQueryString(params ?? {})}`),
};

// ── Products ─────────────────────────────────────────────────────────────

export const products = {
  list: (params?: { limit?: number; offset?: number }) =>
    get<ProductListResponse>(`/products${buildQueryString(params ?? {})}`),
  get: (id: string) => get<Product>(`/products/${id}`),
  create: (data: Partial<Product>) => post<Product>("/products", data),
  update: (id: string, data: Partial<Product>) =>
    put<Product>(`/products/${id}`, data),
  delete: (id: string) => del(`/products/${id}`),
};

// ── Features ────────────────────────────────────────────────────────────

export const features = {
  list: (params?: { product_id?: string; status?: string; limit?: number; offset?: number }) =>
    get<FeatureListResponse>(`/features${buildQueryString(params ?? {})}`),
  get: (id: string) => get<Feature>(`/features/${id}`),
  create: (data: Partial<Feature>) => post<Feature>("/features", data),
  update: (id: string, data: Partial<Feature>) =>
    put<Feature>(`/features/${id}`, data),
  delete: (id: string) => del(`/features/${id}`),
};

// ── Platforms ────────────────────────────────────────────────────────────

export const platforms = {
  list: (params?: { limit?: number; offset?: number }) =>
    get<PlatformListResponse>(`/platforms${buildQueryString(params ?? {})}`),
  get: (id: string) => get<Platform>(`/platforms/${id}`),
  create: (data: Partial<Platform>) => post<Platform>("/platforms", data),
  update: (id: string, data: Partial<Platform>) =>
    put<Platform>(`/platforms/${id}`, data),
  delete: (id: string) => del(`/platforms/${id}`),
};

// ── Capabilities ─────────────────────────────────────────────────────────

export const capabilities = {
  list: (params?: { platform_id?: string; limit?: number; offset?: number }) =>
    get<CapabilityListResponse>(
      `/capabilities${buildQueryString(params ?? {})}`
    ),
  get: (id: string) => get<Capability>(`/capabilities/${id}`),
  create: (data: Partial<Capability>) =>
    post<Capability>("/capabilities", data),
  update: (id: string, data: Partial<Capability>) =>
    put<Capability>(`/capabilities/${id}`, data),
  delete: (id: string) => del(`/capabilities/${id}`),
};

// ── Services ─────────────────────────────────────────────────────────────

export const services = {
  list: (params?: {
    platform_id?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) => get<ServiceListResponse>(`/services${buildQueryString(params ?? {})}`),
  get: (id: string) => get<Service>(`/services/${id}`),
  create: (data: Partial<Service>) => post<Service>("/services", data),
  update: (id: string, data: Partial<Service>) =>
    put<Service>(`/services/${id}`, data),
  delete: (id: string) => del(`/services/${id}`),
  context: (id: string) => get<ServiceContext>(`/services/${id}/context`),
  dependencies: (id: string, depth?: "direct" | "transitive" | "blast-radius") =>
    get<DependencyAnalysis>(
      `/services/${id}/dependencies${buildQueryString({ depth: depth ?? "direct" })}`
    ),
};

// ── Microservices ────────────────────────────────────────────────────────

export const microservices = {
  list: (params?: { service_id?: string; limit?: number; offset?: number }) =>
    get<MicroserviceListResponse>(
      `/microservices${buildQueryString(params ?? {})}`
    ),
  get: (id: string) => get<Microservice>(`/microservices/${id}`),
  create: (data: Partial<Microservice>) =>
    post<Microservice>("/microservices", data),
  update: (id: string, data: Partial<Microservice>) =>
    put<Microservice>(`/microservices/${id}`, data),
  delete: (id: string) => del(`/microservices/${id}`),
};

// ── Flows ────────────────────────────────────────────────────────────────

export const flows = {
  list: (params?: { status?: string; limit?: number; offset?: number }) =>
    get<FlowListResponse>(`/flows${buildQueryString(params ?? {})}`),
  get: (id: string) => get<Flow>(`/flows/${id}`),
  create: (data: Partial<Flow>) => post<Flow>("/flows", data),
  update: (id: string, data: Partial<Flow>) =>
    put<Flow>(`/flows/${id}`, data),
  delete: (id: string) => del(`/flows/${id}`),
  execute: (id: string, params?: { environment?: string; inject_failure?: boolean }) =>
    post<TraceResult>(
      `/flows/${id}/execute${buildQueryString(params ?? {})}`
    ),
  traces: (id: string) => get<FlowTracesResponse>(`/flows/${id}/traces`),
};

// ── Traces ───────────────────────────────────────────────────────────────

export const traces = {
  get: (traceId: string) =>
    get<TraceSpansResponse>(`/traces/${traceId}/spans`),
  list: (params?: { limit?: number }) =>
    get<TraceListResponse>(`/traces${buildQueryString(params ?? {})}`),
};

// ── Dependencies ─────────────────────────────────────────────────────────

export const dependencies = {
  list: (params?: { limit?: number; offset?: number }) =>
    get<DependencyListResponse>(`/dependencies${buildQueryString(params ?? {})}`),
  circular: (params?: { limit?: number }) =>
    get<CircularDependencyResponse>(
      `/dependencies/circular${buildQueryString(params ?? {})}`
    ),
  simulate: (serviceId: string) =>
    post<FailureSimulation>(`/simulate/failure/${serviceId}`),
};

// ── Generator ────────────────────────────────────────────────────────────

export const generator = {
  generate: (params: {
    size?: string;
    seed?: number;
    with_traces?: boolean;
  }) => {
    // Backend expects query params, not JSON body.
    // Map with_traces → execute_flows to match backend parameter name.
    const query: Record<string, string | number | boolean> = {};
    if (params.size) query.size = params.size;
    if (params.seed !== undefined) query.seed = params.seed;
    if (params.with_traces) query.execute_flows = true;
    return post<GenerateResult>(`/generate${buildQueryString(query)}`);
  },
  preview: (params: { size?: string; seed?: number }) =>
    get<GeneratePreview>(`/generate/preview${buildQueryString(params ?? {})}`),
  reset: () => post<{ status: string }>("/generate/reset"),
};

// ── Aggregate export ─────────────────────────────────────────────────────

const api = {
  health,
  ecosystem,
  products,
  features,
  platforms,
  capabilities,
  services,
  microservices,
  flows,
  traces,
  dependencies,
  generator,
};

export default api;
