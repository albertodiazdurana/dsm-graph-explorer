"""Tests for src/graph/cross_repo.py.

Architecture notes
------------------
CrossRepoBridge manages a dedicated bridge graph (_cross_repo) within an
existing GraphStore. Tests share a single GraphStore instance (session scope)
and create a fresh CrossRepoBridge per test to ensure isolation.

Fixture hierarchy:
    store   (session scope)  -- single GraphStore / FalkorDB subprocess
    bridge  (function scope) -- fresh CrossRepoBridge per test, auto-cleaned
"""

import uuid

import pytest

from graph.graph_store import FALKORDB_AVAILABLE, GraphStore

pytestmark = pytest.mark.skipif(
    not FALKORDB_AVAILABLE,
    reason="falkordblite not installed (pip install '.[graph]')",
)


# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def store(tmp_path_factory):
    """Single GraphStore instance shared across all tests in this module."""
    db_path = str(tmp_path_factory.mktemp("falkordb_cross") / "test.db")
    s = GraphStore(db_path)
    yield s
    s.close()


def _unique_bridge_name() -> str:
    return f"_cross_repo_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def bridge(store):
    """A fresh CrossRepoBridge with a unique graph name, cleaned up after test."""
    from graph.cross_repo import CrossRepoBridge

    graph_name = _unique_bridge_name()
    b = CrossRepoBridge(store, graph_name=graph_name)
    yield b
    # Cleanup: delete the bridge graph
    if store.graph_exists(graph_name):
        g = store._db.select_graph(graph_name)
        g.delete()


# ── edge type constants ──────────────────────────────────────────────────────


class TestEdgeTypes:
    """Verify that edge type constants are defined."""

    def test_inbox_notification_type(self):
        from graph.cross_repo import EdgeType

        assert EdgeType.INBOX_NOTIFICATION == "INBOX_NOTIFICATION"

    def test_at_import_type(self):
        from graph.cross_repo import EdgeType

        assert EdgeType.AT_IMPORT == "AT_IMPORT"

    def test_ecosystem_link_type(self):
        from graph.cross_repo import EdgeType

        assert EdgeType.ECOSYSTEM_LINK == "ECOSYSTEM_LINK"


# ── add_edge ─────────────────────────────────────────────────────────────────


class TestAddEdge:
    """Test adding cross-repo edges to the bridge graph."""

    def test_add_inbox_notification(self, bridge):
        from graph.cross_repo import EdgeType

        bridge.add_edge(
            source_repo="dsm-central",
            source_entity_id="backlog/BL-156",
            target_repo="dsm-graph-explorer",
            target_entity_id="_inbox/2026-03-01-bl156",
            edge_type=EdgeType.INBOX_NOTIFICATION,
            properties={"date": "2026-03-01", "subject": "BL-156 notification"},
        )

        edges = bridge.all_edges()
        assert len(edges) == 1
        assert edges[0]["edge_type"] == "INBOX_NOTIFICATION"
        assert edges[0]["source_repo"] == "dsm-central"
        assert edges[0]["target_repo"] == "dsm-graph-explorer"

    def test_add_at_import(self, bridge):
        from graph.cross_repo import EdgeType

        bridge.add_edge(
            source_repo="dsm-graph-explorer",
            source_entity_id=".claude/CLAUDE.md",
            target_repo="dsm-central",
            target_entity_id="DSM_0.2_Custom_Instructions_v1.1.md",
            edge_type=EdgeType.AT_IMPORT,
            properties={"line": 1},
        )

        edges = bridge.all_edges()
        assert len(edges) == 1
        assert edges[0]["edge_type"] == "AT_IMPORT"
        assert edges[0]["source_entity_id"] == ".claude/CLAUDE.md"
        assert edges[0]["target_entity_id"] == "DSM_0.2_Custom_Instructions_v1.1.md"

    def test_add_ecosystem_link(self, bridge):
        from graph.cross_repo import EdgeType

        bridge.add_edge(
            source_repo="dsm-graph-explorer",
            source_entity_id=".claude/dsm-ecosystem.md",
            target_repo="dsm-central",
            target_entity_id="/",
            edge_type=EdgeType.ECOSYSTEM_LINK,
            properties={"name": "dsm-central"},
        )

        edges = bridge.all_edges()
        assert len(edges) == 1
        assert edges[0]["edge_type"] == "ECOSYSTEM_LINK"
        assert edges[0]["properties"]["name"] == "dsm-central"

    def test_add_multiple_edges(self, bridge):
        from graph.cross_repo import EdgeType

        bridge.add_edge(
            source_repo="repo-a",
            source_entity_id="file1.md",
            target_repo="repo-b",
            target_entity_id="file2.md",
            edge_type=EdgeType.AT_IMPORT,
        )
        bridge.add_edge(
            source_repo="repo-a",
            source_entity_id="file3.md",
            target_repo="repo-c",
            target_entity_id="file4.md",
            edge_type=EdgeType.INBOX_NOTIFICATION,
            properties={"date": "2026-03-13"},
        )

        edges = bridge.all_edges()
        assert len(edges) == 2

    def test_edge_without_properties(self, bridge):
        from graph.cross_repo import EdgeType

        bridge.add_edge(
            source_repo="repo-a",
            source_entity_id="a.md",
            target_repo="repo-b",
            target_entity_id="b.md",
            edge_type=EdgeType.AT_IMPORT,
        )

        edges = bridge.all_edges()
        assert len(edges) == 1
        assert edges[0]["properties"] == {}


# ── MERGE behavior (no duplicate nodes) ─────────────────────────────────────


class TestMergeBehavior:
    """Verify that adding edges with the same entity doesn't duplicate nodes."""

    def test_same_source_two_edges_one_node(self, bridge):
        from graph.cross_repo import EdgeType

        bridge.add_edge(
            source_repo="repo-a",
            source_entity_id="shared.md",
            target_repo="repo-b",
            target_entity_id="b1.md",
            edge_type=EdgeType.AT_IMPORT,
        )
        bridge.add_edge(
            source_repo="repo-a",
            source_entity_id="shared.md",
            target_repo="repo-c",
            target_entity_id="c1.md",
            edge_type=EdgeType.ECOSYSTEM_LINK,
        )

        # Should have 3 unique nodes (shared.md, b1.md, c1.md), not 4
        node_count = bridge.node_count()
        assert node_count == 3

        edges = bridge.all_edges()
        assert len(edges) == 2


# ── edges_for_repo ───────────────────────────────────────────────────────────


class TestEdgesForRepo:
    """Test filtering edges by repository name."""

    def test_edges_for_specific_repo(self, bridge):
        from graph.cross_repo import EdgeType

        bridge.add_edge(
            source_repo="repo-a",
            source_entity_id="a.md",
            target_repo="repo-b",
            target_entity_id="b.md",
            edge_type=EdgeType.AT_IMPORT,
        )
        bridge.add_edge(
            source_repo="repo-b",
            source_entity_id="b2.md",
            target_repo="repo-c",
            target_entity_id="c.md",
            edge_type=EdgeType.INBOX_NOTIFICATION,
        )
        bridge.add_edge(
            source_repo="repo-c",
            source_entity_id="c2.md",
            target_repo="repo-a",
            target_entity_id="a2.md",
            edge_type=EdgeType.ECOSYSTEM_LINK,
        )

        # repo-a is source in edge 1, target in edge 3
        edges_a = bridge.edges_for_repo("repo-a")
        assert len(edges_a) == 2

        # repo-b is target in edge 1, source in edge 2
        edges_b = bridge.edges_for_repo("repo-b")
        assert len(edges_b) == 2

        # repo-c is target in edge 2, source in edge 3
        edges_c = bridge.edges_for_repo("repo-c")
        assert len(edges_c) == 2

    def test_edges_for_repo_no_matches(self, bridge):
        from graph.cross_repo import EdgeType

        bridge.add_edge(
            source_repo="repo-a",
            source_entity_id="a.md",
            target_repo="repo-b",
            target_entity_id="b.md",
            edge_type=EdgeType.AT_IMPORT,
        )

        edges = bridge.edges_for_repo("repo-z")
        assert len(edges) == 0


# ── edges_by_type ────────────────────────────────────────────────────────────


class TestEdgesByType:
    """Test filtering edges by edge type."""

    def test_filter_by_type(self, bridge):
        from graph.cross_repo import EdgeType

        bridge.add_edge(
            source_repo="repo-a",
            source_entity_id="a.md",
            target_repo="repo-b",
            target_entity_id="b.md",
            edge_type=EdgeType.AT_IMPORT,
        )
        bridge.add_edge(
            source_repo="repo-a",
            source_entity_id="a2.md",
            target_repo="repo-b",
            target_entity_id="b2.md",
            edge_type=EdgeType.INBOX_NOTIFICATION,
        )
        bridge.add_edge(
            source_repo="repo-a",
            source_entity_id="a3.md",
            target_repo="repo-b",
            target_entity_id="b3.md",
            edge_type=EdgeType.AT_IMPORT,
        )

        at_imports = bridge.edges_by_type(EdgeType.AT_IMPORT)
        assert len(at_imports) == 2

        inbox = bridge.edges_by_type(EdgeType.INBOX_NOTIFICATION)
        assert len(inbox) == 1

        eco = bridge.edges_by_type(EdgeType.ECOSYSTEM_LINK)
        assert len(eco) == 0


# ── empty bridge ─────────────────────────────────────────────────────────────


class TestEmptyBridge:
    """Test behavior with no edges added."""

    def test_all_edges_empty(self, bridge):
        edges = bridge.all_edges()
        assert edges == []

    def test_edges_for_repo_empty(self, bridge):
        edges = bridge.edges_for_repo("anything")
        assert edges == []

    def test_edges_by_type_empty(self, bridge):
        from graph.cross_repo import EdgeType

        edges = bridge.edges_by_type(EdgeType.AT_IMPORT)
        assert edges == []

    def test_node_count_empty(self, bridge):
        assert bridge.node_count() == 0


# ── store_mapping ────────────────────────────────────────────────────────────


class TestStoreMapping:
    """Test storing compare_inventories results as MAPS_TO edges."""

    def test_stores_matched_pairs(self, bridge):
        from graph.cross_repo import EdgeType
        from graph.repo_diff import MatchResult, MatchType
        from inventory.inventory_parser import Entity

        results = [
            MatchResult(
                entity_a=Entity(
                    id="sec/1.0", type="section",
                    path="doc.md", heading="Introduction",
                ),
                entity_b=Entity(
                    id="sec/1.0", type="section",
                    path="doc.md", heading="Introduction",
                ),
                match_type=MatchType.IDENTICAL,
                similarity_score=1.0,
            ),
            MatchResult(
                entity_a=Entity(
                    id="sec/2.0", type="section",
                    path="doc.md", heading="Old Title",
                ),
                entity_b=Entity(
                    id="pub/2.0", type="section",
                    path="doc.md", heading="New Title",
                ),
                match_type=MatchType.RENAMED,
                similarity_score=0.75,
            ),
        ]

        count = bridge.store_mapping(results, "private-repo", "public-repo")
        assert count == 2

        edges = bridge.edges_by_type(EdgeType.MAPS_TO)
        assert len(edges) == 2

        # Check properties carry match metadata
        props = [e["properties"] for e in edges]
        match_types = {p["match_type"] for p in props}
        assert match_types == {"IDENTICAL", "RENAMED"}

    def test_skips_added_removed(self, bridge):
        from graph.repo_diff import MatchResult, MatchType
        from inventory.inventory_parser import Entity

        results = [
            MatchResult(
                entity_a=Entity(
                    id="sec/1.0", type="section",
                    path="doc.md", heading="Only in A",
                ),
                entity_b=None,
                match_type=MatchType.REMOVED,
                similarity_score=0.0,
            ),
            MatchResult(
                entity_a=None,
                entity_b=Entity(
                    id="sec/2.0", type="section",
                    path="doc.md", heading="Only in B",
                ),
                match_type=MatchType.ADDED,
                similarity_score=0.0,
            ),
        ]

        count = bridge.store_mapping(results, "repo-a", "repo-b")
        assert count == 0
        assert bridge.all_edges() == []

    def test_returns_zero_for_empty(self, bridge):
        count = bridge.store_mapping([], "repo-a", "repo-b")
        assert count == 0