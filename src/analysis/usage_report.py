"""Four-layer usage aggregation and classification.

Combines declared, prescribed, observed, and designed evidence into a unified
per-section usage report with gap analysis and ground truth validation.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from analysis.declared_refs import DeclaredReference
from analysis.observed_refs import ObservedReference
from analysis.prescribed_refs import PrescribedReference
from analysis.section_index import SectionIndex


class SectionUsage(BaseModel):
    """Aggregated usage profile for a single DSM_0.2 section."""

    section_id: str
    heading: str
    module: str
    designed_classification: str  # "always-load" or "on-demand" (Layer 4)
    declared_count: int
    declared_sources: list[str]  # match types or line refs
    prescribed_count: int
    prescribed_skills: list[str]  # skill filenames
    observed_count: int
    observed_sessions: list[int]  # session numbers
    total_score: int
    inferred_classification: str  # "high" or "low"


class GapEntry(BaseModel):
    """A designed-vs-observed divergence."""

    section_id: str
    heading: str
    designed: str  # "always-load" or "on-demand"
    observed: str  # "high" or "low"
    gap_type: str  # "over-loaded" or "under-classified"


class UsageReport(BaseModel):
    """Complete four-layer usage report for a spoke project."""

    version: str
    date: str
    spoke: str
    sections: list[SectionUsage]
    gaps: list[GapEntry]
    ground_truth_results: dict[str, str] | None  # section_id -> "pass"/"fail"
    summary: dict[str, int]


def aggregate_usage(
    section_index: SectionIndex,
    declared_refs: list[DeclaredReference],
    prescribed_refs: list[PrescribedReference],
    observed_refs: list[ObservedReference],
    spoke: str,
    ground_truth_ids: list[str] | None = None,
) -> UsageReport:
    """Aggregate all four layers into a usage report.

    Args:
        section_index: The DSM_0.2 section index (provides Layer 4 designed data).
        declared_refs: Layer 1 references from CLAUDE.md.
        prescribed_refs: Layer 2 references from skill definitions.
        observed_refs: Layer 3 references from session transcripts.
        spoke: Name of the spoke project being analyzed.
        ground_truth_ids: Optional list of section IDs expected to be high-usage.

    Returns:
        UsageReport with per-section profiles, gaps, and validation results.
    """
    # Index references by section_id for fast lookup.
    declared_by_id: dict[str, list[DeclaredReference]] = {}
    for ref in declared_refs:
        declared_by_id.setdefault(ref.section_id, []).append(ref)

    prescribed_by_id: dict[str, list[PrescribedReference]] = {}
    for ref in prescribed_refs:
        prescribed_by_id.setdefault(ref.section_id, []).append(ref)

    observed_by_id: dict[str, list[ObservedReference]] = {}
    for ref in observed_refs:
        observed_by_id.setdefault(ref.section_id, []).append(ref)

    sections: list[SectionUsage] = []
    gaps: list[GapEntry] = []

    for entry in section_index.sections:
        sid = entry.section_id

        # Layer 1: Declared.
        d_refs = declared_by_id.get(sid, [])
        declared_count = len(d_refs)
        declared_sources = [f"{r.match_type}:L{r.line_number}" for r in d_refs]

        # Layer 2: Prescribed.
        p_refs = prescribed_by_id.get(sid, [])
        prescribed_count = len(p_refs)
        prescribed_skills = sorted({r.skill_file for r in p_refs})

        # Layer 3: Observed.
        o_refs = observed_by_id.get(sid, [])
        observed_count = len(o_refs)
        observed_sessions = sorted({r.session_number for r in o_refs})

        # Scoring and classification.
        total_score = declared_count + prescribed_count + observed_count
        layers_active = sum([
            declared_count > 0,
            prescribed_count > 0,
            observed_count > 0,
        ])
        inferred = "high" if layers_active >= 2 else "low"

        sections.append(SectionUsage(
            section_id=sid,
            heading=entry.heading,
            module=entry.module,
            designed_classification=entry.designed_classification,
            declared_count=declared_count,
            declared_sources=declared_sources,
            prescribed_count=prescribed_count,
            prescribed_skills=prescribed_skills,
            observed_count=observed_count,
            observed_sessions=observed_sessions,
            total_score=total_score,
            inferred_classification=inferred,
        ))

        # Gap analysis: designed vs observed.
        if entry.designed_classification == "always-load" and inferred == "low":
            gaps.append(GapEntry(
                section_id=sid,
                heading=entry.heading,
                designed="always-load",
                observed="low",
                gap_type="over-loaded",
            ))
        elif entry.designed_classification == "on-demand" and inferred == "high":
            gaps.append(GapEntry(
                section_id=sid,
                heading=entry.heading,
                designed="on-demand",
                observed="high",
                gap_type="under-classified",
            ))

    # Ground truth validation.
    gt_results: dict[str, str] | None = None
    if ground_truth_ids is not None:
        gt_results = {}
        section_map = {s.section_id: s for s in sections}
        for gt_id in ground_truth_ids:
            usage = section_map.get(gt_id)
            # Fallback: suffix match (GT IDs may lack number prefixes).
            if usage is None:
                for sid, s in section_map.items():
                    if sid.endswith(gt_id):
                        usage = s
                        break
            if usage and usage.inferred_classification == "high":
                gt_results[gt_id] = "pass"
            else:
                gt_results[gt_id] = "fail"

    # Summary.
    high_count = sum(1 for s in sections if s.inferred_classification == "high")
    low_count = sum(1 for s in sections if s.inferred_classification == "low")

    return UsageReport(
        version=section_index.version,
        date=date.today().isoformat(),
        spoke=spoke,
        sections=sections,
        gaps=gaps,
        ground_truth_results=gt_results,
        summary={
            "total_sections": len(sections),
            "high_usage": high_count,
            "low_usage": low_count,
            "gaps": len(gaps),
        },
    )
