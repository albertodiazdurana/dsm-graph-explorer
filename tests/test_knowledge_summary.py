"""Tests for knowledge summary generation (Sprint 16, BL-302 Phase 1).

TDD: tests written before implementation.
Tests cover the four summary components (P1 hierarchy, P1 hubs,
P2 hotspots, P2 orphans) and the combined summary generator.
"""

import networkx as nx
import pytest


def _build_summary_graph():
    """Build a graph with known structure for summary testing.

    Structure:
        core.md       -> 3 sections (1.1, 1.2, 1.3), levels 2, 2, 3
        helpers.md    -> 2 sections (2.1, 2.2), levels 2, 2
        orphan.md     -> 1 section (h:intro), level 2

    References:
        helpers.md:2.1 -> core.md:1.1   (cross-file)
        helpers.md:2.2 -> core.md:1.1   (cross-file, same target)
        helpers.md:2.2 -> core.md:1.2   (cross-file)
        core.md:1.2    -> core.md:1.3   (intra-file)

    Expected results:
        Hubs: core.md (3 incoming refs to its sections), helpers.md (1)
        Hotspots: core.md:1.1 (2 refs), core.md:1.2 (1 ref), core.md:1.3 (1 ref)
        Orphans: orphan.md (zero incoming refs to any section)
        Hierarchy: 3 files, 6 sections
    """
    G = nx.DiGraph()

    # FILE nodes
    G.add_node("core.md", type="FILE", title="core.md")
    G.add_node("helpers.md", type="FILE", title="helpers.md")
    G.add_node("orphan.md", type="FILE", title="orphan.md")

    # SECTION nodes for core.md
    G.add_node("core.md:1.1", type="SECTION", title="Introduction",
               number="1.1", file="core.md", line=5, level=2,
               context_excerpt="Core intro text")
    G.add_node("core.md:1.2", type="SECTION", title="Architecture",
               number="1.2", file="core.md", line=20, level=2,
               context_excerpt="Architecture overview")
    G.add_node("core.md:1.3", type="SECTION", title="Components",
               number="1.3", file="core.md", line=35, level=3,
               context_excerpt="Component details")

    # SECTION nodes for helpers.md
    G.add_node("helpers.md:2.1", type="SECTION", title="Utility Functions",
               number="2.1", file="helpers.md", line=5, level=2,
               context_excerpt="Utility functions overview")
    G.add_node("helpers.md:2.2", type="SECTION", title="Validation Helpers",
               number="2.2", file="helpers.md", line=25, level=2,
               context_excerpt="Validation helper functions")

    # SECTION nodes for orphan.md (unnumbered heading)
    G.add_node("orphan.md:h:intro", type="SECTION", title="Intro",
               number=None, file="orphan.md", line=1, level=2,
               context_excerpt="Orphan intro")

    # CONTAINS edges
    G.add_edge("core.md", "core.md:1.1", type="CONTAINS")
    G.add_edge("core.md", "core.md:1.2", type="CONTAINS")
    G.add_edge("core.md", "core.md:1.3", type="CONTAINS")
    G.add_edge("helpers.md", "helpers.md:2.1", type="CONTAINS")
    G.add_edge("helpers.md", "helpers.md:2.2", type="CONTAINS")
    G.add_edge("orphan.md", "orphan.md:h:intro", type="CONTAINS")

    # REFERENCES edges
    G.add_edge("helpers.md:2.1", "core.md:1.1", type="REFERENCES",
               line=10, ref_type="section")
    G.add_edge("helpers.md:2.2", "core.md:1.1", type="REFERENCES",
               line=30, ref_type="section")
    G.add_edge("helpers.md:2.2", "core.md:1.2", type="REFERENCES",
               line=32, ref_type="section")
    G.add_edge("core.md:1.2", "core.md:1.3", type="REFERENCES",
               line=22, ref_type="section")

    return G


# ---------------------------------------------------------------------------
# Tests: generate_hierarchy
# ---------------------------------------------------------------------------

from analysis.knowledge_summary import (
    generate_hierarchy,
    generate_hub_documents,
    generate_hotspots,
    generate_orphans,
    generate_knowledge_summary,
)


class TestGenerateHierarchy:
    def test_contains_all_files(self):
        G = _build_summary_graph()
        result = generate_hierarchy(G)
        assert "core.md" in result
        assert "helpers.md" in result
        assert "orphan.md" in result

    def test_groups_by_directory(self):
        G = _build_summary_graph()
        result = generate_hierarchy(G)
        # All test files are in root dir "."
        assert "**./***" in result or "file" in result.lower()

    def test_shows_section_counts(self):
        G = _build_summary_graph()
        result = generate_hierarchy(G)
        assert "3 sections" in result  # core.md has 3
        assert "2 sections" in result  # helpers.md has 2

    def test_shows_path(self):
        G = _build_summary_graph()
        result = generate_hierarchy(G)
        assert "path:" in result

    def test_respects_top_files_limit(self):
        G = _build_summary_graph()
        # With top_files_per_dir=1, only 1 file per dir shown
        result = generate_hierarchy(G, top_files_per_dir=1)
        assert "... and" in result

    def test_returns_string(self):
        G = _build_summary_graph()
        result = generate_hierarchy(G)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_empty_graph(self):
        G = nx.DiGraph()
        result = generate_hierarchy(G)
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Tests: generate_hub_documents
# ---------------------------------------------------------------------------

class TestGenerateHubDocuments:
    def test_core_is_top_hub(self):
        G = _build_summary_graph()
        result = generate_hub_documents(G, n=10)
        # core.md has 3 incoming refs to its sections
        assert "core.md" in result

    def test_orphan_not_in_hubs(self):
        G = _build_summary_graph()
        result = generate_hub_documents(G, n=10)
        # orphan.md has zero incoming refs, should not appear as a hub
        # (it may appear if we list all files, but not as a top hub)
        lines = result.strip().split("\n")
        hub_lines = [l for l in lines if "orphan.md" in l]
        # If it appears at all, it should be with 0 refs
        for line in hub_lines:
            assert "0" in line or not hub_lines

    def test_respects_n_limit(self):
        G = _build_summary_graph()
        result = generate_hub_documents(G, n=1)
        # Only top 1 hub, should be core.md
        assert "core.md" in result

    def test_returns_string(self):
        G = _build_summary_graph()
        result = generate_hub_documents(G, n=10)
        assert isinstance(result, str)

    def test_empty_graph(self):
        G = nx.DiGraph()
        result = generate_hub_documents(G, n=10)
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Tests: generate_hotspots
# ---------------------------------------------------------------------------

class TestGenerateHotspots:
    def test_finds_high_ref_sections(self):
        G = _build_summary_graph()
        # core.md:1.1 has 2 incoming refs
        result = generate_hotspots(G, threshold=2)
        assert "Introduction" in result or "1.1" in result

    def test_excludes_below_threshold(self):
        G = _build_summary_graph()
        # With threshold=5, nothing qualifies
        result = generate_hotspots(G, threshold=5)
        assert "Introduction" not in result
        assert "1.1" not in result

    def test_low_threshold_includes_more(self):
        G = _build_summary_graph()
        result = generate_hotspots(G, threshold=1)
        # All three referenced sections should appear
        assert "1.1" in result or "Introduction" in result
        assert "1.2" in result or "Architecture" in result

    def test_returns_string(self):
        G = _build_summary_graph()
        result = generate_hotspots(G, threshold=10)
        assert isinstance(result, str)

    def test_empty_graph(self):
        G = nx.DiGraph()
        result = generate_hotspots(G, threshold=10)
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Tests: generate_orphans
# ---------------------------------------------------------------------------

class TestGenerateOrphans:
    def test_finds_orphan_files(self):
        G = _build_summary_graph()
        result = generate_orphans(G)
        assert "orphan.md" in result

    def test_hub_not_orphan(self):
        G = _build_summary_graph()
        result = generate_orphans(G)
        # core.md has incoming refs, should not be listed as orphan
        assert "core.md" not in result

    def test_returns_string(self):
        G = _build_summary_graph()
        result = generate_orphans(G)
        assert isinstance(result, str)

    def test_empty_graph(self):
        G = nx.DiGraph()
        result = generate_orphans(G)
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Tests: generate_knowledge_summary (integration)
# ---------------------------------------------------------------------------

class TestGenerateKnowledgeSummary:
    def test_contains_all_sections(self):
        G = _build_summary_graph()
        result = generate_knowledge_summary(G)
        assert "## Document Hierarchy" in result
        assert "## Hub Documents" in result
        assert "## Cross-Reference Hotspots" in result
        assert "## Orphan Files" in result

    def test_has_header(self):
        G = _build_summary_graph()
        result = generate_knowledge_summary(G)
        assert result.startswith("# Knowledge Summary")

    def test_returns_string(self):
        G = _build_summary_graph()
        result = generate_knowledge_summary(G)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_empty_graph(self):
        G = nx.DiGraph()
        result = generate_knowledge_summary(G)
        assert isinstance(result, str)
        assert "# Knowledge Summary" in result
