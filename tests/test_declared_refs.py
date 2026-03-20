"""Tests for Layer 1: CLAUDE.md declared reference extraction."""

from pathlib import Path

import pytest

from analysis.declared_refs import DeclaredReference, extract_declared_references
from analysis.section_index import SectionIndex, SectionEntry, DispatchEntry


@pytest.fixture()
def section_index() -> SectionIndex:
    """A minimal section index for matching against."""
    return SectionIndex(
        version="v1.3.69",
        date="2026-03-20",
        sections=[
            SectionEntry(
                section_id="session-transcript-protocol",
                heading="Session Transcript Protocol",
                file="DSM_0.2_Custom_Instructions_v1.1.md",
                module="core",
                designed_classification="always-load",
                level=2,
                line_number=198,
            ),
            SectionEntry(
                section_id="reasoning-delimiter-format",
                heading="Reasoning Delimiter Format",
                file="DSM_0.2_Custom_Instructions_v1.1.md",
                module="core",
                designed_classification="always-load",
                level=2,
                line_number=172,
            ),
            SectionEntry(
                section_id="pre-generation-brief-protocol",
                heading="Pre-Generation Brief Protocol",
                file="DSM_0.2_Custom_Instructions_v1.1.md",
                module="core",
                designed_classification="always-load",
                level=2,
                line_number=293,
            ),
            SectionEntry(
                section_id="inclusive-language",
                heading="Inclusive Language",
                file="DSM_0.2_Custom_Instructions_v1.1.md",
                module="core",
                designed_classification="always-load",
                level=2,
                line_number=514,
            ),
            SectionEntry(
                section_id="active-suggestion-protocol",
                heading="Active Suggestion Protocol",
                file="DSM_0.2_Custom_Instructions_v1.1.md",
                module="core",
                designed_classification="always-load",
                level=2,
                line_number=605,
            ),
            SectionEntry(
                section_id="ecosystem-path-registry",
                heading="Ecosystem Path Registry",
                file="DSM_0.2_Custom_Instructions_v1.1.md",
                module="core",
                designed_classification="always-load",
                level=2,
                line_number=696,
            ),
            SectionEntry(
                section_id="three-level-branching-strategy",
                heading="Three-Level Branching Strategy",
                file="DSM_0.2_Custom_Instructions_v1.1.md",
                module="core",
                designed_classification="always-load",
                level=2,
                line_number=767,
            ),
            SectionEntry(
                section_id="11-sprint-cadence-and-feedback-boundaries",
                heading="11. Sprint Cadence and Feedback Boundaries",
                file="DSM_0.2.A_Session_Lifecycle.md",
                module="A",
                designed_classification="on-demand",
                level=2,
                line_number=839,
            ),
            SectionEntry(
                section_id="1-composition-challenge-protocol",
                heading="1. Composition Challenge Protocol",
                file="DSM_0.2.B_Artifact_Creation.md",
                module="B",
                designed_classification="on-demand",
                level=2,
                line_number=14,
            ),
        ],
        dispatch_table=[],
    )


@pytest.fixture()
def claude_md(tmp_path: Path) -> Path:
    """A synthetic CLAUDE.md mimicking graph-explorer's reference patterns."""
    md = tmp_path / "CLAUDE.md"
    md.write_text(
        """\
@~/dsm-agentic-ai-data-science-methodology/DSM_0.2_Custom_Instructions_v1.1.md

# Project: Test Spoke

**Type:** Software Engineering (DSM 4.0 Track)
**Key DSM Sections**: Section 3 (Development Protocol), Section 4 (Tests vs Capability Experiments)

## Session Transcript Protocol (reinforces inherited protocol)
- Append thinking to `.claude/session-transcript.md` BEFORE acting
- Use Reasoning Delimiter Format for every thinking block

## Pre-Generation Brief Protocol (reinforces inherited protocol)

Before creating any artifact, explain what and why.

## Development Approach

- Follow the Sprint Boundary Checklist (DSM 2.0 Template 8)
- Blog as deliverable: Document journey throughout (Section 2.5.6-2.5.8)

## Blog Integration

Following Section 2.5.6 (Blog/Communication Deliverable Process)

## Custom Section

This section mentions the Active Suggestion Protocol in passing.
It also references the Composition Challenge Protocol from Module B.
The Ecosystem Path Registry is used for path resolution.
""",
    )
    return md


class TestExtractDeclaredReferences:
    """Tests for extract_declared_references()."""

    def test_detects_at_import(
        self, claude_md: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_declared_references(claude_md, section_index)
        at_imports = [r for r in refs if r.match_type == "at-import"]
        assert len(at_imports) >= 1
        assert any("DSM_0.2" in r.context for r in at_imports)

    def test_detects_reinforcement_blocks(
        self, claude_md: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_declared_references(claude_md, section_index)
        reinforcements = [r for r in refs if r.match_type == "reinforcement"]
        ids = {r.section_id for r in reinforcements}
        assert "session-transcript-protocol" in ids
        assert "pre-generation-brief-protocol" in ids

    def test_detects_protocol_name_mentions(
        self, claude_md: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_declared_references(claude_md, section_index)
        mentions = [r for r in refs if r.match_type == "name-mention"]
        ids = {r.section_id for r in mentions}
        assert "active-suggestion-protocol" in ids
        assert "ecosystem-path-registry" in ids

    def test_detects_reasoning_delimiter_format_mention(
        self, claude_md: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_declared_references(claude_md, section_index)
        ids = {r.section_id for r in refs}
        assert "reasoning-delimiter-format" in ids

    def test_detects_cross_module_name_mention(
        self, claude_md: Path, section_index: SectionIndex
    ) -> None:
        """References to module protocols (not just core) are detected."""
        refs = extract_declared_references(claude_md, section_index)
        ids = {r.section_id for r in refs}
        assert "1-composition-challenge-protocol" in ids

    def test_reference_has_line_number(
        self, claude_md: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_declared_references(claude_md, section_index)
        for ref in refs:
            assert ref.line_number >= 1

    def test_reference_has_context(
        self, claude_md: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_declared_references(claude_md, section_index)
        for ref in refs:
            assert ref.context  # non-empty string

    def test_no_duplicate_refs_per_line(
        self, claude_md: Path, section_index: SectionIndex
    ) -> None:
        """A section mentioned once on a line should produce one reference, not multiple."""
        refs = extract_declared_references(claude_md, section_index)
        seen = set()
        for ref in refs:
            key = (ref.section_id, ref.line_number, ref.match_type)
            assert key not in seen, f"Duplicate: {key}"
            seen.add(key)

    def test_empty_file_returns_no_refs(
        self, tmp_path: Path, section_index: SectionIndex
    ) -> None:
        empty = tmp_path / "empty.md"
        empty.write_text("")
        refs = extract_declared_references(empty, section_index)
        assert refs == []

    def test_unique_section_ids_collected(
        self, claude_md: Path, section_index: SectionIndex
    ) -> None:
        """Verify we can get unique referenced section IDs from results."""
        refs = extract_declared_references(claude_md, section_index)
        unique_ids = {r.section_id for r in refs}
        # At minimum: the reinforcement blocks + name mentions
        assert len(unique_ids) >= 4
