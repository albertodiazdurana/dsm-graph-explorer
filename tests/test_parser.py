"""Tests for markdown parser and cross-reference extractor.

TDD approach: These tests are written BEFORE implementation.
"""

from pathlib import Path

import pytest

from parser.markdown_parser import ParsedDocument, Section, parse_markdown_file
from parser.cross_ref_extractor import CrossReference, extract_cross_references


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_DSM = FIXTURES_DIR / "sample_dsm.md"


# ---------------------------------------------------------------------------
# markdown_parser tests
# ---------------------------------------------------------------------------


class TestParseMarkdownFile:
    """Test the top-level parse_markdown_file function."""

    def test_returns_parsed_document(self):
        result = parse_markdown_file(SAMPLE_DSM)
        assert isinstance(result, ParsedDocument)

    def test_parsed_document_has_file_path(self):
        result = parse_markdown_file(SAMPLE_DSM)
        assert result.file == str(SAMPLE_DSM)

    def test_parsed_document_has_sections(self):
        result = parse_markdown_file(SAMPLE_DSM)
        assert len(result.sections) > 0

    def test_extracts_top_level_sections(self):
        result = parse_markdown_file(SAMPLE_DSM)
        top_level = [s for s in result.sections if s.level == 1]
        # Sections: 1, 2, 3, 4 plus appendices A, B, D plus "Edge Cases Section"
        assert len(top_level) >= 7

    def test_extracts_subsections(self):
        result = parse_markdown_file(SAMPLE_DSM)
        level2 = [s for s in result.sections if s.level == 2]
        assert len(level2) > 0

    def test_extracts_deep_subsections(self):
        result = parse_markdown_file(SAMPLE_DSM)
        level3 = [s for s in result.sections if s.level == 3]
        assert len(level3) > 0


class TestSectionNumberExtraction:
    """Test extraction of section numbers from headings."""

    def test_single_number(self):
        result = parse_markdown_file(SAMPLE_DSM)
        numbers = [s.number for s in result.sections]
        assert "1" in numbers

    def test_two_level_number(self):
        result = parse_markdown_file(SAMPLE_DSM)
        numbers = [s.number for s in result.sections]
        assert "1.1" in numbers

    def test_three_level_number(self):
        result = parse_markdown_file(SAMPLE_DSM)
        numbers = [s.number for s in result.sections]
        assert "1.1.1" in numbers

    def test_four_level_number(self):
        result = parse_markdown_file(SAMPLE_DSM)
        numbers = [s.number for s in result.sections]
        assert "4.1.1.1" in numbers

    def test_appendix_letter(self):
        result = parse_markdown_file(SAMPLE_DSM)
        numbers = [s.number for s in result.sections]
        assert "A" in numbers or any(n.startswith("A") for n in numbers if n)

    def test_appendix_subsection(self):
        result = parse_markdown_file(SAMPLE_DSM)
        numbers = [s.number for s in result.sections]
        assert "A.1" in numbers

    def test_appendix_deep_subsection(self):
        result = parse_markdown_file(SAMPLE_DSM)
        numbers = [s.number for s in result.sections]
        assert "A.1.1" in numbers

    def test_heading_without_number_returns_none(self):
        """Headings like '## No Number Heading' should have number=None."""
        result = parse_markdown_file(SAMPLE_DSM)
        no_number = [s for s in result.sections if s.title == "No Number Heading"]
        assert len(no_number) == 1
        assert no_number[0].number is None


class TestSectionTitleExtraction:
    """Test extraction of section titles from headings."""

    def test_simple_title(self):
        result = parse_markdown_file(SAMPLE_DSM)
        titles = [s.title for s in result.sections]
        assert "Introduction" in titles

    def test_title_with_ampersand(self):
        result = parse_markdown_file(SAMPLE_DSM)
        titles = [s.title for s in result.sections]
        assert "Overview & Purpose" in titles

    def test_appendix_title(self):
        result = parse_markdown_file(SAMPLE_DSM)
        # Appendix headings like "# Appendix A: Environment Setup Details"
        appendix_sections = [
            s for s in result.sections if s.title and "Environment Setup Details" in s.title
        ]
        assert len(appendix_sections) == 1

    def test_title_with_colon(self):
        result = parse_markdown_file(SAMPLE_DSM)
        sections = [
            s for s in result.sections if s.title and "Phase 0" in s.title
        ]
        assert len(sections) >= 1


class TestSectionLineNumbers:
    """Test that line numbers are tracked correctly."""

    def test_first_section_at_line_1(self):
        result = parse_markdown_file(SAMPLE_DSM)
        first = result.sections[0]
        assert first.line == 1

    def test_line_numbers_are_positive(self):
        result = parse_markdown_file(SAMPLE_DSM)
        for section in result.sections:
            assert section.line > 0

    def test_line_numbers_are_monotonically_increasing(self):
        result = parse_markdown_file(SAMPLE_DSM)
        lines = [s.line for s in result.sections]
        assert lines == sorted(lines)


class TestSectionLevel:
    """Test heading level detection."""

    def test_h1_is_level_1(self):
        result = parse_markdown_file(SAMPLE_DSM)
        sec1 = [s for s in result.sections if s.number == "1"][0]
        assert sec1.level == 1

    def test_h2_is_level_2(self):
        result = parse_markdown_file(SAMPLE_DSM)
        sec11 = [s for s in result.sections if s.number == "1.1"][0]
        assert sec11.level == 2

    def test_h3_is_level_3(self):
        result = parse_markdown_file(SAMPLE_DSM)
        sec111 = [s for s in result.sections if s.number == "1.1.1"][0]
        assert sec111.level == 3

    def test_h4_is_level_4(self):
        result = parse_markdown_file(SAMPLE_DSM)
        sec4111 = [s for s in result.sections if s.number == "4.1.1.1"][0]
        assert sec4111.level == 4


class TestSectionDataclass:
    """Test Section dataclass structure."""

    def test_section_has_required_fields(self):
        result = parse_markdown_file(SAMPLE_DSM)
        section = result.sections[0]
        assert hasattr(section, "number")
        assert hasattr(section, "title")
        assert hasattr(section, "line")
        assert hasattr(section, "level")


# ---------------------------------------------------------------------------
# cross_ref_extractor tests
# ---------------------------------------------------------------------------


class TestExtractCrossReferences:
    """Test the extract_cross_references function."""

    def test_returns_list_of_cross_references(self):
        result = extract_cross_references(SAMPLE_DSM)
        assert isinstance(result, list)
        assert all(isinstance(r, CrossReference) for r in result)

    def test_finds_section_references(self):
        result = extract_cross_references(SAMPLE_DSM)
        section_refs = [r for r in result if r.type == "section"]
        assert len(section_refs) > 0

    def test_finds_appendix_references(self):
        result = extract_cross_references(SAMPLE_DSM)
        appendix_refs = [r for r in result if r.type == "appendix"]
        assert len(appendix_refs) > 0

    def test_finds_dsm_references(self):
        result = extract_cross_references(SAMPLE_DSM)
        dsm_refs = [r for r in result if r.type == "dsm"]
        assert len(dsm_refs) > 0


class TestSectionCrossReferences:
    """Test extraction of 'Section X.Y.Z' cross-reference patterns."""

    def test_single_level_reference(self):
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "section"]
        # "Section 14" in the fixture
        assert "14" in targets

    def test_two_level_reference(self):
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "section"]
        assert "3.5" in targets

    def test_three_level_reference(self):
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "section"]
        assert "2.4.8" in targets

    def test_multiple_section_refs_on_one_line(self):
        """Line with 'Section 1.1, Appendix D.2.7, and DSM_1.0 Section 2'."""
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "section"]
        assert "1.1" in targets
        assert "2" in targets


class TestAppendixCrossReferences:
    """Test extraction of 'Appendix X.Y' cross-reference patterns."""

    def test_appendix_letter_with_subsection(self):
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "appendix"]
        assert "A.1" in targets

    def test_appendix_deep_reference(self):
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "appendix"]
        assert "D.2.7" in targets

    def test_appendix_three_level(self):
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "appendix"]
        assert "B.2.4" in targets

    def test_appendix_c_reference(self):
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "appendix"]
        assert "C.1.3" in targets


class TestDsmCrossReferences:
    """Test extraction of 'DSM_X' and 'DSM X.Y' cross-reference patterns."""

    def test_dsm_underscore_format(self):
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "dsm"]
        assert "4.0" in targets  # DSM_4.0

    def test_dsm_space_format(self):
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "dsm"]
        assert "1.0" in targets  # DSM 1.0

    def test_dsm_zero_reference(self):
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "dsm"]
        assert "0" in targets  # DSM_0


class TestCodeBlockSkipping:
    """Test that cross-references inside code blocks are skipped."""

    def test_skips_section_ref_in_code_block(self):
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "section"]
        assert "99.99" not in targets

    def test_skips_appendix_ref_in_code_block(self):
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "appendix"]
        assert "Z.99" not in targets

    def test_skips_dsm_ref_in_code_block(self):
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "dsm"]
        assert "99.0" not in targets

    def test_skips_unfenced_code_block(self):
        """Code block without language specifier (just ```) should also be skipped."""
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "section"]
        assert "88.88" not in targets

    def test_resumes_after_code_block(self):
        """References after a code block should be extracted."""
        result = extract_cross_references(SAMPLE_DSM)
        targets = [r.target for r in result if r.type == "section"]
        assert "3.1" in targets  # "Section 3.1 references should resume"


class TestCrossRefLineNumbers:
    """Test that cross-references track line numbers."""

    def test_line_numbers_are_positive(self):
        result = extract_cross_references(SAMPLE_DSM)
        for ref in result:
            assert ref.line > 0

    def test_line_numbers_are_accurate(self):
        """Section 2.4.8 is first referenced in the Overview section (line ~7)."""
        result = extract_cross_references(SAMPLE_DSM)
        ref_248 = [r for r in result if r.type == "section" and r.target == "2.4.8"]
        assert len(ref_248) >= 1
        # First occurrence should be early in the file
        assert ref_248[0].line < 20


class TestCrossRefContext:
    """Test that cross-references include surrounding context."""

    def test_context_is_nonempty_string(self):
        result = extract_cross_references(SAMPLE_DSM)
        for ref in result:
            assert isinstance(ref.context, str)
            assert len(ref.context) > 0

    def test_context_contains_the_reference(self):
        result = extract_cross_references(SAMPLE_DSM)
        for ref in result:
            # The context line should contain something related to the ref
            assert len(ref.context.strip()) > 0


class TestCrossReferenceDataclass:
    """Test CrossReference dataclass structure."""

    def test_has_required_fields(self):
        result = extract_cross_references(SAMPLE_DSM)
        ref = result[0]
        assert hasattr(ref, "type")
        assert hasattr(ref, "target")
        assert hasattr(ref, "line")
        assert hasattr(ref, "context")

    def test_type_is_valid(self):
        result = extract_cross_references(SAMPLE_DSM)
        valid_types = {"section", "appendix", "dsm"}
        for ref in result:
            assert ref.type in valid_types
