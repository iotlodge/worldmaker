"""Initial schema — 25 tables for WorldMaker entity model.

Revision ID: 0001
Revises: None
Create Date: 2026-02-08
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Tier 0: No foreign keys ───────────────────────────────────────────

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("version", sa.String(50), server_default="1.0.0"),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_status", "products", ["status"])
    op.create_index("ix_products_name_status", "products", ["name", "status"])
    op.create_index("ix_products_created_at", "products", ["created_at"])

    op.create_table(
        "platforms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("platform_type", sa.String(100), server_default=""),
        sa.Column("owner", sa.String(255), server_default=""),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_platforms_name", "platforms", ["name"])
    op.create_index("ix_platforms_platform_type", "platforms", ["platform_type"])
    op.create_index("ix_platforms_platform_type_owner", "platforms", ["platform_type", "owner"])

    op.create_table(
        "business_processes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("owner", sa.String(255), server_default=""),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_business_processes_name", "business_processes", ["name"])
    op.create_index("ix_business_processes_status", "business_processes", ["status"])
    op.create_index("ix_business_processes_owner_status", "business_processes", ["owner", "status"])

    op.create_table(
        "environments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("environment_type", sa.String(100), server_default=""),
        sa.Column("region", sa.String(100), server_default=""),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_environments_name", "environments", ["name"])
    op.create_index("ix_environments_environment_type", "environments", ["environment_type"])
    op.create_index("ix_environments_environment_type_region", "environments", ["environment_type", "region"])

    op.create_table(
        "data_stores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("data_store_type", sa.String(100), server_default=""),
        sa.Column("owner", sa.String(255), server_default=""),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_data_stores_name", "data_stores", ["name"])
    op.create_index("ix_data_stores_data_store_type", "data_stores", ["data_store_type"])
    op.create_index("ix_data_stores_data_store_type_owner", "data_stores", ["data_store_type", "owner"])

    op.create_table(
        "dependencies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_type", sa.String(100), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_type", sa.String(100), nullable=False),
        sa.Column("dependency_type", sa.String(100), server_default=""),
        sa.Column("strength", sa.String(50), server_default="medium"),
        sa.Column("is_circular", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_dependencies_source_id", "dependencies", ["source_id"])
    op.create_index("ix_dependencies_source_type_col", "dependencies", ["source_type"])
    op.create_index("ix_dependencies_target_id", "dependencies", ["target_id"])
    op.create_index("ix_dependencies_target_type_col", "dependencies", ["target_type"])
    op.create_index("ix_dependencies_dependency_type", "dependencies", ["dependency_type"])
    op.create_index("ix_dependencies_is_circular", "dependencies", ["is_circular"])
    op.create_index("ix_dependencies_source_target", "dependencies", ["source_id", "target_id"])
    op.create_index("ix_dependencies_source_type", "dependencies", ["source_id", "source_type"])
    op.create_index("ix_dependencies_target_type", "dependencies", ["target_id", "target_type"])

    op.create_table(
        "impact_chains",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("chain_path", postgresql.ARRAY(sa.String()), server_default="{}"),
        sa.Column("severity", sa.String(50), server_default="medium"),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_impact_chains_name", "impact_chains", ["name"])
    op.create_index("ix_impact_chains_severity", "impact_chains", ["severity"])

    op.create_table(
        "recovery_patterns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("pattern_type", sa.String(100), server_default=""),
        sa.Column("steps", postgresql.ARRAY(sa.String()), server_default="{}"),
        sa.Column("estimated_time_minutes", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_recovery_patterns_name", "recovery_patterns", ["name"])
    op.create_index("ix_recovery_patterns_pattern_type", "recovery_patterns", ["pattern_type"])

    # Audit / tracking tables (polymorphic — no FK constraints)

    op.create_table(
        "lifecycle_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("old_state", postgresql.JSONB(), server_default="{}"),
        sa.Column("new_state", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_lifecycle_events_entity_id", "lifecycle_events", ["entity_id"])
    op.create_index("ix_lifecycle_events_entity_type", "lifecycle_events", ["entity_type"])
    op.create_index("ix_lifecycle_events_entity", "lifecycle_events", ["entity_id", "entity_type"])
    op.create_index("ix_lifecycle_events_created_at", "lifecycle_events", ["created_at"])

    op.create_table(
        "change_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("change_type", sa.String(100), nullable=False),
        sa.Column("changed_fields", postgresql.JSONB(), server_default="{}"),
        sa.Column("changed_by", sa.String(255), server_default=""),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_change_events_entity_id", "change_events", ["entity_id"])
    op.create_index("ix_change_events_entity_type", "change_events", ["entity_type"])
    op.create_index("ix_change_events_entity", "change_events", ["entity_id", "entity_type"])
    op.create_index("ix_change_events_change_type", "change_events", ["change_type"])
    op.create_index("ix_change_events_created_at", "change_events", ["created_at"])

    op.create_table(
        "version_tracking",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("version_hash", sa.String(64), server_default=""),
        sa.Column("content", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_version_tracking_entity_id", "version_tracking", ["entity_id"])
    op.create_index("ix_version_tracking_entity_type", "version_tracking", ["entity_type"])
    op.create_index(
        "ix_version_tracking_entity_version",
        "version_tracking",
        ["entity_id", "entity_type", "version_number"],
        unique=True,
    )

    op.create_table(
        "criticality_ratings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("justification", sa.Text(), server_default=""),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_criticality_ratings_entity_id", "criticality_ratings", ["entity_id"])
    op.create_index("ix_criticality_ratings_entity_type", "criticality_ratings", ["entity_type"])
    op.create_index("ix_criticality_ratings_entity", "criticality_ratings", ["entity_id", "entity_type"])
    op.create_index("ix_criticality_ratings_rating", "criticality_ratings", ["rating"])

    op.create_table(
        "failure_modes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("failure_mode", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("severity", sa.String(50), server_default="medium"),
        sa.Column("likelihood", sa.String(50), server_default="low"),
        sa.Column("mitigation", sa.Text(), server_default=""),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_failure_modes_entity_id", "failure_modes", ["entity_id"])
    op.create_index("ix_failure_modes_entity_type", "failure_modes", ["entity_type"])
    op.create_index("ix_failure_modes_entity", "failure_modes", ["entity_id", "entity_type"])
    op.create_index("ix_failure_modes_severity", "failure_modes", ["severity"])

    # ── Tier 1: FK → Tier 0 ──────────────────────────────────────────────

    op.create_table(
        "features",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("enabled", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_features_product_id", "features", ["product_id"])
    op.create_index("ix_features_name", "features", ["name"])
    op.create_index("ix_features_enabled", "features", ["enabled"])
    op.create_index("ix_features_product_id_name", "features", ["product_id", "name"])

    op.create_table(
        "capabilities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("platform_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("platforms.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("capability_type", sa.String(100), server_default=""),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_capabilities_platform_id", "capabilities", ["platform_id"])
    op.create_index("ix_capabilities_name", "capabilities", ["name"])
    op.create_index("ix_capabilities_platform_id_name", "capabilities", ["platform_id", "name"])

    op.create_table(
        "data_store_instances",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("data_store_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("data_stores.id"), nullable=False),
        sa.Column("environment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("environments.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_data_store_instances_data_store_id", "data_store_instances", ["data_store_id"])
    op.create_index("ix_data_store_instances_environment_id", "data_store_instances", ["environment_id"])
    op.create_index("ix_data_store_instances_status", "data_store_instances", ["status"])
    op.create_index(
        "ix_data_store_instances_unique",
        "data_store_instances",
        ["data_store_id", "environment_id"],
        unique=True,
    )

    # ── Tier 2: FK → Tier 1 ──────────────────────────────────────────────

    op.create_table(
        "business_process_features",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("business_process_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("business_processes.id"), nullable=False),
        sa.Column("feature_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("features.id"), nullable=False),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_business_process_features_bp_id", "business_process_features", ["business_process_id"])
    op.create_index("ix_business_process_features_feature_id", "business_process_features", ["feature_id"])
    op.create_index(
        "ix_business_process_features_unique",
        "business_process_features",
        ["business_process_id", "feature_id"],
        unique=True,
    )

    op.create_table(
        "services",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("capability_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("capabilities.id"), nullable=False),
        sa.Column("platform_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("platforms.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("service_type", sa.String(100), server_default=""),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("owner", sa.String(255), server_default=""),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_services_capability_id", "services", ["capability_id"])
    op.create_index("ix_services_platform_id", "services", ["platform_id"])
    op.create_index("ix_services_name", "services", ["name"])
    op.create_index("ix_services_service_type", "services", ["service_type"])
    op.create_index("ix_services_status", "services", ["status"])
    op.create_index("ix_services_platform_id_status", "services", ["platform_id", "status"])

    # ── Tier 3: FK → services ─────────────────────────────────────────────

    op.create_table(
        "microservices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("version", sa.String(50), server_default="1.0.0"),
        sa.Column("owner", sa.String(255), server_default=""),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_microservices_service_id", "microservices", ["service_id"])
    op.create_index("ix_microservices_name", "microservices", ["name"])
    op.create_index("ix_microservices_status", "microservices", ["status"])
    op.create_index("ix_microservices_service_id_status", "microservices", ["service_id", "status"])

    op.create_table(
        "flows",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("start_service_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("end_service_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("flow_type", sa.String(100), server_default=""),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_flows_start_service_id", "flows", ["start_service_id"])
    op.create_index("ix_flows_end_service_id", "flows", ["end_service_id"])
    op.create_index("ix_flows_status", "flows", ["status"])

    op.create_table(
        "interfaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("provider_service_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("consumer_service_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("interface_type", sa.String(100), server_default=""),
        sa.Column("protocol", sa.String(100), server_default=""),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_interfaces_provider_service_id", "interfaces", ["provider_service_id"])
    op.create_index("ix_interfaces_consumer_service_id", "interfaces", ["consumer_service_id"])

    op.create_table(
        "event_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("event_schema", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_event_types_service_id", "event_types", ["service_id"])
    op.create_index("ix_event_types_name", "event_types", ["name"])
    op.create_index("ix_event_types_service_id_name", "event_types", ["service_id", "name"])

    op.create_table(
        "slo_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("slo_type", sa.String(100), server_default=""),
        sa.Column("target_value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(50), server_default=""),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_slo_definitions_service_id", "slo_definitions", ["service_id"])

    # ── Tier 4: FK → microservices/flows ──────────────────────────────────

    op.create_table(
        "deployments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("microservice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("microservices.id"), nullable=False),
        sa.Column("environment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("environments.id"), nullable=False),
        sa.Column("version", sa.String(50), server_default=""),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("deployed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_deployments_microservice_id", "deployments", ["microservice_id"])
    op.create_index("ix_deployments_environment_id", "deployments", ["environment_id"])
    op.create_index("ix_deployments_status", "deployments", ["status"])
    op.create_index("ix_deployments_microservice_environment", "deployments", ["microservice_id", "environment_id"])

    op.create_table(
        "flow_steps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("flow_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("flows.id"), nullable=False),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("ix_flow_steps_flow_id", "flow_steps", ["flow_id"])
    op.create_index("ix_flow_steps_service_id", "flow_steps", ["service_id"])
    op.create_index("ix_flow_steps_flow_id_order", "flow_steps", ["flow_id", "step_order"])


def downgrade() -> None:
    # Drop in reverse FK-dependency order (Tier 4 → 0)

    # Tier 4
    op.drop_table("flow_steps")
    op.drop_table("deployments")

    # Tier 3
    op.drop_table("slo_definitions")
    op.drop_table("event_types")
    op.drop_table("interfaces")
    op.drop_table("flows")
    op.drop_table("microservices")

    # Tier 2
    op.drop_table("services")
    op.drop_table("business_process_features")

    # Tier 1
    op.drop_table("data_store_instances")
    op.drop_table("capabilities")
    op.drop_table("features")

    # Tier 0 (polymorphic / no FK)
    op.drop_table("failure_modes")
    op.drop_table("criticality_ratings")
    op.drop_table("version_tracking")
    op.drop_table("change_events")
    op.drop_table("lifecycle_events")
    op.drop_table("recovery_patterns")
    op.drop_table("impact_chains")
    op.drop_table("dependencies")
    op.drop_table("data_stores")
    op.drop_table("environments")
    op.drop_table("business_processes")
    op.drop_table("platforms")
    op.drop_table("products")
