"""Tests for CLI --compare-repo and --drift-report options (Sprint 12)."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from cli import main


@pytest.fixture
def runner():
    return CliRunner()


INVENTORY_A_YAML = """\
version: "1.0"
repo:
  name: private-dsm
  type: dsm-hub

entities:
  - id: "sec/1.0"
    type: section
    path: DSM_1.0.md
    heading: "1.0 Introduction to the Methodology"
    level: 1
    stable: true

  - id: "sec/2.0"
    type: section
    path: DSM_1.0.md
    heading: "2.0 Sprint Boundary Checklist"
    level: 1
    stable: true

  - id: "sec/3.0"
    type: section
    path: DSM_1.0.md
    heading: "3.0 Internal Review Process"
    level: 1
    stable: true
"""

INVENTORY_B_YAML = """\
version: "1.0"
repo:
  name: public-dsm
  type: dsm-hub

entities:
  - id: "sec/1.0"
    type: section
    path: DSM_1.0.md
    heading: "1.0 Introduction to the Methodology"
    level: 1
    stable: true

  - id: "sec/2.0"
    type: section
    path: DSM_1.0.md
    heading: "2.0 Sprint Boundary Best Practices"
    level: 1
    stable: true

  - id: "sec/4.0"
    type: section
    path: DSM_1.0.md
    heading: "4.0 Community Contribution Guide"
    level: 1
    stable: true
"""


@pytest.fixture
def inventory_a(tmp_path):
    path = tmp_path / "inventory-a.yml"
    path.write_text(INVENTORY_A_YAML, encoding="utf-8")
    return path


@pytest.fixture
def inventory_b(tmp_path):
    path = tmp_path / "inventory-b.yml"
    path.write_text(INVENTORY_B_YAML, encoding="utf-8")
    return path


@pytest.fixture
def sample_md(tmp_path):
    """Minimal markdown file so the CLI has something to parse."""
    path = tmp_path / "doc.md"
    path.write_text("# Doc\n\n## 1 Section\n\nContent.\n", encoding="utf-8")
    return path


@pytest.fixture
def empty_config(tmp_path):
    path = tmp_path / ".dsm-graph-explorer.yml"
    path.write_text("{}\n", encoding="utf-8")
    return path


class TestCompareRepoOption:
    """Tests for --compare-repo CLI option."""

    def test_help_shows_compare_repo(self, runner):
        result = runner.invoke(main, ["--help"])
        assert "--compare-repo" in result.output

    def test_compare_repo_shows_mapping(
        self, runner, inventory_a, inventory_b, sample_md, empty_config
    ):
        result = runner.invoke(
            main,
            [
                str(sample_md.parent),
                "--config", str(empty_config),
                "--compare-repo", str(inventory_a), str(inventory_b),
            ],
        )
        assert result.exit_code == 0
        assert "IDENTICAL" in result.output
        assert "MODIFIED" in result.output

    def test_compare_repo_shows_added_removed(
        self, runner, inventory_a, inventory_b, sample_md, empty_config
    ):
        result = runner.invoke(
            main,
            [
                str(sample_md.parent),
                "--config", str(empty_config),
                "--compare-repo", str(inventory_a), str(inventory_b),
            ],
        )
        assert result.exit_code == 0
        assert "REMOVED" in result.output
        assert "ADDED" in result.output

    def test_compare_repo_shows_repo_names(
        self, runner, inventory_a, inventory_b, sample_md, empty_config
    ):
        result = runner.invoke(
            main,
            [
                str(sample_md.parent),
                "--config", str(empty_config),
                "--compare-repo", str(inventory_a), str(inventory_b),
            ],
        )
        assert result.exit_code == 0
        assert "private-dsm" in result.output
        assert "public-dsm" in result.output

    def test_compare_repo_shows_summary(
        self, runner, inventory_a, inventory_b, sample_md, empty_config
    ):
        result = runner.invoke(
            main,
            [
                str(sample_md.parent),
                "--config", str(empty_config),
                "--compare-repo", str(inventory_a), str(inventory_b),
            ],
        )
        assert result.exit_code == 0
        # Should show counts
        assert "identical" in result.output.lower() or "IDENTICAL" in result.output

    def test_compare_repo_missing_file_errors(self, runner, sample_md, empty_config):
        result = runner.invoke(
            main,
            [
                str(sample_md.parent),
                "--config", str(empty_config),
                "--compare-repo", "/nonexistent/a.yml", "/nonexistent/b.yml",
            ],
        )
        assert result.exit_code != 0


class TestDriftReportOption:
    """Tests for --drift-report CLI option."""

    def test_help_shows_drift_report(self, runner):
        result = runner.invoke(main, ["--help"])
        assert "--drift-report" in result.output

    def test_drift_report_filters_to_modified(
        self, runner, inventory_a, inventory_b, sample_md, empty_config
    ):
        result = runner.invoke(
            main,
            [
                str(sample_md.parent),
                "--config", str(empty_config),
                "--compare-repo", str(inventory_a), str(inventory_b),
                "--drift-report",
            ],
        )
        assert result.exit_code == 0
        assert "MODIFIED" in result.output
        # Should NOT show IDENTICAL in the drift report
        assert "IDENTICAL" not in result.output

    def test_drift_report_requires_compare_repo(
        self, runner, sample_md, empty_config
    ):
        result = runner.invoke(
            main,
            [
                str(sample_md.parent),
                "--config", str(empty_config),
                "--drift-report",
            ],
        )
        assert result.exit_code != 0
        assert "--compare-repo" in result.output

    def test_drift_report_no_drift_message(self, runner, sample_md, empty_config, tmp_path):
        """When both inventories are identical, drift report shows no drift."""
        inv = tmp_path / "same.yml"
        inv.write_text(INVENTORY_A_YAML, encoding="utf-8")

        inv2 = tmp_path / "same2.yml"
        inv2.write_text(INVENTORY_A_YAML, encoding="utf-8")

        result = runner.invoke(
            main,
            [
                str(sample_md.parent),
                "--config", str(empty_config),
                "--compare-repo", str(inv), str(inv2),
                "--drift-report",
            ],
        )
        assert result.exit_code == 0
        assert "no drift" in result.output.lower() or "0" in result.output