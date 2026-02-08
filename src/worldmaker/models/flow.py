"""Flow domain models: Flow, FlowStep, Interface, and EventTypeDefinition."""

from uuid import UUID
from typing import Any, Optional
from pydantic import Field, ConfigDict

from worldmaker.models.base import (
    BaseEntity,
    EntityStatus,
    FlowType,
    InterfaceType,
)


class Flow(BaseEntity):
    """Flow domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    name: str = Field(..., description="Flow name")
    description: Optional[str] = Field(None, description="Flow description")
    flow_type: FlowType = Field(..., description="Type of flow")
    status: EntityStatus = Field(..., description="Flow status")
    starting_service_id: Optional[UUID] = Field(
        None, description="Starting service ID"
    )
    ending_service_id: Optional[UUID] = Field(None, description="Ending service ID")
    average_duration_ms: Optional[int] = Field(
        None, description="Average flow duration in milliseconds"
    )
    steps: list[UUID] = Field(default_factory=list, description="List of step IDs")


class FlowStep(BaseEntity):
    """Flow step domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    flow_id: UUID = Field(..., description="Associated flow ID")
    step_number: int = Field(..., description="Step sequence number")
    from_service_id: UUID = Field(..., description="Source service ID")
    to_service_id: UUID = Field(..., description="Target service ID")
    interface_id: Optional[UUID] = Field(None, description="Interface ID used")
    status: EntityStatus = Field(
        default=EntityStatus.ACTIVE, description="Step status"
    )
    average_duration_ms: Optional[int] = Field(
        None, description="Average step duration in milliseconds"
    )
    failure_mode: Optional[str] = Field(None, description="Potential failure mode")
    retry_policy: dict[str, Any] = Field(
        default_factory=lambda: {"max_retries": 3, "backoff_ms": 1000},
        description="Retry policy configuration",
    )


class Interface(BaseEntity):
    """Interface domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    provider_id: UUID = Field(..., description="Provider service ID")
    consumer_id: UUID = Field(..., description="Consumer service ID")
    name: str = Field(..., description="Interface name")
    interface_type: InterfaceType = Field(..., description="Type of interface")
    protocol: str = Field(..., description="Communication protocol")
    version: str = Field(default="1.0.0", description="Interface version")
    schema_definition: dict[str, Any] = Field(
        default_factory=dict, description="Schema definition"
    )
    authentication: dict[str, Any] = Field(
        default_factory=dict, description="Authentication configuration"
    )
    rate_limit: dict[str, Any] = Field(
        default_factory=dict, description="Rate limiting configuration"
    )
    status: EntityStatus = Field(
        default=EntityStatus.ACTIVE, description="Interface status"
    )


class EventTypeDefinition(BaseEntity):
    """Event type definition domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    name: str = Field(..., description="Event type name")
    service_id: UUID = Field(..., description="Publishing service ID")
    description: Optional[str] = Field(None, description="Event type description")
    schema_definition: dict[str, Any] = Field(
        default_factory=dict, description="Event schema definition"
    )
    retention: str = Field(default="30d", description="Event retention period")
    status: EntityStatus = Field(
        default=EntityStatus.ACTIVE, description="Event type status"
    )
    consumed_by_service_ids: list[UUID] = Field(
        default_factory=list, description="Services that consume this event type"
    )
