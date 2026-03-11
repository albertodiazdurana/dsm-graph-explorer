"""Tests for --graph-db and --rebuild CLI options (Phase 9.3).

Composition Challenge (Proposal #30):
    Why:   TDD for Phase 9.3 CLI integration of FalkorDBLite persistence.
    What:  6 tests — creates_file, cached_skip, rebuild, missing_dep, with_stats, real_data.
    Why 6: 5 checkpoint requirements (persist, cache, rebuild, graceful error, stats combo)
           + 1 real-data integration concern. Excluded: empty dir (existing CLI tests),
           lint combo (no interaction), rebuild-alone (no-op), invalid path (FalkorDB's
           job), data verification (test_graph_store.py's 18 tests).
    How:   CliRunner from test_cli.py pattern, skipif(not FALKORDB_AVAILABLE), tmp_path
           for DB files, project docs/ for real-data test.
    When:  TDD — tests written before implementation.
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from cli import main
from graph.graph_store import FALKORDB_AVAILABLE


pytestmark = pytest.mark.skipif(
    not FALKORDB_AVAILABLE,
    reason="falkordblite not installed (pip install '.[graph]')",
)


def _db_files_exist(db_path: Path) -> bool:
    """Check if FalkorDBLite created persistence files for db_path.

    FalkorDBLite does not create a file at db_path itself; it creates
    {db_path}.settings and other internal files in the same directory.
    """
    return any(db_path.parent.glob(f"{db_path.name}*"))


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def md_dir(tmp_path):
    """A small markdown directory with cross-references (triggers graph build)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    doc = repo / "doc.md"
    doc.write_text(
        "# 1 Introduction\n"
        "See Section 2.1 for details.\n"
        "## 2.1 Details\n"
        "Content here.\n"
    )
    return repo


# ── Requirement 1: --graph-db creates a persistence file ─────────────────────


class TestGraphDbCreatesFile:
    """--graph-db PATH persists the graph to a FalkorDB file on disk."""

    def test_graph_db_creates_file(self, runner, md_dir, tmp_path):
        db_path = tmp_path / "test.falkordb"
        result = runner.invoke(
            main, [str(md_dir), "--graph-db", str(db_path)]
        )
        assert result.exit_code == 0, result.output
        assert _db_files_exist(db_path)
        assert "persisted" in result.output.lower() or "Graph" in result.output


# ── Requirement 2: cached graph skip ─────────────────────────────────────────


class TestGraphDbCachedSkip:
    """Second run without --rebuild reports cached graph, skips write."""

    def test_graph_db_cached_skip(self, runner, md_dir, tmp_path):
        db_path = tmp_path / "test.falkordb"
        # First run: persist
        result1 = runner.invoke(
            main, [str(md_dir), "--graph-db", str(db_path)]
        )
        assert result1.exit_code == 0, result1.output

        # Second run: should report cached
        result2 = runner.invoke(
            main, [str(md_dir), "--graph-db", str(db_path)]
        )
        assert result2.exit_code == 0, result2.output
        assert "cached" in result2.output.lower()


# ── Requirement 3: --rebuild forces rewrite ──────────────────────────────────


class TestGraphDbRebuild:
    """--rebuild flag forces a full rewrite even if graph exists."""

    def test_graph_db_rebuild_forces_rewrite(self, runner, md_dir, tmp_path):
        db_path = tmp_path / "test.falkordb"
        # First run: persist
        runner.invoke(main, [str(md_dir), "--graph-db", str(db_path)])

        # Second run with --rebuild: should persist again, not report cached
        result = runner.invoke(
            main, [str(md_dir), "--graph-db", str(db_path), "--rebuild"]
        )
        assert result.exit_code == 0, result.output
        assert "cached" not in result.output.lower()
        assert "persisted" in result.output.lower() or "Graph" in result.output


# ── Requirement 4: graceful error without falkordblite ───────────────────────


@pytest.mark.skipif(False, reason="always runs")  # override module-level skip
class TestGraphDbMissingDependency:
    """--graph-db without falkordblite gives a helpful error, not a traceback."""

    @pytest.mark.skipif(False, reason="always runs")
    def test_graph_db_missing_falkordblite(self, runner, md_dir, tmp_path, monkeypatch):
        import cli as cli_module

        monkeypatch.setattr(cli_module, "FALKORDB_AVAILABLE", False)
        db_path = tmp_path / "test.falkordb"
        result = runner.invoke(
            main, [str(md_dir), "--graph-db", str(db_path)]
        )
        assert result.exit_code == 2
        assert "falkordblite" in result.output.lower() or "falkordb" in result.output.lower()


# ── Requirement 5: --graph-db + --graph-stats compose correctly ──────────────


class TestGraphDbWithStats:
    """--graph-db and --graph-stats can be used together."""

    def test_graph_db_with_graph_stats(self, runner, md_dir, tmp_path):
        db_path = tmp_path / "test.falkordb"
        result = runner.invoke(
            main,
            [str(md_dir), "--graph-db", str(db_path), "--graph-stats"],
        )
        assert result.exit_code == 0, result.output
        assert _db_files_exist(db_path)
        # Stats output present
        assert "node" in result.output.lower() or "Node" in result.output
        assert "edge" in result.output.lower() or "Edge" in result.output


# ── Real-data integration ────────────────────────────────────────────────────


PROJECT_DOCS = Path(__file__).resolve().parent.parent / "docs"


class TestGraphDbRealData:
    """End-to-end test with real project markdown files."""

    @pytest.mark.skipif(
        not PROJECT_DOCS.is_dir()
        or len(list(PROJECT_DOCS.glob("**/*.md"))) < 3,
        reason="Project docs/ not available or too few files",
    )
    def test_graph_db_real_data_integration(self, runner, tmp_path):
        db_path = tmp_path / "real_data.falkordb"
        result = runner.invoke(
            main,
            [str(PROJECT_DOCS), "--graph-db", str(db_path), "--graph-stats"],
        )
        assert result.exit_code == 0, result.output
        assert _db_files_exist(db_path)
        # Real data should produce a non-trivial graph
        assert "Node" in result.output or "node" in result.output.lower()
