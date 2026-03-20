"""Tests for Layer 3: session transcript observed reference extraction."""

from pathlib import Path

import pytest

from analysis.observed_refs import ObservedReference, extract_observed_references
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
                section_id="pre-generation-brief-protocol",
                heading="Pre-Generation Brief Protocol",
                file="DSM_0.2_Custom_Instructions_v1.1.md",
                module="core",
                designed_classification="always-load",
                level=2,
                line_number=293,
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
def transcript_file(tmp_path: Path) -> Path:
    """A synthetic session transcript."""
    t = tmp_path / "session-transcript.md"
    t.write_text(
        """\
# Session 40 Transcript
**Started:** 2026-03-20T10:00:00-03:00
**Project:** Test Project

---

<------------Start Thinking / 10:05------------>
Need to follow the Session Transcript Protocol here.
Also considering the Pre-Generation Brief Protocol for the next artifact.

Output: Applied Session Transcript Protocol, created file.

---

## Session 41 (lightweight continuation)
**Started:** 2026-03-20T14:00:00-03:00

<------------Start Thinking / 14:05------------>
Checking the Three-Level Branching Strategy before creating branches.
The Composition Challenge Protocol applies to this multi-item artifact.

Output: Branch created per Three-Level Branching Strategy.
""",
    )
    return t


@pytest.fixture()
def second_transcript(tmp_path: Path) -> Path:
    """A second transcript file (archived)."""
    t = tmp_path / "2026-03-18T11:15-ST.md"
    t.write_text(
        """\
# Session 38 Transcript
**Started:** 2026-03-18T11:15:00-03:00

<------------Start Thinking / 11:20------------>
The Pre-Generation Brief Protocol requires explaining what and why.
""",
    )
    return t


class TestExtractObservedReferences:
    """Tests for extract_observed_references()."""

    def test_detects_protocol_mentions(
        self, transcript_file: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_observed_references([transcript_file], section_index)
        ids = {r.section_id for r in refs}
        assert "session-transcript-protocol" in ids
        assert "pre-generation-brief-protocol" in ids
        assert "three-level-branching-strategy" in ids

    def test_tracks_session_number(
        self, transcript_file: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_observed_references([transcript_file], section_index)
        # Session 40 mentions
        s40_refs = [r for r in refs if r.session_number == 40]
        s40_ids = {r.section_id for r in s40_refs}
        assert "session-transcript-protocol" in s40_ids
        assert "pre-generation-brief-protocol" in s40_ids

        # Session 41 mentions
        s41_refs = [r for r in refs if r.session_number == 41]
        s41_ids = {r.section_id for r in s41_refs}
        assert "three-level-branching-strategy" in s41_ids
        assert "1-composition-challenge-protocol" in s41_ids

    def test_reference_has_transcript_file(
        self, transcript_file: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_observed_references([transcript_file], section_index)
        for ref in refs:
            assert ref.transcript_file == transcript_file.name

    def test_reference_has_line_number_and_context(
        self, transcript_file: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_observed_references([transcript_file], section_index)
        for ref in refs:
            assert ref.line_number >= 1
            assert ref.context

    def test_scans_multiple_transcripts(
        self,
        transcript_file: Path,
        second_transcript: Path,
        section_index: SectionIndex,
    ) -> None:
        refs = extract_observed_references(
            [transcript_file, second_transcript], section_index
        )
        files = {r.transcript_file for r in refs}
        assert transcript_file.name in files
        assert second_transcript.name in files

    def test_session_from_second_file(
        self, second_transcript: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_observed_references([second_transcript], section_index)
        assert any(r.session_number == 38 for r in refs)

    def test_no_duplicate_refs_per_session_line(
        self, transcript_file: Path, section_index: SectionIndex
    ) -> None:
        refs = extract_observed_references([transcript_file], section_index)
        seen = set()
        for ref in refs:
            key = (ref.section_id, ref.transcript_file, ref.line_number)
            assert key not in seen, f"Duplicate: {key}"
            seen.add(key)

    def test_empty_list_returns_no_refs(
        self, section_index: SectionIndex
    ) -> None:
        refs = extract_observed_references([], section_index)
        assert refs == []

    def test_empty_file_returns_no_refs(
        self, tmp_path: Path, section_index: SectionIndex
    ) -> None:
        empty = tmp_path / "empty.md"
        empty.write_text("")
        refs = extract_observed_references([empty], section_index)
        assert refs == []

    def test_unique_sessions_referenced(
        self,
        transcript_file: Path,
        second_transcript: Path,
        section_index: SectionIndex,
    ) -> None:
        refs = extract_observed_references(
            [transcript_file, second_transcript], section_index
        )
        sessions = {r.session_number for r in refs}
        assert sessions == {38, 40, 41}
