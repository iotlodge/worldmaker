"""Platform domain models: Platform, Capability, Service, and Microservice."""

from uuid import UUID
from typing import Any, Optional
from pydantic import Field, ConfigDict

from worldmaker.models.base import (
    BaseEntity,
    EntityStatus,
    CapabilityType,
    ServiceType,
)


class Platform(BaseEntity):
    """Platform domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    name: str = Field(..., description="Platform name")
    description: Optional[str] = Field(None, description="Platform description")
    category: str = Field(..., description="Platform category")
    owner: str = Field(..., description="Platform owner")
    status: EntityStatus = Field(..., description="Platform status")
    tech_stack: list[str] = Field(
        default_factory=list, description="Technology stack components"
    )
    sla_definition: dict[str, Any] = Field(
        default_factory=dict, description="SLA definition"
    )


class Capability(BaseEntity):
    """Capability domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    platform_id: UUID = Field(..., description="Associated platform ID")
    name: str = Field(..., description="Capability name")
    description: Optional[str] = Field(None, description="Capability description")
    capability_type: CapabilityType = Field(..., description="Type of capability")
    status: EntityStatus = Field(
        default=EntityStatus.ACTIVE, description="Capability status"
    )
    version: str = Field(default="1.0.0", description="Capability version")
    slo: dict[str, Any] = Field(
        default_factory=dict, description="Service level objectives"
    )
    depends_on_capabilities: list[UUID] = Field(
        default_factory=list, description="Capability dependencies"
    )


class Service(BaseEntity):
    """Service domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    name: str = Field(..., description="Service name")
    description: Optional[str] = Field(None, description="Service description")
    capability_id: Optional[UUID] = Field(
        None, description="Associated capability ID"
    )
    platform_id: UUID = Field(..., description="Associated platform ID")
    owner: str = Field(..., description="Service owner")
    status: EntityStatus = Field(..., description="Service status")
    service_type: ServiceType = Field(..., description="Type of service")
    api_version: str = Field(default="v1", description="API version")
    microservice_ids: list[UUID] = Field(
        default_factory=list, description="List of microservice IDs"
    )


class Microservice(BaseEntity):
    """Microservice domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    service_id: UUID = Field(..., description="Associated service ID")
    name: str = Field(..., description="Microservice name")
    description: Optional[str] = Field(None, description="Microservice description")
    container_image: Optional[str] = Field(
        None, description="Container image reference"
    )
    language: str = Field(..., description="Programming language")
    framework: Optional[str] = Field(None, description="Framework used")
    status: EntityStatus = Field(..., description="Microservice status")
    repo_url: Optional[str] = Field(None, description="Repository URL")
    dependencies: list[UUID] = Field(
        default_factory=list, description="Microservice dependencies"
    )
