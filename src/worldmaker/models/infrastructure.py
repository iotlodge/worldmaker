"""Infrastructure domain models: Environment, Deployment, DataStore, and DataStoreInstance."""

from uuid import UUID
from datetime import datetime
from typing import Any, Optional
from pydantic import Field, ConfigDict

from worldmaker.models.base import (
    BaseEntity,
    EntityStatus,
    EnvironmentType,
    DataStoreType,
    DeploymentStatus,
    HealthStatus,
)


class Environment(BaseEntity):
    """Environment domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    name: str = Field(..., description="Environment name")
    env_type: EnvironmentType = Field(..., description="Type of environment")
    region: str = Field(..., description="Cloud region")
    cloud_provider: str = Field(default="aws", description="Cloud provider")
    compliance: list[str] = Field(
        default_factory=list, description="Compliance requirements"
    )


class Deployment(BaseEntity):
    """Deployment domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    microservice_id: UUID = Field(..., description="Microservice ID")
    environment_id: UUID = Field(..., description="Environment ID")
    replica_count: int = Field(default=1, description="Number of replicas")
    cpu_request: str = Field(default="250m", description="CPU request")
    memory_request: str = Field(default="512Mi", description="Memory request")
    status: DeploymentStatus = Field(
        default=DeploymentStatus.PLANNED, description="Deployment status"
    )
    deployed_at: Optional[datetime] = Field(None, description="Deployment timestamp")
    health_status: HealthStatus = Field(
        default=HealthStatus.UNKNOWN, description="Current health status"
    )


class DataStore(BaseEntity):
    """Data store domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    name: str = Field(..., description="Data store name")
    store_type: DataStoreType = Field(..., description="Type of data store")
    technology: str = Field(..., description="Technology/product name")
    owner: str = Field(..., description="Data store owner")
    status: EntityStatus = Field(
        default=EntityStatus.ACTIVE, description="Data store status"
    )


class DataStoreInstance(BaseEntity):
    """Data store instance domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    data_store_id: UUID = Field(..., description="Data store ID")
    environment_id: UUID = Field(..., description="Environment ID")
    deployment_id: Optional[UUID] = Field(None, description="Deployment ID")
    connection_string: Optional[str] = Field(
        None, description="Connection string (sensitive)"
    )
    replication_factor: int = Field(default=1, description="Replication factor")
    backup_policy: dict[str, Any] = Field(
        default_factory=dict, description="Backup policy configuration"
    )
    status: EntityStatus = Field(
        default=EntityStatus.ACTIVE, description="Instance status"
    )
