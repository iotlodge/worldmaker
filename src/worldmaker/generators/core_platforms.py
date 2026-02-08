"""Core management platforms that every enterprise has.

These 9 platforms represent the foundational operational backbone of an
enterprise.  They are bootstrapped at application startup and survive
ecosystem regeneration (layer="core").  The generator creates *additional*
platforms on top of these when ``generate_ecosystem`` is called.

Each platform is created with its capabilities and one implementing
service per capability.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


# ── Platform Definitions ─────────────────────────────────────────────────

CORE_PLATFORMS: list[dict[str, Any]] = [
    {
        "name": "Product Management",
        "description": "Governs product lifecycle from ideation through retirement",
        "category": "product_lifecycle",
        "owner": "product-management-team",
        "capabilities": [
            ("Product Onboarding", "integration"),
            ("Feature Planning", "analytics"),
            ("Feature Lifecycle", "integration"),
            ("Roadmap Management", "analytics"),
            ("Product Retirement", "integration"),
        ],
    },
    {
        "name": "Change Management",
        "description": "Controls change requests, approvals, and implementation across the enterprise",
        "category": "change_control",
        "owner": "change-management-team",
        "capabilities": [
            ("Change Request", "integration"),
            ("Change Approval", "integration"),
            ("Change Implementation", "integration"),
            ("Change Review", "analytics"),
            ("Emergency Change", "integration"),
        ],
    },
    {
        "name": "Incident Management",
        "description": "Detects, triages, and resolves production incidents",
        "category": "incident_response",
        "owner": "incident-management-team",
        "capabilities": [
            ("Incident Detection", "security"),
            ("Incident Triage", "analytics"),
            ("Incident Response", "integration"),
            ("Escalation", "messaging"),
            ("Post-Incident Review", "analytics"),
        ],
    },
    {
        "name": "Problem Management",
        "description": "Investigates root causes and eliminates recurring issues",
        "category": "problem_analysis",
        "owner": "problem-management-team",
        "capabilities": [
            ("Root Cause Analysis", "analytics"),
            ("Problem Investigation", "analytics"),
            ("Known Error Database", "storage"),
            ("Trend Analysis", "analytics"),
        ],
    },
    {
        "name": "Issues Management",
        "description": "Tracks, assigns, and resolves issues with SLA monitoring",
        "category": "issue_tracking",
        "owner": "issues-management-team",
        "capabilities": [
            ("Issue Tracking", "integration"),
            ("Issue Triage", "analytics"),
            ("Issue Assignment", "integration"),
            ("Issue Resolution", "integration"),
            ("SLA Monitoring", "analytics"),
        ],
    },
    {
        "name": "Risk Management",
        "description": "Assesses, mitigates, and monitors enterprise risk and compliance",
        "category": "risk_compliance",
        "owner": "risk-management-team",
        "capabilities": [
            ("Risk Assessment", "analytics"),
            ("Risk Mitigation", "integration"),
            ("Risk Monitoring", "analytics"),
            ("Compliance Tracking", "security"),
            ("Audit Trail", "storage"),
        ],
    },
    {
        "name": "Operations Management",
        "description": "Manages deployment, monitoring, scaling, and maintenance of production systems",
        "category": "operations",
        "owner": "operations-team",
        "capabilities": [
            ("Deployment", "integration"),
            ("Monitoring", "analytics"),
            ("Scaling", "compute"),
            ("Maintenance", "integration"),
            ("Capacity Planning", "analytics"),
        ],
    },
    {
        "name": "Business Continuity Management",
        "description": "Ensures organizational resilience through BIA, DR planning, and recovery execution",
        "category": "business_continuity",
        "owner": "business-continuity-team",
        "capabilities": [
            ("Business Impact Analysis", "analytics"),
            ("Disaster Recovery Planning", "integration"),
            ("DRP Testing", "integration"),
            ("Recovery Execution", "integration"),
            ("Continuity Monitoring", "analytics"),
        ],
    },
    {
        "name": "Security Management",
        "description": "Protects the enterprise through threat detection, vulnerability management, and access control",
        "category": "security_operations",
        "owner": "security-operations-team",
        "capabilities": [
            ("Threat Detection", "security"),
            ("Vulnerability Management", "security"),
            ("Access Control", "identity"),
            ("Security Incident Response", "security"),
            ("Compliance & Audit", "security"),
            ("Penetration Testing", "security"),
        ],
    },
]


def _slug(name: str) -> str:
    """Convert a human name to a service-style slug (e.g. 'Product Onboarding' -> 'ProductOnboardingService')."""
    cleaned = re.sub(r"[^a-zA-Z0-9 ]", "", name)
    return "".join(word.capitalize() for word in cleaned.split()) + "Service"


def bootstrap_core(store: Any) -> dict[str, Any]:
    """Create the 9 core management platforms with capabilities and services.

    This function is **idempotent** — if core platforms already exist in the
    store it returns immediately with ``{"skipped": True}``.

    Parameters
    ----------
    store : InMemoryStore
        The data store to populate.

    Returns
    -------
    dict
        Counts of created entities, or ``{"skipped": True}`` if already
        bootstrapped.
    """
    # Idempotency check: look for any platform with layer="core"
    existing = store.get_all("platform", limit=1, filters={"layer": "core"})
    if existing:
        logger.debug("Core platforms already bootstrapped — skipping")
        return {"skipped": True}

    now = datetime.utcnow().isoformat()
    platform_count = 0
    capability_count = 0
    service_count = 0

    for pdef in CORE_PLATFORMS:
        platform_id = str(uuid4())

        # ── Create Platform ──────────────────────────────────────────
        cap_ids: list[str] = []
        svc_ids: list[str] = []

        for cap_name, cap_type in pdef["capabilities"]:
            cap_id = str(uuid4())
            svc_id = str(uuid4())
            cap_ids.append(cap_id)
            svc_ids.append(svc_id)

            # Create Capability
            store.create("capability", {
                "id": cap_id,
                "platform_id": platform_id,
                "name": cap_name,
                "description": f"{cap_name} capability for {pdef['name']}",
                "capability_type": cap_type,
                "status": "active",
                "version": "1.0.0",
                "slo": {},
                "depends_on_capabilities": [],
                "layer": "core",
                "created_at": now,
                "updated_at": now,
                "metadata": {"core_platform": pdef["name"]},
            })
            capability_count += 1

            # Create Service implementing this capability
            store.create("service", {
                "id": svc_id,
                "name": _slug(cap_name),
                "description": f"Service implementing {cap_name} for {pdef['name']}",
                "capability_id": cap_id,
                "platform_id": platform_id,
                "owner": pdef["owner"],
                "status": "active",
                "service_type": "rest",
                "api_version": "v1",
                "microservice_ids": [],
                "layer": "core",
                "created_at": now,
                "updated_at": now,
                "metadata": {"core_platform": pdef["name"]},
            })
            service_count += 1

        # Now create the Platform with references
        store.create("platform", {
            "id": platform_id,
            "name": pdef["name"],
            "description": pdef["description"],
            "category": pdef["category"],
            "owner": pdef["owner"],
            "status": "active",
            "tech_stack": [],
            "sla_definition": {},
            "layer": "core",
            "created_at": now,
            "updated_at": now,
            "metadata": {
                "capability_count": len(cap_ids),
                "service_count": len(svc_ids),
                "capability_ids": cap_ids,
                "service_ids": svc_ids,
            },
        })
        platform_count += 1

    result = {
        "platforms": platform_count,
        "capabilities": capability_count,
        "services": service_count,
    }
    logger.info("Core platforms bootstrapped: %s", result)
    return result
