"""Tests for four-layer usage aggregation and classification."""

import json

import pytest

from analysis.declared_refs import DeclaredReference
from analysis.observed_refs import ObservedReference
from analysis.prescribed_refs import PrescribedReference
from analysis.section_index import DispatchEntry, SectionEntry, SectionIndex
from analysis.usage_report import UsageReport, aggregate_usage


@pytest.fixture()
def section_index() -> SectionIndex:
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
                section_id="inclusive-language",
                heading="Inclusive Language",
                file="DSM_0.2_Custom_Instructions_v1.1.md",
                module="core",
                designed_classification="always-load",
                level=2,
                line_number=514,
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
            SectionEntry(
                section_id="4-query-sanitization",
                heading="4. Query Sanitization",
                file="DSM_0.2.C_Security_Safety.md",
                module="C",
                designed_classification="on-demand",
                level=2,
                line_number=201,
            ),
        ],
        dispatch_table=[
            DispatchEntry(
                protocol="Composition Challenge Protocol",
                trigger="Producing a collection of 2+ items",
                module="B",
            ),
        ],
    )


@pytest.fixture()
def declared_refs() -> list[DeclaredReference]:
    return [
        DeclaredReference(
            section_id="session-transcript-protocol",
            line_number=77,
            context="## Session Transcript Protocol (reinforces inherited protocol)",
            match_type="reinforcement",
        ),
        DeclaredReference(
            section_id="pre-generation-brief-protocol",
            line_number=86,
            context="## Pre-Generation Brief Protocol (reinforces inherited protocol)",
            match_type="reinforcement",
        ),
        DeclaredReference(
            section_id="1-composition-challenge-protocol",
            line_number=50,
            context="Also uses the Composition Challenge Protocol.",
            match_type="name-mention",
        ),
    ]


@pytest.fixture()
def prescribed_refs() -> list[PrescribedReference]:
    return [
        PrescribedReference(
            section_id="session-transcript-protocol",
            line_number=9,
            context="Follow the Session Transcript Protocol from this point forward.",
            skill_file="dsm-go.md",
        ),
        PrescribedReference(
            section_id="session-transcript-protocol",
            line_number=5,
            context="Follow the Session Transcript Protocol.",
            skill_file="dsm-light-go.md",
        ),
    ]


@pytest.fixture()
def observed_refs() -> list[ObservedReference]:
    return [
        ObservedReference(
            section_id="session-transcript-protocol",
            line_number=10,
            context="Applying Session Transcript Protocol.",
            transcript_file="session-transcript.md",
            session_number=40,
        ),
        ObservedReference(
            section_id="session-transcript-protocol",
            line_number=50,
            context="Session Transcript Protocol followed.",
            transcript_file="session-transcript.md",
            session_number=41,
        ),
        ObservedReference(
            section_id="pre-generation-brief-protocol",
            line_number=20,
            context="Pre-Generation Brief Protocol for this artifact.",
            transcript_file="session-transcript.md",
            session_number=40,
        ),
        ObservedReference(
            section_id="1-composition-challenge-protocol",
            line_number=60,
            context="Applying Composition Challenge Protocol.",
            transcript_file="session-transcript.md",
            session_number=41,
        ),
    ]


class TestAggregateUsage:
    """Tests for aggregate_usage()."""

    def test_returns_usage_report(
        self, section_index, declared_refs, prescribed_refs, observed_refs
    ) -> None:
        report = aggregate_usage(
            section_index, declared_refs, prescribed_refs, observed_refs,
            spoke="dsm-graph-explorer",
        )
        assert isinstance(report, UsageReport)
        assert report.version == "v1.3.69"
        assert report.spoke == "dsm-graph-explorer"

    def test_all_sections_present(
        self, section_index, declared_refs, prescribed_refs, observed_refs
    ) -> None:
        report = aggregate_usage(
            section_index, declared_refs, prescribed_refs, observed_refs,
            spoke="test",
        )
        ids = {s.section_id for s in report.sections}
        assert "session-transcript-protocol" in ids
        assert "pre-generation-brief-protocol" in ids
        assert "inclusive-language" in ids
        assert "1-composition-challenge-protocol" in ids
        assert "4-query-sanitization" in ids

    def test_declared_count(
        self, section_index, declared_refs, prescribed_refs, observed_refs
    ) -> None:
        report = aggregate_usage(
            section_index, declared_refs, prescribed_refs, observed_refs,
            spoke="test",
        )
        stp = next(s for s in report.sections if s.section_id == "session-transcript-protocol")
        assert stp.declared_count == 1

    def test_prescribed_count(
        self, section_index, declared_refs, prescribed_refs, observed_refs
    ) -> None:
        report = aggregate_usage(
            section_index, declared_refs, prescribed_refs, observed_refs,
            spoke="test",
        )
        stp = next(s for s in report.sections if s.section_id == "session-transcript-protocol")
        assert stp.prescribed_count == 2  # in dsm-go.md and dsm-light-go.md

    def test_observed_count_and_sessions(
        self, section_index, declared_refs, prescribed_refs, observed_refs
    ) -> None:
        report = aggregate_usage(
            section_index, declared_refs, prescribed_refs, observed_refs,
            spoke="test",
        )
        stp = next(s for s in report.sections if s.section_id == "session-transcript-protocol")
        assert stp.observed_count == 2
        assert stp.observed_sessions == [40, 41]

    def test_total_score(
        self, section_index, declared_refs, prescribed_refs, observed_refs
    ) -> None:
        report = aggregate_usage(
            section_index, declared_refs, prescribed_refs, observed_refs,
            spoke="test",
        )
        stp = next(s for s in report.sections if s.section_id == "session-transcript-protocol")
        # 1 declared + 2 prescribed + 2 observed = 5
        assert stp.total_score == 5

    def test_high_usage_classification(
        self, section_index, declared_refs, prescribed_refs, observed_refs
    ) -> None:
        """Section referenced by ≥2 layers should be classified as high."""
        report = aggregate_usage(
            section_index, declared_refs, prescribed_refs, observed_refs,
            spoke="test",
        )
        stp = next(s for s in report.sections if s.section_id == "session-transcript-protocol")
        assert stp.inferred_classification == "high"

    def test_low_usage_classification(
        self, section_index, declared_refs, prescribed_refs, observed_refs
    ) -> None:
        """Section with no references should be classified as low."""
        report = aggregate_usage(
            section_index, declared_refs, prescribed_refs, observed_refs,
            spoke="test",
        )
        qs = next(s for s in report.sections if s.section_id == "4-query-sanitization")
        assert qs.inferred_classification == "low"

    def test_designed_vs_observed_gap_over_loaded(
        self, section_index, declared_refs, prescribed_refs, observed_refs
    ) -> None:
        """Core section with no observed usage = potential over-loading."""
        report = aggregate_usage(
            section_index, declared_refs, prescribed_refs, observed_refs,
            spoke="test",
        )
        gaps = {g.section_id: g for g in report.gaps}
        assert "inclusive-language" in gaps
        il = gaps["inclusive-language"]
        assert il.designed == "always-load"
        assert il.observed == "low"
        assert il.gap_type == "over-loaded"

    def test_designed_vs_observed_gap_under_classified(
        self, section_index, declared_refs, prescribed_refs, observed_refs
    ) -> None:
        """On-demand section with high observed usage = potential under-classification."""
        report = aggregate_usage(
            section_index, declared_refs, prescribed_refs, observed_refs,
            spoke="test",
        )
        gaps = {g.section_id: g for g in report.gaps}
        assert "1-composition-challenge-protocol" in gaps
        ccp = gaps["1-composition-challenge-protocol"]
        assert ccp.designed == "on-demand"
        assert ccp.observed == "high"
        assert ccp.gap_type == "under-classified"

    def test_ground_truth_validation(
        self, section_index, declared_refs, prescribed_refs, observed_refs
    ) -> None:
        ground_truth = ["session-transcript-protocol", "pre-generation-brief-protocol"]
        report = aggregate_usage(
            section_index, declared_refs, prescribed_refs, observed_refs,
            spoke="test",
            ground_truth_ids=ground_truth,
        )
        assert report.ground_truth_results is not None
        assert report.ground_truth_results["session-transcript-protocol"] == "pass"
        assert report.ground_truth_results["pre-generation-brief-protocol"] == "pass"

    def test_ground_truth_fail_for_unreferenced(
        self, section_index, declared_refs, prescribed_refs, observed_refs
    ) -> None:
        ground_truth = ["inclusive-language"]  # not referenced by any layer
        report = aggregate_usage(
            section_index, declared_refs, prescribed_refs, observed_refs,
            spoke="test",
            ground_truth_ids=ground_truth,
        )
        assert report.ground_truth_results["inclusive-language"] == "fail"

    def test_summary_stats(
        self, section_index, declared_refs, prescribed_refs, observed_refs
    ) -> None:
        report = aggregate_usage(
            section_index, declared_refs, prescribed_refs, observed_refs,
            spoke="test",
        )
        assert report.summary["total_sections"] == 5
        assert report.summary["high_usage"] >= 1
        assert report.summary["low_usage"] >= 1
        assert report.summary["gaps"] >= 1

    def test_json_roundtrip(
        self, section_index, declared_refs, prescribed_refs, observed_refs
    ) -> None:
        report = aggregate_usage(
            section_index, declared_refs, prescribed_refs, observed_refs,
            spoke="test",
        )
        json_str = report.model_dump_json(indent=2)
        parsed = json.loads(json_str)
        assert parsed["version"] == "v1.3.69"
        assert parsed["spoke"] == "test"
        assert len(parsed["sections"]) == 5
