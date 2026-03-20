"""Tests for DSM_0.2 section index builder."""

import json
from pathlib import Path

import pytest

from analysis.section_index import (
    DispatchEntry,
    SectionEntry,
    SectionIndex,
    build_section_index,
)


@pytest.fixture()
def dsm_dir(tmp_path: Path) -> Path:
    """Create a minimal DSM_0.2 file set for testing."""
    core = tmp_path / "DSM_0.2_Custom_Instructions_v1.1.md"
    core.write_text(
        """\
**Version:** v1.3.69
**Architecture:** Slim core + 4 on-demand modules (see Module Dispatch Table)

## Session Transcript Protocol

Record all reasoning in the session transcript.

### Reasoning Delimiter Format

Use the delimiter format for every thinking block.

## Pre-Generation Brief Protocol

Explain what and why before creating artifacts.

### Gate 1: Concept Approval

Present the concept for approval.

### Gate 2: Implementation Approval

Present the implementation plan.

## Inclusive Language

Use inclusive, bias-free language in all outputs.

## Active Suggestion Protocol

When invited, always offer suggestions before proceeding.

## Ecosystem Path Registry

Central paths for the DSM ecosystem.

## Three-Level Branching Strategy

A universal branching model for all DSM projects.

### Level 1: Main Branch (`main` / `master`)

The production line.

### Level 2: Session Branch

Created at every session start.

## Read-Only Access Within Repository

Never modify files outside the project directory.

## Module Dispatch Table

DSM_0.2 protocols are split into this core file (always loaded via `@`) and
four on-demand modules.

| Protocol | Trigger | Module |
|----------|---------|--------|
| DSM Feedback Tracking | Capturing methodology feedback | [A](DSM_0.2.A_Session_Lifecycle.md) |
| Composition Challenge Protocol | Producing a collection of 2+ items | [B](DSM_0.2.B_Artifact_Creation.md) |
| Secret Exposure Prevention | Staging files for git commit | [C](DSM_0.2.C_Security_Safety.md) |
| Step 0: Situational Assessment | New project onboarding | [D](DSM_0.2.D_Research_Onboarding.md) |
""",
    )

    module_a = tmp_path / "DSM_0.2.A_Session_Lifecycle.md"
    module_a.write_text(
        """\
# DSM_0.2 Module A: Session Lifecycle

## 1. DSM Feedback Tracking

Track methodology observations and backlog proposals.

### Feedback File Naming

Use per-session files with date prefix.

## 2. Lightweight Session Lifecycle

Continuation sessions with known task.
""",
    )

    module_b = tmp_path / "DSM_0.2.B_Artifact_Creation.md"
    module_b.write_text(
        """\
# DSM_0.2 Module B: Artifact Creation

## 1. Composition Challenge Protocol

Reason about collections before producing them.
""",
    )

    return tmp_path


class TestBuildSectionIndex:
    """Tests for build_section_index()."""

    def test_returns_section_index_with_version(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        assert isinstance(index, SectionIndex)
        assert index.version == "v1.3.69"

    def test_date_is_populated(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        assert index.date  # non-empty string

    def test_core_sections_classified_as_always_load(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        core_sections = [s for s in index.sections if s.module == "core"]
        assert len(core_sections) > 0
        for section in core_sections:
            assert section.designed_classification == "always-load"

    def test_module_sections_classified_as_on_demand(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        module_sections = [s for s in index.sections if s.module != "core"]
        assert len(module_sections) > 0
        for section in module_sections:
            assert section.designed_classification == "on-demand"

    def test_extracts_core_headings(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        core_ids = {s.section_id for s in index.sections if s.module == "core"}
        assert "session-transcript-protocol" in core_ids
        assert "pre-generation-brief-protocol" in core_ids
        assert "inclusive-language" in core_ids
        assert "active-suggestion-protocol" in core_ids
        assert "three-level-branching-strategy" in core_ids
        assert "read-only-access-within-repository" in core_ids

    def test_extracts_sub_headings(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        ids = {s.section_id for s in index.sections}
        assert "reasoning-delimiter-format" in ids
        assert "gate-1-concept-approval" in ids
        assert "gate-2-implementation-approval" in ids
        assert "level-1-main-branch-main-master" in ids
        assert "level-2-session-branch" in ids

    def test_extracts_module_a_headings(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        mod_a = [s for s in index.sections if s.module == "A"]
        mod_a_ids = {s.section_id for s in mod_a}
        assert "1-dsm-feedback-tracking" in mod_a_ids
        assert "feedback-file-naming" in mod_a_ids
        assert "2-lightweight-session-lifecycle" in mod_a_ids

    def test_extracts_module_b_headings(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        mod_b = [s for s in index.sections if s.module == "B"]
        mod_b_ids = {s.section_id for s in mod_b}
        assert "1-composition-challenge-protocol" in mod_b_ids

    def test_section_entry_has_line_number(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        for section in index.sections:
            assert section.line_number >= 1

    def test_section_entry_has_heading_level(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        levels = {s.section_id: s.level for s in index.sections}
        assert levels["session-transcript-protocol"] == 2
        assert levels["reasoning-delimiter-format"] == 3
        assert levels["gate-1-concept-approval"] == 3

    def test_section_entry_has_file_path(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        core_section = next(
            s for s in index.sections if s.section_id == "session-transcript-protocol"
        )
        assert "DSM_0.2_Custom_Instructions" in core_section.file

    def test_dispatch_table_parsed(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        assert len(index.dispatch_table) == 4
        protocols = {d.protocol for d in index.dispatch_table}
        assert "DSM Feedback Tracking" in protocols
        assert "Composition Challenge Protocol" in protocols
        assert "Secret Exposure Prevention" in protocols
        assert "Step 0: Situational Assessment" in protocols

    def test_dispatch_entry_has_trigger_and_module(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        feedback = next(
            d for d in index.dispatch_table if d.protocol == "DSM Feedback Tracking"
        )
        assert feedback.trigger == "Capturing methodology feedback"
        assert feedback.module == "A"

    def test_module_dispatch_table_not_in_sections(self, dsm_dir: Path) -> None:
        """The dispatch table heading itself is metadata, not a protocol section."""
        index = build_section_index(dsm_dir, "v1.3.69")
        ids = {s.section_id for s in index.sections}
        assert "module-dispatch-table" not in ids

    def test_module_title_heading_not_in_sections(self, dsm_dir: Path) -> None:
        """Module file H1 titles (e.g., 'DSM_0.2 Module A: ...') are not protocol sections."""
        index = build_section_index(dsm_dir, "v1.3.69")
        ids = {s.section_id for s in index.sections}
        assert "dsm02-module-a-session-lifecycle" not in ids
        assert "dsm02-module-b-artifact-creation" not in ids

    def test_slugify_consistency(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        eco = next(
            s for s in index.sections if s.section_id == "ecosystem-path-registry"
        )
        assert eco.heading == "Ecosystem Path Registry"

    def test_to_json_roundtrip(self, dsm_dir: Path) -> None:
        index = build_section_index(dsm_dir, "v1.3.69")
        json_str = index.model_dump_json(indent=2)
        parsed = json.loads(json_str)
        assert parsed["version"] == "v1.3.69"
        assert len(parsed["sections"]) == len(index.sections)
        assert len(parsed["dispatch_table"]) == len(index.dispatch_table)
