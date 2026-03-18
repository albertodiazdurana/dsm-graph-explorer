"""Tests for src/graph/graph_store.py.

Architecture notes
------------------
FalkorDBLite starts a subprocess (~100-500ms startup). To keep the suite fast,
one FalkorDB instance is shared across all tests (session scope). Each test
gets a uniquely-named graph (UUID prefix) so tests are fully isolated. Every
test cleans up with g.delete() via the `graph` fixture's teardown.

Fixture hierarchy:
    falkor_db   (session scope)  -- single FalkorDB subprocess
    graph       (function scope) -- unique named graph per test, auto-deleted

See: docs/research/epoch-3-falkordblite-deep-dive.md Section 7 (Testing Patterns)
"""

import uuid

import networkx as nx
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
    db_path = str(tmp_path_factory.mktemp("falkordb") / "test.db")
    s = GraphStore(db_path)
    yield s
    s.close()


def _unique_name(prefix: str = "test") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def graph_name():
    """A unique graph name for one test."""
    return _unique_name()


@pytest.fixture
def populated_store(store, graph_name):
    """A GraphStore with a small NetworkX graph already written.

    Graph shape (matches EXP-005 test data):
        FILE: repo/DSM_1.0.md, repo/DSM_2.0.md
        SECTION: repo/DSM_1.0.md:1, repo/DSM_1.0.md:2, repo/DSM_2.0.md:1
        CONTAINS: each FILE -> its SECTIONs
        REFERENCES: repo/DSM_1.0.md:2 -> repo/DSM_2.0.md:1
    """
    G = _small_nx_graph()
    store.write_graph(G, graph_name=graph_name, git_ref="HEAD")
    yield store, graph_name
    # cleanup: delete graph after test
    g = store._db.select_graph(graph_name)
    try:
        g.delete()
    except Exception:
        pass


def _small_nx_graph() -> nx.DiGraph:
    """Build a minimal NetworkX graph matching graph_builder.py schema."""
    G = nx.DiGraph()

    # FILE nodes
    G.add_node("repo/DSM_1.0.md", type="FILE", title="DSM_1.0.md")
    G.add_node("repo/DSM_2.0.md", type="FILE", title="DSM_2.0.md")

    # SECTION nodes
    G.add_node(
        "repo/DSM_1.0.md:1",
        type="SECTION",
        title="Introduction",
        number="1",
        level=1,
        line=5,
        file="repo/DSM_1.0.md",
        context_excerpt="First section prose.",
    )
    G.add_node(
        "repo/DSM_1.0.md:2",
        type="SECTION",
        title="Lifecycle",
        number="2",
        level=2,
        line=20,
        file="repo/DSM_1.0.md",
        context_excerpt="Lifecycle overview prose.",
    )
    G.add_node(
        "repo/DSM_2.0.md:1",
        type="SECTION",
        title="Sprint Checklist",
        number="1",
        level=1,
        line=3,
        file="repo/DSM_2.0.md",
        context_excerpt="Checklist section prose.",
    )

    # CONTAINS edges
    G.add_edge("repo/DSM_1.0.md", "repo/DSM_1.0.md:1", type="CONTAINS")
    G.add_edge("repo/DSM_1.0.md", "repo/DSM_1.0.md:2", type="CONTAINS")
    G.add_edge("repo/DSM_2.0.md", "repo/DSM_2.0.md:1", type="CONTAINS")

    # REFERENCES edge
    G.add_edge(
        "repo/DSM_1.0.md:2",
        "repo/DSM_2.0.md:1",
        type="REFERENCES",
        line=25,
        ref_type="section",
    )

    return G


# ── availability guard ────────────────────────────────────────────────────────


def test_falkordb_available_flag():
    """FALKORDB_AVAILABLE is True when falkordblite is installed."""
    assert FALKORDB_AVAILABLE is True


# ── GraphStore lifecycle ──────────────────────────────────────────────────────


def test_store_opens(store):
    """GraphStore opens without error when falkordblite is installed."""
    assert store is not None


def test_close_is_idempotent(tmp_path):
    """Calling close() twice does not raise."""
    s = GraphStore(str(tmp_path / "close_test.db"))
    s.close()
    s.close()  # second close must not raise


# ── graph_exists ──────────────────────────────────────────────────────────────


def test_graph_exists_false_before_write(store):
    """graph_exists() returns False for a graph that has not been written."""
    assert store.graph_exists(_unique_name("nonexistent")) is False


def test_graph_exists_true_after_write(populated_store):
    """graph_exists() returns True after write_graph()."""
    s, gname = populated_store
    assert s.graph_exists(gname) is True


# ── write_graph node counts ───────────────────────────────────────────────────


def test_write_graph_document_count(populated_store):
    """write_graph() creates the correct number of Document nodes."""
    s, gname = populated_store
    result = s.ro_query("MATCH (d:Document) RETURN d", graph_name=gname)
    assert len(result.result_set) == 2


def test_write_graph_section_count(populated_store):
    """write_graph() creates the correct number of Section nodes."""
    s, gname = populated_store
    result = s.ro_query("MATCH (sec:Section) RETURN sec", graph_name=gname)
    assert len(result.result_set) == 3


def test_write_graph_contains_edge_count(populated_store):
    """write_graph() creates the correct number of CONTAINS edges."""
    s, gname = populated_store
    result = s.ro_query(
        "MATCH ()-[r:CONTAINS]->() RETURN r", graph_name=gname
    )
    assert len(result.result_set) == 3


def test_write_graph_references_edge_count(populated_store):
    """write_graph() creates the correct number of REFERENCES edges."""
    s, gname = populated_store
    result = s.ro_query(
        "MATCH ()-[r:REFERENCES]->() RETURN r", graph_name=gname
    )
    assert len(result.result_set) == 1


# ── node properties ───────────────────────────────────────────────────────────


def test_document_has_git_ref(populated_store):
    """Document nodes carry the git_ref property."""
    s, gname = populated_store
    result = s.ro_query(
        "MATCH (d:Document {path: $path}) RETURN d.git_ref",
        graph_name=gname,
        params={"path": "repo/DSM_1.0.md"},
    )
    assert result.result_set[0][0] == "HEAD"


def test_document_has_repo(populated_store):
    """Document nodes carry the repo property (set to graph_name)."""
    s, gname = populated_store
    result = s.ro_query(
        "MATCH (d:Document) RETURN d.repo LIMIT 1", graph_name=gname
    )
    assert result.result_set[0][0] == gname


def test_section_has_heading(populated_store):
    """Section nodes carry the heading property from the NetworkX title."""
    s, gname = populated_store
    result = s.ro_query(
        "MATCH (sec:Section {number: $num}) RETURN sec.heading",
        graph_name=gname,
        params={"num": "1"},
    )
    headings = {row[0] for row in result.result_set}
    # Both DSM_1.0.md:1 and DSM_2.0.md:1 have number "1"
    assert "Introduction" in headings or "Sprint Checklist" in headings


# ── index-backed lookups ──────────────────────────────────────────────────────


def test_lookup_by_node_id(populated_store):
    """Section nodes can be looked up by node_id (uses Section.node_id index)."""
    s, gname = populated_store
    result = s.ro_query(
        "MATCH (sec:Section {node_id: $nid}) RETURN sec.heading",
        graph_name=gname,
        params={"nid": "repo/DSM_1.0.md:2"},
    )
    assert len(result.result_set) == 1
    assert result.result_set[0][0] == "Lifecycle"


def test_lookup_by_heading(populated_store):
    """Section nodes can be looked up by heading (uses Section.heading index)."""
    s, gname = populated_store
    result = s.ro_query(
        "MATCH (sec:Section {heading: $h}) RETURN sec.node_id",
        graph_name=gname,
        params={"h": "Sprint Checklist"},
    )
    assert len(result.result_set) == 1
    assert result.result_set[0][0] == "repo/DSM_2.0.md:1"


def test_lookup_heading_section_by_node_id(store):
    """Heading-based section (h:slug) can be looked up by node_id."""
    gname = _unique_name("heading_idx")
    G = nx.DiGraph()
    G.add_node("doc.md", type="FILE", title="doc.md")
    G.add_node(
        "doc.md:h:inclusive-language",
        type="SECTION",
        title="Inclusive Language",
        number="",
        level=2,
        line=10,
        file="doc.md",
        context_excerpt="Guidelines for inclusive language.",
    )
    G.add_edge("doc.md", "doc.md:h:inclusive-language", type="CONTAINS")
    store.write_graph(G, graph_name=gname, git_ref="HEAD")

    result = store.ro_query(
        "MATCH (sec:Section {node_id: $nid}) RETURN sec.heading",
        graph_name=gname,
        params={"nid": "doc.md:h:inclusive-language"},
    )
    store._db.select_graph(gname).delete()

    assert len(result.result_set) == 1
    assert result.result_set[0][0] == "Inclusive Language"


# ── traversal queries ─────────────────────────────────────────────────────────


def test_contains_traversal(populated_store):
    """MATCH (d:Document)-[:CONTAINS]->(s:Section) returns correct sections."""
    s, gname = populated_store
    result = s.ro_query(
        """
        MATCH (d:Document {path: $path})-[:CONTAINS]->(sec:Section)
        RETURN sec.heading ORDER BY sec.heading
        """,
        graph_name=gname,
        params={"path": "repo/DSM_1.0.md"},
    )
    headings = [row[0] for row in result.result_set]
    assert set(headings) == {"Introduction", "Lifecycle"}


def test_references_traversal(populated_store):
    """MATCH (:Section)-[:REFERENCES]->(:Section) returns correct pair."""
    s, gname = populated_store
    result = s.ro_query(
        """
        MATCH (src:Section)-[:REFERENCES]->(tgt:Section)
        RETURN src.heading, tgt.heading
        """,
        graph_name=gname,
    )
    assert len(result.result_set) == 1
    src_heading, tgt_heading = result.result_set[0]
    assert src_heading == "Lifecycle"
    assert tgt_heading == "Sprint Checklist"


# ── idempotent write ──────────────────────────────────────────────────────────


def test_write_graph_idempotent(store, graph_name):
    """Writing the same graph twice results in correct node counts (no duplicates)."""
    G = _small_nx_graph()
    store.write_graph(G, graph_name=graph_name, git_ref="HEAD")
    store.write_graph(G, graph_name=graph_name, git_ref="HEAD")  # second write

    result = store.ro_query("MATCH (d:Document) RETURN d", graph_name=graph_name)
    doc_count = len(result.result_set)

    # cleanup
    store._db.select_graph(graph_name).delete()

    assert doc_count == 2  # not 4 (no duplicates from double write)


# ── multi-graph isolation ─────────────────────────────────────────────────────


def test_multi_graph_isolation(store):
    """Two graphs with different names are fully isolated."""
    name_a = _unique_name("repo_a")
    name_b = _unique_name("repo_b")

    G = _small_nx_graph()
    store.write_graph(G, graph_name=name_a, git_ref="HEAD")

    # Write only one document to repo_b
    G_small = nx.DiGraph()
    G_small.add_node("only.md", type="FILE", title="only.md")
    store.write_graph(G_small, graph_name=name_b, git_ref="HEAD")

    result_a = store.ro_query("MATCH (d:Document) RETURN d", graph_name=name_a)
    result_b = store.ro_query("MATCH (d:Document) RETURN d", graph_name=name_b)

    # cleanup
    store._db.select_graph(name_a).delete()
    store._db.select_graph(name_b).delete()

    assert len(result_a.result_set) == 2
    assert len(result_b.result_set) == 1


# ── list_graphs ───────────────────────────────────────────────────────────────


def test_list_graphs_includes_written(store, graph_name):
    """list_graphs() includes a graph after it is written."""
    G = _small_nx_graph()
    store.write_graph(G, graph_name=graph_name, git_ref="HEAD")

    graphs = store.list_graphs()
    store._db.select_graph(graph_name).delete()

    assert graph_name in graphs


# ── incremental updates (update_files) ────────────────────────────────────────


# ── to_networkx export ────────────────────────────────────────────────────────


def test_to_networkx_roundtrip_node_counts(populated_store):
    """to_networkx() returns the same number of nodes as the original graph."""
    s, gname = populated_store
    G = s.to_networkx(gname)
    file_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "FILE"]
    section_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "SECTION"]
    assert len(file_nodes) == 2
    assert len(section_nodes) == 3


def test_to_networkx_roundtrip_edge_counts(populated_store):
    """to_networkx() returns the same number of edges as the original graph."""
    s, gname = populated_store
    G = s.to_networkx(gname)
    contains = [e for _, _, e in G.edges(data=True) if e.get("type") == "CONTAINS"]
    refs = [e for _, _, e in G.edges(data=True) if e.get("type") == "REFERENCES"]
    assert len(contains) == 3
    assert len(refs) == 1


def test_to_networkx_preserves_section_properties(populated_store):
    """to_networkx() preserves section node properties."""
    s, gname = populated_store
    G = s.to_networkx(gname)
    node = G.nodes["repo/DSM_1.0.md:2"]
    assert node["title"] == "Lifecycle"
    assert node["number"] == "2"
    assert node["file"] == "repo/DSM_1.0.md"
    assert node["type"] == "SECTION"


def test_to_networkx_preserves_reference_properties(populated_store):
    """to_networkx() preserves reference edge properties."""
    s, gname = populated_store
    G = s.to_networkx(gname)
    edge = G.edges["repo/DSM_1.0.md:2", "repo/DSM_2.0.md:1"]
    assert edge["type"] == "REFERENCES"
    assert edge["ref_type"] == "section"
    assert edge["line"] == 25


def test_to_networkx_raises_on_missing_graph(store):
    """to_networkx() raises ValueError for non-existent graph."""
    with pytest.raises(ValueError, match="does not exist"):
        store.to_networkx(_unique_name("no_such"))


# ── incremental updates (update_files) ────────────────────────────────────────


def test_update_files_changes_one_file(store):
    """update_files() updates only the changed file, preserves the other."""
    gname = _unique_name("incr")
    G = _small_nx_graph()
    store.write_graph(G, graph_name=gname, git_ref="v1")

    # Modify DSM_1.0.md: change section title, add a new section
    G2 = _small_nx_graph()
    G2.nodes["repo/DSM_1.0.md:1"]["title"] = "Updated Introduction"
    G2.add_node(
        "repo/DSM_1.0.md:3",
        type="SECTION",
        title="New Section",
        number="3",
        level=1,
        line=40,
        file="repo/DSM_1.0.md",
        context_excerpt="Brand new section.",
    )
    G2.add_edge("repo/DSM_1.0.md", "repo/DSM_1.0.md:3", type="CONTAINS")

    store.update_files(G2, graph_name=gname, changed_files=["repo/DSM_1.0.md"], git_ref="v2")

    # DSM_1.0.md should have 3 sections now
    result = store.ro_query(
        "MATCH (d:Document {path: $p})-[:CONTAINS]->(s:Section) RETURN s.heading ORDER BY s.heading",
        graph_name=gname,
        params={"p": "repo/DSM_1.0.md"},
    )
    headings = [row[0] for row in result.result_set]
    assert "Updated Introduction" in headings
    assert "New Section" in headings
    assert len(headings) == 3

    # DSM_2.0.md should be unchanged
    result2 = store.ro_query(
        "MATCH (d:Document {path: $p})-[:CONTAINS]->(s:Section) RETURN s.heading",
        graph_name=gname,
        params={"p": "repo/DSM_2.0.md"},
    )
    assert len(result2.result_set) == 1
    assert result2.result_set[0][0] == "Sprint Checklist"

    store._db.select_graph(gname).delete()


def test_update_files_preserves_references(store):
    """update_files() rebuilds REFERENCES edges after file update."""
    gname = _unique_name("incr_ref")
    G = _small_nx_graph()
    store.write_graph(G, graph_name=gname, git_ref="v1")

    # Update DSM_1.0.md without changing the reference structure
    store.update_files(G, graph_name=gname, changed_files=["repo/DSM_1.0.md"], git_ref="v2")

    result = store.ro_query(
        "MATCH (s1:Section)-[:REFERENCES]->(s2:Section) RETURN s1.heading, s2.heading",
        graph_name=gname,
    )
    assert len(result.result_set) == 1
    assert result.result_set[0][0] == "Lifecycle"
    assert result.result_set[0][1] == "Sprint Checklist"

    store._db.select_graph(gname).delete()


def test_update_files_no_duplicates(store):
    """update_files() does not create duplicate nodes for changed files."""
    gname = _unique_name("incr_dup")
    G = _small_nx_graph()
    store.write_graph(G, graph_name=gname, git_ref="v1")

    # Update same file twice
    store.update_files(G, graph_name=gname, changed_files=["repo/DSM_1.0.md"], git_ref="v2")
    store.update_files(G, graph_name=gname, changed_files=["repo/DSM_1.0.md"], git_ref="v3")

    result = store.ro_query("MATCH (d:Document) RETURN d.path", graph_name=gname)
    assert len(result.result_set) == 2  # still 2 documents, not more

    result2 = store.ro_query("MATCH (s:Section) RETURN s", graph_name=gname)
    assert len(result2.result_set) == 3  # still 3 sections

    store._db.select_graph(gname).delete()


def test_update_files_updates_git_ref(store):
    """update_files() stamps the new git_ref on updated nodes."""
    gname = _unique_name("incr_ref_stamp")
    G = _small_nx_graph()
    store.write_graph(G, graph_name=gname, git_ref="abc123")

    store.update_files(G, graph_name=gname, changed_files=["repo/DSM_1.0.md"], git_ref="def456")

    # Changed file should have new ref
    result = store.ro_query(
        "MATCH (d:Document {path: $p}) RETURN d.git_ref",
        graph_name=gname,
        params={"p": "repo/DSM_1.0.md"},
    )
    assert result.result_set[0][0] == "def456"

    # Unchanged file keeps old ref
    result2 = store.ro_query(
        "MATCH (d:Document {path: $p}) RETURN d.git_ref",
        graph_name=gname,
        params={"p": "repo/DSM_2.0.md"},
    )
    assert result2.result_set[0][0] == "abc123"

    store._db.select_graph(gname).delete()


def test_get_stored_ref(store):
    """get_stored_ref() returns the git_ref stored on Document nodes."""
    gname = _unique_name("stored_ref")
    G = _small_nx_graph()
    store.write_graph(G, graph_name=gname, git_ref="abc123def")

    assert store.get_stored_ref(gname) == "abc123def"

    store._db.select_graph(gname).delete()


def test_get_stored_ref_none_when_missing(store):
    """get_stored_ref() returns None for a non-existent graph."""
    assert store.get_stored_ref(_unique_name("no_such")) is None


def test_update_files_fallback_to_write(store):
    """update_files() falls back to write_graph() when graph does not exist."""
    gname = _unique_name("incr_fallback")
    G = _small_nx_graph()

    # Graph doesn't exist yet, should create it
    store.update_files(G, graph_name=gname, changed_files=["repo/DSM_1.0.md"], git_ref="HEAD")

    result = store.ro_query("MATCH (d:Document) RETURN d", graph_name=gname)
    assert len(result.result_set) == 2

    store._db.select_graph(gname).delete()


# ── import guard ──────────────────────────────────────────────────────────────


def test_import_error_without_falkordb(monkeypatch):
    """GraphStore raises ImportError if falkordblite is not available."""
    import graph.graph_store as gs

    monkeypatch.setattr(gs, "FALKORDB_AVAILABLE", False)
    with pytest.raises(ImportError, match="falkordblite"):
        GraphStore.__new__(GraphStore)
        gs.GraphStore("/tmp/should_not_be_created.db")
