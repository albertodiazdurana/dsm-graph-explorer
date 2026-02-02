"""Tests for cross-reference and version validators.

TDD approach: These tests are written BEFORE implementation.
"""

from pathlib import Path

import pytest

from parser.markdown_parser import ParsedDocument, Section, parse_markdown_file
from parser.cross_ref_extractor import CrossReference, extract_cross_references
from validator.cross_ref_validator import (
    Severity,
    ValidationResult,
    build_section_index,
    validate_cross_references,
    KNOWN_DSM_IDS,
)
from validator.version_validator import (
    VersionInfo,
    VersionMismatch,
    extract_versions,
    validate_version_consistency,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_DSM = FIXTURES_DIR / "sample_dsm.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_doc(
    file: str, sections: list[tuple[str | None, str, int, int]]
) -> ParsedDocument:
    """Create a ParsedDocument from (number, title, line, level) tuples."""
    return ParsedDocument(
        file=file,
        sections=[
            Section(number=n, title=t, line=l, level=lv) for n, t, l, lv in sections
        ],
    )


def make_ref(
    type: str, target: str, line: int = 1, context: str = ""
) -> CrossReference:
    """Create a CrossReference for testing."""
    return CrossReference(type=type, target=target, line=line, context=context)


# ===========================================================================
# Cross-Reference Validator Tests
# ===========================================================================


class TestBuildSectionIndex:
    """Test building a section index from parsed documents."""

    def test_returns_dict(self):
        doc = make_doc("file.md", [("1", "Intro", 1, 1)])
        index = build_section_index([doc])
        assert isinstance(index, dict)

    def test_index_contains_numbered_sections(self):
        doc = make_doc(
            "file.md",
            [("1", "Intro", 1, 1), ("1.1", "Sub", 5, 2)],
        )
        index = build_section_index([doc])
        assert "1" in index
        assert "1.1" in index

    def test_index_excludes_unnumbered_headings(self):
        doc = make_doc(
            "file.md",
            [(None, "Unnumbered", 1, 1), ("1", "Numbered", 5, 1)],
        )
        index = build_section_index([doc])
        assert None not in index
        assert "1" in index

    def test_index_maps_to_file_paths(self):
        doc = make_doc("readme.md", [("2.1", "Phase", 10, 2)])
        index = build_section_index([doc])
        assert index["2.1"] == ["readme.md"]

    def test_multi_document_index(self):
        doc1 = make_doc("a.md", [("1", "Intro", 1, 1)])
        doc2 = make_doc("b.md", [("1", "Intro", 1, 1), ("2", "Next", 5, 1)])
        index = build_section_index([doc1, doc2])
        assert "a.md" in index["1"]
        assert "b.md" in index["1"]
        assert "2" in index

    def test_appendix_sections_in_index(self):
        doc = make_doc(
            "file.md",
            [("A", "Appendix A", 1, 1), ("A.1", "Sub", 5, 2)],
        )
        index = build_section_index([doc])
        assert "A" in index
        assert "A.1" in index

    def test_empty_documents(self):
        index = build_section_index([])
        assert index == {}


class TestValidateCrossReferences:
    """Test the main validation function."""

    def test_returns_list(self):
        doc = make_doc("f.md", [("1", "Intro", 1, 1)])
        results = validate_cross_references([doc], {})
        assert isinstance(results, list)

    def test_valid_section_ref_no_result(self):
        doc = make_doc("f.md", [("1.1", "Sub", 5, 2)])
        refs = {"f.md": [make_ref("section", "1.1")]}
        results = validate_cross_references([doc], refs)
        assert len(results) == 0

    def test_broken_section_ref_produces_error(self):
        doc = make_doc("f.md", [("1", "Intro", 1, 1)])
        refs = {"f.md": [make_ref("section", "9.9", line=10, context="See Section 9.9")]}
        results = validate_cross_references([doc], refs)
        assert len(results) == 1
        assert results[0].severity == Severity.ERROR

    def test_valid_appendix_ref_no_result(self):
        doc = make_doc("f.md", [("A.1", "Setup", 20, 2)])
        refs = {"f.md": [make_ref("appendix", "A.1")]}
        results = validate_cross_references([doc], refs)
        assert len(results) == 0

    def test_broken_appendix_ref_produces_error(self):
        doc = make_doc("f.md", [("A.1", "Setup", 20, 2)])
        refs = {"f.md": [make_ref("appendix", "C.1.3")]}
        results = validate_cross_references([doc], refs)
        assert len(results) == 1
        assert results[0].severity == Severity.ERROR

    def test_known_dsm_ref_no_result(self):
        doc = make_doc("f.md", [])
        refs = {"f.md": [make_ref("dsm", "4.0")]}
        results = validate_cross_references([doc], refs, known_dsm_ids=["4.0"])
        assert len(results) == 0

    def test_unknown_dsm_ref_produces_warning(self):
        doc = make_doc("f.md", [])
        refs = {"f.md": [make_ref("dsm", "99.0")]}
        results = validate_cross_references([doc], refs, known_dsm_ids=["4.0"])
        assert len(results) == 1
        assert results[0].severity == Severity.WARNING

    def test_default_known_dsm_ids(self):
        """KNOWN_DSM_IDS should include standard DSM versions."""
        assert "0" in KNOWN_DSM_IDS
        assert "1.0" in KNOWN_DSM_IDS
        assert "4.0" in KNOWN_DSM_IDS

    def test_error_includes_source_file(self):
        doc = make_doc("readme.md", [("1", "Intro", 1, 1)])
        refs = {"readme.md": [make_ref("section", "99")]}
        results = validate_cross_references([doc], refs)
        assert results[0].source_file == "readme.md"

    def test_error_includes_line_number(self):
        doc = make_doc("f.md", [("1", "Intro", 1, 1)])
        refs = {"f.md": [make_ref("section", "99", line=42)]}
        results = validate_cross_references([doc], refs)
        assert results[0].line == 42

    def test_error_includes_context(self):
        doc = make_doc("f.md", [("1", "Intro", 1, 1)])
        refs = {"f.md": [make_ref("section", "99", context="See Section 99")]}
        results = validate_cross_references([doc], refs)
        assert "Section 99" in results[0].context

    def test_error_includes_target(self):
        doc = make_doc("f.md", [("1", "Intro", 1, 1)])
        refs = {"f.md": [make_ref("section", "99")]}
        results = validate_cross_references([doc], refs)
        assert results[0].target == "99"

    def test_error_includes_ref_type(self):
        doc = make_doc("f.md", [("1", "Intro", 1, 1)])
        refs = {"f.md": [make_ref("appendix", "Z.1")]}
        results = validate_cross_references([doc], refs)
        assert results[0].ref_type == "appendix"

    def test_cross_file_validation(self):
        """Ref in file A to section defined in file B should be valid."""
        doc_a = make_doc("a.md", [("1", "Intro", 1, 1)])
        doc_b = make_doc("b.md", [("2.1", "Details", 1, 2)])
        refs = {"a.md": [make_ref("section", "2.1")]}
        results = validate_cross_references([doc_a, doc_b], refs)
        assert len(results) == 0

    def test_multiple_broken_refs(self):
        doc = make_doc("f.md", [("1", "Intro", 1, 1)])
        refs = {
            "f.md": [
                make_ref("section", "99"),
                make_ref("section", "88"),
                make_ref("appendix", "Z.1"),
            ]
        }
        results = validate_cross_references([doc], refs)
        assert len(results) == 3

    def test_mixed_valid_and_broken(self):
        doc = make_doc("f.md", [("1", "Intro", 1, 1), ("A.1", "App", 10, 2)])
        refs = {
            "f.md": [
                make_ref("section", "1"),  # valid
                make_ref("section", "99"),  # broken
                make_ref("appendix", "A.1"),  # valid
            ]
        }
        results = validate_cross_references([doc], refs)
        assert len(results) == 1
        assert results[0].target == "99"

    def test_empty_references(self):
        doc = make_doc("f.md", [("1", "Intro", 1, 1)])
        results = validate_cross_references([doc], {})
        assert len(results) == 0

    def test_no_documents_all_refs_broken(self):
        refs = {"f.md": [make_ref("section", "1")]}
        results = validate_cross_references([], refs)
        assert len(results) == 1
        assert results[0].severity == Severity.ERROR

    def test_multiple_files_with_refs(self):
        doc = make_doc("f.md", [("1", "Intro", 1, 1), ("2", "Body", 10, 1)])
        refs = {
            "a.md": [make_ref("section", "1")],  # valid
            "b.md": [make_ref("section", "99")],  # broken
        }
        results = validate_cross_references([doc], refs)
        assert len(results) == 1
        assert results[0].source_file == "b.md"


class TestSeverityEnum:
    """Test the Severity enum values."""

    def test_error_value(self):
        assert Severity.ERROR.value == "error"

    def test_warning_value(self):
        assert Severity.WARNING.value == "warning"


class TestValidationResultDataclass:
    """Test ValidationResult dataclass structure."""

    def test_has_required_fields(self):
        r = ValidationResult(
            severity=Severity.ERROR,
            source_file="f.md",
            line=10,
            ref_type="section",
            target="99",
            message="broken",
            context="See Section 99",
        )
        assert r.severity == Severity.ERROR
        assert r.source_file == "f.md"
        assert r.line == 10
        assert r.ref_type == "section"
        assert r.target == "99"
        assert r.message == "broken"
        assert r.context == "See Section 99"


class TestFixtureValidation:
    """Integration tests using the sample_dsm.md fixture."""

    @pytest.fixture
    def parsed(self):
        doc = parse_markdown_file(SAMPLE_DSM)
        refs = extract_cross_references(SAMPLE_DSM)
        return doc, refs

    def test_detects_broken_section_refs(self, parsed):
        doc, refs = parsed
        results = validate_cross_references([doc], {doc.file: refs})
        broken_sections = [
            r
            for r in results
            if r.ref_type == "section" and r.severity == Severity.ERROR
        ]
        broken_targets = {r.target for r in broken_sections}
        # Known broken: 2.4.8, 3.5, 4.4, 14
        assert "2.4.8" in broken_targets
        assert "3.5" in broken_targets
        assert "4.4" in broken_targets
        assert "14" in broken_targets

    def test_detects_broken_appendix_refs(self, parsed):
        doc, refs = parsed
        results = validate_cross_references([doc], {doc.file: refs})
        broken_appendixes = [
            r
            for r in results
            if r.ref_type == "appendix" and r.severity == Severity.ERROR
        ]
        broken_targets = {r.target for r in broken_appendixes}
        assert "C.1.3" in broken_targets

    def test_valid_section_refs_not_flagged(self, parsed):
        doc, refs = parsed
        results = validate_cross_references([doc], {doc.file: refs})
        flagged_targets = {r.target for r in results}
        # These should NOT be flagged
        assert "1.1" not in flagged_targets
        assert "2.1.1" not in flagged_targets
        assert "3.1" not in flagged_targets
        assert "A.1" not in flagged_targets
        assert "B.2.4" not in flagged_targets
        assert "D.2.7" not in flagged_targets

    def test_total_error_count(self, parsed):
        doc, refs = parsed
        results = validate_cross_references([doc], {doc.file: refs})
        errors = [r for r in results if r.severity == Severity.ERROR]
        # 2.4.8 (x2), 3.5, 4.4, 14, C.1.3 = at least 6 errors
        assert len(errors) >= 6


# ===========================================================================
# Version Validator Tests
# ===========================================================================


class TestExtractVersions:
    """Test version pattern extraction from files."""

    def test_finds_version_colon_pattern(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("**Version:** 1.3.19\n")
        result = extract_versions(f)
        assert len(result) >= 1
        assert result[0].version == "1.3.19"

    def test_finds_dsm_version_pattern(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("**DSM Version:** 2.0.1\n")
        result = extract_versions(f)
        assert len(result) >= 1
        assert result[0].version == "2.0.1"

    def test_finds_v_prefix(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("Current release: v1.2.3\n")
        result = extract_versions(f)
        versions = [v.version for v in result]
        assert "1.2.3" in versions

    def test_finds_changelog_bracket_version(self, tmp_path):
        f = tmp_path / "CHANGELOG.md"
        f.write_text("## [1.3.19] - 2026-01-30\n")
        result = extract_versions(f)
        versions = [v.version for v in result]
        assert "1.3.19" in versions

    def test_tracks_line_numbers(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("Line 1\n**Version:** 3.0.0\nLine 3\n")
        result = extract_versions(f)
        assert result[0].line == 2

    def test_tracks_file_path(self, tmp_path):
        f = tmp_path / "readme.md"
        f.write_text("**Version:** 1.0.0\n")
        result = extract_versions(f)
        assert result[0].file == str(f)

    def test_includes_context(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("**Version:** 1.0.0\n")
        result = extract_versions(f)
        assert "1.0.0" in result[0].context

    def test_no_versions_returns_empty(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("No version information here.\n")
        result = extract_versions(f)
        assert result == []

    def test_multiple_versions_in_file(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("**Version:** 1.0.0\nOld release: v0.9.0\n")
        result = extract_versions(f)
        assert len(result) >= 2

    def test_two_part_version(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("**Version:** 1.0\n")
        result = extract_versions(f)
        assert len(result) >= 1
        assert result[0].version == "1.0"


class TestVersionInfoDataclass:
    """Test VersionInfo dataclass structure."""

    def test_has_required_fields(self):
        v = VersionInfo(file="test.md", version="1.0.0", line=1, context="Version: 1.0.0")
        assert v.file == "test.md"
        assert v.version == "1.0.0"
        assert v.line == 1
        assert v.context == "Version: 1.0.0"


class TestVersionConsistency:
    """Test version consistency checking across files."""

    def test_consistent_returns_empty(self, tmp_path):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text("**Version:** 1.0.0\n")
        f2.write_text("**Version:** 1.0.0\n")
        results = validate_version_consistency([f1, f2])
        assert len(results) == 0

    def test_mismatch_detected(self, tmp_path):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text("**Version:** 1.0.0\n")
        f2.write_text("**Version:** 2.0.0\n")
        results = validate_version_consistency([f1, f2])
        assert len(results) >= 1

    def test_mismatch_includes_all_versions(self, tmp_path):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text("**Version:** 1.0.0\n")
        f2.write_text("**Version:** 2.0.0\n")
        results = validate_version_consistency([f1, f2])
        all_versions = set()
        for r in results:
            for v in r.versions:
                all_versions.add(v.version)
        assert "1.0.0" in all_versions
        assert "2.0.0" in all_versions

    def test_single_file_no_comparison(self, tmp_path):
        f = tmp_path / "a.md"
        f.write_text("**Version:** 1.0.0\n")
        results = validate_version_consistency([f])
        assert len(results) == 0

    def test_mismatch_has_message(self, tmp_path):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text("**Version:** 1.0.0\n")
        f2.write_text("**Version:** 2.0.0\n")
        results = validate_version_consistency([f1, f2])
        assert results[0].message  # non-empty message

    def test_no_version_files_excluded(self, tmp_path):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text("**Version:** 1.0.0\n")
        f2.write_text("No version here.\n")
        results = validate_version_consistency([f1, f2])
        assert len(results) == 0

    def test_three_files_one_mismatch(self, tmp_path):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f3 = tmp_path / "c.md"
        f1.write_text("**Version:** 1.0.0\n")
        f2.write_text("**Version:** 1.0.0\n")
        f3.write_text("**Version:** 2.0.0\n")
        results = validate_version_consistency([f1, f2, f3])
        assert len(results) >= 1
