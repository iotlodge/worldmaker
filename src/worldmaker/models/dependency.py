"""Dependency domain models: Dependency and ImpactChain."""

from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import Field, ConfigDict

from worldmaker.models.base import (
    BaseEntity,
    EntityType,
    DependencyType,
    Severity,
    EntityReference,
)


class Dependency(BaseEntity):
    """Dependency domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    source_id: UUID = Field(..., description="Source entity ID")
    target_id: UUID = Field(..., description="Target entity ID")
    source_type: EntityType = Field(..., description="Source entity type")
    target_type: EntityType = Field(..., description="Target entity type")
    dependency_type: DependencyType = Field(..., description="Type of dependency")
    severity: Severity = Field(
        default=Severity.MEDIUM, description="Dependency severity"
    )
    is_circular: bool = Field(
        default=False, description="Whether this dependency is circular"
    )
    description: Optional[str] = Field(None, description="Dependency description")


class ImpactChain(BaseEntity):
    """Impact chain domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    root_cause_id: UUID = Field(..., description="Root cause entity ID")
    root_cause_type: EntityType = Field(..., description="Root cause entity type")
    affected_entities: list[EntityReference] = Field(
        default_factory=list, description="List of affected entities"
    )
    blast_radius: int = Field(
        default=0, description="Number of affected entities"
    )
    estimated_recovery_minutes: int = Field(
        default=0, description="Estimated recovery time in minutes"
    )
    last_calculated: datetime = Field(
        default_factory=datetime.utcnow, description="When this chain was calculated"
    )
