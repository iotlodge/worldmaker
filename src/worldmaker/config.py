from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # PostgreSQL
    POSTGRES_URL: str = "postgresql+asyncpg://worldmaker:worldmaker@localhost:5432/worldmaker"

    # MongoDB
    MONGO_URL: str = "mongodb://localhost:27017"
    MONGO_DB: str = "worldmaker"

    # Neo4j
    NEO4J_URL: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "worldmaker"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    # Event Bus
    EVENT_BUS_BACKEND: Literal["memory", "kafka"] = "memory"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Generator
    GENERATOR_SEED: int = 42

    class Config:
        env_prefix = "WM_"
        case_sensitive = True


settings = Settings()
