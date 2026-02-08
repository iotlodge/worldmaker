"""Service management endpoints — full CRUD for Products, Platforms,
Capabilities, Services, and Microservices."""
from __future__ import annotations

try:
    from fastapi import APIRouter, Depends, Path, Query, HTTPException, Body
    from typing import Any, Optional

    from worldmaker.api.deps import get_memory_store
    from worldmaker.db.memory import InMemoryStore

    router = APIRouter()

    # ── Products ────────────────────────────────────────────────────────

    @router.get("/products")
    async def list_products(
        status: Optional[str] = Query(None, description="Filter by status"),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """List all products."""
        filters = {"status": status} if status else None
        products = store.get_all("product", limit=limit, offset=offset, filters=filters)
        total = store.count("product", filters=filters)
        return {"total": total, "limit": limit, "offset": offset, "products": products}

    @router.get("/products/{product_id}")
    async def get_product(
        product_id: str = Path(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get a single product by ID."""
        product = store.get("product", product_id)
        if not product:
            raise HTTPException(404, f"Product {product_id} not found")
        return product

    @router.post("/products", status_code=201)
    async def create_product(
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Create a new product."""
        return store.create("product", data)

    @router.put("/products/{product_id}")
    async def update_product(
        product_id: str = Path(...),
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Update a product."""
        result = store.update("product", product_id, data)
        if not result:
            raise HTTPException(404, f"Product {product_id} not found")
        return result

    @router.delete("/products/{product_id}")
    async def delete_product(
        product_id: str = Path(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Delete a product."""
        if not store.delete("product", product_id):
            raise HTTPException(404, f"Product {product_id} not found")
        return {"deleted": True, "id": product_id}

    # ── Features ──────────────────────────────────────────────────────

    @router.get("/features")
    async def list_features(
        product_id: Optional[str] = Query(None, description="Filter by product"),
        status: Optional[str] = Query(None, description="Filter by status"),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """List all features."""
        filters: dict[str, Any] = {}
        if product_id:
            filters["product_id"] = product_id
        if status:
            filters["status"] = status
        filt = filters if filters else None
        items = store.get_all("feature", limit=limit, offset=offset, filters=filt)
        return {"total": store.count("feature", filters=filt), "limit": limit,
                "offset": offset, "features": items}

    @router.get("/features/{feature_id}")
    async def get_feature(
        feature_id: str = Path(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get a single feature by ID."""
        item = store.get("feature", feature_id)
        if not item:
            raise HTTPException(404, f"Feature {feature_id} not found")
        return item

    @router.post("/features", status_code=201)
    async def create_feature(
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Create a new feature."""
        return store.create("feature", data)

    @router.put("/features/{feature_id}")
    async def update_feature(
        feature_id: str = Path(...),
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Update a feature."""
        result = store.update("feature", feature_id, data)
        if not result:
            raise HTTPException(404, f"Feature {feature_id} not found")
        return result

    @router.delete("/features/{feature_id}")
    async def delete_feature(
        feature_id: str = Path(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Delete a feature."""
        if not store.delete("feature", feature_id):
            raise HTTPException(404, f"Feature {feature_id} not found")
        return {"deleted": True, "id": feature_id}

    # ── Platforms ───────────────────────────────────────────────────────

    @router.get("/platforms")
    async def list_platforms(
        status: Optional[str] = Query(None),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """List all platforms."""
        filters = {"status": status} if status else None
        items = store.get_all("platform", limit=limit, offset=offset, filters=filters)
        return {"total": store.count("platform", filters=filters), "limit": limit,
                "offset": offset, "platforms": items}

    @router.get("/platforms/{platform_id}")
    async def get_platform(
        platform_id: str = Path(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get a platform with its capabilities."""
        item = store.get("platform", platform_id)
        if not item:
            raise HTTPException(404, f"Platform {platform_id} not found")
        caps = store.get_all("capability", limit=1000,
                              filters={"platform_id": platform_id})
        item["capabilities"] = caps
        return item

    @router.post("/platforms", status_code=201)
    async def create_platform(
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Create a new platform."""
        return store.create("platform", data)

    @router.put("/platforms/{platform_id}")
    async def update_platform(
        platform_id: str = Path(...),
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Update a platform."""
        result = store.update("platform", platform_id, data)
        if not result:
            raise HTTPException(404, f"Platform {platform_id} not found")
        return result

    @router.delete("/platforms/{platform_id}")
    async def delete_platform(
        platform_id: str = Path(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Delete a platform."""
        if not store.delete("platform", platform_id):
            raise HTTPException(404, f"Platform {platform_id} not found")
        return {"deleted": True, "id": platform_id}

    # ── Capabilities ───────────────────────────────────────────────────

    @router.get("/capabilities")
    async def list_capabilities(
        platform_id: Optional[str] = Query(None, description="Filter by platform"),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """List all capabilities."""
        filters = {"platform_id": platform_id} if platform_id else None
        items = store.get_all("capability", limit=limit, offset=offset, filters=filters)
        return {"total": store.count("capability", filters=filters), "limit": limit,
                "offset": offset, "capabilities": items}

    @router.post("/capabilities", status_code=201)
    async def create_capability(
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Create a new capability."""
        return store.create("capability", data)

    # ── Services ───────────────────────────────────────────────────────

    @router.get("/services")
    async def list_services(
        status: Optional[str] = Query(None, description="Filter by status"),
        platform_id: Optional[str] = Query(None, description="Filter by platform"),
        capability_id: Optional[str] = Query(None, description="Filter by capability"),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """List all services with optional filtering."""
        filters: dict[str, Any] = {}
        if status:
            filters["status"] = status
        if platform_id:
            filters["platform_id"] = platform_id
        if capability_id:
            filters["capability_id"] = capability_id
        filt = filters if filters else None

        services = store.get_all("service", limit=limit, offset=offset, filters=filt)
        total = store.count("service", filters=filt)
        return {"total": total, "limit": limit, "offset": offset, "services": services}

    @router.get("/services/{service_id}")
    async def get_service(
        service_id: str = Path(..., description="Service ID"),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get detailed information about a specific service."""
        service = store.get("service", service_id)
        if not service:
            raise HTTPException(404, f"Service {service_id} not found")
        ms = store.get_all("microservice", limit=1000,
                            filters={"service_id": service_id})
        service["microservices"] = ms
        return service

    @router.post("/services", status_code=201)
    async def create_service(
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Create a new service."""
        return store.create("service", data)

    @router.put("/services/{service_id}")
    async def update_service(
        service_id: str = Path(...),
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Update a service."""
        result = store.update("service", service_id, data)
        if not result:
            raise HTTPException(404, f"Service {service_id} not found")
        return result

    @router.delete("/services/{service_id}")
    async def delete_service(
        service_id: str = Path(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Delete a service."""
        if not store.delete("service", service_id):
            raise HTTPException(404, f"Service {service_id} not found")
        return {"deleted": True, "id": service_id}

    @router.get("/services/{service_id}/context")
    async def get_service_context(
        service_id: str = Path(..., description="Service ID"),
        include_dependencies: bool = Query(True),
        include_health: bool = Query(True),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get complete context for a service (agentic consumption).

        Includes dependencies, health, audit trail, microservices, and impact analysis.
        """
        service = store.get("service", service_id)
        if not service:
            raise HTTPException(404, f"Service {service_id} not found")

        result: dict[str, Any] = {"service_id": service_id, "entity": service}

        if include_dependencies:
            upstream = store.get_dependencies_of(service_id)
            downstream = store.get_dependents_of(service_id)
            blast = store.calculate_blast_radius(service_id)
            result["dependencies"] = {
                "upstream": upstream,
                "downstream": downstream,
                "blast_radius": blast["blast_radius"],
            }

        if include_health:
            slos = store.get_all("slo_definition", limit=1,
                                  filters={"entity_id": service_id})
            ratings = store.get_all("criticality_rating", limit=1,
                                     filters={"entity_id": service_id})
            result["health"] = {
                "service_status": service.get("status", "unknown"),
                "slo": slos[0] if slos else None,
                "criticality": ratings[0] if ratings else None,
            }

        ms = store.get_all("microservice", limit=1000,
                            filters={"service_id": service_id})
        result["microservices"] = ms

        audit = store.get_audit_log(entity_id=service_id, limit=20)
        result["audit"] = {"recent_changes": len(audit), "entries": audit}

        return result

    # ── Microservices ──────────────────────────────────────────────────

    @router.get("/microservices")
    async def list_microservices(
        service_id: Optional[str] = Query(None, description="Filter by service"),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """List all microservices."""
        filters = {"service_id": service_id} if service_id else None
        items = store.get_all("microservice", limit=limit, offset=offset, filters=filters)
        return {"total": store.count("microservice", filters=filters),
                "limit": limit, "offset": offset, "microservices": items}

    @router.post("/microservices", status_code=201)
    async def create_microservice(
        data: dict[str, Any] = Body(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Create a new microservice."""
        return store.create("microservice", data)

    @router.get("/microservices/{ms_id}")
    async def get_microservice(
        ms_id: str = Path(...),
        store: InMemoryStore = Depends(get_memory_store),
    ) -> dict[str, Any]:
        """Get a microservice by ID."""
        item = store.get("microservice", ms_id)
        if not item:
            raise HTTPException(404, f"Microservice {ms_id} not found")
        return item

except ImportError:
    router = None
