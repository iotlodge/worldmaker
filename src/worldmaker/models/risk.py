"""Risk domain models: CriticalityRating, SLODefinition, FailureMode, and RecoveryPattern."""

from uuid import UUID
from datetime import datetime
from typing import Any, Optional
from pydantic import Field, ConfigDict

from worldmaker.models.base import (
    BaseEntity,
    EntityType,
    CriticalityLevel,
    Severity,
    FailureModeType,
    RecoveryPatternType,
)


class CriticalityRating(BaseEntity):
    """Criticality rating domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    entity_id: UUID = Field(..., description="Entity ID")
    entity_type: EntityType = Field(..., description="Entity type")
    criticality: CriticalityLevel = Field(..., description="Criticality level")
    business_impact: Optional[str] = Field(None, description="Business impact")
    risk_score: float = Field(
        default=0.0, ge=0.0, le=10.0, description="Risk score (0-10)"
    )
    last_reviewed_at: Optional[datetime] = Field(
        None, description="Last review timestamp"
    )
    reviewed_by: Optional[str] = Field(None, description="Reviewer name")


class SLODefinition(BaseEntity):
    """SLO definition domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    entity_id: UUID = Field(..., description="Entity ID")
    entity_type: EntityType = Field(..., description="Entity type")
    availability: float = Field(
        default=0.999, ge=0.0, le=1.0, description="Availability target"
    )
    latency_p50_ms: int = Field(default=100, description="P50 latency in ms")
    latency_p95_ms: int = Field(default=500, description="P95 latency in ms")
    latency_p99_ms: int = Field(default=1000, description="P99 latency in ms")
    error_rate: float = Field(
        default=0.001, ge=0.0, le=1.0, description="Error rate threshold"
    )
    throughput_min_rps: int = Field(
        default=100, description="Minimum throughput in RPS"
    )


class FailureMode(BaseEntity):
    """Failure mode domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    entity_id: UUID = Field(..., description="Entity ID")
    entity_type: EntityType = Field(..., description="Entity type")
    failure_type: FailureModeType = Field(..., description="Type of failure")
    probability: float = Field(
        default=0.01, ge=0.0, le=1.0, description="Probability of failure"
    )
    severity: Severity = Field(..., description="Failure severity")
    affected_service_ids: list[UUID] = Field(
        default_factory=list, description="Affected service IDs"
    )
    description: Optional[str] = Field(None, description="Failure description")
    recovery_path: list[str] = Field(
        default_factory=list, description="Recovery steps"
    )


class RecoveryPattern(BaseEntity):
    """Recovery pattern domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    name: str = Field(..., description="Recovery pattern name")
    description: Optional[str] = Field(None, description="Pattern description")
    pattern_type: RecoveryPatternType = Field(..., description="Type of pattern")
    failure_mode_id: Optional[UUID] = Field(
        None, description="Associated failure mode ID"
    )
    step_sequence: list[str] = Field(
        default_factory=list, description="Recovery steps in order"
    )
    estimated_recovery_minutes: int = Field(
        default=5, description="Estimated recovery time"
    )
    success_rate: float = Field(
        default=0.95, ge=0.0, le=1.0, description="Pattern success rate"
    )
