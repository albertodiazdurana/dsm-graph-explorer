"""Tests for heading-based section detection (BL-042, Sprint 13).

Verifies that the parser and graph builder handle markdown headings
(## Title) as sections, not just numbered sections (### 2.1 Title).
TDD: tests written before implementation.
"""

import pytest

from parser.markdown_parser import ParsedDocument, Section, parse_markdown_content
from graph.graph_builder import build_reference_graph


# ---------------------------------------------------------------------------
# Test fixtures: heading-only document (like DSM_0.2)
# ---------------------------------------------------------------------------

HEADING_ONLY_DOC = """\
# Project Configuration

This document describes project configuration.

## Session Transcript Protocol

Append thinking to session transcript before acting.

### Per-Turn Flow

1. First tool call: append thinking
2. Agent acts
3. Last tool call: append output

## Pre-Generation Brief Protocol

Before creating any artifact, explain what and why.

### Gate 1: Concept Approval

Explain the artifact to be created.

### Gate 2: Implementation Approval

Create the artifact using Write/Edit tools.

## Inclusive Language

All documents must use inclusive, neutral language.
"""

MIXED_DOC = """\
# 1 Introduction

Overview of the methodology.

## 1.1 Scope

This section covers scope.

## Unnumbered Context Section

Additional context without a number.

## 2.1 Development Protocol

How to develop.

### 2.1.1 TDD Approach

Write tests first.
"""

NESTED_HEADINGS_DOC = """\
# Top Level

## Chapter One

### Section Alpha

Content alpha.

### Section Beta

Content beta.

## Chapter Two

### Section Gamma

Content gamma.

#### Subsection Deep

Very deep content.
"""


# ---------------------------------------------------------------------------
# Tests: Parser extracts heading-based sections
# ---------------------------------------------------------------------------


class TestParserHeadingSections:
    """Verify the parser already captures unnumbered headings."""

    def test_heading_only_doc_extracts_all_sections(self):
        result = parse_markdown_content(HEADING_ONLY_DOC, "config.md")
        assert len(result.sections) == 7

    def test_heading_sections_have_none_number(self):
        result = parse_markdown_content(HEADING_ONLY_DOC, "config.md")
        for section in result.sections:
            assert section.number is None

    def test_heading_levels_correct(self):
        result = parse_markdown_content(HEADING_ONLY_DOC, "config.md")
        levels = [s.level for s in result.sections]
        assert levels == [1, 2, 3, 2, 3, 3, 2]

    def test_heading_titles_correct(self):
        result = parse_markdown_content(HEADING_ONLY_DOC, "config.md")
        titles = [s.title for s in result.sections]
        assert titles == [
            "Project Configuration",
            "Session Transcript Protocol",
            "Per-Turn Flow",
            "Pre-Generation Brief Protocol",
            "Gate 1: Concept Approval",
            "Gate 2: Implementation Approval",
            "Inclusive Language",
        ]

    def test_heading_line_numbers_monotonic(self):
        result = parse_markdown_content(HEADING_ONLY_DOC, "config.md")
        lines = [s.line for s in result.sections]
        assert lines == sorted(lines)
        assert all(ln > 0 for ln in lines)

    def test_heading_context_excerpts_populated(self):
        result = parse_markdown_content(HEADING_ONLY_DOC, "config.md")
        # First heading (h1) has prose after it
        top = result.sections[0]
        assert "project configuration" in top.context_excerpt.lower()

    def test_mixed_doc_captures_both_styles(self):
        result = parse_markdown_content(MIXED_DOC, "mixed.md")
        numbered = [s for s in result.sections if s.number is not None]
        unnumbered = [s for s in result.sections if s.number is None]
        assert len(numbered) == 4  # 1, 1.1, 2.1, 2.1.1
        assert len(unnumbered) == 1  # "Unnumbered Context Section"


# ---------------------------------------------------------------------------
# Tests: Graph builder includes heading-based sections
# ---------------------------------------------------------------------------


class TestGraphHeadingSections:
    """Verify graph builder creates nodes for heading-based sections."""

    def _build_heading_graph(self):
        doc = parse_markdown_content(HEADING_ONLY_DOC, "config.md")
        return build_reference_graph([doc], {}, {})

    def test_heading_sections_become_graph_nodes(self):
        G = self._build_heading_graph()
        section_nodes = [
            n for n, d in G.nodes(data=True) if d.get("type") == "SECTION"
        ]
        # 7 headings should produce 7 SECTION nodes
        assert len(section_nodes) == 7

    def test_file_node_exists(self):
        G = self._build_heading_graph()
        file_nodes = [
            n for n, d in G.nodes(data=True) if d.get("type") == "FILE"
        ]
        assert len(file_nodes) == 1

    def test_contains_edges_for_heading_sections(self):
        G = self._build_heading_graph()
        contains = [
            (u, v) for u, v, d in G.edges(data=True)
            if d.get("type") == "CONTAINS"
        ]
        assert len(contains) == 7

    def test_heading_node_has_title_attribute(self):
        G = self._build_heading_graph()
        section_nodes = {
            n: d for n, d in G.nodes(data=True) if d.get("type") == "SECTION"
        }
        titles = [d["title"] for d in section_nodes.values()]
        assert "Session Transcript Protocol" in titles
        assert "Pre-Generation Brief Protocol" in titles
        assert "Inclusive Language" in titles

    def test_heading_node_has_level_attribute(self):
        G = self._build_heading_graph()
        section_nodes = {
            n: d for n, d in G.nodes(data=True) if d.get("type") == "SECTION"
        }
        levels = {d["title"]: d["level"] for d in section_nodes.values()}
        assert levels["Project Configuration"] == 1
        assert levels["Session Transcript Protocol"] == 2
        assert levels["Per-Turn Flow"] == 3

    def test_heading_node_has_line_attribute(self):
        G = self._build_heading_graph()
        section_nodes = {
            n: d for n, d in G.nodes(data=True) if d.get("type") == "SECTION"
        }
        for data in section_nodes.values():
            assert "line" in data
            assert data["line"] > 0

    def test_heading_node_id_is_unique(self):
        G = self._build_heading_graph()
        section_nodes = [
            n for n, d in G.nodes(data=True) if d.get("type") == "SECTION"
        ]
        assert len(section_nodes) == len(set(section_nodes))

    def test_mixed_doc_graph_includes_both_styles(self):
        doc = parse_markdown_content(MIXED_DOC, "mixed.md")
        G = build_reference_graph([doc], {}, {})
        section_nodes = [
            n for n, d in G.nodes(data=True) if d.get("type") == "SECTION"
        ]
        # 4 numbered + 1 unnumbered = 5 sections
        assert len(section_nodes) == 5

    def test_numbered_sections_keep_number_based_id(self):
        doc = parse_markdown_content(MIXED_DOC, "mixed.md")
        G = build_reference_graph([doc], {}, {})
        assert G.has_node("mixed.md:1")
        assert G.has_node("mixed.md:1.1")
        assert G.has_node("mixed.md:2.1")
        assert G.has_node("mixed.md:2.1.1")


# ---------------------------------------------------------------------------
# Tests: Nested heading hierarchy
# ---------------------------------------------------------------------------


class TestNestedHeadingHierarchy:
    """Verify correct handling of deeply nested heading structures."""

    def test_four_levels_of_headings(self):
        doc = parse_markdown_content(NESTED_HEADINGS_DOC, "nested.md")
        G = build_reference_graph([doc], {}, {})
        section_nodes = [
            n for n, d in G.nodes(data=True) if d.get("type") == "SECTION"
        ]
        # 1 h1 + 2 h2 + 3 h3 + 1 h4 = 7
        assert len(section_nodes) == 7

    def test_h4_section_has_level_4(self):
        doc = parse_markdown_content(NESTED_HEADINGS_DOC, "nested.md")
        G = build_reference_graph([doc], {}, {})
        section_nodes = {
            n: d for n, d in G.nodes(data=True) if d.get("type") == "SECTION"
        }
        deep = [d for d in section_nodes.values() if d["title"] == "Subsection Deep"]
        assert len(deep) == 1
        assert deep[0]["level"] == 4


# ---------------------------------------------------------------------------
# Tests: Heading reference edges in graph
# ---------------------------------------------------------------------------


class TestGraphHeadingRefEdges:
    """Verify graph builder creates REFERENCES edges for heading refs."""

    def test_heading_ref_creates_edge(self):
        """A heading ref from prose to a defined heading produces an edge."""
        from parser.cross_ref_extractor import CrossReference

        doc = parse_markdown_content(HEADING_ONLY_DOC, "config.md")
        refs = {
            "config.md": [
                CrossReference(
                    type="heading",
                    target="Inclusive Language",
                    line=5,
                    context="See Inclusive Language for guidelines.",
                ),
            ],
        }
        G = build_reference_graph([doc], refs, {})
        ref_edges = [
            (u, v, d) for u, v, d in G.edges(data=True)
            if d.get("type") == "REFERENCES"
        ]
        assert len(ref_edges) == 1

    def test_heading_ref_edge_has_correct_attributes(self):
        """REFERENCES edge for heading ref has line and ref_type."""
        from parser.cross_ref_extractor import CrossReference

        doc = parse_markdown_content(HEADING_ONLY_DOC, "config.md")
        refs = {
            "config.md": [
                CrossReference(
                    type="heading",
                    target="Session Transcript Protocol",
                    line=46,
                    context="Follow Session Transcript Protocol.",
                ),
            ],
        }
        G = build_reference_graph([doc], refs, {})
        ref_edges = [
            (u, v, d) for u, v, d in G.edges(data=True)
            if d.get("type") == "REFERENCES"
        ]
        assert len(ref_edges) == 1
        _, _, data = ref_edges[0]
        assert data["ref_type"] == "heading"
        assert data["line"] == 46

    def test_heading_ref_cross_file_edge(self):
        """Heading defined in one file, referenced from another."""
        from parser.cross_ref_extractor import CrossReference

        defs_doc = parse_markdown_content(HEADING_ONLY_DOC, "config.md")
        prose_doc = parse_markdown_content(
            "# Notes\n\nSee Pre-Generation Brief Protocol for details.\n",
            "notes.md",
        )
        refs = {
            "notes.md": [
                CrossReference(
                    type="heading",
                    target="Pre-Generation Brief Protocol",
                    line=3,
                    context="See Pre-Generation Brief Protocol for details.",
                ),
            ],
        }
        G = build_reference_graph([defs_doc, prose_doc], refs, {})
        ref_edges = [
            (u, v, d) for u, v, d in G.edges(data=True)
            if d.get("type") == "REFERENCES"
        ]
        assert len(ref_edges) == 1
        src, tgt, _ = ref_edges[0]
        assert src.startswith("notes.md:")
        assert tgt.startswith("config.md:")

    def test_unmatched_heading_ref_no_edge(self):
        """A heading ref to a nonexistent heading produces no edge."""
        from parser.cross_ref_extractor import CrossReference

        doc = parse_markdown_content(HEADING_ONLY_DOC, "config.md")
        refs = {
            "config.md": [
                CrossReference(
                    type="heading",
                    target="Nonexistent Heading",
                    line=5,
                    context="See Nonexistent Heading.",
                ),
            ],
        }
        G = build_reference_graph([doc], refs, {})
        ref_edges = [
            (u, v, d) for u, v, d in G.edges(data=True)
            if d.get("type") == "REFERENCES"
        ]
        assert len(ref_edges) == 0

    def test_heading_ref_case_insensitive(self):
        """Heading ref resolution is case-insensitive via slugify."""
        from parser.cross_ref_extractor import CrossReference

        doc = parse_markdown_content(HEADING_ONLY_DOC, "config.md")
        refs = {
            "config.md": [
                CrossReference(
                    type="heading",
                    target="inclusive language",
                    line=5,
                    context="See inclusive language.",
                ),
            ],
        }
        G = build_reference_graph([doc], refs, {})
        ref_edges = [
            (u, v, d) for u, v, d in G.edges(data=True)
            if d.get("type") == "REFERENCES"
        ]
        assert len(ref_edges) == 1
