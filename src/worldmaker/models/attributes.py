"""Attribute definition model for the enterprise attribute registry.

Attributes are the data layer powering MTTD < 0: core platforms stamp
lifecycle attributes onto entities, and the gap analysis engine detects
entities missing required attributes as risk signals.
"""
from __future__ import annotations

from typing import Any, Optional
from pydantic import Field, ConfigDict

from worldmaker.models.base import BaseEntity, AttributeTier


class AttributeDefinition(BaseEntity):
    """Defines a named attribute that can be attached to entities.

    Three tiers:
    - CORE: Required for AI intelligence (absence = risk signal)
    - LIFECYCLE: Stamped by core functions during workflows
    - FUNCTION: Extensible, added by platform owners at runtime
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    name: str = Field(..., description="Machine name, e.g. 'risk_classification'")
    display_name: str = Field(..., description="Human-readable name")
    tier: str = Field(..., description="Attribute tier: core, lifecycle, or function")
    data_type: str = Field(
        ..., description="Data type: string, number, boolean, enum, json"
    )
    description: str = Field(..., description="What this attribute measures")
    applies_to: list[str] = Field(
        default_factory=list,
        description="Entity types this attribute applies to",
    )
    required: bool = Field(
        default=False,
        description="If true, absence on an applicable entity = gap = risk signal",
    )
    default_value: Optional[Any] = Field(
        None, description="Default value when entity is created"
    )
    enum_values: list[str] = Field(
        default_factory=list,
        description="Valid values when data_type is 'enum'",
    )
    owner_platform: Optional[str] = Field(
        None, description="Core function that stamps this attribute"
    )
    category: str = Field(
        default="general",
        description="Grouping: security, operations, compliance, risk, etc.",
    )
