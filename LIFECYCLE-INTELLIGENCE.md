# From Source Code to Risk Response: Lifecycle Intelligence at Machine Speed

> *Compliance does not need AI. Risk outcomes need AI.*

---

## The Problem

Enterprise risk management is reactive. The industry measures Mean Time to Detect (MTTD) in hours to days. Compliance frameworks are backward-looking checklists. SOX says "have a change management process" — check the box. PCI says "maintain a firewall" — check the box. HIPAA says "conduct risk assessments" — check the box.

None of these tell you that a microservice three hops deep in your payment pipeline has 12 transitive dependencies, 3 of which form a circular chain, 1 carrying a blast radius weight of 85, and none of which have a completed threat model. None of them detect that a service deployed last Tuesday introduced a dependency on a component that's been deprecated for six months and scheduled for decommission in two weeks.

The gap between "what teams think they own" and "what actually happens at runtime" is where incidents live. That gap doesn't close with more checklists. It closes with a system that knows the topology, tracks every entity through its lifecycle, and treats the absence of expected metadata as the earliest possible signal that something is wrong.

---

## The Thesis: MTTD < 0

Mean Time to Detect below zero. Detecting the conditions for an incident *before* the incident occurs.

This isn't theoretical. It's graph traversal plus attribute gap analysis plus real-time dependency reasoning.

Consider: an incident requires conditions. A service fails because its dependency was unavailable. That dependency was unavailable because it was deprecated and no migration path existed. The deprecation was known — it was in the entity metadata. The missing migration path was also known — or rather, its absence was known, because the attribute `migration_plan_status` was never stamped.

Every link in that causal chain existed as detectable data *before* the incident. The information was there. The system just wasn't looking.

WorldMaker builds the system that looks.

---

## Source Code → Microservice → Lifecycle Lineage

The lineage is the risk model. Every entity in WorldMaker participates in a chain that connects source code to operational risk:

**Code Generation** stamps each microservice with real artifacts — a handler function, a Dockerfile, a dependency manifest, and a README. These aren't placeholders. They're framework-specific implementations across 6 languages (Python, Go, Java, TypeScript, Rust, Kotlin) and 24 frameworks. The generated code contains metadata blocks that trace back to the microservice, the parent service, the owning capability, and the platform.

**Microservice → Service** links deployment units to the services they implement. A service might decompose into 3-5 microservices, each in a different language, each carrying its own dependency chain. The service level is where blast radius is calculated.

**Service → Capability → Platform** establishes the organizational lineage. A service implements a capability (like "Payment Processing"), which belongs to a platform (like "Commerce Platform"). The platform is where governance policy originates — what attributes must exist, what compliance scope applies, what criticality tier is appropriate.

**Dependencies** create the directed graph that connects services to each other. Runtime dependencies, build dependencies, data dependencies, event dependencies, deployment dependencies, infrastructure dependencies — each type carries different risk characteristics. Circular dependencies are detected at creation time via BFS. Transitive chains are resolved to any depth. Blast radius is calculated as the cascading impact of any single node failure.

**Flows** connect services through execution steps — the actual paths that requests and events take through the architecture. Flows generate OpenTelemetry-compatible traces on execution, proving the actual runtime topology.

**Traces** are the evidence layer. Span trees with timing data, status codes, attributes, and events show what actually happened. The gap between what the dependency graph *says* should happen and what the traces *prove* did happen is another risk signal.

**Attributes** stamp lifecycle state at every level. When a core management platform processes an entity — when Security Management completes a threat model review, when Incident Management closes a postmortem, when Change Management approves a deployment — the attribute is stamped. When it's *not* stamped, the gap is visible.

**The lineage IS the risk model.** Any break in this chain — a missing attribute, a circular dependency, a service without a threat model, a microservice without a code repository, a platform without a defined compliance scope — is a condition detectable before the incident.

---

## The Three-Tier Attribute System

Attributes are the intelligence layer. They define what *should* be true about an entity and make it visible when it isn't.

### CORE Tier — Required for AI Intelligence

Five attributes that must exist on every qualifying entity. Their absence is an immediate risk signal:

| Attribute | Type | Applies To | What It Measures |
|-----------|------|-----------|-----------------|
| `risk_classification` | low / medium / high / critical | service, microservice, platform | Inherent risk level of the entity |
| `data_sensitivity` | public / internal / confidential / restricted | service, microservice | Data handling classification |
| `compliance_scope` | sox / pci / hipaa / gdpr / none | service, platform | Regulatory framework applicability |
| `criticality_tier` | tier1 / tier2 / tier3 / tier4 | service, microservice, platform | Business criticality ranking |
| `blast_radius_weight` | 0-100 | service | Potential cascading impact score |

If a service carries `criticality_tier: tier1` but has no `risk_classification`, that's not a data quality issue. That's a risk condition. The entity is critical enough to warrant Tier 1 classification but nobody has assessed its risk. That gap is the signal.

### LIFECYCLE Tier — Stamped by Core Functions

Twelve attributes stamped by core management platforms as entities move through operational workflows:

| Attribute | Stamped By | What It Proves |
|-----------|-----------|---------------|
| `change_risk_score` | Change Management | Risk score of the last approved change |
| `last_change_ticket_id` | Change Management | Traceability to change control |
| `threat_model_status` | Security Management | Current state of threat modeling |
| `last_pentest_date` | Security Management | When security was last validated |
| `vulnerability_count` | Security Management | Known exposure count |
| `incident_count_30d` | Incident Management | Recent incident frequency |
| `mttr_hours` | Incident Management | Mean Time to Recovery |
| `last_incident_date` | Incident Management | Recency of last incident |
| `rto_hours` | Business Continuity | Recovery Time Objective |
| `rpo_hours` | Business Continuity | Recovery Point Objective |
| `dr_plan_status` | Business Continuity | State of disaster recovery planning |
| `sla_compliance_pct` | Operations Management | SLA adherence rate |

When `threat_model_status` is `not_started` on a service that handles `confidential` data in a `sox` compliance scope, the system doesn't need to wait for a security incident. The conditions for the incident are already visible.

### FUNCTION Tier — Extensible by Platform Owners

Domain-specific attributes added at runtime. Platform owners define what matters for their context. Examples:

- `product_retirement_date` (Product Management) — signals upcoming decommission risk
- `known_error_count` (Problem Management) — accumulated defect exposure
- `open_issues_count` (Issues Management) — unresolved issue backlog

The FUNCTION tier is where the attribute system becomes a living model. As the organization learns what signals matter, they add attributes that capture them. The gap analysis engine treats any `required: true` attribute with the same urgency regardless of tier.

---

## Gap Analysis: Absence as Signal

The gap analysis algorithm is simple:

1. Walk every entity of each type (service, microservice, platform)
2. For each entity, find all attribute definitions where `applies_to` includes that entity type
3. For each attribute where `required: true`, check if the entity's metadata contains a value
4. Missing required attributes are gaps
5. Gaps are scored by the attribute tier (CORE > LIFECYCLE > FUNCTION)
6. Entities are ranked by total gap count and cumulative risk score

The output is a risk surface that tells you exactly which entities are missing which attributes, who should have stamped them, and how severe the gap is.

This is fundamentally different from compliance. Compliance asks: "Do you have a process?" Gap analysis asks: "Did the process actually run against this specific entity, and can you prove it?"

---

## Compliance Does Not Need AI. Risk Outcomes Need AI.

This is the positioning that matters.

**Compliance is checklist-based.** It's backward-looking, point-in-time, and binary. SOX says "have a change management process" — you either have one or you don't. PCI says "encrypt data at rest" — it's either encrypted or it isn't. The compliance question is always "does this control exist?" The answer is always yes or no.

You don't need AI to check boxes. You need a spreadsheet.

**Risk outcomes are topology-aware.** They're real-time, forward-looking, and probabilistic. The risk question isn't "does this control exist?" — it's "given this entity's position in the dependency graph, its attribute gaps, the blast radius of its downstream dependencies, and the state of its threat model, what is the probability that a change to this entity cascades into a production incident affecting the payment pipeline?"

That question requires:

- Traversing a directed dependency graph with cycle detection
- Correlating attribute gaps across multiple entities in the same dependency chain
- Weighing blast radius against criticality tier
- Factoring in the recency and severity of recent incidents on connected services
- Reasoning about the cumulative effect of multiple small gaps versus a single critical gap

This is where AI sits — not on the compliance checklist, but on the intelligence graph. LangGraph agents that traverse the entity model, read the attribute state, correlate the dependency topology, and produce risk assessments in real time.

The intelligence graph that WorldMaker builds IS the substrate for this reasoning. Every entity, every attribute, every dependency, every trace, every gap — it's all first-class data that an AI agent can traverse.

---

## Inside-Out Risk Discovery

Traditional risk discovery is outside-in: scan the perimeter, test the endpoints, check the configurations. You find what's visible from the outside.

WorldMaker enables inside-out risk discovery: start with the source code, understand what the microservice does, trace its dependencies, check its attributes, follow its flows, and identify risk conditions from the inside of the architecture out.

The scaffolded code repositories are the foundation. Each microservice has:

- A handler with real framework-specific implementation
- A Dockerfile that reveals the base image, exposed ports, and build dependencies
- A dependency manifest (requirements.txt, go.mod, pom.xml, etc.) listing every library
- Metadata linking back to the service, capability, platform, and compliance scope

Static analysis on this code — dependency vulnerability scanning, base image CVE checking, security control verification, framework-specific misconfigurations — happens before runtime. Before deployment. Before the microservice ever processes a request.

Combined with the attribute gap analysis and dependency graph topology, inside-out discovery means the system can identify risk conditions across the full stack — from a missing `require("helmet")` in a Node.js handler to a missing `threat_model_status` on the service that handler implements, to a circular dependency in the platform that service belongs to.

That's end-to-end risk visibility. Source code to operational risk. And it all happens before the incident.

---

## The Architecture for What's Next

WorldMaker today is the intelligence substrate. What's built:

- **22 interactive views** across the full entity lifecycle
- **41 API endpoints** with full CRUD, graph queries, and risk analysis
- **195 test cases** covering generators, trace engine, attributes, code generation, and API surface
- **6-language code generation** with 24 framework-specific implementations
- **Dependency graph** with circular detection, blast radius, and failure simulation
- **OTel-native traces** with span waterfall visualization and Jaeger export
- **Three-tier attribute system** with gap analysis as the pre-incident detection mechanism
- **9 core management platforms** with onboarding workflows and enterprise governance

What's next builds on this substrate:

### LangGraph Agents for Autonomous Risk Reasoning

AI agents that continuously traverse the entity graph, evaluate attribute states, detect emerging risk patterns, and surface conditions before they become incidents. The graph structure — entities, relationships, attributes, gaps — is the context window for these agents.

### Static Code Analysis

Automated vulnerability detection on scaffolded microservice code. Dependency scanning against CVE databases. Base image vulnerability checking. Framework-specific security misconfigurations. The code repositories are already structured for this — each contains the dependency manifest, Dockerfile, and handler that analysis tools need.

### Real-Time Attribute Enrichment

Event-driven architecture (Kafka) for attribute stamping as entities flow through lifecycle workflows. When Change Management approves a change, the `last_change_ticket_id` attribute is stamped in real time. When Incident Management closes a postmortem, `mttr_hours` is updated. The gap analysis surface refreshes continuously.

### Risk Scoring Models

Machine learning models trained on the topology graph and attribute state to predict cascade failure probability. The training data is inherent in the generated ecosystems — the circular dependencies, the blast radius patterns, the attribute gaps. The models learn what combinations of conditions precede incidents.

### AWS Deployment

Enterprise-scale deployment on AWS infrastructure: ECS/EKS for container orchestration, RDS for persistent entity storage, S3-backed code repositories for microservice source, CloudWatch for operational monitoring. The Docker Compose configuration provides the local development experience; the architecture is designed for cloud-native operation.

---

## The Bottom Line

WorldMaker is not a compliance tool. It doesn't check boxes.

WorldMaker is an intelligence platform that models enterprise digital ecosystems end-to-end — from source code to operational risk — and builds the data structure that makes MTTD < 0 achievable.

Every entity is a node. Every dependency is an edge. Every attribute is a fact. Every gap is a signal.

The system that sees everything can detect anything.

---

<p align="center">
  <a href="README.md">← Back to README</a>
</p>
