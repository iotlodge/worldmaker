"""Code repository manager for microservice source code.

Scaffolds, lists, and manages per-microservice code repositories
stored on the local filesystem.
"""
from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Any

from .templates import (
    LANGUAGE_TEMPLATES,
    generate_handler,
    generate_deps,
    generate_dockerfile,
    generate_readme,
)

logger = logging.getLogger(__name__)


class CodeRepoManager:
    """Manages microservice code repositories on disk.

    Parameters
    ----------
    base_path : str
        Root directory for all microservice repos.  Can be relative
        (resolved from cwd) or absolute.
    """

    def __init__(self, base_path: str = "repos"):
        self._base = Path(base_path).resolve()
        self._base.mkdir(parents=True, exist_ok=True)
        logger.debug("CodeRepoManager base path: %s", self._base)

    @property
    def base_path(self) -> Path:
        return self._base

    # ── Scaffold ─────────────────────────────────────────────────────────

    def scaffold(self, microservice: dict[str, Any]) -> dict[str, Any]:
        """Generate code files for a single microservice.

        Returns a manifest dict with file listing and paths.
        """
        name = microservice.get("name", "unknown")
        lang = microservice.get("language", "python")
        tmpl = LANGUAGE_TEMPLATES.get(lang, LANGUAGE_TEMPLATES["python"])

        repo_dir = self._base / name
        repo_dir.mkdir(parents=True, exist_ok=True)

        files_written: list[dict[str, Any]] = []

        # Handler
        handler_content = generate_handler(microservice)
        handler_path = repo_dir / tmpl["handler_file"]
        handler_path.write_text(handler_content, encoding="utf-8")
        files_written.append({
            "name": tmpl["handler_file"],
            "size": len(handler_content),
            "path": str(handler_path),
        })

        # Dependency file
        deps_content = generate_deps(microservice)
        dep_path = repo_dir / tmpl["dep_file"]
        dep_path.write_text(deps_content, encoding="utf-8")
        files_written.append({
            "name": tmpl["dep_file"],
            "size": len(deps_content),
            "path": str(dep_path),
        })

        # Dockerfile
        dockerfile_content = generate_dockerfile(microservice)
        dockerfile_path = repo_dir / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content, encoding="utf-8")
        files_written.append({
            "name": "Dockerfile",
            "size": len(dockerfile_content),
            "path": str(dockerfile_path),
        })

        # README
        readme_content = generate_readme(microservice)
        readme_path = repo_dir / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")
        files_written.append({
            "name": "README.md",
            "size": len(readme_content),
            "path": str(readme_path),
        })

        manifest = {
            "microservice_id": microservice.get("id", ""),
            "microservice_name": name,
            "language": lang,
            "framework": microservice.get("framework", ""),
            "files": files_written,
            "repo_path": str(repo_dir),
        }

        logger.debug("Scaffolded %s (%s/%s): %d files",
                      name, lang, microservice.get("framework", ""), len(files_written))
        return manifest

    def scaffold_batch(self, microservices: list[dict[str, Any]]) -> dict[str, Any]:
        """Bulk-scaffold code repos for multiple microservices.

        Returns summary counts.
        """
        manifests = []
        errors = []

        for ms in microservices:
            try:
                manifest = self.scaffold(ms)
                manifests.append(manifest)
            except Exception as exc:
                logger.error("Failed to scaffold %s: %s", ms.get("name", "?"), exc)
                errors.append({"name": ms.get("name", "?"), "error": str(exc)})

        result = {
            "total": len(microservices),
            "scaffolded": len(manifests),
            "errors": len(errors),
            "error_details": errors if errors else None,
        }
        logger.info("Batch scaffold complete: %s", result)
        return result

    # ── Query ────────────────────────────────────────────────────────────

    def get_manifest(self, ms_name: str) -> dict[str, Any] | None:
        """Get file manifest for a microservice repo."""
        repo_dir = self._base / ms_name
        if not repo_dir.is_dir():
            return None

        files = []
        for f in sorted(repo_dir.iterdir()):
            if f.is_file():
                files.append({
                    "name": f.name,
                    "size": f.stat().st_size,
                    "path": str(f),
                })

        return {
            "microservice_name": ms_name,
            "files": files,
            "repo_path": str(repo_dir),
        }

    def get_file_content(self, ms_name: str, filename: str) -> str | None:
        """Read a specific file from a microservice repo."""
        file_path = self._base / ms_name / filename
        if not file_path.is_file():
            return None
        # Prevent path traversal
        if not file_path.resolve().is_relative_to(self._base):
            return None
        return file_path.read_text(encoding="utf-8")

    def list_repos(self) -> list[str]:
        """List all microservice repo names."""
        if not self._base.is_dir():
            return []
        return sorted(d.name for d in self._base.iterdir() if d.is_dir())

    # ── Cleanup ──────────────────────────────────────────────────────────

    def delete_repo(self, ms_name: str) -> bool:
        """Remove a microservice's code directory."""
        repo_dir = self._base / ms_name
        if not repo_dir.is_dir():
            return False
        shutil.rmtree(repo_dir)
        logger.info("Deleted code repo: %s", ms_name)
        return True

    def clear_all(self) -> int:
        """Remove all microservice repos.  Returns count deleted."""
        repos = self.list_repos()
        for name in repos:
            shutil.rmtree(self._base / name, ignore_errors=True)
        logger.info("Cleared %d code repos", len(repos))
        return len(repos)
