"""Realistic naming patterns for enterprise ecosystem generation.

Uses industry-standard naming conventions to generate believable
products, platforms, services, and microservice names.
"""
from __future__ import annotations
import random
from typing import Any


# Product domains
PRODUCT_DOMAINS = [
    "payments", "identity", "commerce", "messaging", "analytics",
    "logistics", "billing", "compliance", "marketplace", "media",
    "insurance", "lending", "trading", "healthcare", "education",
    "supply-chain", "rewards", "notifications", "search", "recommendations",
]

PRODUCT_PREFIXES = [
    "Smart", "Next", "Core", "Ultra", "Prime", "Edge", "Cloud",
    "Digital", "Unified", "Global", "Express", "Flex", "Pro", "Max",
]

# Platform categories
PLATFORM_CATEGORIES = {
    "payment": ["Payment Gateway", "Transaction Processing", "Payment Orchestration", "Card Processing"],
    "identity": ["Identity Management", "Access Control", "Authentication Hub", "SSO Platform"],
    "data": ["Data Platform", "Analytics Engine", "Data Warehouse", "Stream Processing"],
    "messaging": ["Messaging Platform", "Notification Hub", "Event Streaming", "Communication Gateway"],
    "commerce": ["Commerce Engine", "Catalog Platform", "Order Management", "Pricing Engine"],
    "infrastructure": ["API Gateway", "Service Mesh", "Config Management", "Secret Management"],
    "security": ["Security Platform", "Fraud Detection", "Risk Engine", "Compliance Gateway"],
    "observability": ["Monitoring Platform", "Logging Hub", "Tracing System", "Alerting Engine"],
}

# Service naming patterns
SERVICE_PATTERNS = {
    "payment": ["PaymentService", "LedgerService", "SettlementService", "ReconciliationService", "RefundService"],
    "identity": ["AuthService", "UserService", "RoleService", "TokenService", "SessionService", "MFAService"],
    "data": ["IngestionService", "TransformService", "QueryService", "CatalogService", "LineageService"],
    "messaging": ["NotificationService", "EmailService", "SMSService", "PushService", "WebhookService"],
    "commerce": ["OrderService", "CartService", "CatalogService", "PricingService", "InventoryService", "ShippingService"],
    "infrastructure": ["GatewayService", "RoutingService", "RateLimitService", "DiscoveryService", "ConfigService"],
    "security": ["FraudService", "RiskScoringService", "AuditService", "EncryptionService", "ComplianceService"],
    "observability": ["MetricsService", "LoggingService", "TracingService", "AlertingService", "DashboardService"],
}

# Microservice naming (suffix patterns)
MICROSERVICE_SUFFIXES = [
    "-srv", "-api", "-worker", "-gateway", "-processor",
    "-handler", "-consumer", "-producer", "-scheduler", "-validator",
    "-transformer", "-aggregator", "-router", "-proxy", "-adapter",
]

MICROSERVICE_PREFIXES_BY_FUNCTION = {
    "frontend": ["form", "ui", "web", "portal", "dashboard"],
    "backend": ["srv", "core", "engine", "processor", "handler"],
    "data": ["db", "cache", "store", "index", "query"],
    "integration": ["adapter", "connector", "bridge", "proxy", "gateway"],
    "async": ["worker", "consumer", "producer", "scheduler", "queue"],
}

# Languages and frameworks
LANGUAGES = {
    "python": ["FastAPI", "Django", "Flask", "Celery"],
    "go": ["Gin", "Echo", "Fiber", "gRPC"],
    "java": ["Spring Boot", "Micronaut", "Quarkus", "Vert.x"],
    "typescript": ["NestJS", "Express", "Fastify", "Koa"],
    "rust": ["Actix", "Axum", "Rocket", "Warp"],
    "kotlin": ["Ktor", "Spring Boot", "Micronaut"],
}

# Data store technologies
DATA_STORE_TECHNOLOGIES = {
    "relational_db": ["PostgreSQL", "MySQL", "Aurora", "CockroachDB"],
    "document_db": ["MongoDB", "DynamoDB", "Couchbase", "Firestore"],
    "cache": ["Redis", "Memcached", "Hazelcast", "Aerospike"],
    "queue": ["Kafka", "RabbitMQ", "SQS", "NATS"],
    "blob_storage": ["S3", "GCS", "Azure Blob", "MinIO"],
    "graph_db": ["Neo4j", "Neptune", "ArangoDB", "JanusGraph"],
    "search_engine": ["Elasticsearch", "OpenSearch", "Solr", "Meilisearch"],
}

# Cloud regions
CLOUD_REGIONS = [
    "us-east-1", "us-west-2", "eu-west-1", "eu-central-1",
    "ap-southeast-1", "ap-northeast-1",
]

# Owner teams
TEAMS = [
    "platform-core", "payments-team", "identity-team", "data-engineering",
    "commerce-team", "security-ops", "sre-team", "api-platform",
    "mobile-team", "growth-team", "infrastructure", "devex-team",
    "ml-platform", "fraud-team", "compliance-team", "messaging-team",
]


class NameGenerator:
    """Generates realistic enterprise system names."""
    
    def __init__(self, rng: random.Random):
        self._rng = rng
        self._used_names: set[str] = set()
    
    def _unique(self, name: str) -> str:
        """Ensure name uniqueness by appending suffix if needed."""
        if name not in self._used_names:
            self._used_names.add(name)
            return name
        counter = 2
        while f"{name}-{counter}" in self._used_names:
            counter += 1
        unique = f"{name}-{counter}"
        self._used_names.add(unique)
        return unique
    
    def product_name(self) -> str:
        prefix = self._rng.choice(PRODUCT_PREFIXES)
        domain = self._rng.choice(PRODUCT_DOMAINS).title().replace("-", " ")
        return self._unique(f"{prefix} {domain}")
    
    def platform_name(self, category: str | None = None) -> tuple[str, str]:
        """Returns (name, category)."""
        cat = category or self._rng.choice(list(PLATFORM_CATEGORIES.keys()))
        names = PLATFORM_CATEGORIES.get(cat, ["Platform"])
        name = self._rng.choice(names)
        return self._unique(name), cat
    
    def service_name(self, category: str) -> str:
        patterns = SERVICE_PATTERNS.get(category, SERVICE_PATTERNS["infrastructure"])
        name = self._rng.choice(patterns)
        return self._unique(name)
    
    def microservice_name(self, service_name: str) -> str:
        # Convert CamelCase to kebab-case
        base = ""
        for i, c in enumerate(service_name):
            if c.isupper() and i > 0:
                base += "-"
            base += c.lower()
        base = base.replace("service", "").strip("-")
        
        suffix = self._rng.choice(MICROSERVICE_SUFFIXES)
        return self._unique(f"{base}{suffix}")
    
    def datastore_name(self, store_type: str) -> tuple[str, str]:
        """Returns (name, technology)."""
        techs = DATA_STORE_TECHNOLOGIES.get(store_type, ["Unknown"])
        tech = self._rng.choice(techs)
        prefix = self._rng.choice(["primary", "shared", "dedicated", "global", "regional"])
        name = f"{prefix}-{tech.lower().replace(' ', '-')}"
        return self._unique(name), tech
    
    def team(self) -> str:
        return self._rng.choice(TEAMS)
    
    def language_and_framework(self) -> tuple[str, str]:
        lang = self._rng.choice(list(LANGUAGES.keys()))
        framework = self._rng.choice(LANGUAGES[lang])
        return lang, framework
    
    def region(self) -> str:
        return self._rng.choice(CLOUD_REGIONS)
    
    def capability_name(self, category: str) -> str:
        templates = {
            "payment": ["Credit Card Processing", "ACH Transfers", "Wire Transfers", "Digital Wallet", "Subscription Billing", "Invoicing"],
            "identity": ["OAuth2 Authentication", "SAML SSO", "MFA Verification", "API Key Management", "RBAC", "User Provisioning"],
            "data": ["Real-time Ingestion", "Batch ETL", "Data Quality", "Schema Registry", "Data Lineage", "Query Federation"],
            "messaging": ["Email Delivery", "SMS Gateway", "Push Notifications", "In-App Messaging", "Webhook Dispatch", "Event Routing"],
            "commerce": ["Product Search", "Cart Management", "Checkout Flow", "Pricing Rules", "Inventory Tracking", "Fulfillment"],
            "infrastructure": ["API Routing", "Rate Limiting", "Circuit Breaking", "Service Discovery", "Config Distribution", "Secret Rotation"],
            "security": ["Fraud Scoring", "Transaction Monitoring", "PCI Compliance", "Data Encryption", "Access Logging", "Threat Detection"],
            "observability": ["Metric Collection", "Log Aggregation", "Distributed Tracing", "Alert Management", "SLO Tracking", "Incident Response"],
        }
        names = templates.get(category, ["General Capability"])
        return self._unique(self._rng.choice(names))
    
    def feature_name(self) -> str:
        """Generate a product feature name."""
        actions = ["Real-time", "Automated", "Self-service", "Intelligent", "Unified",
                   "Adaptive", "Contextual", "Integrated", "Multi-channel", "Predictive"]
        domains = ["Analytics Dashboard", "Reporting", "Notifications", "Search",
                   "Personalization", "Document Management", "Workflow Automation",
                   "Collaboration Hub", "Data Export", "Audit Trail", "User Management",
                   "API Access", "Billing Portal", "Onboarding Flow", "Access Control",
                   "Activity Feed", "Performance Insights", "Compliance Reporting",
                   "Content Delivery", "Configuration Manager"]
        return self._unique(f"{self._rng.choice(actions)} {self._rng.choice(domains)}")

    def flow_name(self) -> str:
        actions = ["Process", "Handle", "Execute", "Complete", "Verify", "Initiate", "Resolve"]
        objects = ["Payment", "Order", "Authentication", "Refund", "Notification", "Transfer", 
                   "Registration", "Checkout", "Subscription", "Invoice", "Claim", "Settlement"]
        return self._unique(f"{self._rng.choice(actions)} {self._rng.choice(objects)}")
    
    def interface_name(self, provider: str, consumer: str) -> str:
        return self._unique(f"{provider}-to-{consumer}-api")
