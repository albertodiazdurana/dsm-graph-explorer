"""Tests for CLI --semantic flag integration (Phase 6.3).

Verifies that the semantic validation pipeline is correctly wired into the CLI,
including summary output, drift warnings, insufficient context, and markdown
report generation.
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from cli import main
from semantic.similarity import SKLEARN_AVAILABLE

pytestmark = pytest.mark.skipif(
    not SKLEARN_AVAILABLE, reason="scikit-learn not installed"
)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def empty_config(tmp_path):
    """Empty config file to prevent repo-level auto-discovery."""
    cfg = tmp_path / ".dsm-graph-explorer.yml"
    cfg.write_text("")
    return cfg


@pytest.fixture
def semantic_fixture(tmp_path):
    """Two markdown files for semantic testing.

    definitions.md: section definitions with prose content.
    refs.md: cross-references with controlled surrounding context.

    This separation ensures context_before/after for each ref comes from
    the ref file, not the target section's body.

    Expected results:
    - Section 2.1 ref: matching (data quality context → data quality section)
    - Section 3.1 ref: drifted (blog context → database schema section)
    - Section 5.1 ref: insufficient (target title "Z" has < 3 tokens)
    """
    definitions = tmp_path / "definitions.md"
    definitions.write_text(
        "## 2.1 Data Quality Assessment\n"
        "\n"
        "Validate assumptions about data completeness and accuracy.\n"
        "Implement automated checks for missing values, outlier detection,\n"
        "and consistency across data sources. Document all quality metrics\n"
        "in the assessment report with statistical summaries.\n"
        "\n"
        "## 3.1 Database Schema\n"
        "\n"
        "Define table structures for user accounts, transactions,\n"
        "and audit logs. Normalize to third normal form. Create\n"
        "indexes on frequently queried columns for performance.\n"
        "\n"
        "## 5.1 Z\n"
    )

    refs = tmp_path / "refs.md"
    refs.write_text(
        "# 1 Cross References\n"
        "\n"
        "This document validates data quality and accuracy metrics.\n"
        "Data completeness checks are described in Section 2.1 above.\n"
        "Missing values and outlier detection are key quality measures.\n"
        "\n"
        "The blog content delivery process handles publication workflow.\n"
        "Blog post metadata formatting is covered in Section 3.1 below.\n"
        "Blog drafts require editorial review before final publication.\n"
        "\n"
        "Section 5.1 noted.\n"
    )
    return tmp_path


class TestSemanticFlagAccepted:
    """--semantic flag should be accepted and not cause errors."""

    def test_semantic_flag_runs_without_error(self, runner, semantic_fixture, empty_config):
        result = runner.invoke(main, [
            str(semantic_fixture), "--semantic",
            "--config", str(empty_config),
        ])
        assert result.exit_code == 0


class TestSemanticSummaryOutput:
    """When --semantic is used, summary line should include semantic counts."""

    def test_summary_contains_semantic_counts(self, runner, semantic_fixture, empty_config):
        result = runner.invoke(main, [
            str(semantic_fixture), "--semantic",
            "--config", str(empty_config),
        ])
        assert result.exit_code == 0
        assert "Semantic:" in result.output
        assert "drift warning" in result.output
        assert "insufficient context" in result.output


class TestDriftWarningDisplayed:
    """Drifted cross-references should appear in output."""

    def test_drift_warning_in_output(self, runner, semantic_fixture, empty_config):
        result = runner.invoke(main, [
            str(semantic_fixture), "--semantic",
            "--config", str(empty_config),
        ])
        assert result.exit_code == 0
        # The ref about "blog content delivery" pointing to "Database Schema" should drift
        assert "Semantic Drift" in result.output or "3.1" in result.output


class TestInsufficientContextDisplayed:
    """References with too few tokens should be flagged."""

    def test_insufficient_context_in_output(self, runner, semantic_fixture, empty_config):
        result = runner.invoke(main, [
            str(semantic_fixture), "--semantic",
            "--config", str(empty_config),
        ])
        assert result.exit_code == 0
        # Section 5.1 "Z" has very little content, should be insufficient
        assert "Insufficient" in result.output or "5.1" in result.output


class TestWithoutSemanticFlag:
    """Without --semantic, no semantic output should appear."""

    def test_no_semantic_output_without_flag(self, runner, semantic_fixture, empty_config):
        result = runner.invoke(main, [
            str(semantic_fixture),
            "--config", str(empty_config),
        ])
        assert result.exit_code == 0
        assert "Semantic:" not in result.output
        assert "Semantic Drift" not in result.output


class TestSemanticWithMarkdownReport:
    """--semantic combined with --output should include semantic sections."""

    def test_markdown_report_contains_semantic_sections(
        self, runner, semantic_fixture, empty_config, tmp_path
    ):
        report_path = tmp_path / "report.md"
        result = runner.invoke(main, [
            str(semantic_fixture), "--semantic",
            "--output", str(report_path),
            "--config", str(empty_config),
        ])
        assert result.exit_code == 0
        assert report_path.exists()
        content = report_path.read_text(encoding="utf-8")
        # Report should contain at least one semantic section
        has_drift = "Semantic Drift Warnings" in content
        has_insufficient = "Insufficient Context" in content
        assert has_drift or has_insufficient
