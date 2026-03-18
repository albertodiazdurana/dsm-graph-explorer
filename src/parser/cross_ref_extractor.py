"""Cross-reference extractor for DSM documentation.

Extracts prose cross-reference patterns from markdown files:
- "Section X.Y.Z" references
- "Appendix X.Y" references
- "DSM_X.Y" and "DSM X.Y" document references
- Heading title references (exact match against known heading titles)

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

    with path.open(encoding="utf-8") as f:
        lines = f.readlines()

    return _extract_from_lines(lines, context_window)


def extract_cross_references_from_content(
    content: str, file_path: str, context_window: int = _DEFAULT_CONTEXT_WINDOW
) -> list[CrossReference]:
    """Extract cross-references from markdown content string.

    Same logic as extract_cross_references but accepts content directly,
    useful when file contents come from git show rather than disk.

    Args:
        content: Markdown text content.
        file_path: Virtual file path (unused in extraction, kept for symmetry).
        context_window: Number of non-blank, non-code lines to capture.

    Returns:
        List of CrossReference objects found in the content.
    """
    lines = content.splitlines(keepends=True)
    return _extract_from_lines(lines, context_window)


def _extract_from_lines(
    lines: list[str], context_window: int
) -> list[CrossReference]:
    """Core extraction logic operating on pre-read lines."""
    references: list[CrossReference] = []

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


def extract_heading_references(
    path: Path | str | None = None,
    known_headings: set[str] | None = None,
    *,
    content: str | None = None,
    file_path: str = "<string>",
) -> list[CrossReference]:
    """Extract references to known heading titles from prose text.

    Scans each non-code-block, non-heading line for exact (case-insensitive)
    occurrences of known heading titles. Returns CrossReference objects with
    type="heading" and target set to the original-case title as found in
    the text.

    Args:
        path: Path to the markdown file (mutually exclusive with content).
        known_headings: Set of normalized (lowercase) heading titles to match.
        content: Markdown text content (mutually exclusive with path).
        file_path: Virtual file path when using content parameter.

    Returns:
        List of CrossReference objects for heading title matches.
    """
    if known_headings is None or len(known_headings) == 0:
        return []

    if path is not None and content is not None:
        raise ValueError("Provide either path or content, not both")
    if path is not None:
        p = Path(path)
        with p.open(encoding="utf-8") as f:
            lines = f.readlines()
    elif content is not None:
        lines = content.splitlines(keepends=True)
    else:
        raise ValueError("Provide either path or content")

    # Build code block map
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

    references: list[CrossReference] = []

    for idx, raw_line in enumerate(lines):
        if idx in code_block_lines:
            continue

        line = raw_line.rstrip("\n")
        stripped = line.lstrip()

        # Skip heading definition lines (## Title)
        if stripped.startswith("#"):
            continue

        line_lower = line.lower()

        for heading in known_headings:
            pos = line_lower.find(heading)
            if pos == -1:
                continue

            # Extract the original-case text from the line
            original_title = line[pos : pos + len(heading)]
            # Capitalize to match heading style
            original_title = _restore_title_case(original_title, heading, line, pos)

            references.append(
                CrossReference(
                    type="heading",
                    target=original_title,
                    line=idx + 1,
                    context=line,
                )
            )

    return references


def _restore_title_case(
    matched_text: str, _heading: str, line: str, pos: int
) -> str:
    """Restore the original case of a matched heading title from the source line."""
    return line[pos : pos + len(_heading)]
