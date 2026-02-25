"""Tests for the CLI interface.

TDD approach: These tests are written BEFORE implementation.
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from cli import main


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_DSM = FIXTURES_DIR / "sample_dsm.md"


@pytest.fixture
def runner():
    return CliRunner()


# ===========================================================================
# Basic CLI Tests
# ===========================================================================


class TestCliHelp:
    """Test help output and basic CLI structure."""

    def test_help_flag(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "DSM" in result.output or "validate" in result.output.lower()

    def test_version_flag(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.2.0" in result.output


class TestCliFileInput:
    """Test CLI with file and directory arguments."""

    def test_single_file(self, runner):
        result = runner.invoke(main, [str(SAMPLE_DSM)])
        assert result.exit_code == 0
        # Should show validation results
        assert "Integrity Report" in result.output or "Error" in result.output

    def test_directory_input(self, runner, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# 1 Intro\nSee Section 99.\n")
        result = runner.invoke(main, [str(tmp_path)])
        assert result.exit_code == 0

    def test_nonexistent_path(self, runner):
        result = runner.invoke(main, ["/nonexistent/path"])
        assert result.exit_code != 0

    def test_multiple_files(self, runner, tmp_path):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text("# 1 Intro\nSee Section 2.1.\n")
        f2.write_text("## 2.1 Details\nContent here.\n")
        result = runner.invoke(main, [str(f1), str(f2)])
        assert result.exit_code == 0


# ===========================================================================
# Output Format Tests
# ===========================================================================


class TestCliOutput:
    """Test output format options."""

    def test_default_shows_rich_output(self, runner):
        result = runner.invoke(main, [str(SAMPLE_DSM)])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_output_flag_writes_file(self, runner, tmp_path):
        output = tmp_path / "report.md"
        result = runner.invoke(main, [str(SAMPLE_DSM), "--output", str(output)])
        assert result.exit_code == 0
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "Integrity Report" in content

    def test_output_creates_parent_dirs(self, runner, tmp_path):
        output = tmp_path / "deep" / "nested" / "report.md"
        result = runner.invoke(main, [str(SAMPLE_DSM), "--output", str(output)])
        assert result.exit_code == 0
        assert output.exists()


# ===========================================================================
# Exit Code Tests
# ===========================================================================


class TestCliExitCodes:
    """Test exit code behaviour."""

    def test_clean_file_exits_zero(self, runner, tmp_path):
        md = tmp_path / "clean.md"
        md.write_text("# 1 Intro\nSee Section 1.\n")
        result = runner.invoke(main, [str(md)])
        assert result.exit_code == 0

    def test_errors_without_strict_exits_zero(self, runner):
        result = runner.invoke(main, [str(SAMPLE_DSM)])
        assert result.exit_code == 0

    def test_errors_with_strict_exits_one(self, runner, tmp_path):
        empty_config = tmp_path / ".dsm-graph-explorer.yml"
        empty_config.write_text("")
        result = runner.invoke(main, [str(SAMPLE_DSM), "--strict", "--config", str(empty_config)])
        assert result.exit_code == 1

    def test_strict_clean_exits_zero(self, runner, tmp_path):
        md = tmp_path / "clean.md"
        md.write_text("# 1 Intro\nSee Section 1.\n")
        result = runner.invoke(main, [str(md), "--strict"])
        assert result.exit_code == 0


# ===========================================================================
# Validation Content Tests
# ===========================================================================


class TestCliValidation:
    """Test that CLI validation produces expected results."""

    def test_detects_broken_refs_in_fixture(self, runner):
        result = runner.invoke(main, [str(SAMPLE_DSM)])
        # Should report broken section refs
        assert "2.4.8" in result.output

    def test_cross_file_validation(self, runner, tmp_path):
        """Ref in file A to section in file B should be valid."""
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text("# 1 Intro\nSee Section 2.1 for details.\n")
        f2.write_text("## 2.1 Details\nContent.\n")
        result = runner.invoke(main, [str(tmp_path)])
        # Section 2.1 exists in b.md, so ref from a.md should be valid
        assert "2.1" not in result.output or "0 errors" in result.output.lower() or "Errors:" in result.output

    def test_version_check_flag(self, runner, tmp_path):
        f1 = tmp_path / "DSM_0.md"
        f2 = tmp_path / "README.md"
        f1.write_text("# DSM\n**Version:** 1.0.0\n")
        f2.write_text("# README\n**Version:** 2.0.0\n")
        result = runner.invoke(
            main,
            [str(f1), "--version-files", str(f1), "--version-files", str(f2)],
        )
        assert result.exit_code == 0
        assert "version" in result.output.lower() or "mismatch" in result.output.lower() or "Version" in result.output


# ===========================================================================
# Glob Pattern Tests
# ===========================================================================


class TestCliGlob:
    """Test glob pattern filtering for directories."""

    def test_default_finds_md_files(self, runner, tmp_path):
        (tmp_path / "test.md").write_text("# 1 Intro\n")
        (tmp_path / "test.txt").write_text("Not markdown.\n")
        result = runner.invoke(main, [str(tmp_path)])
        assert result.exit_code == 0

    def test_nested_directory_scan(self, runner, tmp_path):
        sub = tmp_path / "docs"
        sub.mkdir()
        (sub / "test.md").write_text("# 1 Intro\nSee Section 99.\n")
        result = runner.invoke(main, [str(tmp_path)])
        assert result.exit_code == 0

    def test_glob_filter(self, runner, tmp_path):
        (tmp_path / "include.md").write_text("# 1 Intro\n")
        (tmp_path / "exclude.md").write_text("# 2 Other\n")
        result = runner.invoke(main, [str(tmp_path), "--glob", "include*.md"])
        assert result.exit_code == 0


# ===========================================================================
# Graph Export & Stats Tests (Phase 7.3)
# ===========================================================================


class TestCliGraphExport:
    """Test --graph-export and --graph-stats CLI options."""

    def test_graph_export_creates_file(self, runner, tmp_path):
        md = tmp_path / "doc.md"
        md.write_text("# 1 Intro\nSee Section 2.1.\n## 2.1 Details\nContent.\n")
        output = tmp_path / "graph.graphml"
        result = runner.invoke(
            main, [str(md), "--graph-export", str(output)]
        )
        assert result.exit_code == 0
        assert output.exists()
        assert output.stat().st_size > 0

    def test_graph_export_mentions_path(self, runner, tmp_path):
        md = tmp_path / "doc.md"
        md.write_text("# 1 Intro\n")
        output = tmp_path / "graph.graphml"
        result = runner.invoke(
            main, [str(md), "--graph-export", str(output)]
        )
        assert result.exit_code == 0
        assert "graph.graphml" in result.output or "Graph exported" in result.output

    def test_graph_stats_shows_summary(self, runner, tmp_path):
        md = tmp_path / "doc.md"
        md.write_text("# 1 Intro\nSee Section 2.1.\n## 2.1 Details\nContent.\n")
        result = runner.invoke(main, [str(md), "--graph-stats"])
        assert result.exit_code == 0
        assert "node" in result.output.lower() or "Node" in result.output
        assert "edge" in result.output.lower() or "Edge" in result.output

    def test_graph_stats_shows_orphans(self, runner, tmp_path):
        md = tmp_path / "doc.md"
        md.write_text("# 1 Intro\n## 2.1 Details\nContent.\n")
        result = runner.invoke(main, [str(md), "--graph-stats"])
        assert result.exit_code == 0
        assert "orphan" in result.output.lower() or "Orphan" in result.output

    def test_graph_export_and_stats_combined(self, runner, tmp_path):
        md = tmp_path / "doc.md"
        md.write_text("# 1 Intro\nSee Section 2.1.\n## 2.1 Details\nContent.\n")
        output = tmp_path / "graph.graphml"
        result = runner.invoke(
            main, [str(md), "--graph-export", str(output), "--graph-stats"]
        )
        assert result.exit_code == 0
        assert output.exists()
        assert "node" in result.output.lower() or "Node" in result.output

    def test_help_shows_graph_options(self, runner):
        result = runner.invoke(main, ["--help"])
        assert "--graph-export" in result.output
        assert "--graph-stats" in result.output
