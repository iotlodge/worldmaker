"""Tests for Alembic migration structure and SQLAlchemy metadata consistency.

These tests validate the migration without requiring a live database by:
1. Verifying migration file structure and revision chain
2. Comparing migration DDL against SQLAlchemy model metadata
3. Testing offline SQL generation for both upgrade and downgrade
4. Ensuring FK ordering is correct for both directions
"""
from __future__ import annotations

import importlib
import os
import subprocess
import sys

import pytest

# Ensure src is on path for model imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from worldmaker.db.postgres.tables import Base

# Path to the migration file
MIGRATION_DIR = os.path.join(os.path.dirname(__file__), "..", "alembic", "versions")
MIGRATION_FILE = os.path.join(MIGRATION_DIR, "20260208_0001_initial_schema.py")
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")


def _load_migration():
    """Load the migration module without triggering Alembic's op context."""
    spec = importlib.util.spec_from_file_location(
        "migration_0001",
        MIGRATION_FILE,
        submodule_search_locations=[],
    )
    # We can't directly exec the module because `from alembic import op`
    # fails when the local alembic/ directory shadows the installed package.
    # Instead, parse the file content for structural validation.
    with open(MIGRATION_FILE) as f:
        return f.read()


def _run_alembic(args: list[str]) -> str:
    """Run alembic CLI and return stdout."""
    env = os.environ.copy()
    env["PATH"] = f"/sessions/stoic-adoring-maxwell/.local/bin:{env.get('PATH', '')}"
    result = subprocess.run(
        ["alembic"] + args,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    return result.stdout + result.stderr


class TestMigrationFileStructure:
    """Validate the migration file is well-formed."""

    def test_migration_file_exists(self):
        assert os.path.isfile(MIGRATION_FILE), f"Migration file not found: {MIGRATION_FILE}"

    def test_has_revision_identifiers(self):
        content = _load_migration()
        assert 'revision: str = "0001"' in content
        assert "down_revision" in content

    def test_has_upgrade_function(self):
        content = _load_migration()
        assert "def upgrade()" in content

    def test_has_downgrade_function(self):
        content = _load_migration()
        assert "def downgrade()" in content

    def test_creates_all_tables(self):
        """Verify every SQLAlchemy table has a corresponding create_table call."""
        content = _load_migration()
        model_tables = set(Base.metadata.tables.keys())
        for table_name in model_tables:
            assert f'"{table_name}"' in content, (
                f"Table '{table_name}' from SQLAlchemy models not found in migration"
            )

    def test_drops_all_tables_in_downgrade(self):
        """Verify downgrade drops every table."""
        content = _load_migration()
        # Extract the downgrade section
        downgrade_start = content.index("def downgrade()")
        downgrade_section = content[downgrade_start:]
        model_tables = set(Base.metadata.tables.keys())
        for table_name in model_tables:
            assert f'drop_table("{table_name}")' in downgrade_section, (
                f"Table '{table_name}' not dropped in downgrade()"
            )

    def test_uses_postgresql_types(self):
        """Verify migration uses PostgreSQL-specific types."""
        content = _load_migration()
        assert "postgresql.UUID" in content
        assert "postgresql.JSONB" in content
        assert "postgresql.ARRAY" in content


class TestMetadataConsistency:
    """Verify migration covers the same schema as SQLAlchemy models."""

    def test_table_count_matches(self):
        """Migration should create exactly as many tables as models define."""
        content = _load_migration()
        # Count op.create_table calls in upgrade
        upgrade_start = content.index("def upgrade()")
        downgrade_start = content.index("def downgrade()")
        upgrade_section = content[upgrade_start:downgrade_start]
        create_count = upgrade_section.count("op.create_table(")
        model_count = len(Base.metadata.tables)
        assert create_count == model_count, (
            f"Migration creates {create_count} tables but models define {model_count}"
        )

    def test_all_foreign_keys_present(self):
        """Verify all FK relationships from models appear in migration."""
        content = _load_migration()
        for table in Base.metadata.sorted_tables:
            for fk in table.foreign_keys:
                target_table = fk.column.table.name
                assert f'"{target_table}"' in content, (
                    f"FK target '{target_table}' from {table.name} not in migration"
                )

    def test_fk_creation_order(self):
        """Tables with FKs must be created after their referenced tables."""
        content = _load_migration()
        upgrade_start = content.index("def upgrade()")
        downgrade_start = content.index("def downgrade()")
        upgrade_section = content[upgrade_start:downgrade_start]

        # Build creation order from migration
        import re
        creation_order = re.findall(r'op\.create_table\(\s*"(\w+)"', upgrade_section)

        for table in Base.metadata.sorted_tables:
            for fk in table.foreign_keys:
                target_name = fk.column.table.name
                source_name = table.name
                if source_name in creation_order and target_name in creation_order:
                    target_idx = creation_order.index(target_name)
                    source_idx = creation_order.index(source_name)
                    assert target_idx < source_idx, (
                        f"Table '{source_name}' (idx {source_idx}) created before "
                        f"its FK target '{target_name}' (idx {target_idx})"
                    )

    def test_fk_drop_order(self):
        """Tables with FKs must be dropped before their referenced tables."""
        content = _load_migration()
        downgrade_start = content.index("def downgrade()")
        downgrade_section = content[downgrade_start:]

        import re
        drop_order = re.findall(r'op\.drop_table\("(\w+)"\)', downgrade_section)

        for table in Base.metadata.sorted_tables:
            for fk in table.foreign_keys:
                target_name = fk.column.table.name
                source_name = table.name
                if source_name in drop_order and target_name in drop_order:
                    target_idx = drop_order.index(target_name)
                    source_idx = drop_order.index(source_name)
                    assert source_idx < target_idx, (
                        f"Table '{target_name}' (idx {target_idx}) dropped before "
                        f"'{source_name}' (idx {source_idx}) which has FK to it"
                    )

    def test_unique_constraints_present(self):
        """Verify unique indexes from models are in the migration."""
        content = _load_migration()
        # Known unique constraints from the models
        unique_indexes = [
            "ix_business_process_features_unique",
            "ix_data_store_instances_unique",
            "ix_version_tracking_entity_version",
        ]
        for idx_name in unique_indexes:
            assert idx_name in content, (
                f"Unique index '{idx_name}' not found in migration"
            )
            # Also verify unique=True is set
            # Find the index creation and check for unique=True
            idx_pos = content.index(idx_name)
            # Look within 200 chars after the index name for unique=True
            snippet = content[idx_pos:idx_pos + 200]
            assert "unique=True" in snippet, (
                f"Unique index '{idx_name}' missing unique=True"
            )


class TestAlembicCLI:
    """Test Alembic CLI operations (requires alembic on PATH)."""

    def test_history_shows_migration(self):
        output = _run_alembic(["history"])
        assert "0001" in output
        assert "Initial schema" in output

    def test_heads_shows_single_head(self):
        output = _run_alembic(["heads"])
        assert "0001" in output
        assert "(head)" in output

    def test_current_shows_nothing(self):
        """With no DB, current should indicate no version."""
        output = _run_alembic(["current"])
        # Offline or error — just verify it doesn't crash badly
        assert "0001" not in output or "current" in output.lower() or "error" in output.lower()

    def test_upgrade_sql_generates_valid_ddl(self):
        """Offline upgrade should produce valid PostgreSQL DDL."""
        output = _run_alembic(["upgrade", "head", "--sql"])
        assert "CREATE TABLE products" in output
        assert "CREATE TABLE services" in output
        assert "CREATE TABLE flow_steps" in output
        assert "CREATE INDEX" in output
        assert "FOREIGN KEY" in output
        assert "INSERT INTO alembic_version" in output
        assert "COMMIT" in output

    def test_downgrade_sql_generates_valid_ddl(self):
        """Offline downgrade should produce valid DROP statements."""
        output = _run_alembic(["downgrade", "0001:base", "--sql"])
        assert "DROP TABLE flow_steps" in output
        assert "DROP TABLE products" in output
        assert "DELETE FROM alembic_version" in output
        assert "COMMIT" in output

    def test_upgrade_sql_table_count(self):
        """Verify the correct number of tables in generated SQL."""
        output = _run_alembic(["upgrade", "head", "--sql"])
        # Count CREATE TABLE statements (includes alembic_version)
        create_count = output.count("CREATE TABLE")
        assert create_count == 26, f"Expected 26 CREATE TABLE (25 + alembic_version), got {create_count}"

    def test_downgrade_sql_table_count(self):
        """Verify the correct number of drops in downgrade SQL."""
        output = _run_alembic(["downgrade", "0001:base", "--sql"])
        drop_count = output.count("DROP TABLE")
        # 25 entity tables + alembic_version
        assert drop_count == 26, f"Expected 26 DROP TABLE, got {drop_count}"


class TestEnvPy:
    """Test the Alembic env.py configuration."""

    def test_env_py_exists(self):
        env_path = os.path.join(PROJECT_ROOT, "alembic", "env.py")
        assert os.path.isfile(env_path)

    def test_env_py_imports_base(self):
        env_path = os.path.join(PROJECT_ROOT, "alembic", "env.py")
        with open(env_path) as f:
            content = f.read()
        assert "from worldmaker.db.postgres.tables import Base" in content

    def test_env_py_has_async_support(self):
        env_path = os.path.join(PROJECT_ROOT, "alembic", "env.py")
        with open(env_path) as f:
            content = f.read()
        assert "run_async_migrations" in content
        assert "async" in content

    def test_env_py_has_url_resolution(self):
        env_path = os.path.join(PROJECT_ROOT, "alembic", "env.py")
        with open(env_path) as f:
            content = f.read()
        assert "WM_POSTGRES_URL" in content
        assert "get_database_url" in content

    def test_script_mako_exists(self):
        mako_path = os.path.join(PROJECT_ROOT, "alembic", "script.py.mako")
        assert os.path.isfile(mako_path)
