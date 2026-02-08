"""Attribute registry endpoints — CRUD, gap analysis, and stamping.

IMPORTANT: Static sub-paths (/attributes/gaps, /attributes/stamp) MUST
be declared BEFORE the parameterised /{attr_id} route, otherwise FastAPI
will match "gaps" / "stamp" as an attr_id and return 404.
"""
from __future__ import annotations

try:
    from fastapi import APIRouter, Depends, Path, Query, HTTPException, Body
    from typing import Any, Optional
    from datetime import datetime

    from worldmaker.api.deps import get_memory_store
    from worldmaker.db.memory import InMemoryStore

    router = APIRouter()

    # ── List (no path param — safe anywhere) ─────────────────────────────

    @router.get("/attributes")
    async def list_attributes(
        tier: Optional[str] = Query(None, description="Filter by tier: core, lifecycle, function"),
        category: Optional[str] = Query(None, description="Filter by category"),
        applies_to: Optional[str] = Query(None, description="Filter by entity type"),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """List all attribute definitions with optional filtering."""
        filters: dict[str, Any] = {}
        if tier:
            filters["tier"] = tier
        if category:
            filters["category"] = category
        filt = filters if filters else None

        attrs = store.get_all("attribute_definition", limit=limit, offset=offset, filters=filt)

        # Post-filter by applies_to (can't do equality match on list)
        if applies_to:
            attrs = [a for a in attrs if applies_to in a.get("applies_to", [])]

        total = len(attrs) if (applies_to or filt) else store.count("attribute_definition", filters=filt)
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "attribute_definitions": attrs,
        }

    # ── Gap Analysis (static sub-path — MUST come before /{attr_id}) ──

    @router.get("/attributes/gaps")
    async def gap_analysis(
        entity_type: Optional[str] = Query(
            None, description="Filter gaps by entity type (service, microservice, platform)"
        ),
        tier: Optional[str] = Query(None, description="Filter by attribute tier"),
        limit: int = Query(100, ge=1, le=1000),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Detect entities missing required attributes.

        This IS the risk signal.  Absence of a required attribute means
        the entity hasn't been assessed by the responsible core function.
        """
        # Get required attribute definitions
        all_attrs = store.get_all("attribute_definition", limit=1000)
        required_attrs = [
            a for a in all_attrs
            if a.get("required") or (tier and a.get("tier") == tier)
        ]
        if tier:
            required_attrs = [a for a in required_attrs if a.get("tier") == tier]

        # Build lookup: entity_type -> list of required attribute names
        type_required: dict[str, list[dict[str, Any]]] = {}
        for attr in required_attrs:
            for et in attr.get("applies_to", []):
                type_required.setdefault(et, []).append(attr)

        # Scan entity types
        target_types = [entity_type] if entity_type else list(type_required.keys())
        gaps: list[dict[str, Any]] = []
        total_entities = 0

        for et in target_types:
            req_attrs = type_required.get(et, [])
            if not req_attrs:
                continue

            entities = store.get_all(et, limit=10000)
            total_entities += len(entities)

            for entity in entities:
                metadata = entity.get("metadata", {})
                missing = []

                for attr in req_attrs:
                    attr_name = attr["name"]
                    # Check if attribute value exists in metadata
                    if attr_name not in metadata:
                        missing.append({
                            "name": attr_name,
                            "display_name": attr.get("display_name", attr_name),
                            "tier": attr.get("tier", "unknown"),
                            "required": attr.get("required", False),
                        })

                if missing:
                    # Risk score: weighted by tier
                    tier_weights = {"core": 10, "lifecycle": 5, "function": 2}
                    risk_score = sum(
                        tier_weights.get(m["tier"], 1)
                        for m in missing
                        if m["required"]
                    )

                    gaps.append({
                        "entity_id": str(entity.get("id", "")),
                        "entity_type": et,
                        "entity_name": entity.get("name", "unknown"),
                        "missing_attributes": missing,
                        "gap_count": len(missing),
                        "risk_score": risk_score,
                    })

        # Sort by risk_score descending
        gaps.sort(key=lambda g: g["risk_score"], reverse=True)
        gaps = gaps[:limit]

        return {
            "total_entities": total_entities,
            "entities_with_gaps": len(gaps),
            "total_gaps": sum(g["gap_count"] for g in gaps),
            "gaps": gaps,
        }

    # ── Attribute Stamping (static sub-path — MUST come before /{attr_id}) ──

    @router.post("/attributes/stamp")
    async def stamp_attribute(
        data: dict[str, Any] = Body(
            ...,
            examples=[{
                "entity_type": "service",
                "entity_id": "some-uuid",
                "attribute_name": "risk_classification",
                "value": "high",
                "stamped_by": "Security Management",
            }],
        ),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Stamp an attribute value onto an entity.

        Core functions call this to enrich entities with lifecycle data.
        Updates the entity's metadata dict and creates an audit entry.
        """
        entity_type = data.get("entity_type")
        entity_id = data.get("entity_id")
        attr_name = data.get("attribute_name")
        value = data.get("value")
        stamped_by = data.get("stamped_by", "system")

        if not all([entity_type, entity_id, attr_name]):
            raise HTTPException(400, "entity_type, entity_id, and attribute_name are required")

        # Verify entity exists
        entity = store.get(entity_type, entity_id)
        if not entity:
            raise HTTPException(404, f"{entity_type} {entity_id} not found")

        # Update metadata with attribute value
        metadata = entity.get("metadata", {})
        old_value = metadata.get(attr_name)
        metadata[attr_name] = value
        metadata[f"{attr_name}_stamped_by"] = stamped_by
        metadata[f"{attr_name}_stamped_at"] = datetime.utcnow().isoformat()

        store.update(entity_type, entity_id, {"metadata": metadata})

        return {
            "status": "stamped",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "attribute_name": attr_name,
            "value": value,
            "previous_value": old_value,
            "stamped_by": stamped_by,
        }

    # ── Create (POST /attributes — no path param conflict) ───────────────

    @router.post("/attributes", status_code=201)
    async def create_attribute(
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Create a new attribute definition (typically FUNCTION tier)."""
        return store.create("attribute_definition", data)

    # ── Parameterised routes (/{attr_id} — MUST come AFTER static paths) ──

    @router.get("/attributes/{attr_id}")
    async def get_attribute(
        attr_id: str = Path(..., description="Attribute definition ID"),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get a single attribute definition."""
        attr = store.get("attribute_definition", attr_id)
        if not attr:
            raise HTTPException(404, f"Attribute definition {attr_id} not found")
        return attr

    @router.put("/attributes/{attr_id}")
    async def update_attribute(
        attr_id: str = Path(...),
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Update an attribute definition."""
        result = store.update("attribute_definition", attr_id, data)
        if not result:
            raise HTTPException(404, f"Attribute definition {attr_id} not found")
        return result

    @router.delete("/attributes/{attr_id}")
    async def delete_attribute(
        attr_id: str = Path(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Delete an attribute definition.

        Only FUNCTION tier attributes can be deleted.  CORE and LIFECYCLE
        are protected.
        """
        attr = store.get("attribute_definition", attr_id)
        if not attr:
            raise HTTPException(404, f"Attribute definition {attr_id} not found")

        tier = attr.get("tier", "")
        if tier in ("core", "lifecycle"):
            raise HTTPException(
                403,
                f"Cannot delete {tier}-tier attribute '{attr.get('name', '')}'. "
                "Only function-tier attributes can be deleted.",
            )

        store.delete("attribute_definition", attr_id)
        return {"deleted": True, "id": attr_id}

    # ── Entity Attributes View ───────────────────────────────────────────

    @router.get("/entities/{entity_type}/{entity_id}/attributes")
    async def get_entity_attributes(
        entity_type: str = Path(..., description="Entity type"),
        entity_id: str = Path(..., description="Entity ID"),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get all attribute values for an entity.

        Merges attribute definitions with actual values from the entity's
        metadata to give a complete attribute profile.
        """
        entity = store.get(entity_type, entity_id)
        if not entity:
            raise HTTPException(404, f"{entity_type} {entity_id} not found")

        # Get definitions applicable to this entity type
        all_attrs = store.get_all("attribute_definition", limit=1000)
        applicable = [a for a in all_attrs if entity_type in a.get("applies_to", [])]

        metadata = entity.get("metadata", {})
        attributes: list[dict[str, Any]] = []

        for attr_def in applicable:
            attr_name = attr_def["name"]
            has_value = attr_name in metadata
            attributes.append({
                "name": attr_name,
                "display_name": attr_def.get("display_name", attr_name),
                "tier": attr_def.get("tier"),
                "data_type": attr_def.get("data_type"),
                "required": attr_def.get("required", False),
                "value": metadata.get(attr_name) if has_value else None,
                "has_value": has_value,
                "stamped_by": metadata.get(f"{attr_name}_stamped_by"),
                "stamped_at": metadata.get(f"{attr_name}_stamped_at"),
                "category": attr_def.get("category", "general"),
            })

        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity_name": entity.get("name", "unknown"),
            "total_applicable": len(applicable),
            "total_populated": sum(1 for a in attributes if a["has_value"]),
            "attributes": attributes,
        }

except ImportError:
    router = None
