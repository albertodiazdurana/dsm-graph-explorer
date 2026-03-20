"""Layer 1: CLAUDE.md declared reference extraction.

Parses a spoke project's CLAUDE.md to find explicit references to DSM_0.2
sections, protocols, and templates. Matches references against a SectionIndex
to identify which sections the project declares it uses.
"""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel

from analysis.section_index import SectionIndex


class DeclaredReference(BaseModel):
    """A single reference to a DSM_0.2 section found in CLAUDE.md."""

    section_id: str
    line_number: int
    context: str  # the line where the reference was found
    match_type: str  # "at-import", "reinforcement", "name-mention"


# Pattern for @-import lines.
_AT_IMPORT_RE = re.compile(r"^@.+DSM_0\.2")

# Pattern for reinforcement headings: "## Protocol Name (reinforces inherited protocol)"
_REINFORCEMENT_RE = re.compile(
    r"^#{1,6}\s+(.+?)\s*\(reinforces\s+inherited\s+protocol\)",
    re.IGNORECASE,
)


def build_heading_patterns(
    index: SectionIndex,
) -> list[tuple[re.Pattern, str]]:
    """Build regex patterns for each section heading in the index.

    Returns a list of (compiled_pattern, section_id) tuples, sorted by
    heading length descending so longer matches take priority.
    """
    patterns = []
    for section in index.sections:
        # Match the heading text as a whole phrase (case-insensitive).
        # Use word boundaries to avoid partial matches.
        # Strip numbering prefix (e.g., "1. " from "1. Composition Challenge Protocol")
        # for matching, but keep the full heading for the pattern.
        heading = section.heading
        # Escape for regex.
        escaped = re.escape(heading)
        pattern = re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)
        patterns.append((pattern, section.section_id))

        # Also create pattern without numbering prefix for module sections.
        stripped = re.sub(r"^\d+\.\s+", "", heading)
        if stripped != heading:
            escaped_stripped = re.escape(stripped)
            pattern_stripped = re.compile(
                rf"(?<!\w){escaped_stripped}(?!\w)", re.IGNORECASE
            )
            patterns.append((pattern_stripped, section.section_id))

    # Sort by pattern length (longer first) to prefer specific matches.
    patterns.sort(key=lambda p: len(p[0].pattern), reverse=True)
    return patterns


def extract_declared_references(
    claude_md_path: Path,
    section_index: SectionIndex,
) -> list[DeclaredReference]:
    """Extract references to DSM_0.2 sections from a CLAUDE.md file.

    Args:
        claude_md_path: Path to the spoke project's CLAUDE.md.
        section_index: The DSM_0.2 section index to match against.

    Returns:
        List of DeclaredReference objects, one per reference found.
    """
    claude_md_path = Path(claude_md_path)
    text = claude_md_path.read_text()
    if not text.strip():
        return []

    lines = text.splitlines()
    heading_patterns = build_heading_patterns(section_index)
    references: list[DeclaredReference] = []
    seen: set[tuple[str, int, str]] = set()

    def _add(section_id: str, line_num: int, context: str, match_type: str) -> None:
        key = (section_id, line_num, match_type)
        if key not in seen:
            seen.add(key)
            references.append(DeclaredReference(
                section_id=section_id,
                line_number=line_num,
                context=context.strip(),
                match_type=match_type,
            ))

    for line_num, line in enumerate(lines, start=1):
        # 1. Check @-imports.
        if _AT_IMPORT_RE.match(line):
            _add("__at_import__", line_num, line, "at-import")
            continue

        # 2. Check reinforcement headings.
        reinforce_match = _REINFORCEMENT_RE.match(line)
        if reinforce_match:
            heading_text = reinforce_match.group(1).strip()
            # Find matching section in index.
            for pattern, section_id in heading_patterns:
                if pattern.search(heading_text):
                    _add(section_id, line_num, line, "reinforcement")
                    break
            continue

        # 3. Check name mentions (protocol/section names in body text).
        for pattern, section_id in heading_patterns:
            if pattern.search(line):
                _add(section_id, line_num, line, "name-mention")

    return references
