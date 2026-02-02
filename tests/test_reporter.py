"""Tests for the integrity report generator.

TDD approach: These tests are written BEFORE implementation.
"""

from pathlib import Path

import pytest

from parser.markdown_parser import parse_markdown_file
from parser.cross_ref_extractor import extract_cross_references
from validator.cross_ref_validator import Severity, ValidationResult, validate_cross_references
from validator.version_validator import VersionInfo, VersionMismatch, validate_version_consistency
from reporter.report_generator import generate_markdown_report, print_rich_report


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_DSM = FIXTURES_DIR / "sample_dsm.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_error(
    target: str = "9.9",
    ref_type: str = "section",
    source_file: str = "doc.md",
    line: int = 10,
) -> ValidationResult:
    """Create a sample ERROR ValidationResult."""
    return ValidationResult(
        severity=Severity.ERROR,
        source_file=source_file,
        line=line,
        ref_type=ref_type,
        target=target,
        message=f"Broken {ref_type} reference: {target} not found",
        context=f"See {ref_type.title()} {target} for details",
    )


def make_warning(
    target: str = "99.0",
    source_file: str = "doc.md",
    line: int = 20,
) -> ValidationResult:
    """Create a sample WARNING ValidationResult."""
    return ValidationResult(
        severity=Severity.WARNING,
        source_file=source_file,
        line=line,
        ref_type="dsm",
        target=target,
        message=f"Unknown DSM document: DSM {target}",
        context=f"Reference to DSM {target}",
    )


def make_version_mismatch() -> VersionMismatch:
    """Create a sample VersionMismatch."""
    return VersionMismatch(
        versions=[
            VersionInfo(file="DSM_0.md", version="1.3.19", line=5, context="**Version:** 1.3.19"),
            VersionInfo(file="README.md", version="1.3.18", line=3, context="**Version:** 1.3.18"),
        ],
        message="Version mismatch: DSM_0.md declares 1.3.19, README.md declares 1.3.18",
    )


# ===========================================================================
# Markdown Report Tests
# ===========================================================================


class TestMarkdownReportContent:
    """Test the content of generated markdown reports."""

    def test_returns_string(self):
        report = generate_markdown_report([], [])
        assert isinstance(report, str)

    def test_includes_title(self):
        report = generate_markdown_report([], [])
        assert "Integrity Report" in report

    def test_includes_error_count(self):
        errors = [make_error(), make_error(target="8.8")]
        report = generate_markdown_report(errors, [])
        assert "2" in report  # error count appears

    def test_includes_warning_count(self):
        warnings = [make_warning()]
        report = generate_markdown_report(warnings, [])
        # The report should distinguish errors from warnings
        assert "warning" in report.lower() or "Warning" in report

    def test_includes_file_reference(self):
        errors = [make_error(source_file="my_doc.md")]
        report = generate_markdown_report(errors, [])
        assert "my_doc.md" in report

    def test_includes_line_number(self):
        errors = [make_error(line=42)]
        report = generate_markdown_report(errors, [])
        assert "42" in report

    def test_includes_target(self):
        errors = [make_error(target="2.4.8")]
        report = generate_markdown_report(errors, [])
        assert "2.4.8" in report

    def test_includes_version_mismatch(self):
        mismatch = make_version_mismatch()
        report = generate_markdown_report([], [mismatch])
        assert "1.3.19" in report
        assert "1.3.18" in report

    def test_clean_report_no_issues(self):
        report = generate_markdown_report([], [])
        assert "no issues" in report.lower() or "clean" in report.lower() or "0 errors" in report.lower()

    def test_errors_and_warnings_separated(self):
        results = [make_error(), make_warning()]
        report = generate_markdown_report(results, [])
        # Both should appear in the report
        assert "error" in report.lower()
        assert "warning" in report.lower()


class TestMarkdownReportFile:
    """Test writing markdown reports to files."""

    def test_writes_to_file(self, tmp_path):
        output = tmp_path / "report.md"
        report = generate_markdown_report([], [], output_path=output)
        assert output.exists()
        assert output.read_text(encoding="utf-8") == report

    def test_no_file_without_path(self, tmp_path):
        report = generate_markdown_report([], [])
        # Should return string without writing
        assert isinstance(report, str)


class TestMarkdownReportSummary:
    """Test the summary section of the report."""

    def test_summary_counts_by_severity(self):
        results = [make_error(), make_error(), make_warning()]
        report = generate_markdown_report(results, [])
        # Should contain counts for errors and warnings
        assert "2" in report  # 2 errors
        assert "1" in report  # 1 warning

    def test_summary_counts_version_mismatches(self):
        mismatch = make_version_mismatch()
        report = generate_markdown_report([], [mismatch])
        assert "version" in report.lower()


# ===========================================================================
# Rich Console Report Tests
# ===========================================================================


class TestRichReport:
    """Test the Rich console output (smoke tests)."""

    def test_prints_without_error(self, capsys):
        print_rich_report([], [])
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_prints_errors(self, capsys):
        errors = [make_error(target="2.4.8")]
        print_rich_report(errors, [])
        captured = capsys.readouterr()
        assert "2.4.8" in captured.out

    def test_prints_warnings(self, capsys):
        warnings = [make_warning(target="99.0")]
        print_rich_report(warnings, [])
        captured = capsys.readouterr()
        assert "99.0" in captured.out

    def test_prints_version_mismatches(self, capsys):
        mismatch = make_version_mismatch()
        print_rich_report([], [mismatch])
        captured = capsys.readouterr()
        assert "1.3.19" in captured.out or "version" in captured.out.lower()

    def test_clean_report_message(self, capsys):
        print_rich_report([], [])
        captured = capsys.readouterr()
        assert "no issues" in captured.out.lower() or "clean" in captured.out.lower() or "0" in captured.out


# ===========================================================================
# End-to-End Integration Tests
# ===========================================================================


class TestEndToEndPipeline:
    """Integration test: parse -> extract -> validate -> report."""

    def test_full_pipeline_with_fixture(self, tmp_path):
        """Parse sample_dsm.md, validate, and generate a report."""
        doc = parse_markdown_file(SAMPLE_DSM)
        refs = extract_cross_references(SAMPLE_DSM)
        results = validate_cross_references([doc], {doc.file: refs})

        # Generate markdown report
        output = tmp_path / "report.md"
        report = generate_markdown_report(results, [], output_path=output)

        assert output.exists()
        assert "Integrity Report" in report
        assert "2.4.8" in report  # known broken ref

    def test_full_pipeline_with_rich_output(self, capsys):
        """Parse sample_dsm.md, validate, and print Rich report."""
        doc = parse_markdown_file(SAMPLE_DSM)
        refs = extract_cross_references(SAMPLE_DSM)
        results = validate_cross_references([doc], {doc.file: refs})
        print_rich_report(results, [])

        captured = capsys.readouterr()
        assert "2.4.8" in captured.out

    def test_full_pipeline_version_check(self, tmp_path):
        """Version consistency check with temporary files."""
        f1 = tmp_path / "DSM_0.md"
        f2 = tmp_path / "README.md"
        f1.write_text("# DSM\n**Version:** 1.0.0\n")
        f2.write_text("# README\n**Version:** 2.0.0\n")

        version_results = validate_version_consistency([f1, f2])
        report = generate_markdown_report([], version_results)

        assert "Version" in report
        assert "1.0.0" in report
        assert "2.0.0" in report

    def test_full_pipeline_combined_report(self, tmp_path):
        """Combined cross-ref + version report."""
        doc = parse_markdown_file(SAMPLE_DSM)
        refs = extract_cross_references(SAMPLE_DSM)
        cross_results = validate_cross_references([doc], {doc.file: refs})

        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text("**Version:** 1.0.0\n")
        f2.write_text("**Version:** 2.0.0\n")
        version_results = validate_version_consistency([f1, f2])

        output = tmp_path / "combined.md"
        report = generate_markdown_report(
            cross_results, version_results, output_path=output
        )

        assert output.exists()
        assert "Errors" in report
        assert "Version" in report
