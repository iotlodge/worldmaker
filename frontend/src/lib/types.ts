/**
 * WorldMaker Frontend Types
 *
 * Generated from Pydantic models in src/worldmaker/models/
 * This file serves as the type contract between the FastAPI backend
 * and the Next.js frontend.
 */

// ── Enums ────────────────────────────────────────────────────────────────

export type EntityStatus =
  | "planned"
  | "active"
  | "deprecated"
  | "decommissioned"
  | "sunset";

export type EntityType =
  | "product"
  | "feature"
  | "business_process"
  | "platform"
  | "capability"
  | "service"
  | "microservice"
  | "flow"
  | "flow_step"
  | "interface"
  | "event_type"
  | "environment"
  | "deployment"
  | "data_store"
  | "data_store_instance"
  | "dependency";

export type DependencyType =
  | "runtime"
  | "build"
  | "data"
  | "event"
  | "deployment"
  | "infrastructure";

export type Severity = "critical" | "high" | "medium" | "low";

export type ServiceType =
  | "rest"
  | "grpc"
  | "event_driven"
  | "batch"
  | "graphql";

export type FlowType =
  | "request_response"
  | "event_stream"
  | "batch"
  | "scheduled"
  | "saga";

export type CapabilityType =
  | "compute"
  | "storage"
  | "networking"
  | "integration"
  | "identity"
  | "payment"
  | "messaging"
  | "analytics"
  | "security";

export type HealthStatus = "healthy" | "degraded" | "unhealthy" | "unknown";

export type Layer = "core" | "generated";

// ── Base Entity ──────────────────────────────────────────────────────────

export interface BaseEntity {
  id: string;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
  metadata: Record<string, unknown>;
  layer?: Layer;
}

// ── Domain Entities ──────────────────────────────────────────────────────

export interface Product extends BaseEntity {
  name: string;
  description?: string;
  status: EntityStatus;
  owner: string;
  version: number;
  tags: string[];
  features: string[]; // Feature IDs
}

export interface Feature extends BaseEntity {
  product_id: string;
  name: string;
  description?: string;
  user_flows: string[];
  status: EntityStatus;
  owner: string;
  depends_on_features: string[];
}

export interface Platform extends BaseEntity {
  name: string;
  description?: string;
  category: string;
  owner: string;
  status: EntityStatus;
  tech_stack: string[];
  sla_definition: Record<string, unknown>;
}

export interface Capability extends BaseEntity {
  platform_id: string;
  name: string;
  description?: string;
  capability_type: CapabilityType;
  status: EntityStatus;
  version: string;
  slo: Record<string, unknown>;
  depends_on_capabilities: string[];
}

export interface Service extends BaseEntity {
  name: string;
  description?: string;
  capability_id?: string;
  platform_id: string;
  owner: string;
  status: EntityStatus;
  service_type: ServiceType;
  api_version: string;
  microservice_ids: string[];
}

export interface Microservice extends BaseEntity {
  service_id: string;
  name: string;
  description?: string;
  container_image?: string;
  language: string;
  framework?: string;
  status: EntityStatus;
  repo_url?: string;
  dependencies: string[];
}

export interface Flow extends BaseEntity {
  name: string;
  description?: string;
  flow_type: FlowType;
  status: EntityStatus;
  starting_service_id?: string;
  ending_service_id?: string;
  average_duration_ms?: number;
  steps: string[];
}

export interface FlowStep extends BaseEntity {
  flow_id: string;
  step_number: number;
  from_service_id: string;
  to_service_id: string;
  interface_id?: string;
  status: EntityStatus;
  average_duration_ms?: number;
  failure_mode?: string;
  retry_policy: {
    max_retries: number;
    backoff_ms: number;
  };
}

export interface Dependency extends BaseEntity {
  source_id: string;
  target_id: string;
  source_type: EntityType;
  target_type: EntityType;
  dependency_type: DependencyType;
  severity: Severity;
  is_circular: boolean;
  description?: string;
}

// ── API Response Types ───────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  total: number;
  limit: number;
  offset: number;
}

export interface ProductListResponse extends PaginatedResponse<Product> {
  products: Product[];
}

export interface PlatformListResponse extends PaginatedResponse<Platform> {
  platforms: Platform[];
}

export interface ServiceListResponse extends PaginatedResponse<Service> {
  services: Service[];
}

export interface FlowListResponse extends PaginatedResponse<Flow> {
  flows: Flow[];
}

export interface CapabilityListResponse extends PaginatedResponse<Capability> {
  capabilities: Capability[];
}

export interface MicroserviceListResponse extends PaginatedResponse<Microservice> {
  microservices: Microservice[];
}

export interface FeatureListResponse {
  total: number;
  limit: number;
  offset: number;
  features: Feature[];
}

// ── Circular Dependency Types ──────────────────────────────────────────

export interface CircularDependency {
  id: string;
  source_id: string;
  target_id: string;
  source_name?: string;
  target_name?: string;
  source_type: EntityType;
  target_type: EntityType;
  dependency_type: DependencyType;
  severity: Severity;
  is_circular: boolean;
  description?: string;
  created_at: string;
}

export interface CircularDependencyResponse {
  total: number;
  limit: number;
  circular_dependencies: CircularDependency[];
}

// ── Dependency List Types ──────────────────────────────────────────────

export interface DependencyListResponse {
  total: number;
  limit: number;
  offset: number;
  dependencies: Dependency[];
}

// ── Trace List Response Types ────────────────────────────────────────────

export interface TraceListResponse {
  total: number;
  traces: TraceSummary[];
}

export interface FlowTracesResponse {
  flow_id: string;
  total: number;
  traces: TraceSummary[];
}

export interface TraceSpansResponse {
  trace_id: string;
  format: string;
  span_count: number;
  spans: Span[];
}

// ── Trace & Observability Types ──────────────────────────────────────────

export interface TraceResult {
  trace_id: string;
  execution_id: string;
  flow_id: string;
  flow_name: string;
  environment: string;
  duration_ms: number;
  status: string;
  span_count: number;
  error?: string;
}

export interface TraceSummary {
  trace_id: string;
  flow_id: string;
  flow_name: string;
  duration_ms: number;
  status: string;
  span_count: number;
  start_time?: string;
  end_time?: string;
  error?: string;
}

export interface Span {
  span_id: string;
  trace_id: string;
  parent_span_id?: string;
  operation_name: string;
  service_name: string;
  kind: "CLIENT" | "SERVER" | "INTERNAL";
  start_time: string;
  end_time: string;
  duration_us: number;
  status_code: string;
  attributes: Record<string, unknown>;
  events: SpanEvent[];
  links: SpanLink[];
}

export interface SpanEvent {
  name: string;
  timestamp: string;
  attributes: Record<string, unknown>;
}

export interface SpanLink {
  trace_id: string;
  span_id: string;
  attributes: Record<string, unknown>;
}

// ── Ecosystem & Health Types ─────────────────────────────────────────────

export interface EcosystemOverview {
  status: string;
  ecosystem: {
    products: { total: number };
    platforms: { total: number };
    capabilities: { total: number };
    services: { total: number; active: number; degraded: number };
    microservices: { total: number };
    flows: { total: number; active: number };
    dependencies: { total: number; circular: number };
    environments: { total: number };
  };
  total_entities: number;
  statistics: {
    avg_dependencies_per_service: number;
    circular_dependency_count: number;
    audit_log_entries: number;
    traces_generated: number;
    spans_generated: number;
  };
}

export interface EcosystemHealth {
  overall_health: HealthStatus | "empty";
  health_score: number;
  total_services: number;
  critical_issues: string[];
  warnings: string[];
}

// ── Dependency Analysis Types ────────────────────────────────────────────

export interface DependencyAnalysis {
  service_id: string;
  service_name: string;
  depth: "direct" | "transitive" | "blast-radius";
  depends_on: Service[];
  depended_on_by: Service[];
  transitive_dependencies?: Service[];
  transitive_count?: number;
  blast_radius?: BlastRadius;
  statistics: {
    direct_dependency_count: number;
    direct_dependent_count: number;
    total_count: number;
  };
}

export interface BlastRadius {
  affected_services: AffectedService[];
  blast_radius: number;
  max_cascade_depth: number;
}

export interface AffectedService extends Service {
  severity: Severity;
  hops_away: number;
}

export interface FailureSimulation {
  service_id: string;
  service_name: string;
  blast_radius: number;
  max_cascade_depth: number;
  severity: Severity;
  affected_services: AffectedService[];
  impact_by_severity: Record<Severity, number>;
  impact_by_depth: Record<string, string[]>;
  failure_modes: unknown[];
  recovery_patterns: unknown[];
  recommendations: string[];
}

// ── Generation Types ─────────────────────────────────────────────────────

export interface GenerateResult {
  status: string;
  seed: number;
  size: string;
  summary: Record<string, number>;
  loaded: Record<string, number>;
  traces_generated?: number;
  total_spans?: number;
}

export interface GeneratePreview {
  seed: number;
  size: string;
  preview: {
    total_entities: number;
    breakdown: Record<string, number>;
  };
}

// ── Service Context (Agentic) ────────────────────────────────────────────

export interface ServiceContext {
  service_id: string;
  entity: Service;
  dependencies: {
    upstream: Service[];
    downstream: Service[];
    blast_radius: BlastRadius;
  };
  health: {
    service_status: string;
    slo: Record<string, unknown> | null;
    criticality: Record<string, unknown> | null;
  };
  microservices: Microservice[];
  audit: {
    recent_changes: number;
    entries: unknown[];
  };
}

// ── Audit Types ──────────────────────────────────────────────────────────

export interface AuditEntry {
  entity_id: string;
  entity_type: EntityType;
  action: string;
  timestamp: string;
  [key: string]: unknown;
}

export interface AuditLogResponse {
  total: number;
  limit: number;
  entries: AuditEntry[];
}

// ── Store Status ─────────────────────────────────────────────────────────

export interface StoreStatus {
  status: string;
  store_type: string;
  entity_counts: Record<string, number>;
  total_entities: number;
  dependency_count: number;
  circular_dependencies: number;
  audit_log_entries: number;
  trace_count: number;
  span_count: number;
}

// ── Search ───────────────────────────────────────────────────────────────

export interface SearchResult {
  results: Array<{
    entity_type: string;
    entity: BaseEntity & { name?: string };
    score?: number;
  }>;
  total: number;
  query: string;
}
