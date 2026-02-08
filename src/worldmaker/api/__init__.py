"""API module for WorldMaker.

Export the app factory for easy access.
"""
from __future__ import annotations

try:
    from .app import create_app
    __all__ = ["create_app"]
except ImportError:
    __all__ = []
