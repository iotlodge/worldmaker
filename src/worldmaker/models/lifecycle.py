"""Lifecycle domain models: LifecycleEvent, ChangeEvent, and VersionTracking."""

from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import Field, ConfigDict

from worldmaker.models.base import (
    BaseEntity,
    EntityType,
    LifecycleEventType,
    ChangeEventType,
    ChangeEventStatus,
    Severity,
    EntityReference,
)


class LifecycleEvent(BaseEntity):
    """Lifecycle event domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    entity_id: UUID = Field(..., description="Entity ID")
    entity_type: EntityType = Field(..., description="Entity type")
    event_type: LifecycleEventType = Field(..., description="Lifecycle event type")
    from_state: Optional[str] = Field(None, description="Previous state")
    to_state: str = Field(..., description="New state")
    reason: Optional[str] = Field(None, description="Reason for state change")
    author: str = Field(..., description="Author of the change")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Event timestamp"
    )


class ChangeEvent(BaseEntity):
    """Change event domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    title: str = Field(..., description="Change title")
    description: Optional[str] = Field(None, description="Change description")
    change_type: ChangeEventType = Field(..., description="Type of change")
    author: str = Field(..., description="Change author")
    severity: Severity = Field(default=Severity.MEDIUM, description="Change severity")
    status: ChangeEventStatus = Field(
        default=ChangeEventStatus.PROPOSED, description="Change status"
    )
    affected_entities: list[EntityReference] = Field(
        default_factory=list, description="Affected entities"
    )
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


class VersionTracking(BaseEntity):
    """Version tracking domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    entity_id: UUID = Field(..., description="Entity ID")
    entity_type: EntityType = Field(..., description="Entity type")
    version: str = Field(..., description="Version string")
    version_hash: Optional[str] = Field(None, description="Hash of version content")
    previous_version: Optional[str] = Field(None, description="Previous version")
    change_summary: Optional[str] = Field(None, description="Summary of changes")
    author: str = Field(..., description="Version author")
