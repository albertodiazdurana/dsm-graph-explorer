"""CLI integration tests for --git-ref option.

Uses this repository's git history with known refs:
- REF_OLD (87d869d): Sprint 1 complete, 12 markdown files
- HEAD: current state
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from cli import main

REPO_ROOT = Path(__file__).resolve().parents[1]
REF_OLD = "87d869d"


@pytest.fixture
def runner():
    return CliRunner()


class TestGitRefBasic:
    def test_git_ref_old_commit(self, runner):
        result = runner.invoke(main, [str(REPO_ROOT), "--git-ref", REF_OLD])
        assert result.exit_code == 0
        assert "87d869d8ef33" in result.output
        assert "12 markdown file(s)" in result.output

    def test_git_ref_head(self, runner):
        result = runner.invoke(main, [str(REPO_ROOT), "--git-ref", "HEAD"])
        assert result.exit_code == 0
        assert "markdown file(s)" in result.output

    def test_git_ref_produces_validation_output(self, runner):
        result = runner.invoke(main, [str(REPO_ROOT), "--git-ref", REF_OLD])
        assert result.exit_code == 0
        assert "Scanned" in result.output
        assert "file(s)" in result.output


class TestGitRefErrors:
    def test_invalid_ref(self, runner):
        result = runner.invoke(
            main, [str(REPO_ROOT), "--git-ref", "nonexistent-ref-xyz"]
        )
        assert result.exit_code == 2
        assert "Cannot resolve ref" in result.output

    def test_lint_with_git_ref_rejected(self, runner):
        result = runner.invoke(
            main, [str(REPO_ROOT), "--lint", "--git-ref", REF_OLD]
        )
        assert result.exit_code == 2
        assert "--lint cannot be combined with --git-ref" in result.output


class TestGitRefWithGraphStats:
    def test_git_ref_with_graph_stats(self, runner):
        """--git-ref + --graph-stats builds graph from historical content."""
        try:
            import networkx  # noqa: F401
        except ImportError:
            pytest.skip("networkx not installed")

        result = runner.invoke(
            main,
            [str(REPO_ROOT), "--git-ref", REF_OLD, "--graph-stats"],
        )
        assert result.exit_code == 0
        assert "Graph Statistics:" in result.output
        assert "Nodes:" in result.output


class TestGitRefDifferentResults:
    def test_old_ref_has_fewer_findings(self, runner):
        """Old ref with fewer files should produce different results than HEAD."""
        old = runner.invoke(main, [str(REPO_ROOT), "--git-ref", REF_OLD])
        head = runner.invoke(main, [str(REPO_ROOT), "--git-ref", "HEAD"])
        assert old.exit_code == 0
        assert head.exit_code == 0
        # Different file counts in the resolved message
        assert "12 markdown file(s)" in old.output
        assert "12 markdown file(s)" not in head.output