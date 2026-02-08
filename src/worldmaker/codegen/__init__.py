"""Code generation for microservice source repositories.

Each microservice gets a real code repository with handler, Dockerfile,
and dependency file per its language/framework — the basis for inside-out
risk discovery.
"""
from .manager import CodeRepoManager
from .templates import LANGUAGE_TEMPLATES

__all__ = ["CodeRepoManager", "LANGUAGE_TEMPLATES"]
