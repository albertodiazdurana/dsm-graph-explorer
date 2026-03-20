"""Layer 3: Session transcript observed reference extraction.

Scans session transcripts for references to DSM_0.2 sections and protocols.
These represent what the agent actually consulted and executed during real
sessions, as evidenced by mentions in reasoning blocks and output summaries.
"""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel

from analysis.declared_refs import build_heading_patterns
from analysis.section_index import SectionIndex


class ObservedReference(BaseModel):
    """A reference to a DSM_0.2 section found in a session transcript."""

    section_id: str
    line_number: int
    context: str
    transcript_file: str
    session_number: int


# Patterns for session boundary markers.
# "# Session N Transcript" or "## Session N (...)"
_SESSION_HEADER_RE = re.compile(
    r"^#{1,3}\s+Session\s+(\d+)",
    re.IGNORECASE,
)


def extract_observed_references(
    transcript_paths: list[Path],
    section_index: SectionIndex,
) -> list[ObservedReference]:
    """Extract references to DSM_0.2 sections from session transcripts.

    Args:
        transcript_paths: List of paths to transcript files to scan.
        section_index: The DSM_0.2 section index to match against.

    Returns:
        List of ObservedReference objects, one per reference found.
    """
    if not transcript_paths:
        return []

    heading_patterns = build_heading_patterns(section_index)
    references: list[ObservedReference] = []
    seen: set[tuple[str, str, int]] = set()

    for filepath in transcript_paths:
        filepath = Path(filepath)
        text = filepath.read_text()
        if not text.strip():
            continue

        lines = text.splitlines()
        current_session = 0

        for line_num, line in enumerate(lines, start=1):
            # Track session number from boundary markers.
            session_match = _SESSION_HEADER_RE.match(line)
            if session_match:
                current_session = int(session_match.group(1))
                continue

            # Match protocol names.
            for pattern, section_id in heading_patterns:
                if pattern.search(line):
                    key = (section_id, filepath.name, line_num)
                    if key not in seen:
                        seen.add(key)
                        references.append(ObservedReference(
                            section_id=section_id,
                            line_number=line_num,
                            context=line.strip(),
                            transcript_file=filepath.name,
                            session_number=current_session,
                        ))

    return references
