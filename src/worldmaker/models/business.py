"""Business domain models: Product, Feature, and BusinessProcess."""

from uuid import UUID
from typing import Optional
from pydantic import Field, ConfigDict

from worldmaker.models.base import (
    BaseEntity,
    EntityStatus,
    BusinessProcessType,
)


class Product(BaseEntity):
    """Product domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    status: EntityStatus = Field(
        default=EntityStatus.ACTIVE, description="Current product status"
    )
    owner: str = Field(..., description="Product owner")
    version: int = Field(default=1, description="Product version")
    tags: list[str] = Field(default_factory=list, description="Product tags")
    features: list[UUID] = Field(
        default_factory=list, description="List of feature IDs in this product"
    )


class Feature(BaseEntity):
    """Feature domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    product_id: UUID = Field(..., description="Associated product ID")
    name: str = Field(..., description="Feature name")
    description: Optional[str] = Field(None, description="Feature description")
    user_flows: list[str] = Field(
        default_factory=list, description="User flow descriptions"
    )
    status: EntityStatus = Field(
        default=EntityStatus.PLANNED, description="Feature status"
    )
    owner: str = Field(..., description="Feature owner")
    depends_on_features: list[UUID] = Field(
        default_factory=list, description="Feature dependencies"
    )


class BusinessProcess(BaseEntity):
    """Business process domain entity."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    name: str = Field(..., description="Business process name")
    description: Optional[str] = Field(
        None, description="Business process description"
    )
    process_type: BusinessProcessType = Field(
        ..., description="Type of business process"
    )
    owner: str = Field(..., description="Process owner")
    status: EntityStatus = Field(
        default=EntityStatus.ACTIVE, description="Process status"
    )
    feature_ids: list[UUID] = Field(
        default_factory=list, description="Associated feature IDs"
    )
    flow_ids: list[UUID] = Field(
        default_factory=list, description="Associated flow IDs"
    )
