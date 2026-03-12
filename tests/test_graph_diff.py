"""Tests for graph.graph_diff (temporal diff between git refs).

Uses this repository's git history:
- REF_OLD (87d869d): Sprint 1 complete, 12 markdown files
- HEAD: current state, 86+ markdown files
"""

from pathlib import Path

import pytest

try:
    import networkx  # noqa: F401

    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

from click.testing import CliRunner

from cli import main

pytestmark = pytest.mark.skipif(not HAS_NETWORKX, reason="networkx not installed")

REPO_ROOT = Path(__file__).resolve().parents[1]
REF_OLD = "87d869d"


@pytest.fixture
def runner():
    return CliRunner()


# ── Unit tests: _compare_graphs ──────────────────────────────────────


class TestCompareGraphs:
    def test_identical_graphs(self):
        from graph.graph_diff import _compare_graphs

        G = networkx.DiGraph()
        G.add_node("README.md", type="FILE", title="README.md")
        G.add_node("README.md:1.1", type="SECTION", title="Intro")

        result = _compare_graphs(G, G, "aaa", "bbb")
        assert not result.has_changes

    def test_added_file(self):
        from graph.graph_diff import _compare_graphs

        G_a = networkx.DiGraph()
        G_a.add_node("old.md", type="FILE", title="old.md")

        G_b = networkx.DiGraph()
        G_b.add_node("old.md", type="FILE", title="old.md")
        G_b.add_node("new.md", type="FILE", title="new.md")

        result = _compare_graphs(G_a, G_b, "aaa", "bbb")
        assert result.added_files == ["new.md"]
        assert result.removed_files == []

    def test_removed_file(self):
        from graph.graph_diff import _compare_graphs

        G_a = networkx.DiGraph()
        G_a.add_node("old.md", type="FILE", title="old.md")
        G_a.add_node("gone.md", type="FILE", title="gone.md")

        G_b = networkx.DiGraph()
        G_b.add_node("old.md", type="FILE", title="old.md")

        result = _compare_graphs(G_a, G_b, "aaa", "bbb")
        assert result.removed_files == ["gone.md"]
        assert result.added_files == []

    def test_added_section(self):
        from graph.graph_diff import _compare_graphs

        G_a = networkx.DiGraph()
        G_a.add_node("f.md:1.1", type="SECTION", title="Old")

        G_b = networkx.DiGraph()
        G_b.add_node("f.md:1.1", type="SECTION", title="Old")
        G_b.add_node("f.md:1.2", type="SECTION", title="New")

        result = _compare_graphs(G_a, G_b, "aaa", "bbb")
        assert result.added_sections == ["f.md:1.2"]

    def test_changed_title(self):
        from graph.graph_diff import _compare_graphs

        G_a = networkx.DiGraph()
        G_a.add_node("f.md:1.1", type="SECTION", title="Old Title")

        G_b = networkx.DiGraph()
        G_b.add_node("f.md:1.1", type="SECTION", title="New Title")

        result = _compare_graphs(G_a, G_b, "aaa", "bbb")
        assert len(result.changed) == 1
        assert result.changed[0].field == "title"
        assert result.changed[0].old_value == "Old Title"
        assert result.changed[0].new_value == "New Title"

    def test_has_changes_property(self):
        from graph.graph_diff import DiffResult

        empty = DiffResult(ref_a="a", ref_b="b")
        assert not empty.has_changes

        with_added = DiffResult(ref_a="a", ref_b="b", added_files=["x.md"])
        assert with_added.has_changes


# ── Integration: diff_graphs with real repo ──────────────────────────


class TestDiffGraphsIntegration:
    def test_old_vs_head(self):
        from graph.graph_diff import diff_graphs

        result = diff_graphs(REPO_ROOT, REF_OLD, "HEAD")
        assert result.has_changes
        assert len(result.added_files) > 0
        # Old ref had fewer files, so we expect additions
        assert result.ref_a.startswith("87d869d")

    def test_same_ref_no_changes(self):
        from graph.graph_diff import diff_graphs

        result = diff_graphs(REPO_ROOT, REF_OLD, REF_OLD)
        assert not result.has_changes

    def test_invalid_ref_raises_error(self):
        from git_ref.git_resolver import GitRefError
        from graph.graph_diff import diff_graphs

        with pytest.raises(GitRefError):
            diff_graphs(REPO_ROOT, "nonexistent-ref-xyz", "HEAD")


# ── CLI integration ──────────────────────────────────────────────────


class TestGraphDiffCli:
    def test_graph_diff_output(self, runner):
        result = runner.invoke(
            main, [str(REPO_ROOT), "--graph-diff", REF_OLD, "HEAD"]
        )
        assert result.exit_code == 0
        assert "Graph Diff:" in result.output
        assert "+added" in result.output

    def test_graph_diff_same_ref(self, runner):
        result = runner.invoke(
            main, [str(REPO_ROOT), "--graph-diff", REF_OLD, REF_OLD]
        )
        assert result.exit_code == 0
        assert "No differences" in result.output

    def test_graph_diff_invalid_ref(self, runner):
        result = runner.invoke(
            main, [str(REPO_ROOT), "--graph-diff", "bad-ref-xyz", "HEAD"]
        )
        assert result.exit_code == 2
        assert "Cannot resolve ref" in result.output