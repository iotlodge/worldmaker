"""Full ecosystem generator — the heart of WorldMaker's synthetic data.

Generates a complete enterprise digital ecosystem top-down:
Products → Platforms → Capabilities → Services → Microservices → Flows → Dependencies → Risk
"""
from __future__ import annotations
import logging
from typing import Any
from uuid import uuid4

from .base import BaseGenerator, GeneratorConfig
from .names import NameGenerator

logger = logging.getLogger(__name__)


class EcosystemGenerator(BaseGenerator):
    """Generates a complete synthetic enterprise ecosystem."""
    
    def __init__(self, seed: int = 42, size: str = "small", config: GeneratorConfig | None = None):
        super().__init__(seed, config or GeneratorConfig(size))
        self._names = NameGenerator(self._rng)
        
        # Generated entity storage
        self.products: list[dict[str, Any]] = []
        self.platforms: list[dict[str, Any]] = []
        self.capabilities: list[dict[str, Any]] = []
        self.services: list[dict[str, Any]] = []
        self.microservices: list[dict[str, Any]] = []
        self.interfaces: list[dict[str, Any]] = []
        self.flows: list[dict[str, Any]] = []
        self.flow_steps: list[dict[str, Any]] = []
        self.dependencies: list[dict[str, Any]] = []
        self.environments: list[dict[str, Any]] = []
        self.deployments: list[dict[str, Any]] = []
        self.data_stores: list[dict[str, Any]] = []
        self.data_store_instances: list[dict[str, Any]] = []
        self.features: list[dict[str, Any]] = []
        self.criticality_ratings: list[dict[str, Any]] = []
        self.slo_definitions: list[dict[str, Any]] = []
        self.failure_modes: list[dict[str, Any]] = []
        self.recovery_patterns: list[dict[str, Any]] = []
        self.event_types: list[dict[str, Any]] = []
    
    def generate(self) -> dict[str, Any]:
        """Generate the complete ecosystem. Returns all entities."""
        logger.info("Generating ecosystem with seed=%d, config=%s", self._seed, self._config.config)
        
        self._generate_environments()
        self._generate_products()
        self._generate_platforms()
        self._generate_data_stores()
        self._generate_flows()
        self._generate_dependencies()
        self._generate_risk_metadata()
        self._generate_deployments()
        
        summary = self._summarize()
        logger.info("Ecosystem generated: %s", summary)
        return self.to_dict()
    
    def _generate_environments(self) -> None:
        """Generate deployment environments."""
        env_types = ["dev", "staging", "qa", "prod"]
        num_envs = self._config.get("environments", 3)
        for env_type in env_types[:num_envs]:
            env = {
                **self._base_entity(),
                "name": env_type,
                "env_type": env_type,
                "region": self._names.region(),
                "cloud_provider": "aws",
                "compliance": ["SOC2"] if env_type == "prod" else [],
            }
            self.environments.append(env)
    
    def _generate_products(self) -> None:
        """Generate products with features."""
        num = self._random_range("products")
        for _ in range(num):
            product = {
                **self._base_entity(),
                "name": self._names.product_name(),
                "description": f"Enterprise {self._choice(['digital', 'cloud', 'smart'])} product",
                "status": self._choice(["active", "active", "active", "planned"]),
                "owner": self._names.team(),
                "version": self._randint(1, 5),
                "tags": self._sample(["enterprise", "b2b", "b2c", "fintech", "saas", "platform"], 2),
                "features": [],
            }
            self.products.append(product)

            # Generate features for this product
            num_features = self._random_range("features_per_product")
            for _ in range(num_features):
                feature = {
                    **self._base_entity(),
                    "product_id": product["id"],
                    "name": self._names.feature_name(),
                    "description": f"Feature of {product['name']}",
                    "user_flows": [],
                    "status": self._choice(["active", "active", "active", "planned", "deprecated"]),
                    "owner": self._names.team(),
                    "depends_on_features": [],
                }
                self.features.append(feature)
                product["features"].append(feature["id"])
    
    def _generate_platforms(self) -> None:
        """Generate platforms → capabilities → services → microservices."""
        num = self._random_range("platforms")
        categories = list(["payment", "identity", "data", "messaging", "commerce", 
                          "infrastructure", "security", "observability"])
        
        for i in range(num):
            cat = categories[i % len(categories)]
            plat_name, plat_cat = self._names.platform_name(cat)
            
            platform = {
                **self._base_entity(),
                "name": plat_name,
                "description": f"Enterprise {plat_cat} platform",
                "category": plat_cat,
                "owner": self._names.team(),
                "status": "active",
                "tech_stack": self._sample(["kubernetes", "docker", "terraform", "helm", "istio", "envoy"], 3),
                "sla_definition": {"availability": self._randfloat(0.99, 0.9999), "response_time_ms": self._randint(50, 500)},
            }
            self.platforms.append(platform)
            
            # Generate capabilities for this platform
            num_caps = self._random_range("capabilities_per_platform")
            for _ in range(num_caps):
                capability = {
                    **self._base_entity(),
                    "platform_id": platform["id"],
                    "name": self._names.capability_name(cat),
                    "description": f"Capability of {plat_name}",
                    "capability_type": cat,
                    "status": self._choice(["active", "active", "experimental"]),
                    "version": f"{self._randint(1,3)}.{self._randint(0,9)}.0",
                    "slo": {},
                    "depends_on_capabilities": [],
                }
                self.capabilities.append(capability)
                
                # Generate services for this capability
                num_svcs = self._random_range("services_per_capability")
                for _ in range(num_svcs):
                    svc_name = self._names.service_name(cat)
                    lang, framework = self._names.language_and_framework()
                    
                    service = {
                        **self._base_entity(),
                        "name": svc_name,
                        "description": f"Service implementing {capability['name']}",
                        "capability_id": capability["id"],
                        "platform_id": platform["id"],
                        "owner": self._names.team(),
                        "status": "active",
                        "service_type": self._choice(["rest", "rest", "grpc", "event_driven"]),
                        "api_version": f"v{self._randint(1,3)}",
                        "microservice_ids": [],
                    }
                    self.services.append(service)
                    
                    # Assign to a random product
                    if self.products:
                        product = self._choice(self.products)
                        product["features"].append(service["id"])
                    
                    # Generate microservices
                    num_ms = self._random_range("microservices_per_service")
                    for _ in range(num_ms):
                        ms_name = self._names.microservice_name(svc_name)
                        ms_lang, ms_fw = self._names.language_and_framework()
                        
                        microservice = {
                            **self._base_entity(),
                            "service_id": service["id"],
                            "name": ms_name,
                            "description": f"Microservice of {svc_name}",
                            "container_image": f"registry.example.com/{ms_name}:{self._randint(1,20)}.{self._randint(0,99)}.{self._randint(0,999)}",
                            "language": ms_lang,
                            "framework": ms_fw,
                            "status": "active",
                            "repo_url": f"https://github.com/org/{ms_name}",
                            "dependencies": [],
                        }
                        self.microservices.append(microservice)
                        service["microservice_ids"].append(microservice["id"])
                    
                    # Generate event types emitted by this service
                    if self._probability(0.6):
                        event_type = {
                            **self._base_entity(),
                            "name": f"{svc_name.replace('Service', '')}.completed",
                            "service_id": service["id"],
                            "description": f"Event emitted by {svc_name}",
                            "schema_definition": {"type": "object", "properties": {}},
                            "retention": self._choice(["7d", "14d", "30d", "90d"]),
                            "status": "active",
                            "consumed_by_service_ids": [],
                        }
                        self.event_types.append(event_type)
    
    def _generate_data_stores(self) -> None:
        """Generate data stores and assign to services."""
        store_types = ["relational_db", "document_db", "cache", "queue", "search_engine"]
        num = self._random_range("data_stores")
        
        for i in range(num):
            store_type = store_types[i % len(store_types)]
            ds_name, technology = self._names.datastore_name(store_type)
            
            data_store = {
                **self._base_entity(),
                "name": ds_name,
                "store_type": store_type,
                "technology": technology,
                "owner": self._names.team(),
                "status": "active",
            }
            self.data_stores.append(data_store)
            
            # Create instances in each environment
            for env in self.environments:
                instance = {
                    **self._base_entity(),
                    "data_store_id": data_store["id"],
                    "environment_id": env["id"],
                    "deployment_id": None,
                    "connection_string": f"{technology.lower()}://{ds_name}.{env['name']}.internal:5432/worldmaker",
                    "replication_factor": 3 if env["env_type"] == "prod" else 1,
                    "backup_policy": {"enabled": env["env_type"] == "prod", "frequency": "daily"},
                    "status": "active",
                }
                self.data_store_instances.append(instance)
    
    def _generate_flows(self) -> None:
        """Generate flows that traverse services."""
        if len(self.services) < 2:
            return
        
        num = self._random_range("flows")
        for _ in range(num):
            num_steps = self._random_range("steps_per_flow")
            flow_services = self._sample(self.services, min(num_steps + 1, len(self.services)))
            
            flow = {
                **self._base_entity(),
                "name": self._names.flow_name(),
                "description": f"End-to-end flow through {len(flow_services)} services",
                "flow_type": self._choice(["request_response", "request_response", "event_stream", "saga"]),
                "status": "active",
                "starting_service_id": flow_services[0]["id"],
                "ending_service_id": flow_services[-1]["id"],
                "average_duration_ms": self._randint(50, 5000),
                "steps": [],
            }
            self.flows.append(flow)
            
            # Generate steps
            for step_idx in range(len(flow_services) - 1):
                from_svc = flow_services[step_idx]
                to_svc = flow_services[step_idx + 1]
                
                # Create interface between these services
                interface = {
                    **self._base_entity(),
                    "provider_id": from_svc["id"],
                    "consumer_id": to_svc["id"],
                    "name": self._names.interface_name(
                        from_svc["name"].replace("Service", ""),
                        to_svc["name"].replace("Service", ""),
                    ),
                    "interface_type": self._choice(["rest", "grpc", "async_event"]),
                    "protocol": self._choice(["HTTP/2", "HTTP/1.1", "gRPC", "AMQP"]),
                    "version": "1.0.0",
                    "schema_definition": {},
                    "authentication": {"type": self._choice(["jwt", "api_key", "mtls", "oauth2"])},
                    "rate_limit": {"requests_per_second": self._randint(100, 10000)},
                    "status": "active",
                }
                self.interfaces.append(interface)
                
                step = {
                    **self._base_entity(),
                    "flow_id": flow["id"],
                    "step_number": step_idx + 1,
                    "from_service_id": from_svc["id"],
                    "to_service_id": to_svc["id"],
                    "interface_id": interface["id"],
                    "status": "active",
                    "average_duration_ms": self._randint(10, 1000),
                    "failure_mode": self._choice([None, "timeout", "5xx", "circuit_open"]),
                    "retry_policy": {"max_retries": self._randint(1, 5), "backoff_ms": self._randint(100, 5000)},
                }
                self.flow_steps.append(step)
                flow["steps"].append(step["id"])
    
    def _generate_dependencies(self) -> None:
        """Generate dependency graph between services.
        
        Creates realistic patterns:
        - Hub-and-spoke (shared services like auth, logging)
        - Chain dependencies (payment → ledger → reconciliation)
        - Mesh clusters (tightly coupled microservice groups)
        - Configurable circular dependency injection
        """
        if len(self.services) < 2:
            return
        
        density = self._config.get("dependency_density", 0.15)
        circular_prob = self._config.get("circular_dep_probability", 0.05)
        
        # Identify hub services (infrastructure, auth, observability)
        hub_categories = {"infrastructure", "identity", "observability", "security"}
        hub_services = [s for s in self.services 
                       if any(c.get("capability_type") in hub_categories 
                             for c in self.capabilities 
                             if c["id"] == s.get("capability_id"))]
        non_hub_services = [s for s in self.services if s not in hub_services]
        
        # Hub-and-spoke: most services depend on hubs
        for service in non_hub_services:
            for hub in hub_services:
                if self._probability(0.4):
                    dep = {
                        **self._base_entity(),
                        "source_id": service["id"],
                        "target_id": hub["id"],
                        "source_type": "service",
                        "target_type": "service",
                        "dependency_type": "runtime",
                        "severity": self._choice(["critical", "high", "medium"]),
                        "is_circular": False,
                        "description": f"{service['name']} depends on {hub['name']}",
                    }
                    self.dependencies.append(dep)
        
        # Random inter-service dependencies
        for service in self.services:
            num_deps = max(0, int(len(self.services) * density) - 1)
            targets = [s for s in self.services if s["id"] != service["id"]]
            if targets:
                dep_targets = self._sample(targets, min(num_deps, len(targets)))
                for target in dep_targets:
                    # Check if dependency already exists
                    existing = any(
                        d["source_id"] == service["id"] and d["target_id"] == target["id"]
                        for d in self.dependencies
                    )
                    if not existing:
                        dep = {
                            **self._base_entity(),
                            "source_id": service["id"],
                            "target_id": target["id"],
                            "source_type": "service",
                            "target_type": "service",
                            "dependency_type": self._choice(["runtime", "runtime", "data", "event"]),
                            "severity": self._choice(["critical", "high", "medium", "low"]),
                            "is_circular": False,
                            "description": f"{service['name']} depends on {target['name']}",
                        }
                        self.dependencies.append(dep)
        
        # Intentional circular dependencies (for testing detection)
        if len(self.services) >= 3 and self._probability(circular_prob * 5):
            cycle_size = self._randint(2, min(4, len(self.services)))
            cycle_services = self._sample(self.services, cycle_size)
            for i in range(len(cycle_services)):
                source = cycle_services[i]
                target = cycle_services[(i + 1) % len(cycle_services)]
                existing = any(
                    d["source_id"] == source["id"] and d["target_id"] == target["id"]
                    for d in self.dependencies
                )
                if not existing:
                    dep = {
                        **self._base_entity(),
                        "source_id": source["id"],
                        "target_id": target["id"],
                        "source_type": "service",
                        "target_type": "service",
                        "dependency_type": "runtime",
                        "severity": "high",
                        "is_circular": True,
                        "description": f"CIRCULAR: {source['name']} -> {target['name']}",
                    }
                    self.dependencies.append(dep)
    
    def _generate_risk_metadata(self) -> None:
        """Generate criticality ratings, SLOs, failure modes, recovery patterns."""
        for service in self.services:
            # Criticality rating
            criticality = self._choice(["critical", "high", "medium", "medium", "low"])
            rating = {
                **self._base_entity(),
                "entity_id": service["id"],
                "entity_type": "service",
                "criticality": criticality,
                "business_impact": f"Impact to {service['name']} operations",
                "risk_score": self._randfloat(1.0, 10.0),
                "last_reviewed_at": self._random_datetime(90),
                "reviewed_by": self._names.team(),
            }
            self.criticality_ratings.append(rating)
            
            # SLO definition
            slo = {
                **self._base_entity(),
                "entity_id": service["id"],
                "entity_type": "service",
                "availability": self._randfloat(0.99, 0.9999),
                "latency_p50_ms": self._randint(10, 200),
                "latency_p95_ms": self._randint(100, 1000),
                "latency_p99_ms": self._randint(200, 3000),
                "error_rate": self._randfloat(0.0001, 0.01),
                "throughput_min_rps": self._randint(50, 5000),
            }
            self.slo_definitions.append(slo)
            
            # Failure modes (probability-based)
            if self._probability(0.7):
                fm = {
                    **self._base_entity(),
                    "entity_id": service["id"],
                    "entity_type": "service",
                    "failure_type": self._choice(["service_unavailable", "latency_spike", "dependency_failure", "resource_exhaustion"]),
                    "probability": self._randfloat(0.001, 0.05),
                    "severity": self._choice(["critical", "high", "medium"]),
                    "affected_service_ids": [s["id"] for s in self._sample(self.services, self._randint(1, 3))],
                    "description": f"Potential failure in {service['name']}",
                    "recovery_path": self._sample(["restart", "failover", "rollback", "scale-up", "circuit-break"], 2),
                }
                self.failure_modes.append(fm)
        
        # Recovery patterns
        pattern_types = ["retry", "failover", "rollback", "degraded_mode", "circuit_breaker", "bulkhead"]
        for pt in pattern_types:
            pattern = {
                **self._base_entity(),
                "name": f"{pt.replace('_', '-')}-pattern",
                "description": f"Standard {pt} recovery pattern",
                "pattern_type": pt,
                "failure_mode_id": self.failure_modes[0]["id"] if self.failure_modes else None,
                "step_sequence": [f"step-{i+1}" for i in range(self._randint(2, 5))],
                "estimated_recovery_minutes": self._randint(1, 30),
                "success_rate": self._randfloat(0.85, 0.99),
            }
            self.recovery_patterns.append(pattern)
    
    def _generate_deployments(self) -> None:
        """Generate deployments for microservices across environments."""
        for ms in self.microservices:
            for env in self.environments:
                deployment = {
                    **self._base_entity(),
                    "microservice_id": ms["id"],
                    "environment_id": env["id"],
                    "replica_count": 3 if env["env_type"] == "prod" else 1,
                    "cpu_request": self._choice(["250m", "500m", "1000m", "2000m"]),
                    "memory_request": self._choice(["256Mi", "512Mi", "1Gi", "2Gi"]),
                    "status": "running",
                    "deployed_at": self._random_datetime(30),
                    "health_status": self._choice(["healthy", "healthy", "healthy", "degraded"]),
                }
                self.deployments.append(deployment)
    
    def _summarize(self) -> dict[str, int]:
        return {
            "products": len(self.products),
            "features": len(self.features),
            "platforms": len(self.platforms),
            "capabilities": len(self.capabilities),
            "services": len(self.services),
            "microservices": len(self.microservices),
            "interfaces": len(self.interfaces),
            "flows": len(self.flows),
            "flow_steps": len(self.flow_steps),
            "dependencies": len(self.dependencies),
            "environments": len(self.environments),
            "deployments": len(self.deployments),
            "data_stores": len(self.data_stores),
            "criticality_ratings": len(self.criticality_ratings),
            "slo_definitions": len(self.slo_definitions),
            "failure_modes": len(self.failure_modes),
            "recovery_patterns": len(self.recovery_patterns),
            "event_types": len(self.event_types),
        }
    
    def to_dict(self) -> dict[str, Any]:
        """Export complete ecosystem as a dictionary."""
        return {
            "seed": self._seed,
            "summary": self._summarize(),
            "products": self.products,
            "features": self.features,
            "platforms": self.platforms,
            "capabilities": self.capabilities,
            "services": self.services,
            "microservices": self.microservices,
            "interfaces": self.interfaces,
            "flows": self.flows,
            "flow_steps": self.flow_steps,
            "dependencies": self.dependencies,
            "environments": self.environments,
            "deployments": self.deployments,
            "data_stores": self.data_stores,
            "data_store_instances": self.data_store_instances,
            "criticality_ratings": self.criticality_ratings,
            "slo_definitions": self.slo_definitions,
            "failure_modes": self.failure_modes,
            "recovery_patterns": self.recovery_patterns,
            "event_types": self.event_types,
        }


def generate_ecosystem(
    seed: int = 42, size: str = "small", config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Convenience function to generate a complete ecosystem.
    
    Args:
        seed: Random seed for reproducibility.
        size: Preset size ('small', 'medium', 'large').
        config: Optional custom configuration overrides.
    
    Returns:
        Complete ecosystem dictionary with all entity types.
    """
    gen_config = GeneratorConfig(size, config)
    generator = EcosystemGenerator(seed=seed, size=size, config=gen_config)
    return generator.generate()
