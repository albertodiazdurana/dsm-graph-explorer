"""Tests for Layer 2: skill definition prescribed reference extraction."""

from pathlib import Path

import pytest

from analysis.prescribed_refs import PrescribedReference, extract_prescribed_references
from analysis.section_index import SectionEntry, SectionIndex


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
                section_id="three-level-branching-strategy",
                heading="Three-Level Branching Strategy",
                file="DSM_0.2_Custom_Instructions_v1.1.md",
                module="core",
                designed_classification="always-load",
                level=2,
                line_number=767,
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
                section_id="8-reasoning-lessons-protocol",
                heading="8. Reasoning Lessons Protocol",
                file="DSM_0.2.A_Session_Lifecycle.md",
                module="A",
                designed_classification="on-demand",
                level=2,
                line_number=558,
            ),
            SectionEntry(
                section_id="1-session-end-inbox-push",
                heading="1. Session-End Inbox Push",
                file="DSM_0.2.A_Session_Lifecycle.md",
                module="A",
                designed_classification="on-demand",
                level=2,
                line_number=14,
            ),
        ],
        dispatch_table=[],
    )


@pytest.fixture()
def commands_dir(tmp_path: Path) -> Path:
    """Create synthetic skill definition files."""
    cmd_dir = tmp_path / "commands"
    cmd_dir.mkdir()

    go = cmd_dir / "dsm-go.md"
    go.write_text(
        """\
Resume a DSM session. Read context and report current state.

## Step 0: Session Branch Setup

This step implements the Three-Level Branching Strategy (DSM_0.2).

## Step 9: Behavioral activation

Follow the Session Transcript Protocol from this point forward.
""",
    )

    wrap = cmd_dir / "dsm-wrap-up.md"
    wrap.write_text(
        """\
Execute the DSM session wrap-up checklist.

0. **Extract reasoning lessons:** Follow the Reasoning Lessons Protocol.

1. **README check:** Use the Ecosystem Path Registry for portfolio path.

6. **Feedback push:** Follow Session-End Inbox Push procedure.
""",
    )

    # A non-skill file should be ignored.
    readme = cmd_dir / "README.md"
    readme.write_text("This is not a skill file.\n")

    return cmd_dir


class TestExtractPrescribedReferences:
    """Tests for extract_prescribed_references()."""

    def test_detects_references_in_dsm_go(
        self, commands_dir: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_prescribed_references(commands_dir, section_index)
        go_refs = [r for r in refs if r.skill_file == "dsm-go.md"]
        ids = {r.section_id for r in go_refs}
        assert "three-level-branching-strategy" in ids
        assert "session-transcript-protocol" in ids

    def test_detects_references_in_dsm_wrap_up(
        self, commands_dir: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_prescribed_references(commands_dir, section_index)
        wrap_refs = [r for r in refs if r.skill_file == "dsm-wrap-up.md"]
        ids = {r.section_id for r in wrap_refs}
        assert "8-reasoning-lessons-protocol" in ids
        assert "ecosystem-path-registry" in ids
        assert "1-session-end-inbox-push" in ids

    def test_reference_has_skill_file(
        self, commands_dir: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_prescribed_references(commands_dir, section_index)
        for ref in refs:
            assert ref.skill_file.endswith(".md")

    def test_reference_has_line_number_and_context(
        self, commands_dir: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_prescribed_references(commands_dir, section_index)
        for ref in refs:
            assert ref.line_number >= 1
            assert ref.context

    def test_only_scans_dsm_prefixed_files(
        self, commands_dir: Path, section_index: SectionIndex
    ) -> None:
        """README.md and other non-dsm files should be skipped."""
        refs = extract_prescribed_references(commands_dir, section_index)
        skill_files = {r.skill_file for r in refs}
        assert "README.md" not in skill_files

    def test_no_duplicate_refs_per_file_line(
        self, commands_dir: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_prescribed_references(commands_dir, section_index)
        seen = set()
        for ref in refs:
            key = (ref.section_id, ref.skill_file, ref.line_number)
            assert key not in seen, f"Duplicate: {key}"
            seen.add(key)

    def test_empty_dir_returns_no_refs(
        self, tmp_path: Path, section_index: SectionIndex
    ) -> None:
        empty = tmp_path / "empty_commands"
        empty.mkdir()
        refs = extract_prescribed_references(empty, section_index)
        assert refs == []

    def test_unique_section_ids_across_skills(
        self, commands_dir: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_prescribed_references(commands_dir, section_index)
        unique_ids = {r.section_id for r in refs}
        assert len(unique_ids) >= 4
