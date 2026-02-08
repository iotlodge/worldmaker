"""SQLAlchemy 2.0 table definitions for all WorldMaker entities."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

try:
    from sqlalchemy import (
        ARRAY,
        Boolean,
        DateTime,
        Float,
        ForeignKey,
        Index,
        Integer,
        JSON,
        String,
        Text,
    )
    from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


if HAS_SQLALCHEMY:

    class ProductTable(Base):
        """Product entity."""

        __tablename__ = "products"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
        description: Mapped[str] = mapped_column(Text, default="")
        version: Mapped[str] = mapped_column(String(50), default="1.0.0")
        status: Mapped[str] = mapped_column(String(50), default="active", index=True)
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, index=True
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_products_name_status", "name", "status"),
            Index("ix_products_created_at", "created_at"),
        )

    class FeatureTable(Base):
        """Feature entity linked to products."""

        __tablename__ = "features"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        product_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
        description: Mapped[str] = mapped_column(Text, default="")
        enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_features_product_id_name", "product_id", "name"),
            Index("ix_features_enabled", "enabled"),
        )

    class BusinessProcessTable(Base):
        """Business process entity."""

        __tablename__ = "business_processes"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
        description: Mapped[str] = mapped_column(Text, default="")
        owner: Mapped[str] = mapped_column(String(255), default="")
        status: Mapped[str] = mapped_column(String(50), default="active", index=True)
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_business_processes_owner_status", "owner", "status"),
        )

    class BusinessProcessFeatureTable(Base):
        """Junction table for business processes and features."""

        __tablename__ = "business_process_features"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        business_process_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True),
            ForeignKey("business_processes.id"),
            nullable=False,
            index=True,
        )
        feature_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), ForeignKey("features.id"), nullable=False, index=True
        )
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index(
                "ix_business_process_features_unique",
                "business_process_id",
                "feature_id",
                unique=True,
            ),
        )

    class PlatformTable(Base):
        """Platform entity."""

        __tablename__ = "platforms"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
        description: Mapped[str] = mapped_column(Text, default="")
        platform_type: Mapped[str] = mapped_column(String(100), default="", index=True)
        owner: Mapped[str] = mapped_column(String(255), default="")
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_platforms_platform_type_owner", "platform_type", "owner"),
        )

    class CapabilityTable(Base):
        """Capability entity linked to platforms."""

        __tablename__ = "capabilities"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        platform_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), ForeignKey("platforms.id"), nullable=False, index=True
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
        description: Mapped[str] = mapped_column(Text, default="")
        capability_type: Mapped[str] = mapped_column(String(100), default="")
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_capabilities_platform_id_name", "platform_id", "name"),
        )

    class ServiceTable(Base):
        """Service entity linked to capabilities and platforms."""

        __tablename__ = "services"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        capability_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True),
            ForeignKey("capabilities.id"),
            nullable=False,
            index=True,
        )
        platform_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), ForeignKey("platforms.id"), nullable=False, index=True
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
        description: Mapped[str] = mapped_column(Text, default="")
        service_type: Mapped[str] = mapped_column(String(100), default="", index=True)
        status: Mapped[str] = mapped_column(String(50), default="active", index=True)
        owner: Mapped[str] = mapped_column(String(255), default="")
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_services_platform_id_status", "platform_id", "status"),
            Index("ix_services_service_type", "service_type"),
        )

    class MicroserviceTable(Base):
        """Microservice entity linked to services."""

        __tablename__ = "microservices"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        service_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
        description: Mapped[str] = mapped_column(Text, default="")
        status: Mapped[str] = mapped_column(String(50), default="active", index=True)
        version: Mapped[str] = mapped_column(String(50), default="1.0.0")
        owner: Mapped[str] = mapped_column(String(255), default="")
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_microservices_service_id_status", "service_id", "status"),
        )

    class FlowTable(Base):
        """Flow entity linked to services as start/end points."""

        __tablename__ = "flows"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        start_service_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True
        )
        end_service_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False)
        description: Mapped[str] = mapped_column(Text, default="")
        flow_type: Mapped[str] = mapped_column(String(100), default="")
        status: Mapped[str] = mapped_column(String(50), default="active", index=True)
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_flows_start_service_id", "start_service_id"),
            Index("ix_flows_end_service_id", "end_service_id"),
        )

    class FlowStepTable(Base):
        """Flow step entity for steps within a flow."""

        __tablename__ = "flow_steps"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        flow_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), ForeignKey("flows.id"), nullable=False, index=True
        )
        service_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True
        )
        step_order: Mapped[int] = mapped_column(Integer, nullable=False)
        name: Mapped[str] = mapped_column(String(255), nullable=False)
        description: Mapped[str] = mapped_column(Text, default="")
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_flow_steps_flow_id_order", "flow_id", "step_order"),
        )

    class InterfaceTable(Base):
        """Interface entity with provider and consumer services."""

        __tablename__ = "interfaces"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        provider_service_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True
        )
        consumer_service_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False)
        description: Mapped[str] = mapped_column(Text, default="")
        interface_type: Mapped[str] = mapped_column(String(100), default="")
        protocol: Mapped[str] = mapped_column(String(100), default="")
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_interfaces_provider_service_id", "provider_service_id"),
            Index("ix_interfaces_consumer_service_id", "consumer_service_id"),
        )

    class EventTypeTable(Base):
        """Event type entity linked to services."""

        __tablename__ = "event_types"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        service_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
        description: Mapped[str] = mapped_column(Text, default="")
        event_schema: Mapped[dict] = mapped_column(JSONB, default=dict)
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_event_types_service_id_name", "service_id", "name"),
        )

    class EnvironmentTable(Base):
        """Environment entity."""

        __tablename__ = "environments"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
        description: Mapped[str] = mapped_column(Text, default="")
        environment_type: Mapped[str] = mapped_column(
            String(100), default="", index=True
        )
        region: Mapped[str] = mapped_column(String(100), default="")
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_environments_environment_type_region", "environment_type", "region"),
        )

    class DeploymentTable(Base):
        """Deployment entity linked to microservices and environments."""

        __tablename__ = "deployments"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        microservice_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True),
            ForeignKey("microservices.id"),
            nullable=False,
            index=True,
        )
        environment_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True),
            ForeignKey("environments.id"),
            nullable=False,
            index=True,
        )
        version: Mapped[str] = mapped_column(String(50), default="")
        status: Mapped[str] = mapped_column(String(50), default="active", index=True)
        deployed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index(
                "ix_deployments_microservice_environment",
                "microservice_id",
                "environment_id",
            ),
            Index("ix_deployments_status", "status"),
        )

    class DataStoreTable(Base):
        """Data store entity."""

        __tablename__ = "data_stores"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
        description: Mapped[str] = mapped_column(Text, default="")
        data_store_type: Mapped[str] = mapped_column(
            String(100), default="", index=True
        )
        owner: Mapped[str] = mapped_column(String(255), default="")
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_data_stores_data_store_type_owner", "data_store_type", "owner"),
        )

    class DataStoreInstanceTable(Base):
        """Data store instance entity linked to data stores and environments."""

        __tablename__ = "data_store_instances"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        data_store_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True),
            ForeignKey("data_stores.id"),
            nullable=False,
            index=True,
        )
        environment_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True),
            ForeignKey("environments.id"),
            nullable=False,
            index=True,
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False)
        status: Mapped[str] = mapped_column(String(50), default="active", index=True)
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index(
                "ix_data_store_instances_unique",
                "data_store_id",
                "environment_id",
                unique=True,
            ),
        )

    class DependencyTable(Base):
        """Dependency entity with polymorphic source and target."""

        __tablename__ = "dependencies"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        source_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), nullable=False, index=True
        )
        source_type: Mapped[str] = mapped_column(
            String(100), nullable=False, index=True
        )
        target_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), nullable=False, index=True
        )
        target_type: Mapped[str] = mapped_column(
            String(100), nullable=False, index=True
        )
        dependency_type: Mapped[str] = mapped_column(
            String(100), default="", index=True
        )
        strength: Mapped[str] = mapped_column(String(50), default="medium")
        is_circular: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_dependencies_source_target", "source_id", "target_id"),
            Index(
                "ix_dependencies_source_type",
                "source_id",
                "source_type",
            ),
            Index(
                "ix_dependencies_target_type",
                "target_id",
                "target_type",
            ),
        )

    class ImpactChainTable(Base):
        """Impact chain entity."""

        __tablename__ = "impact_chains"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
        description: Mapped[str] = mapped_column(Text, default="")
        chain_path: Mapped[list] = mapped_column(ARRAY(String), default=list)
        severity: Mapped[str] = mapped_column(String(50), default="medium", index=True)
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (Index("ix_impact_chains_severity", "severity"),)

    class LifecycleEventTable(Base):
        """Lifecycle event entity."""

        __tablename__ = "lifecycle_events"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        entity_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), nullable=False, index=True
        )
        entity_type: Mapped[str] = mapped_column(
            String(100), nullable=False, index=True
        )
        event_type: Mapped[str] = mapped_column(String(100), nullable=False)
        old_state: Mapped[dict] = mapped_column(JSONB, default=dict)
        new_state: Mapped[dict] = mapped_column(JSONB, default=dict)
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, index=True
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_lifecycle_events_entity", "entity_id", "entity_type"),
        )

    class ChangeEventTable(Base):
        """Change event entity for tracking modifications."""

        __tablename__ = "change_events"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        entity_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), nullable=False, index=True
        )
        entity_type: Mapped[str] = mapped_column(
            String(100), nullable=False, index=True
        )
        change_type: Mapped[str] = mapped_column(String(100), nullable=False)
        changed_fields: Mapped[dict] = mapped_column(JSONB, default=dict)
        changed_by: Mapped[str] = mapped_column(String(255), default="")
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, index=True
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_change_events_entity", "entity_id", "entity_type"),
            Index("ix_change_events_change_type", "change_type"),
        )

    class VersionTrackingTable(Base):
        """Version tracking entity."""

        __tablename__ = "version_tracking"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        entity_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), nullable=False, index=True
        )
        entity_type: Mapped[str] = mapped_column(
            String(100), nullable=False, index=True
        )
        version_number: Mapped[int] = mapped_column(Integer, nullable=False)
        version_hash: Mapped[str] = mapped_column(String(64), default="")
        content: Mapped[dict] = mapped_column(JSONB, default=dict)
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index(
                "ix_version_tracking_entity_version",
                "entity_id",
                "entity_type",
                "version_number",
                unique=True,
            ),
        )

    class CriticalityRatingTable(Base):
        """Criticality rating entity."""

        __tablename__ = "criticality_ratings"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        entity_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), nullable=False, index=True
        )
        entity_type: Mapped[str] = mapped_column(
            String(100), nullable=False, index=True
        )
        rating: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
        justification: Mapped[str] = mapped_column(Text, default="")
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_criticality_ratings_entity", "entity_id", "entity_type"),
        )

    class SLODefinitionTable(Base):
        """SLO (Service Level Objective) definition entity."""

        __tablename__ = "slo_definitions"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        service_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False)
        description: Mapped[str] = mapped_column(Text, default="")
        slo_type: Mapped[str] = mapped_column(String(100), default="")
        target_value: Mapped[float] = mapped_column(Float, nullable=False)
        unit: Mapped[str] = mapped_column(String(50), default="")
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_slo_definitions_service_id", "service_id"),
        )

    class FailureModeTable(Base):
        """Failure mode entity."""

        __tablename__ = "failure_modes"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        entity_id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), nullable=False, index=True
        )
        entity_type: Mapped[str] = mapped_column(
            String(100), nullable=False, index=True
        )
        failure_mode: Mapped[str] = mapped_column(String(255), nullable=False)
        description: Mapped[str] = mapped_column(Text, default="")
        severity: Mapped[str] = mapped_column(String(50), default="medium", index=True)
        likelihood: Mapped[str] = mapped_column(String(50), default="low")
        mitigation: Mapped[str] = mapped_column(Text, default="")
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_failure_modes_entity", "entity_id", "entity_type"),
            Index("ix_failure_modes_severity", "severity"),
        )

    class RecoveryPatternTable(Base):
        """Recovery pattern entity."""

        __tablename__ = "recovery_patterns"

        id: Mapped[uuid.UUID] = mapped_column(
            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
        description: Mapped[str] = mapped_column(Text, default="")
        pattern_type: Mapped[str] = mapped_column(
            String(100), default="", index=True
        )
        steps: Mapped[list] = mapped_column(ARRAY(String), default=list)
        estimated_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
        created_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )
        metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

        __table_args__ = (
            Index("ix_recovery_patterns_pattern_type", "pattern_type"),
        )
