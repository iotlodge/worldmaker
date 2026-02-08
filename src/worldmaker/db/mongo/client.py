"""Async MongoDB client via Motor."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

logger = logging.getLogger(__name__)

try:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

    HAS_MOTOR = True
except ImportError:
    HAS_MOTOR = False


class MongoClient:
    """Manages async MongoDB connections."""

    def __init__(self, mongo_url: str, database_name: str = "worldmaker"):
        self._mongo_url = mongo_url
        self._database_name = database_name
        self._client: Any = None  # AsyncIOMotorClient
        self._db: Any = None  # AsyncIOMotorDatabase

    async def initialize(self) -> None:
        """Initialize MongoDB connection and ensure indexes."""
        if not HAS_MOTOR:
            raise RuntimeError("motor package not installed")
        self._client = AsyncIOMotorClient(self._mongo_url)
        self._db = self._client[self._database_name]
        # Verify connection
        await self._client.admin.command("ping")
        logger.info(
            "MongoDB connected: %s/%s", self._mongo_url, self._database_name
        )
        await self._ensure_indexes()

    async def dispose(self) -> None:
        """Close MongoDB client connection."""
        if self._client:
            self._client.close()
            logger.info("MongoDB client closed")

    @property
    def db(self) -> Any:
        """Get the database instance."""
        if not self._db:
            raise RuntimeError("MongoDB not initialized")
        return self._db

    def collection(self, name: str) -> Any:
        """Get a collection by name."""
        return self.db[name]

    async def _ensure_indexes(self) -> None:
        """Create indexes for all collections."""
        # Audit logs
        audit = self.db["audit_logs"]
        await audit.create_index(
            [("entity_id", 1), ("entity_type", 1), ("timestamp", -1)]
        )
        await audit.create_index([("timestamp", -1)])
        await audit.create_index([("actor", 1), ("timestamp", -1)])

        # Service configs
        configs = self.db["service_configs"]
        await configs.create_index([("service_id", 1), ("environment", 1)])
        await configs.create_index([("created_at", -1)])

        # Flow execution traces
        traces = self.db["flow_execution_traces"]
        await traces.create_index([("flow_id", 1), ("start_time", -1)])
        await traces.create_index([("execution_id", 1)], unique=True)
        await traces.create_index([("status", 1), ("end_time", 1)])

        # Dependency snapshots
        snapshots = self.db["dependency_snapshots"]
        await snapshots.create_index([("timestamp", -1)])
        await snapshots.create_index([("snapshot_id", 1)], unique=True)

        # Event stream
        events = self.db["event_stream"]
        await events.create_index([("source_id", 1), ("timestamp", -1)])
        await events.create_index([("event_type", 1), ("timestamp", -1)])

        # Config change history
        history = self.db["config_change_history"]
        await history.create_index([("entity_id", 1), ("change_timestamp", -1)])

        logger.info("MongoDB indexes ensured")
