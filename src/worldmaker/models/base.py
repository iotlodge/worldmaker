"""Base entity definitions, enums, and mixins for WorldMaker domain models."""

from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class EntityStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DECOMMISSIONED = "decommissioned"
    SUNSET = "sunset"


class EntityType(str, Enum):
    PRODUCT = "product"
    FEATURE = "feature"
    BUSINESS_PROCESS = "business_process"
    PLATFORM = "platform"
    CAPABILITY = "capability"
    SERVICE = "service"
    MICROSERVICE = "microservice"
    FLOW = "flow"
    FLOW_STEP = "flow_step"
    INTERFACE = "interface"
    EVENT_TYPE = "event_type"
    ENVIRONMENT = "environment"
    DEPLOYMENT = "deployment"
    DATA_STORE = "data_store"
    DATA_STORE_INSTANCE = "data_store_instance"
    DEPENDENCY = "dependency"


class DependencyType(str, Enum):
    RUNTIME = "runtime"
    BUILD = "build"
    DATA = "data"
    EVENT = "event"
    DEPLOYMENT = "deployment"
    INFRASTRUCTURE = "infrastructure"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CriticalityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ServiceType(str, Enum):
    REST = "rest"
    GRPC = "grpc"
    EVENT_DRIVEN = "event_driven"
    BATCH = "batch"
    GRAPHQL = "graphql"


class InterfaceType(str, Enum):
    REST = "rest"
    GRPC = "grpc"
    ASYNC_EVENT = "async_event"
    WEBHOOK = "webhook"
    DATABASE = "database"
    GRAPHQL = "graphql"


class EnvironmentType(str, Enum):
    DEV = "dev"
    STAGING = "staging"
    QA = "qa"
    PROD = "prod"


class DataStoreType(str, Enum):
    RELATIONAL_DB = "relational_db"
    DOCUMENT_DB = "document_db"
    CACHE = "cache"
    QUEUE = "queue"
    BLOB_STORAGE = "blob_storage"
    GRAPH_DB = "graph_db"
    SEARCH_ENGINE = "search_engine"


class DeploymentStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    PAUSED = "paused"
    FAILED = "failed"


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class LifecycleEventType(str, Enum):
    CREATED = "created"
    ACTIVATED = "activated"
    MODIFIED = "modified"
    DEPRECATED = "deprecated"
    DECOMMISSIONED = "decommissioned"


class ChangeEventType(str, Enum):
    FEATURE_RELEASE = "feature_release"
    HOTFIX = "hotfix"
    SECURITY_PATCH = "security_patch"
    DEPRECATION = "deprecation"
    MIGRATION = "migration"


class ChangeEventStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"


class FailureModeType(str, Enum):
    SERVICE_UNAVAILABLE = "service_unavailable"
    DATA_LOSS = "data_loss"
    LATENCY_SPIKE = "latency_spike"
    DEPENDENCY_FAILURE = "dependency_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DATA_CORRUPTION = "data_corruption"


class RecoveryPatternType(str, Enum):
    RETRY = "retry"
    FAILOVER = "failover"
    ROLLBACK = "rollback"
    DEGRADED_MODE = "degraded_mode"
    CIRCUIT_BREAKER = "circuit_breaker"
    BULKHEAD = "bulkhead"


class FlowType(str, Enum):
    REQUEST_RESPONSE = "request_response"
    EVENT_STREAM = "event_stream"
    BATCH = "batch"
    SCHEDULED = "scheduled"
    SAGA = "saga"


class CapabilityType(str, Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORKING = "networking"
    INTEGRATION = "integration"
    IDENTITY = "identity"
    PAYMENT = "payment"
    MESSAGING = "messaging"
    ANALYTICS = "analytics"
    SECURITY = "security"


class BusinessProcessType(str, Enum):
    CROSS_PRODUCT = "cross_product"
    INTERNAL = "internal"
    EXTERNAL = "external"


class BaseEntity(BaseModel):
    """Base for all WorldMaker domain entities."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        json_schema_extra={"example": {}},
    )

    id: UUID = Field(default_factory=uuid4, description="Unique entity identifier")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Extensible metadata"
    )


class EntityReference(BaseModel):
    """Lightweight reference to any entity."""

    id: UUID
    entity_type: EntityType
    name: Optional[str] = None
