"""Cross-reference extractor for DSM documentation.

Extracts prose cross-reference patterns from markdown files:
- "Section X.Y.Z" references
- "Appendix X.Y" references
- "DSM_X.Y" and "DSM X.Y" document references

Skips references inside fenced code blocks to avoid false positives.
"""

import re
from dataclasses import dataclass
from pathlib import Path

_DEFAULT_CONTEXT_WINDOW = 3


@dataclass
class CrossReference:
    """A cross-reference found in a markdown document."""

    type: str  # "section", "appendix", or "dsm"
    target: str
    line: int
    context: str
    context_before: str = ""
    context_after: str = ""


# Cross-reference patterns
_SECTION_REF = re.compile(r"Section\s+(\d+(?:\.\d+)*)")
_APPENDIX_REF = re.compile(r"Appendix\s+([A-E](?:\.\d+)*)")
_DSM_REF = re.compile(r"DSM[_ ](\d+(?:\.\d+)*)")


def extract_cross_references(
    path: Path | str, context_window: int = _DEFAULT_CONTEXT_WINDOW
) -> list[CrossReference]:
    """Extract all cross-references from a markdown file.

    Reads all lines, tracks fenced code block state, and applies three
    regex patterns for Section, Appendix, and DSM references. Captures
    surrounding lines as context_before/context_after.

    Args:
        path: Path to the markdown file.
        context_window: Number of non-blank, non-code lines to capture
            before and after each reference.

    Returns:
        List of CrossReference objects found in the file.
    """
    path = Path(path)
    references: list[CrossReference] = []

    with path.open(encoding="utf-8") as f:
        lines = f.readlines()

    # Build a map of which lines are inside code blocks
    in_code_block = False
    code_block_lines: set[int] = set()
    for idx, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            code_block_lines.add(idx)
            continue
        if in_code_block:
            code_block_lines.add(idx)

    # Build list of content line indices (not in code blocks, not blank)
    content_indices = [
        idx
        for idx in range(len(lines))
        if idx not in code_block_lines and lines[idx].strip()
    ]

    for idx, raw_line in enumerate(lines):
        if idx in code_block_lines:
            continue

        line = raw_line.rstrip("\n")
        line_num = idx + 1

        patterns = [
            (_SECTION_REF, "section"),
            (_APPENDIX_REF, "appendix"),
            (_DSM_REF, "dsm"),
        ]

        for pattern, ref_type in patterns:
            for m in pattern.finditer(raw_line):
                before = _gather_context(lines, content_indices, idx, context_window, direction=-1)
                after = _gather_context(lines, content_indices, idx, context_window, direction=1)
                references.append(
                    CrossReference(
                        type=ref_type,
                        target=m.group(1),
                        line=line_num,
                        context=line,
                        context_before=before,
                        context_after=after,
                    )
                )

    return references


def _gather_context(
    lines: list[str],
    content_indices: list[int],
    ref_idx: int,
    count: int,
    direction: int,
) -> str:
    """Gather up to `count` content lines before or after ref_idx.

    Args:
        lines: All file lines.
        content_indices: Sorted indices of non-blank, non-code-block lines.
        ref_idx: Index of the reference line.
        count: Number of lines to gather.
        direction: -1 for before, +1 for after.

    Returns:
        Gathered lines joined with spaces.
    """
    gathered: list[str] = []

    if direction == -1:
        for ci in reversed(content_indices):
            if ci >= ref_idx:
                continue
            gathered.append(lines[ci].strip())
            if len(gathered) >= count:
                break
        gathered.reverse()
    else:
        for ci in content_indices:
            if ci <= ref_idx:
                continue
            gathered.append(lines[ci].strip())
            if len(gathered) >= count:
                break

    return " ".join(gathered)
