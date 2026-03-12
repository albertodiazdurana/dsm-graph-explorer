"""Tests for CLI --inventory option (Sprint 11, Phase 11.2)."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from cli import main


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_DSM = FIXTURES_DIR / "sample_dsm.md"

VALID_INVENTORY_YAML = """\
version: "1.0"
repo:
  name: dsm-central-test
  type: dsm-hub

entities:
  - id: "DSM_1.0/section/2.3.7"
    type: section
    path: DSM_1.0.md
    heading: "2.3.7 Data Leakage Prevention"
    level: 3
    stable: true

  - id: "DSM_2.0/section/3.1"
    type: section
    path: DSM_2.0.md
    heading: "3.1 Sprint Planning"
    level: 2
    stable: true
"""


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def inventory_file(tmp_path):
    """Create a temporary inventory YAML file."""
    path = tmp_path / "dsm-entity-inventory.yml"
    path.write_text(VALID_INVENTORY_YAML, encoding="utf-8")
    return path


@pytest.fixture
def md_with_external_ref(tmp_path):
    """Create a markdown file with a reference to an external section."""
    path = tmp_path / "test.md"
    path.write_text(
        "# Test Document\n\n"
        "## 1 Introduction\n\n"
        "See Section 2.3.7 for data leakage details.\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def empty_config(tmp_path):
    """Create an empty config file to avoid repo's config."""
    path = tmp_path / ".dsm-graph-explorer.yml"
    path.write_text("{}\n", encoding="utf-8")
    return path


class TestCliInventoryOption:
    """Tests for --inventory CLI option."""

    def test_inventory_help_shown(self, runner):
        """--inventory appears in help output."""
        result = runner.invoke(main, ["--help"])
        assert "--inventory" in result.output

    def test_inventory_loads_successfully(
        self, runner, md_with_external_ref, inventory_file, empty_config
    ):
        """--inventory loads the inventory and reports entities."""
        result = runner.invoke(main, [
            str(md_with_external_ref.parent),
            "--inventory", str(inventory_file),
            "--config", str(empty_config),
        ])
        assert result.exit_code == 0
        assert "dsm-central-test" in result.output
        assert "2 entities" in result.output

    def test_inventory_resolves_external_ref(
        self, runner, md_with_external_ref, inventory_file, empty_config
    ):
        """External ref resolved via inventory shows in output."""
        result = runner.invoke(main, [
            str(md_with_external_ref.parent),
            "--inventory", str(inventory_file),
            "--config", str(empty_config),
        ])
        assert result.exit_code == 0
        assert "external" in result.output.lower() or "External" in result.output

    def test_inventory_nonexistent_file_errors(self, runner, tmp_path):
        """--inventory with nonexistent file exits with error."""
        result = runner.invoke(main, [
            str(tmp_path),
            "--inventory", str(tmp_path / "nonexistent.yml"),
        ])
        assert result.exit_code != 0

    def test_inventory_invalid_yaml_errors(self, runner, tmp_path):
        """--inventory with invalid YAML exits with error."""
        bad_file = tmp_path / "bad.yml"
        bad_file.write_text("{{invalid", encoding="utf-8")
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n", encoding="utf-8")
        result = runner.invoke(main, [
            str(tmp_path),
            "--inventory", str(bad_file),
        ])
        assert result.exit_code == 2

    def test_multiple_inventories(self, runner, md_with_external_ref, tmp_path, empty_config):
        """Multiple --inventory options load all inventories."""
        inv1 = tmp_path / "inv1.yml"
        inv1.write_text(
            'version: "1.0"\n'
            "repo:\n  name: repo-a\n  type: dsm-spoke\n"
            "entities: []\n",
            encoding="utf-8",
        )
        inv2 = tmp_path / "inv2.yml"
        inv2.write_text(VALID_INVENTORY_YAML, encoding="utf-8")

        result = runner.invoke(main, [
            str(md_with_external_ref.parent),
            "--inventory", str(inv1),
            "--inventory", str(inv2),
            "--config", str(empty_config),
        ])
        assert result.exit_code == 0
        assert "repo-a" in result.output
        assert "dsm-central-test" in result.output

    def test_no_inventory_backward_compatible(
        self, runner, md_with_external_ref, empty_config
    ):
        """Without --inventory, broken refs are still errors."""
        result = runner.invoke(main, [
            str(md_with_external_ref.parent),
            "--config", str(empty_config),
        ])
        assert result.exit_code == 0
        # Should have errors for unresolved section refs
        assert "error" in result.output.lower()


class TestCliExportInventory:
    """Tests for --export-inventory CLI option."""

    def test_export_inventory_help_shown(self, runner):
        """--export-inventory appears in help output."""
        result = runner.invoke(main, ["--help"])
        assert "--export-inventory" in result.output

    def test_export_inventory_creates_file(self, runner, tmp_path, empty_config):
        """--export-inventory creates a YAML file."""
        md_file = tmp_path / "test.md"
        md_file.write_text(
            "# Test\n\n## 1 Introduction\n\nSome text.\n\n## 2 Body\n\nMore text.\n",
            encoding="utf-8",
        )
        output = tmp_path / "inventory.yml"
        result = runner.invoke(main, [
            str(tmp_path),
            "--export-inventory", str(output),
            "--config", str(empty_config),
        ])
        assert result.exit_code == 0
        assert output.exists()
        assert "exported" in result.output.lower()

    def test_export_inventory_contains_entities(self, runner, tmp_path, empty_config):
        """Exported inventory contains entities from scanned files."""
        md_file = tmp_path / "guide.md"
        md_file.write_text(
            "# Guide\n\n## 1 Setup\n\nSetup info.\n\n## 2 Usage\n\nUsage info.\n",
            encoding="utf-8",
        )
        output = tmp_path / "inventory.yml"
        runner.invoke(main, [
            str(tmp_path),
            "--export-inventory", str(output),
            "--config", str(empty_config),
        ])

        # Load and verify
        from inventory.inventory_parser import load_inventory
        inv = load_inventory(output)
        assert len(inv.entities) >= 2

    def test_export_inventory_reports_count(self, runner, tmp_path, empty_config):
        """Output shows entity and file counts."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\n## 1 Intro\n\nText.\n", encoding="utf-8")
        output = tmp_path / "out.yml"
        result = runner.invoke(main, [
            str(tmp_path),
            "--export-inventory", str(output),
            "--config", str(empty_config),
        ])
        assert result.exit_code == 0
        assert "entities" in result.output
        assert "file(s)" in result.output

    def test_export_inventory_roundtrip(self, runner, tmp_path, empty_config):
        """Exported inventory can be loaded back with --inventory."""
        md_file = tmp_path / "source.md"
        md_file.write_text(
            "# Source\n\n## 1 Overview\n\nSome content.\n",
            encoding="utf-8",
        )
        inv_path = tmp_path / "dsm-entity-inventory.yml"

        # Export
        runner.invoke(main, [
            str(tmp_path),
            "--export-inventory", str(inv_path),
            "--config", str(empty_config),
        ])
        assert inv_path.exists()

        # Use it as --inventory for another file
        other_dir = tmp_path / "other"
        other_dir.mkdir()
        other_md = other_dir / "consumer.md"
        other_md.write_text(
            "# Consumer\n\nSee Section 1 for overview.\n",
            encoding="utf-8",
        )
        other_config = other_dir / ".dsm-graph-explorer.yml"
        other_config.write_text("{}\n", encoding="utf-8")

        result = runner.invoke(main, [
            str(other_dir),
            "--inventory", str(inv_path),
            "--config", str(other_config),
        ])
        assert result.exit_code == 0