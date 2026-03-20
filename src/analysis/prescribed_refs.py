"""Layer 2: Skill definition prescribed reference extraction.

Parses DSM skill definition files (dsm-go.md, dsm-wrap-up.md, etc.) to find
references to DSM_0.2 sections and protocols. These represent what the session
lifecycle prescribes the agent to follow.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from analysis.declared_refs import build_heading_patterns
from analysis.section_index import SectionIndex


class PrescribedReference(BaseModel):
    """A reference to a DSM_0.2 section found in a skill definition."""

    section_id: str
    line_number: int
    context: str
    skill_file: str  # filename of the skill definition


def extract_prescribed_references(
    commands_dir: Path,
    section_index: SectionIndex,
) -> list[PrescribedReference]:
    """Extract references to DSM_0.2 sections from skill definition files.

    Args:
        commands_dir: Directory containing dsm-*.md skill files.
        section_index: The DSM_0.2 section index to match against.

    Returns:
        List of PrescribedReference objects, one per reference found.
    """
    commands_dir = Path(commands_dir)
    heading_patterns = build_heading_patterns(section_index)
    references: list[PrescribedReference] = []
    seen: set[tuple[str, str, int]] = set()

    # Only scan dsm-*.md files (skip README, etc.).
    skill_files = sorted(commands_dir.glob("dsm-*.md"))

    for filepath in skill_files:
        lines = filepath.read_text().splitlines()
        for line_num, line in enumerate(lines, start=1):
            for pattern, section_id in heading_patterns:
                if pattern.search(line):
                    key = (section_id, filepath.name, line_num)
                    if key not in seen:
                        seen.add(key)
                        references.append(PrescribedReference(
                            section_id=section_id,
                            line_number=line_num,
                            context=line.strip(),
                            skill_file=filepath.name,
                        ))

    return references
