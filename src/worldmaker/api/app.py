"""FastAPI application factory for WorldMaker API."""
from __future__ import annotations
import logging
import time
from contextlib import asynccontextmanager
from typing import Any

logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


def create_app(
    title: str = "WorldMaker API",
    version: str = "0.1.0",
    description: str = "Sustained Enterprise Digital Lifecycle Management",
) -> Any:
    """Create and configure the FastAPI application."""
    if not HAS_FASTAPI:
        raise RuntimeError("FastAPI not installed")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application startup and shutdown lifecycle."""
        start_time = time.monotonic()
        logger.info("WorldMaker API starting up...")

        # Eagerly initialize the in-memory store so first request isn't slow
        from .deps import get_memory_store, get_trace_engine
        from worldmaker.generators import bootstrap_core, bootstrap_core_attributes

        store = get_memory_store()
        engine = get_trace_engine()

        # Bootstrap core management platforms (idempotent)
        core_result = bootstrap_core(store)
        if not core_result.get("skipped"):
            logger.info("Core platforms bootstrapped: %s", core_result)
        else:
            logger.debug("Core platforms already present — skipped bootstrap")

        # Bootstrap core attribute definitions (idempotent)
        attr_result = bootstrap_core_attributes(store)
        if not attr_result.get("skipped"):
            logger.info("Core attributes bootstrapped: %s", attr_result)
        else:
            logger.debug("Core attributes already present — skipped bootstrap")

        entity_count = sum(len(v) for v in store._entities.values())
        logger.info(
            "Store initialized: %d entities, %d traces",
            entity_count,
            len(store._traces),
        )

        # Check optional backend connectivity (non-blocking, log-only)
        _check_optional_backends()

        elapsed = (time.monotonic() - start_time) * 1000
        logger.info("Startup complete in %.0fms", elapsed)

        yield  # ← app is running

        # Shutdown
        logger.info("WorldMaker API shutting down...")
        logger.info("Shutdown complete.")

    app = FastAPI(
        title=title,
        version=version,
        description=description,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    from .routes import ecosystem, services, flows, dependencies, generators, health, codegen, attributes
    if health.router:
        app.include_router(health.router, prefix="/api/v1", tags=["health"])
    if ecosystem.router:
        app.include_router(ecosystem.router, prefix="/api/v1", tags=["ecosystem"])
    if services.router:
        app.include_router(services.router, prefix="/api/v1",
                           tags=["products", "platforms", "capabilities",
                                 "services", "microservices"])
    if flows.router:
        app.include_router(flows.router, prefix="/api/v1",
                           tags=["flows", "traces"])
    if dependencies.router:
        app.include_router(dependencies.router, prefix="/api/v1",
                           tags=["dependencies"])
    if generators.router:
        app.include_router(generators.router, prefix="/api/v1",
                           tags=["generators"])
    if codegen.router:
        app.include_router(codegen.router, prefix="/api/v1",
                           tags=["codegen"])
    if attributes.router:
        app.include_router(attributes.router, prefix="/api/v1",
                           tags=["attributes"])

    return app


def _check_optional_backends() -> None:
    """Best-effort connectivity check for optional backends (non-fatal)."""
    from ..config import Settings

    settings = Settings()

    # PostgreSQL
    try:
        import asyncpg  # noqa: F401
        logger.info("PostgreSQL configured: %s", settings.POSTGRES_URL.split("@")[-1])
    except ImportError:
        logger.debug("asyncpg not installed — PostgreSQL unavailable")

    # MongoDB
    try:
        from ..db import _import_mongo
        mongo = _import_mongo()
        if mongo.get("HAS_MOTOR"):
            logger.info("MongoDB driver available")
        else:
            logger.debug("Motor not installed — MongoDB unavailable")
    except Exception:
        logger.debug("MongoDB check skipped")

    # Neo4j
    try:
        from ..db import _import_graph
        graph = _import_graph()
        if graph.get("HAS_NEO4J"):
            logger.info("Neo4j driver available")
        else:
            logger.debug("neo4j driver not installed — Neo4j unavailable")
    except Exception:
        logger.debug("Neo4j check skipped")


# Module-level instance for uvicorn import string (reload mode)
app = create_app() if HAS_FASTAPI else None
