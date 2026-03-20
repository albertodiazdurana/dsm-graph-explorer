"""Tests for version diff/compare between two usage reports."""

import pytest

from analysis.usage_report import GapEntry, SectionUsage, UsageReport
from analysis.usage_diff import DiffReport, compare_reports


def _section(
    section_id: str,
    heading: str = "",
    module: str = "core",
    designed: str = "always-load",
    inferred: str = "high",
    total_score: int = 5,
) -> SectionUsage:
    return SectionUsage(
        section_id=section_id,
        heading=heading or section_id.replace("-", " ").title(),
        module=module,
        designed_classification=designed,
        declared_count=1,
        declared_sources=["name-mention:L10"],
        prescribed_count=2,
        prescribed_skills=["dsm-go.md"],
        observed_count=2,
        observed_sessions=[40, 41],
        total_score=total_score,
        inferred_classification=inferred,
    )


def _report(
    version: str,
    sections: list[SectionUsage],
    gaps: list[GapEntry] | None = None,
) -> UsageReport:
    return UsageReport(
        version=version,
        date="2026-03-20",
        spoke="test",
        sections=sections,
        gaps=gaps or [],
        ground_truth_results=None,
        summary={
            "total_sections": len(sections),
            "high_usage": sum(1 for s in sections if s.inferred_classification == "high"),
            "low_usage": sum(1 for s in sections if s.inferred_classification == "low"),
            "gaps": len(gaps or []),
        },
    )


@pytest.fixture()
def old_report() -> UsageReport:
    return _report(
        "v1.3.69",
        [
            _section("session-transcript-protocol", inferred="high"),
            _section("inclusive-language", inferred="low", total_score=0),
            _section("old-removed-section", inferred="low", total_score=0),
        ],
        gaps=[
            GapEntry(
                section_id="inclusive-language",
                heading="Inclusive Language",
                designed="always-load",
                observed="low",
                gap_type="over-loaded",
            ),
        ],
    )


@pytest.fixture()
def new_report() -> UsageReport:
    return _report(
        "v1.4.0",
        [
            _section("session-transcript-protocol", inferred="high"),
            _section("inclusive-language", inferred="high", total_score=4),
            _section("new-added-section", inferred="low", total_score=0),
        ],
    )


class TestCompareReports:
    """Tests for compare_reports()."""

    def test_returns_diff_report(self, old_report, new_report) -> None:
        diff = compare_reports(old_report, new_report)
        assert isinstance(diff, DiffReport)
        assert diff.version_old == "v1.3.69"
        assert diff.version_new == "v1.4.0"

    def test_detects_added_section(self, old_report, new_report) -> None:
        diff = compare_reports(old_report, new_report)
        added = [c for c in diff.structural_changes if c.change_type == "added"]
        added_ids = {c.section_id for c in added}
        assert "new-added-section" in added_ids

    def test_detects_removed_section(self, old_report, new_report) -> None:
        diff = compare_reports(old_report, new_report)
        removed = [c for c in diff.structural_changes if c.change_type == "removed"]
        removed_ids = {c.section_id for c in removed}
        assert "old-removed-section" in removed_ids

    def test_detects_classification_change(self, old_report, new_report) -> None:
        diff = compare_reports(old_report, new_report)
        changes = {c.section_id: c for c in diff.classification_changes}
        assert "inclusive-language" in changes
        il = changes["inclusive-language"]
        assert il.old_classification == "low"
        assert il.new_classification == "high"

    def test_stable_section_not_in_changes(self, old_report, new_report) -> None:
        diff = compare_reports(old_report, new_report)
        changed_ids = {c.section_id for c in diff.classification_changes}
        assert "session-transcript-protocol" not in changed_ids

    def test_resolved_gaps(self, old_report, new_report) -> None:
        """Gap in old report that disappeared in new report."""
        diff = compare_reports(old_report, new_report)
        resolved_ids = {g.section_id for g in diff.resolved_gaps}
        assert "inclusive-language" in resolved_ids

    def test_new_gaps(self, old_report, new_report) -> None:
        """No new gaps expected in this fixture set."""
        diff = compare_reports(old_report, new_report)
        # inclusive-language gap resolved, no new gaps added
        assert len(diff.new_gaps) == 0

    def test_identical_reports_produce_empty_diff(self) -> None:
        report = _report("v1.3.69", [_section("session-transcript-protocol")])
        diff = compare_reports(report, report)
        assert len(diff.structural_changes) == 0
        assert len(diff.classification_changes) == 0
        assert len(diff.new_gaps) == 0
        assert len(diff.resolved_gaps) == 0
