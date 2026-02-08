"""Cypher query templates for dependency graph analysis.

These queries power the real-time dependency resolution that agentic
consumers use to understand interoperability and derive system state.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# --- Node Management ---

UPSERT_SERVICE_NODE = """
MERGE (s:Service {id: $id})
SET s.name = $name,
    s.status = $status,
    s.service_type = $service_type,
    s.criticality = $criticality,
    s.owner = $owner,
    s.health_status = $health_status,
    s.updated_at = datetime()
RETURN s
"""

UPSERT_PLATFORM_NODE = """
MERGE (p:Platform {id: $id})
SET p.name = $name,
    p.status = $status,
    p.category = $category,
    p.owner = $owner,
    p.updated_at = datetime()
RETURN p
"""

UPSERT_MICROSERVICE_NODE = """
MERGE (m:Microservice {id: $id})
SET m.name = $name,
    m.service_id = $service_id,
    m.language = $language,
    m.framework = $framework,
    m.status = $status,
    m.updated_at = datetime()
RETURN m
"""

UPSERT_DATASTORE_NODE = """
MERGE (d:DataStore {id: $id})
SET d.name = $name,
    d.store_type = $store_type,
    d.technology = $technology,
    d.status = $status,
    d.updated_at = datetime()
RETURN d
"""

UPSERT_CAPABILITY_NODE = """
MERGE (c:Capability {id: $id})
SET c.name = $name,
    c.platform_id = $platform_id,
    c.capability_type = $capability_type,
    c.status = $status,
    c.updated_at = datetime()
RETURN c
"""

UPSERT_FLOW_NODE = """
MERGE (f:Flow {id: $id})
SET f.name = $name,
    f.flow_type = $flow_type,
    f.status = $status,
    f.updated_at = datetime()
RETURN f
"""

# --- Relationship Management ---

CREATE_DEPENDENCY = """
MATCH (source {id: $source_id})
MATCH (target {id: $target_id})
MERGE (source)-[r:DEPENDS_ON {type: $dep_type}]->(target)
SET r.severity = $severity,
    r.is_circular = $is_circular,
    r.created_at = datetime()
RETURN source, r, target
"""

CREATE_HOSTED_BY = """
MATCH (s:Service {id: $service_id})
MATCH (p:Platform {id: $platform_id})
MERGE (s)-[r:HOSTED_BY]->(p)
SET r.created_at = datetime()
RETURN s, r, p
"""

CREATE_IMPLEMENTS = """
MATCH (s:Service {id: $service_id})
MATCH (c:Capability {id: $capability_id})
MERGE (s)-[r:IMPLEMENTS]->(c)
SET r.created_at = datetime()
RETURN s, r, c
"""

CREATE_USES_DATASTORE = """
MATCH (s:Service {id: $service_id})
MATCH (d:DataStore {id: $datastore_id})
MERGE (s)-[r:USES]->(d)
SET r.access_pattern = $access_pattern,
    r.criticality = $criticality,
    r.created_at = datetime()
RETURN s, r, d
"""

CREATE_FLOW_TRAVERSAL = """
MATCH (f:Flow {id: $flow_id})
MATCH (s:Service {id: $service_id})
MERGE (f)-[r:TRAVERSES]->(s)
SET r.step_number = $step_number,
    r.created_at = datetime()
RETURN f, r, s
"""

CREATE_CALLS = """
MATCH (s1:Service {id: $from_service_id})
MATCH (s2:Service {id: $to_service_id})
MERGE (s1)-[r:CALLS]->(s2)
SET r.interface_type = $interface_type,
    r.latency_ms = $latency_ms,
    r.created_at = datetime()
RETURN s1, r, s2
"""

# --- Dependency Analysis Queries (Agentic Consumer Core) ---

GET_DIRECT_DEPENDENCIES = """
MATCH (s {id: $service_id})
OPTIONAL MATCH (s)-[out:DEPENDS_ON]->(downstream)
OPTIONAL MATCH (upstream)-[in_:DEPENDS_ON]->(s)
RETURN {
    service: s{.id, .name, .status, .criticality, .health_status},
    downstream: collect(DISTINCT {
        entity: downstream{.id, .name, .status, .criticality},
        relationship: out{.type, .severity, .is_circular}
    }),
    upstream: collect(DISTINCT {
        entity: upstream{.id, .name, .status, .criticality},
        relationship: in_{.type, .severity, .is_circular}
    })
} as result
"""

GET_TRANSITIVE_DEPENDENCIES = """
MATCH (s {id: $service_id})
MATCH path = (s)-[r:DEPENDS_ON*1..]->(dep)
WHERE dep <> s
RETURN DISTINCT dep{.id, .name, .status, .criticality} as dependency,
       length(path) as hops_away,
       [rel in relationships(path) | rel.severity] as severity_chain,
       [node in nodes(path) | node.name] as path_names
ORDER BY hops_away ASC
"""

CALCULATE_BLAST_RADIUS = """
MATCH (root {id: $service_id})
OPTIONAL MATCH (dependent)-[r:DEPENDS_ON*1..10]->(root)
WITH root, collect(DISTINCT dependent) as affected_list
RETURN {
    root_service: root{.id, .name, .status, .criticality},
    blast_radius: size(affected_list),
    affected_services: [s IN affected_list | s{.id, .name, .status, .criticality}]
} as result
"""

DETECT_CIRCULAR_DEPENDENCIES = """
MATCH path = (a)-[r:DEPENDS_ON*2..10]->(a)
WITH a, nodes(path) as cycle_nodes, relationships(path) as cycle_rels
RETURN DISTINCT {
    cycle_root: a{.id, .name},
    cycle_nodes: [n IN cycle_nodes | n{.id, .name}],
    cycle_length: size(cycle_nodes),
    severities: [r IN cycle_rels | r.severity]
} as circular_dependency
"""

FIND_CRITICAL_PATHS = """
MATCH (start:Service {criticality: 'critical'})
MATCH (end:Service {criticality: 'critical'})
WHERE start <> end
MATCH path = shortestPath((start)-[r:DEPENDS_ON*]->(end))
RETURN {
    from_service: start{.id, .name},
    to_service: end{.id, .name},
    hops: length(path),
    path: [n IN nodes(path) | n{.id, .name, .criticality}],
    relationships: [r IN relationships(path) | r{.type, .severity}]
} as critical_path
ORDER BY length(path) ASC
"""

GET_FULL_SERVICE_CONTEXT = """
MATCH (s:Service {id: $service_id})
OPTIONAL MATCH (s)-[hosted:HOSTED_BY]->(platform:Platform)
OPTIONAL MATCH (s)-[uses:USES]->(datastore:DataStore)
OPTIONAL MATCH (s)-[impl:IMPLEMENTS]->(capability:Capability)
OPTIONAL MATCH (upstream:Service)-[in_dep:DEPENDS_ON]->(s)
OPTIONAL MATCH (s)-[out_dep:DEPENDS_ON]->(downstream:Service)
OPTIONAL MATCH (s)-[calls_out:CALLS]->(called:Service)
OPTIONAL MATCH (caller:Service)-[calls_in:CALLS]->(s)
RETURN {
    service: s{.id, .name, .status, .criticality, .health_status, .service_type, .owner},
    platform: platform{.id, .name, .category},
    capabilities: collect(DISTINCT capability{.id, .name, .capability_type}),
    data_stores: collect(DISTINCT {store: datastore{.id, .name, .store_type, .technology}, access: uses.access_pattern}),
    upstream_dependencies: collect(DISTINCT {service: upstream{.id, .name, .status, .criticality}, dep: in_dep{.type, .severity}}),
    downstream_dependencies: collect(DISTINCT {service: downstream{.id, .name, .status, .criticality}, dep: out_dep{.type, .severity}}),
    calls_to: collect(DISTINCT {service: called{.id, .name}, interface: calls_out.interface_type}),
    called_by: collect(DISTINCT {service: caller{.id, .name}, interface: calls_in.interface_type})
} as context
"""

SHARED_RESOURCE_CORRELATION = """
MATCH (d:DataStore {id: $datastore_id})<-[u1:USES]-(s1:Service)
MATCH (d)<-[u2:USES]-(s2:Service)
WHERE s1 <> s2
RETURN {
    datastore: d{.id, .name, .store_type},
    services: collect(DISTINCT {service: s1{.id, .name, .criticality}, access: u1.access_pattern}),
    correlation_type: 'shared_resource'
} as correlation
"""

HEALTH_CASCADE = """
MATCH (unhealthy:Service)
WHERE unhealthy.health_status IN ['unhealthy', 'degraded']
MATCH (dependent:Service)-[r:DEPENDS_ON*1..5]->(unhealthy)
RETURN {
    failing_service: unhealthy{.id, .name, .health_status},
    affected_service: dependent{.id, .name, .criticality},
    hops_to_failure: length(r),
    action: CASE
        WHEN dependent.criticality = 'critical' THEN 'ALERT'
        WHEN dependent.criticality = 'high' THEN 'WARN'
        ELSE 'MONITOR'
    END
} as cascade
ORDER BY cascade.action ASC, cascade.hops_to_failure ASC
"""

GET_ECOSYSTEM_OVERVIEW = """
MATCH (s:Service)
WITH count(s) as service_count
MATCH (p:Platform)
WITH service_count, count(p) as platform_count
MATCH (d:DataStore)
WITH service_count, platform_count, count(d) as datastore_count
MATCH ()-[r:DEPENDS_ON]->()
WITH service_count, platform_count, datastore_count, count(r) as dependency_count
OPTIONAL MATCH circular = (a)-[:DEPENDS_ON*2..10]->(a)
WITH service_count, platform_count, datastore_count, dependency_count,
     count(DISTINCT a) as circular_count
RETURN {
    services: service_count,
    platforms: platform_count,
    data_stores: datastore_count,
    dependencies: dependency_count,
    circular_dependencies: circular_count
} as overview
"""

SIMULATE_FAILURE = """
MATCH (failed:Service {id: $service_id})
SET failed.health_status = 'unhealthy'
WITH failed
MATCH (dependent:Service)-[r:DEPENDS_ON*1..10]->(failed)
WHERE r[0].severity IN ['critical', 'high']
WITH failed, collect(DISTINCT {
    service: dependent{.id, .name, .criticality, .status},
    hops: length(r),
    severity_chain: [rel in r | rel.severity]
}) as impact
RETURN {
    failed_service: failed{.id, .name},
    total_impact: size(impact),
    affected: impact
} as simulation
"""
