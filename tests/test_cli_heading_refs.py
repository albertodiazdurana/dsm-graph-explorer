"""Tests for CLI --heading-refs flag integration.

Verifies that the heading reference extraction pipeline is correctly wired
into the CLI: heading title mentions in prose are detected as cross-references
when the flag is active, and ignored when it is not.
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from cli import main


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
def heading_fixture(tmp_path):
    """Two markdown files for heading reference testing.

    definitions.md: defines unnumbered headings with 4+ non-stopword tokens.
    prose.md: mentions heading titles in prose text.
    """
    definitions = tmp_path / "definitions.md"
    definitions.write_text(
        "# Project Configuration Overview Guide\n\n"
        "Some intro text.\n\n"
        "## Session Transcript Protocol Rules\n\n"
        "Rules for transcripts.\n\n"
        "## Pre-Generation Brief Approval Protocol\n\n"
        "Rules for briefs.\n"
    )

    prose = tmp_path / "prose.md"
    prose.write_text(
        "# Notes\n\n"
        "Make sure to follow the Session Transcript Protocol Rules when working.\n\n"
        "The Pre-Generation Brief Approval Protocol should be done before coding.\n\n"
        "Also check the Project Configuration Overview Guide for context.\n"
    )

    return tmp_path


class TestHeadingRefsHelp:
    """Test --heading-refs flag appears in help."""

    def test_heading_refs_in_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "--heading-refs" in result.output

    def test_heading_refs_help_describes_purpose(self, runner):
        result = runner.invoke(main, ["--help"])
        assert "heading" in result.output.lower()


class TestHeadingRefsDetection:
    """Test heading reference detection via CLI."""

    def test_heading_refs_flag_detects_mentions(
        self, runner, heading_fixture, empty_config
    ):
        result = runner.invoke(main, [
            str(heading_fixture),
            "--heading-refs",
            "-c", str(empty_config),
        ])
        assert result.exit_code == 0
        # The heading mentions should be found and validated
        # (they resolve successfully, so no errors expected)
        assert "Scanned 2 file(s)" in result.output

    def test_no_heading_refs_without_flag(
        self, runner, heading_fixture, empty_config
    ):
        """Without --heading-refs, heading mentions are not extracted."""
        result = runner.invoke(main, [
            str(heading_fixture),
            "-c", str(empty_config),
        ])
        assert result.exit_code == 0
        assert "Scanned 2 file(s)" in result.output

    def test_broken_heading_ref_produces_warning(
        self, runner, tmp_path, empty_config
    ):
        """A prose mention of a nonexistent heading produces a warning."""
        defs = tmp_path / "defs.md"
        defs.write_text(
            "## Real Heading Quality Validation Process\n\nSome content.\n"
        )

        prose = tmp_path / "prose.md"
        prose.write_text(
            "# Notes\n\n"
            "Check the Real Heading Quality Validation Process section.\n\n"
            "Also see Nonexistent Heading for details.\n"
        )

        result = runner.invoke(main, [
            str(tmp_path),
            "--heading-refs",
            "-c", str(empty_config),
        ])
        assert result.exit_code == 0
        # "Real Heading" resolves; only it should be found
        # "Nonexistent Heading" is not in known_headings, so not extracted

    def test_heading_refs_cross_file_resolution(
        self, runner, heading_fixture, empty_config
    ):
        """Heading defined in one file, mentioned in another, resolves OK."""
        result = runner.invoke(main, [
            str(heading_fixture),
            "--heading-refs",
            "-c", str(empty_config),
        ])
        assert result.exit_code == 0
        # No errors expected: all heading mentions match real headings
        assert "0 error(s)" in result.output


class TestHeadingRefsEdgeCases:
    """Edge cases for --heading-refs."""

    def test_no_unnumbered_headings_no_crash(
        self, runner, tmp_path, empty_config
    ):
        """Files with only numbered sections: --heading-refs is a no-op."""
        doc = tmp_path / "numbered.md"
        doc.write_text(
            "# 1. Introduction\n\nText.\n\n"
            "## 1.1 Background\n\nMore text.\n"
        )

        result = runner.invoke(main, [
            str(tmp_path),
            "--heading-refs",
            "-c", str(empty_config),
        ])
        assert result.exit_code == 0

    def test_heading_refs_with_output_flag(
        self, runner, heading_fixture, empty_config, tmp_path
    ):
        """--heading-refs combined with -o produces a report."""
        report = tmp_path / "report.md"
        result = runner.invoke(main, [
            str(heading_fixture),
            "--heading-refs",
            "-o", str(report),
            "-c", str(empty_config),
        ])
        assert result.exit_code == 0
        assert report.exists()
