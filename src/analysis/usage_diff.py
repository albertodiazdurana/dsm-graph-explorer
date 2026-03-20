"""Version diff/compare for usage reports.

Compares two version-stamped UsageReport objects and produces a structured
diff showing what changed between DSM_0.2 versions.
"""

from __future__ import annotations

from pydantic import BaseModel

from analysis.usage_report import GapEntry, UsageReport


class StructuralChange(BaseModel):
    """A section added or removed between versions."""

    section_id: str
    heading: str
    change_type: str  # "added" or "removed"


class ClassificationChange(BaseModel):
    """A section whose inferred classification changed."""

    section_id: str
    heading: str
    old_classification: str
    new_classification: str


class DiffReport(BaseModel):
    """Comparison between two version-stamped usage reports."""

    version_old: str
    version_new: str
    structural_changes: list[StructuralChange]
    classification_changes: list[ClassificationChange]
    new_gaps: list[GapEntry]
    resolved_gaps: list[GapEntry]


def compare_reports(old: UsageReport, new: UsageReport) -> DiffReport:
    """Compare two usage reports and produce a diff.

    Args:
        old: The earlier version's usage report.
        new: The later version's usage report.

    Returns:
        DiffReport with structural changes, classification changes, and gap deltas.
    """
    old_by_id = {s.section_id: s for s in old.sections}
    new_by_id = {s.section_id: s for s in new.sections}

    old_ids = set(old_by_id.keys())
    new_ids = set(new_by_id.keys())

    # Structural changes.
    structural: list[StructuralChange] = []
    for sid in new_ids - old_ids:
        structural.append(StructuralChange(
            section_id=sid,
            heading=new_by_id[sid].heading,
            change_type="added",
        ))
    for sid in old_ids - new_ids:
        structural.append(StructuralChange(
            section_id=sid,
            heading=old_by_id[sid].heading,
            change_type="removed",
        ))

    # Classification changes (for sections present in both).
    classification: list[ClassificationChange] = []
    for sid in old_ids & new_ids:
        old_class = old_by_id[sid].inferred_classification
        new_class = new_by_id[sid].inferred_classification
        if old_class != new_class:
            classification.append(ClassificationChange(
                section_id=sid,
                heading=new_by_id[sid].heading,
                old_classification=old_class,
                new_classification=new_class,
            ))

    # Gap deltas.
    old_gap_ids = {g.section_id for g in old.gaps}
    new_gap_ids = {g.section_id for g in new.gaps}

    new_gaps = [g for g in new.gaps if g.section_id not in old_gap_ids]
    resolved_gaps = [g for g in old.gaps if g.section_id not in new_gap_ids]

    return DiffReport(
        version_old=old.version,
        version_new=new.version,
        structural_changes=structural,
        classification_changes=classification,
        new_gaps=new_gaps,
        resolved_gaps=resolved_gaps,
    )
