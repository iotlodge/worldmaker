"""PostgreSQL persistence layer for WorldMaker."""
from __future__ import annotations

__all__ = [
    "PostgresEngine",
    "Base",
    "PostgresRepository",
    "ServiceRepository",
    "DependencyRepository",
]

try:
    from .engine import PostgresEngine
    from .tables import Base
    from .repository import PostgresRepository, ServiceRepository, DependencyRepository
except ImportError:
    # SQLAlchemy may not be installed during development
    pass
