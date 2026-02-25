"""Tests for graph builder and query modules (Phases 7.1-7.2).

Uses synthetic test data to verify graph construction from parsed
documents and cross-references, and query functions over the graph.
TDD: tests written before implementation.
"""

import pytest

from parser.cross_ref_extractor import CrossReference
from parser.markdown_parser import ParsedDocument, Section
from validator.cross_ref_validator import build_section_lookup

# Import will fail until module is created; tests should fail with ImportError
from graph.graph_builder import build_reference_graph


# ---------------------------------------------------------------------------
# Synthetic test data
# ---------------------------------------------------------------------------

def _make_doc(file: str, sections: list[Section]) -> ParsedDocument:
    """Helper to create a ParsedDocument."""
    return ParsedDocument(file=file, sections=sections)


def _make_section(number: str | None, title: str, line: int, level: int = 2) -> Section:
    """Helper to create a Section."""
    return Section(number=number, title=title, line=line, level=level)


def _make_ref(ref_type: str, target: str, line: int) -> CrossReference:
    """Helper to create a CrossReference."""
    return CrossReference(type=ref_type, target=target, line=line, context="")


# Two-document corpus for multi-file tests
DOC_A = _make_doc("docs/DSM_1.0.md", [
    _make_section("1.1", "Introduction", line=5, level=2),
    _make_section("1.2", "Scope", line=20, level=2),
    _make_section("1.2.1", "In Scope", line=30, level=3),
])

DOC_B = _make_doc("docs/DSM_4.0.md", [
    _make_section("3.1", "Development Protocol", line=10, level=2),
    _make_section("3.2", "Testing Strategy", line=40, level=2),
])


# ---------------------------------------------------------------------------
# Tests: Empty and minimal cases
# ---------------------------------------------------------------------------

class TestEmptyAndMinimal:
    def test_empty_documents_produces_empty_graph(self):
        G = build_reference_graph([], {}, {})
        assert G.number_of_nodes() == 0
        assert G.number_of_edges() == 0

    def test_single_document_no_sections(self):
        doc = _make_doc("README.md", [])
        G = build_reference_graph([doc], {}, {})
        assert G.number_of_nodes() == 1
        assert G.nodes["README.md"]["type"] == "FILE"


# ---------------------------------------------------------------------------
# Tests: Node creation
# ---------------------------------------------------------------------------

class TestNodeCreation:
    def test_file_node_attributes(self):
        G = build_reference_graph([DOC_A], {}, {})
        node = G.nodes["docs/DSM_1.0.md"]
        assert node["type"] == "FILE"
        assert node["title"] == "DSM_1.0.md"

    def test_numbered_sections_create_section_nodes(self):
        G = build_reference_graph([DOC_A], {}, {})
        section_nodes = [
            n for n, d in G.nodes(data=True) if d.get("type") == "SECTION"
        ]
        assert len(section_nodes) == 3
        assert "docs/DSM_1.0.md:1.1" in section_nodes
        assert "docs/DSM_1.0.md:1.2" in section_nodes
        assert "docs/DSM_1.0.md:1.2.1" in section_nodes

    def test_section_node_attributes(self):
        G = build_reference_graph([DOC_A], {}, {})
        node = G.nodes["docs/DSM_1.0.md:1.1"]
        assert node["type"] == "SECTION"
        assert node["title"] == "Introduction"
        assert node["number"] == "1.1"
        assert node["file"] == "docs/DSM_1.0.md"
        assert node["line"] == 5
        assert node["level"] == 2
        assert node["context_excerpt"] == ""

    def test_unnumbered_sections_are_skipped(self):
        doc = _make_doc("file.md", [
            _make_section(None, "Unnumbered Heading", line=1),
            _make_section("2.1", "Numbered", line=10),
        ])
        G = build_reference_graph([doc], {}, {})
        section_nodes = [
            n for n, d in G.nodes(data=True) if d.get("type") == "SECTION"
        ]
        assert len(section_nodes) == 1
        assert "file.md:2.1" in section_nodes

    def test_node_id_format(self):
        G = build_reference_graph([DOC_A, DOC_B], {}, {})
        all_nodes = list(G.nodes)
        # FILE nodes use file path
        assert "docs/DSM_1.0.md" in all_nodes
        assert "docs/DSM_4.0.md" in all_nodes
        # SECTION nodes use file:number
        assert "docs/DSM_1.0.md:1.1" in all_nodes
        assert "docs/DSM_4.0.md:3.1" in all_nodes


# ---------------------------------------------------------------------------
# Tests: Edge creation
# ---------------------------------------------------------------------------

class TestEdgeCreation:
    def test_contains_edges(self):
        G = build_reference_graph([DOC_A], {}, {})
        contains = [
            (u, v) for u, v, d in G.edges(data=True)
            if d.get("type") == "CONTAINS"
        ]
        assert len(contains) == 3
        assert ("docs/DSM_1.0.md", "docs/DSM_1.0.md:1.1") in contains
        assert ("docs/DSM_1.0.md", "docs/DSM_1.0.md:1.2") in contains
        assert ("docs/DSM_1.0.md", "docs/DSM_1.0.md:1.2.1") in contains

    def test_resolved_reference_creates_edge(self):
        docs = [DOC_A, DOC_B]
        lookup = build_section_lookup(docs)
        # Section 3.2 (line 40) references Section 1.1
        refs = {"docs/DSM_4.0.md": [_make_ref("section", "1.1", line=45)]}
        G = build_reference_graph(docs, refs, lookup)
        ref_edges = [
            (u, v, d) for u, v, d in G.edges(data=True)
            if d.get("type") == "REFERENCES"
        ]
        assert len(ref_edges) == 1
        src, tgt, data = ref_edges[0]
        assert src == "docs/DSM_4.0.md:3.2"
        assert tgt == "docs/DSM_1.0.md:1.1"
        assert data["line"] == 45
        assert data["ref_type"] == "section"

    def test_unresolved_reference_creates_no_edge(self):
        docs = [DOC_A]
        lookup = build_section_lookup(docs)
        # Reference to section 99.99 which doesn't exist
        refs = {"docs/DSM_1.0.md": [_make_ref("section", "99.99", line=25)]}
        G = build_reference_graph(docs, refs, lookup)
        ref_edges = [
            (u, v) for u, v, d in G.edges(data=True)
            if d.get("type") == "REFERENCES"
        ]
        assert len(ref_edges) == 0

    def test_reference_enclosing_section_by_line_proximity(self):
        """Reference at line 25 should be enclosed by section 1.2 (line 20), not 1.2.1 (line 30)."""
        docs = [DOC_A, DOC_B]
        lookup = build_section_lookup(docs)
        refs = {"docs/DSM_1.0.md": [_make_ref("section", "3.1", line=25)]}
        G = build_reference_graph(docs, refs, lookup)
        ref_edges = [
            (u, v) for u, v, d in G.edges(data=True)
            if d.get("type") == "REFERENCES"
        ]
        assert len(ref_edges) == 1
        assert ref_edges[0][0] == "docs/DSM_1.0.md:1.2"

    def test_reference_before_first_section_creates_no_edge(self):
        """Reference at line 1 (before any section) has no enclosing section."""
        docs = [DOC_A]
        lookup = build_section_lookup(docs)
        refs = {"docs/DSM_1.0.md": [_make_ref("section", "1.2", line=1)]}
        G = build_reference_graph(docs, refs, lookup)
        ref_edges = [
            (u, v) for u, v, d in G.edges(data=True)
            if d.get("type") == "REFERENCES"
        ]
        assert len(ref_edges) == 0


# ---------------------------------------------------------------------------
# Tests: Multi-document
# ---------------------------------------------------------------------------

class TestMultiDocument:
    def test_multiple_documents_all_nodes_created(self):
        G = build_reference_graph([DOC_A, DOC_B], {}, {})
        file_nodes = [
            n for n, d in G.nodes(data=True) if d.get("type") == "FILE"
        ]
        section_nodes = [
            n for n, d in G.nodes(data=True) if d.get("type") == "SECTION"
        ]
        assert len(file_nodes) == 2
        assert len(section_nodes) == 5  # 3 from A + 2 from B

    def test_cross_file_reference(self):
        """Section in DOC_B references section in DOC_A."""
        docs = [DOC_A, DOC_B]
        lookup = build_section_lookup(docs)
        refs = {"docs/DSM_4.0.md": [_make_ref("section", "1.2.1", line=42)]}
        G = build_reference_graph(docs, refs, lookup)
        ref_edges = [
            (u, v) for u, v, d in G.edges(data=True)
            if d.get("type") == "REFERENCES"
        ]
        assert len(ref_edges) == 1
        assert ref_edges[0][0] == "docs/DSM_4.0.md:3.2"
        assert ref_edges[0][1] == "docs/DSM_1.0.md:1.2.1"


# ---------------------------------------------------------------------------
# Tests: Graph queries (Phase 7.2)
# ---------------------------------------------------------------------------

import networkx as nx

from graph.graph_queries import (
    most_referenced_sections,
    orphan_sections,
    reference_chain,
)


def _build_query_graph():
    """Build a graph with known reference patterns for query testing.

    Structure:
        A -> B (2 refs), A -> C (1 ref), B -> C (1 ref), D (orphan)
    So: C has 2 incoming refs, B has 1, A has 0, D has 0.
    """
    G = nx.DiGraph()
    for node_id in ["f.md:A", "f.md:B", "f.md:C", "f.md:D"]:
        G.add_node(node_id, type="SECTION", title=node_id, number=node_id[-1])
    G.add_node("f.md", type="FILE", title="f.md")
    for s in ["f.md:A", "f.md:B", "f.md:C", "f.md:D"]:
        G.add_edge("f.md", s, type="CONTAINS")
    # A references B twice (two edges with different lines)
    G.add_edge("f.md:A", "f.md:B", type="REFERENCES", line=10, ref_type="section")
    # A references C
    G.add_edge("f.md:A", "f.md:C", type="REFERENCES", line=20, ref_type="section")
    # B references C
    G.add_edge("f.md:B", "f.md:C", type="REFERENCES", line=30, ref_type="section")
    return G


class TestMostReferenced:
    def test_returns_sorted_by_count(self):
        G = _build_query_graph()
        result = most_referenced_sections(G)
        assert len(result) == 2  # B (1 ref) and C (2 refs)
        assert result[0] == ("f.md:C", 2)
        assert result[1] == ("f.md:B", 1)

    def test_respects_n_limit(self):
        G = _build_query_graph()
        result = most_referenced_sections(G, n=1)
        assert len(result) == 1
        assert result[0][0] == "f.md:C"

    def test_empty_graph_returns_empty(self):
        G = nx.DiGraph()
        assert most_referenced_sections(G) == []

    def test_no_references_returns_empty(self):
        G = nx.DiGraph()
        G.add_node("f.md:A", type="SECTION")
        G.add_node("f.md", type="FILE")
        G.add_edge("f.md", "f.md:A", type="CONTAINS")
        assert most_referenced_sections(G) == []


class TestOrphanSections:
    def test_finds_orphan_sections(self):
        G = _build_query_graph()
        result = orphan_sections(G)
        # A and D have zero incoming REFERENCES
        assert sorted(result) == ["f.md:A", "f.md:D"]

    def test_all_referenced_returns_empty(self):
        G = nx.DiGraph()
        G.add_node("f.md:A", type="SECTION")
        G.add_node("f.md:B", type="SECTION")
        G.add_edge("f.md:A", "f.md:B", type="REFERENCES", line=1, ref_type="section")
        G.add_edge("f.md:B", "f.md:A", type="REFERENCES", line=2, ref_type="section")
        assert orphan_sections(G) == []

    def test_empty_graph_returns_empty(self):
        G = nx.DiGraph()
        assert orphan_sections(G) == []


class TestReferenceChain:
    def test_follows_references_bfs(self):
        G = _build_query_graph()
        # A -> B, A -> C, B -> C
        chain = reference_chain(G, "f.md:A")
        # BFS from A: first level is B and C, then from B: C (already visited)
        assert "f.md:B" in chain
        assert "f.md:C" in chain
        assert "f.md:A" not in chain  # source excluded

    def test_orphan_returns_empty_chain(self):
        G = _build_query_graph()
        chain = reference_chain(G, "f.md:D")
        assert chain == []

    def test_max_depth_limits_traversal(self):
        # Build a linear chain: A -> B -> C -> D
        G = nx.DiGraph()
        for n in ["A", "B", "C", "D"]:
            G.add_node(f"f.md:{n}", type="SECTION")
        G.add_edge("f.md:A", "f.md:B", type="REFERENCES", line=1, ref_type="section")
        G.add_edge("f.md:B", "f.md:C", type="REFERENCES", line=2, ref_type="section")
        G.add_edge("f.md:C", "f.md:D", type="REFERENCES", line=3, ref_type="section")
        chain = reference_chain(G, "f.md:A", max_depth=2)
        assert "f.md:B" in chain
        assert "f.md:C" in chain
        assert "f.md:D" not in chain  # depth 3, beyond limit

    def test_handles_cycles(self):
        G = nx.DiGraph()
        G.add_node("f.md:A", type="SECTION")
        G.add_node("f.md:B", type="SECTION")
        G.add_edge("f.md:A", "f.md:B", type="REFERENCES", line=1, ref_type="section")
        G.add_edge("f.md:B", "f.md:A", type="REFERENCES", line=2, ref_type="section")
        chain = reference_chain(G, "f.md:A")
        assert chain == ["f.md:B"]  # visits B, then B->A is already visited

    def test_nonexistent_node_returns_empty(self):
        G = _build_query_graph()
        chain = reference_chain(G, "nonexistent")
        assert chain == []


# ---------------------------------------------------------------------------
# Tests: GraphML export (Phase 7.3)
# ---------------------------------------------------------------------------

from graph.graph_export import export_graphml


class TestGraphExport:
    def test_export_creates_file(self, tmp_path):
        G = _build_query_graph()
        path = tmp_path / "test.graphml"
        export_graphml(G, str(path))
        assert path.exists()
        assert path.stat().st_size > 0

    def test_export_is_valid_graphml(self, tmp_path):
        G = _build_query_graph()
        path = tmp_path / "test.graphml"
        export_graphml(G, str(path))
        # Read it back and verify structure preserved
        H = nx.read_graphml(str(path))
        assert H.number_of_nodes() == G.number_of_nodes()
        assert H.number_of_edges() == G.number_of_edges()
