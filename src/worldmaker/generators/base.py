"""Base generator with seeded randomness for reproducible synthetic data."""
from __future__ import annotations
import random
import string
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, TypeVar
from uuid import UUID, uuid4

T = TypeVar("T")


class GeneratorConfig:
    """Configuration for ecosystem generation scale."""
    
    # Presets
    SMALL = "small"    # ~10 services
    MEDIUM = "medium"  # ~50 services
    LARGE = "large"    # ~200+ services
    
    PRESETS = {
        "small": {
            "products": (2, 4),
            "features_per_product": (2, 4),
            "platforms": (3, 5),
            "capabilities_per_platform": (1, 3),
            "services_per_capability": (1, 2),
            "microservices_per_service": (1, 2),
            "flows": (3, 6),
            "steps_per_flow": (2, 4),
            "dependency_density": 0.15,
            "circular_dep_probability": 0.05,
            "environments": 3,
            "data_stores": (2, 4),
        },
        "medium": {
            "products": (4, 8),
            "features_per_product": (3, 6),
            "platforms": (6, 12),
            "capabilities_per_platform": (2, 4),
            "services_per_capability": (2, 3),
            "microservices_per_service": (1, 3),
            "flows": (8, 15),
            "steps_per_flow": (3, 6),
            "dependency_density": 0.12,
            "circular_dep_probability": 0.08,
            "environments": 4,
            "data_stores": (4, 8),
        },
        "large": {
            "products": (8, 15),
            "features_per_product": (5, 10),
            "platforms": (12, 25),
            "capabilities_per_platform": (3, 6),
            "services_per_capability": (2, 4),
            "microservices_per_service": (2, 4),
            "flows": (15, 30),
            "steps_per_flow": (4, 8),
            "dependency_density": 0.08,
            "circular_dep_probability": 0.1,
            "environments": 4,
            "data_stores": (8, 15),
        },
    }
    
    def __init__(self, size: str = "small", custom: dict[str, Any] | None = None):
        preset = self.PRESETS.get(size, self.PRESETS["small"])
        self.config = {**preset, **(custom or {})}
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
    
    def range(self, key: str) -> tuple[int, int]:
        val = self.config.get(key, (1, 2))
        if isinstance(val, tuple):
            return val
        return (val, val)


class BaseGenerator:
    """Base class for all generators with seeded randomness."""
    
    def __init__(self, seed: int = 42, config: GeneratorConfig | None = None):
        self._seed = seed
        self._rng = random.Random(seed)
        self._config = config or GeneratorConfig("small")
        self._id_counter = 0
    
    def _uuid(self) -> str:
        """Generate a deterministic UUID-like string."""
        self._id_counter += 1
        # Use rng to create reproducible UUIDs
        return str(UUID(int=self._rng.getrandbits(128)))
    
    def _choice(self, items: list[T]) -> T:
        return self._rng.choice(items)
    
    def _choices(self, items: list[T], k: int) -> list[T]:
        return self._rng.choices(items, k=k)
    
    def _sample(self, items: list[T], k: int) -> list[T]:
        k = min(k, len(items))
        return self._rng.sample(items, k)
    
    def _randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)
    
    def _randfloat(self, a: float, b: float) -> float:
        return round(self._rng.uniform(a, b), 4)
    
    def _random_range(self, key: str) -> int:
        """Get a random value within a config range."""
        lo, hi = self._config.range(key)
        return self._randint(lo, hi)
    
    def _random_datetime(self, days_back: int = 365) -> str:
        """Generate a random datetime within the past N days."""
        delta = timedelta(days=self._rng.randint(0, days_back))
        dt = datetime.utcnow() - delta
        return dt.isoformat()
    
    def _probability(self, p: float) -> bool:
        """Return True with probability p."""
        return self._rng.random() < p
    
    def _base_entity(self) -> dict[str, Any]:
        """Create base entity fields."""
        return {
            "id": self._uuid(),
            "created_at": self._random_datetime(365),
            "updated_at": self._random_datetime(30),
            "metadata": {},
            "layer": "generated",
        }
