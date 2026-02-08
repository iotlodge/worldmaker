"""Tests for microservice code repository generation.

Verifies:
- Scaffold creates correct files per language
- Manifests return correct file listings
- Batch scaffolding works
- Scaffolding is idempotent
- Repo deletion works
- Clear all removes everything
"""
from __future__ import annotations

import os
import shutil
import tempfile

import pytest

from worldmaker.codegen.manager import CodeRepoManager
from worldmaker.codegen.templates import (
    LANGUAGE_TEMPLATES,
    generate_handler,
    generate_deps,
    generate_dockerfile,
    generate_readme,
)


@pytest.fixture
def tmp_repo_path(tmp_path):
    """Provide a temporary directory for code repos."""
    repo_dir = tmp_path / "repos"
    repo_dir.mkdir()
    return str(repo_dir)


@pytest.fixture
def code_mgr(tmp_repo_path):
    """Provide a CodeRepoManager with temp path."""
    return CodeRepoManager(base_path=tmp_repo_path)


def _make_microservice(
    name: str = "order-processor",
    language: str = "python",
    framework: str = "FastAPI",
    service_id: str = "svc-001",
) -> dict:
    return {
        "id": f"ms-{name}",
        "name": name,
        "language": language,
        "framework": framework,
        "service_id": service_id,
        "capability": "Order Processing",
        "container_image": f"registry/{name}:latest",
        "endpoints": ["/orders", "/orders/{id}"],
    }


class TestScaffold:
    """Tests for code scaffolding."""

    def test_scaffold_creates_files(self, code_mgr: CodeRepoManager):
        ms = _make_microservice()
        manifest = code_mgr.scaffold(ms)

        assert manifest["microservice_name"] == "order-processor"
        assert manifest["language"] == "python"
        assert len(manifest["files"]) == 4  # handler, deps, Dockerfile, README

        file_names = [f["name"] for f in manifest["files"]]
        assert "handler.py" in file_names
        assert "requirements.txt" in file_names
        assert "Dockerfile" in file_names
        assert "README.md" in file_names

    def test_scaffold_python_handler(self, code_mgr: CodeRepoManager):
        ms = _make_microservice(language="python")
        manifest = code_mgr.scaffold(ms)

        content = code_mgr.get_file_content("order-processor", "handler.py")
        assert content is not None
        assert "order-processor" in content
        assert "handle_event" in content
        assert "__metadata__" in content

    def test_scaffold_go_handler(self, code_mgr: CodeRepoManager):
        ms = _make_microservice(name="go-svc", language="go", framework="Gin")
        manifest = code_mgr.scaffold(ms)

        file_names = [f["name"] for f in manifest["files"]]
        assert "main.go" in file_names
        assert "go.mod" in file_names

        content = code_mgr.get_file_content("go-svc", "main.go")
        assert content is not None
        assert "gin" in content.lower() or "Gin" in content

    def test_scaffold_java_handler(self, code_mgr: CodeRepoManager):
        ms = _make_microservice(name="java-svc", language="java", framework="Spring Boot")
        manifest = code_mgr.scaffold(ms)

        file_names = [f["name"] for f in manifest["files"]]
        assert "Handler.java" in file_names
        assert "pom.xml" in file_names

    def test_scaffold_typescript_handler(self, code_mgr: CodeRepoManager):
        ms = _make_microservice(name="ts-svc", language="typescript", framework="NestJS")
        manifest = code_mgr.scaffold(ms)

        file_names = [f["name"] for f in manifest["files"]]
        assert "handler.ts" in file_names
        assert "package.json" in file_names

    def test_scaffold_rust_handler(self, code_mgr: CodeRepoManager):
        ms = _make_microservice(name="rust-svc", language="rust", framework="Actix")
        manifest = code_mgr.scaffold(ms)

        file_names = [f["name"] for f in manifest["files"]]
        assert "main.rs" in file_names
        assert "Cargo.toml" in file_names

    def test_scaffold_kotlin_handler(self, code_mgr: CodeRepoManager):
        ms = _make_microservice(name="kt-svc", language="kotlin", framework="Ktor")
        manifest = code_mgr.scaffold(ms)

        file_names = [f["name"] for f in manifest["files"]]
        assert "Application.kt" in file_names
        assert "build.gradle.kts" in file_names

    def test_scaffold_correct_language_templates(self):
        """Verify all 6 language templates are registered."""
        assert "python" in LANGUAGE_TEMPLATES
        assert "go" in LANGUAGE_TEMPLATES
        assert "java" in LANGUAGE_TEMPLATES
        assert "typescript" in LANGUAGE_TEMPLATES
        assert "rust" in LANGUAGE_TEMPLATES
        assert "kotlin" in LANGUAGE_TEMPLATES

    def test_scaffold_idempotent(self, code_mgr: CodeRepoManager):
        """Re-scaffolding doesn't error."""
        ms = _make_microservice()
        m1 = code_mgr.scaffold(ms)
        m2 = code_mgr.scaffold(ms)
        assert len(m1["files"]) == len(m2["files"])

    def test_dockerfile_has_correct_base(self, code_mgr: CodeRepoManager):
        ms = _make_microservice(language="python")
        code_mgr.scaffold(ms)
        content = code_mgr.get_file_content("order-processor", "Dockerfile")
        assert content is not None
        assert "python:" in content.lower()

    def test_readme_contains_ms_name(self, code_mgr: CodeRepoManager):
        ms = _make_microservice()
        code_mgr.scaffold(ms)
        content = code_mgr.get_file_content("order-processor", "README.md")
        assert content is not None
        assert "order-processor" in content


class TestBatchScaffold:
    """Tests for bulk code generation."""

    def test_scaffold_batch(self, code_mgr: CodeRepoManager):
        microservices = [
            _make_microservice(name="svc-a", language="python"),
            _make_microservice(name="svc-b", language="go"),
            _make_microservice(name="svc-c", language="java"),
        ]
        result = code_mgr.scaffold_batch(microservices)
        assert result["total"] == 3
        assert result["scaffolded"] == 3
        assert result["errors"] == 0

    def test_scaffold_batch_empty(self, code_mgr: CodeRepoManager):
        result = code_mgr.scaffold_batch([])
        assert result["total"] == 0
        assert result["scaffolded"] == 0


class TestManifestAndQuery:
    """Tests for manifest retrieval and querying."""

    def test_manifest_returns_files(self, code_mgr: CodeRepoManager):
        ms = _make_microservice()
        code_mgr.scaffold(ms)
        manifest = code_mgr.get_manifest("order-processor")
        assert manifest is not None
        assert len(manifest["files"]) == 4

    def test_manifest_nonexistent(self, code_mgr: CodeRepoManager):
        manifest = code_mgr.get_manifest("nonexistent-service")
        assert manifest is None

    def test_get_file_content(self, code_mgr: CodeRepoManager):
        ms = _make_microservice()
        code_mgr.scaffold(ms)
        content = code_mgr.get_file_content("order-processor", "handler.py")
        assert content is not None
        assert len(content) > 0

    def test_get_file_content_nonexistent(self, code_mgr: CodeRepoManager):
        content = code_mgr.get_file_content("order-processor", "nofile.py")
        assert content is None

    def test_list_repos(self, code_mgr: CodeRepoManager):
        code_mgr.scaffold(_make_microservice(name="svc-a"))
        code_mgr.scaffold(_make_microservice(name="svc-b"))
        repos = code_mgr.list_repos()
        assert "svc-a" in repos
        assert "svc-b" in repos


class TestCleanup:
    """Tests for repo deletion."""

    def test_delete_repo(self, code_mgr: CodeRepoManager):
        ms = _make_microservice()
        code_mgr.scaffold(ms)
        assert code_mgr.delete_repo("order-processor") is True
        assert code_mgr.get_manifest("order-processor") is None

    def test_delete_nonexistent(self, code_mgr: CodeRepoManager):
        assert code_mgr.delete_repo("ghost") is False

    def test_clear_all(self, code_mgr: CodeRepoManager):
        code_mgr.scaffold(_make_microservice(name="svc-a"))
        code_mgr.scaffold(_make_microservice(name="svc-b"))
        deleted = code_mgr.clear_all()
        assert deleted == 2
        assert len(code_mgr.list_repos()) == 0


class TestTemplateGenerators:
    """Tests for template generation functions directly."""

    def test_generate_handler_python(self):
        ms = _make_microservice(language="python")
        content = generate_handler(ms)
        assert "FastAPI" in content
        assert "order-processor" in content

    def test_generate_handler_unknown_falls_back(self):
        ms = _make_microservice(language="cobol")
        content = generate_handler(ms)
        # Falls back to python
        assert "FastAPI" in content

    def test_generate_deps_python(self):
        ms = _make_microservice(language="python")
        content = generate_deps(ms)
        assert "fastapi" in content.lower()

    def test_generate_dockerfile(self):
        ms = _make_microservice(language="python")
        content = generate_dockerfile(ms)
        assert "FROM" in content
        assert "EXPOSE" in content

    def test_generate_readme(self):
        ms = _make_microservice()
        content = generate_readme(ms)
        assert "order-processor" in content
        assert "python" in content.lower()
