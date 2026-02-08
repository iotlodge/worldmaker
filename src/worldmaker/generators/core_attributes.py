"""Bootstrap core and lifecycle attribute definitions.

These attribute definitions are the data backbone of MTTD < 0:
- CORE attributes are required — their absence on an entity IS the risk signal.
- LIFECYCLE attributes are stamped by core management platforms during workflows.
- FUNCTION attributes are extensible examples that platform owners add at runtime.

All definitions are bootstrapped at app startup alongside core platforms.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


# ── Attribute Definitions ────────────────────────────────────────────────

CORE_ATTRIBUTES: list[dict[str, Any]] = [
    {
        "name": "risk_classification",
        "display_name": "Risk Classification",
        "tier": "core",
        "data_type": "enum",
        "description": "Overall risk classification level for the entity",
        "applies_to": ["service", "microservice", "platform"],
        "required": True,
        "enum_values": ["low", "medium", "high", "critical"],
        "category": "risk",
    },
    {
        "name": "data_sensitivity",
        "display_name": "Data Sensitivity",
        "tier": "core",
        "data_type": "enum",
        "description": "Classification of data handled by this entity",
        "applies_to": ["service", "microservice"],
        "required": True,
        "enum_values": ["public", "internal", "confidential", "restricted"],
        "category": "security",
    },
    {
        "name": "compliance_scope",
        "display_name": "Compliance Scope",
        "tier": "core",
        "data_type": "enum",
        "description": "Regulatory compliance frameworks applicable to this entity",
        "applies_to": ["service", "platform"],
        "required": True,
        "enum_values": ["sox", "pci", "hipaa", "gdpr", "none"],
        "category": "compliance",
    },
    {
        "name": "criticality_tier",
        "display_name": "Criticality Tier",
        "tier": "core",
        "data_type": "enum",
        "description": "Business criticality tier (tier1 = most critical)",
        "applies_to": ["service", "microservice", "platform"],
        "required": True,
        "enum_values": ["tier1", "tier2", "tier3", "tier4"],
        "category": "operations",
    },
    {
        "name": "blast_radius_weight",
        "display_name": "Blast Radius Weight",
        "tier": "core",
        "data_type": "number",
        "description": "Weighted impact score (0-100) used in blast radius calculations",
        "applies_to": ["service"],
        "required": True,
        "default_value": 50,
        "category": "risk",
    },
]

LIFECYCLE_ATTRIBUTES: list[dict[str, Any]] = [
    {
        "name": "change_risk_score",
        "display_name": "Change Risk Score",
        "tier": "lifecycle",
        "data_type": "number",
        "description": "Risk score (0-100) assigned by Change Management during change review",
        "applies_to": ["service", "microservice"],
        "owner_platform": "Change Management",
        "category": "risk",
    },
    {
        "name": "last_change_ticket_id",
        "display_name": "Last Change Ticket",
        "tier": "lifecycle",
        "data_type": "string",
        "description": "ID of the most recent change ticket affecting this entity",
        "applies_to": ["service", "microservice"],
        "owner_platform": "Change Management",
        "category": "change",
    },
    {
        "name": "threat_model_status",
        "display_name": "Threat Model Status",
        "tier": "lifecycle",
        "data_type": "enum",
        "description": "Current status of threat modeling for this entity",
        "applies_to": ["service", "microservice"],
        "enum_values": ["not_started", "in_progress", "complete", "expired"],
        "owner_platform": "Security Management",
        "category": "security",
    },
    {
        "name": "last_pentest_date",
        "display_name": "Last Penetration Test",
        "tier": "lifecycle",
        "data_type": "string",
        "description": "ISO date of the most recent penetration test",
        "applies_to": ["service", "platform"],
        "owner_platform": "Security Management",
        "category": "security",
    },
    {
        "name": "vulnerability_count",
        "display_name": "Vulnerability Count",
        "tier": "lifecycle",
        "data_type": "number",
        "description": "Number of known vulnerabilities (from Security Management scans)",
        "applies_to": ["microservice"],
        "owner_platform": "Security Management",
        "default_value": 0,
        "category": "security",
    },
    {
        "name": "incident_count_30d",
        "display_name": "Incidents (30d)",
        "tier": "lifecycle",
        "data_type": "number",
        "description": "Number of incidents in the last 30 days",
        "applies_to": ["service"],
        "owner_platform": "Incident Management",
        "default_value": 0,
        "category": "operations",
    },
    {
        "name": "mttr_hours",
        "display_name": "MTTR (hours)",
        "tier": "lifecycle",
        "data_type": "number",
        "description": "Mean time to repair in hours",
        "applies_to": ["service"],
        "owner_platform": "Incident Management",
        "category": "operations",
    },
    {
        "name": "last_incident_date",
        "display_name": "Last Incident",
        "tier": "lifecycle",
        "data_type": "string",
        "description": "ISO date of the most recent incident",
        "applies_to": ["service"],
        "owner_platform": "Incident Management",
        "category": "operations",
    },
    {
        "name": "rto_hours",
        "display_name": "RTO (hours)",
        "tier": "lifecycle",
        "data_type": "number",
        "description": "Recovery Time Objective in hours",
        "applies_to": ["service", "platform"],
        "owner_platform": "Business Continuity Management",
        "category": "continuity",
    },
    {
        "name": "rpo_hours",
        "display_name": "RPO (hours)",
        "tier": "lifecycle",
        "data_type": "number",
        "description": "Recovery Point Objective in hours",
        "applies_to": ["service", "platform"],
        "owner_platform": "Business Continuity Management",
        "category": "continuity",
    },
    {
        "name": "dr_plan_status",
        "display_name": "DR Plan Status",
        "tier": "lifecycle",
        "data_type": "enum",
        "description": "Disaster recovery plan status",
        "applies_to": ["service"],
        "enum_values": ["none", "draft", "tested", "current"],
        "owner_platform": "Business Continuity Management",
        "category": "continuity",
    },
    {
        "name": "sla_compliance_pct",
        "display_name": "SLA Compliance %",
        "tier": "lifecycle",
        "data_type": "number",
        "description": "SLA compliance percentage (0-100)",
        "applies_to": ["service"],
        "owner_platform": "Operations Management",
        "default_value": 100,
        "category": "operations",
    },
]

FUNCTION_ATTRIBUTES: list[dict[str, Any]] = [
    {
        "name": "product_retirement_date",
        "display_name": "Product Retirement Date",
        "tier": "function",
        "data_type": "string",
        "description": "Planned retirement date for the product (ISO date)",
        "applies_to": ["product", "feature"],
        "owner_platform": "Product Management",
        "category": "lifecycle",
    },
    {
        "name": "known_error_count",
        "display_name": "Known Errors",
        "tier": "function",
        "data_type": "number",
        "description": "Count of known errors tracked by Problem Management",
        "applies_to": ["service"],
        "owner_platform": "Problem Management",
        "default_value": 0,
        "category": "quality",
    },
    {
        "name": "open_issues_count",
        "display_name": "Open Issues",
        "tier": "function",
        "data_type": "number",
        "description": "Count of open issues assigned to this entity",
        "applies_to": ["service", "microservice"],
        "owner_platform": "Issues Management",
        "default_value": 0,
        "category": "quality",
    },
]

ALL_ATTRIBUTES = CORE_ATTRIBUTES + LIFECYCLE_ATTRIBUTES + FUNCTION_ATTRIBUTES


# ── Bootstrap Function ───────────────────────────────────────────────────

def bootstrap_core_attributes(store: Any) -> dict[str, Any]:
    """Create all attribute definitions in the store.

    This function is **idempotent** — if attribute definitions with
    ``layer="core"`` already exist, it returns immediately.

    Parameters
    ----------
    store : InMemoryStore
        The data store to populate.

    Returns
    -------
    dict
        Counts by tier, or ``{"skipped": True}``.
    """
    # Idempotency check
    existing = store.get_all("attribute_definition", limit=1, filters={"layer": "core"})
    if existing:
        logger.debug("Core attributes already bootstrapped — skipping")
        return {"skipped": True}

    now = datetime.utcnow().isoformat()
    counts: dict[str, int] = {"core": 0, "lifecycle": 0, "function": 0}

    for attr_def in ALL_ATTRIBUTES:
        store.create("attribute_definition", {
            "id": str(uuid4()),
            "name": attr_def["name"],
            "display_name": attr_def["display_name"],
            "tier": attr_def["tier"],
            "data_type": attr_def["data_type"],
            "description": attr_def["description"],
            "applies_to": attr_def.get("applies_to", []),
            "required": attr_def.get("required", False),
            "default_value": attr_def.get("default_value"),
            "enum_values": attr_def.get("enum_values", []),
            "owner_platform": attr_def.get("owner_platform"),
            "category": attr_def.get("category", "general"),
            "layer": "core",
            "created_at": now,
            "updated_at": now,
            "metadata": {},
        })
        counts[attr_def["tier"]] += 1

    result = {
        "attribute_definitions": sum(counts.values()),
        "by_tier": counts,
    }
    logger.info("Core attributes bootstrapped: %s", result)
    return result
