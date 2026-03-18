"""Markdown parser for extracting sections from DSM documentation.

Reads markdown files and extracts section headings with their hierarchical
numbering, titles, line numbers, and heading levels. Handles both numbered
sections (1.2.3) and appendix sections (A.1.2).
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

_DEFAULT_EXCERPT_WORDS = 50


@dataclass
class Section:
    """A section extracted from a markdown document."""

    number: str | None
    title: str
    line: int
    level: int
    context_excerpt: str = ""


@dataclass
class SkeletonEntry:
    """A lightweight heading entry for structural scanning.

    Contains heading text, nesting level, and line range without
    excerpt extraction. Useful for quick structural overviews.
    """

    heading: str
    level: int
    line: int
    end_line: int
    number: str | None


@dataclass
class ParsedDocument:
    """Result of parsing a markdown file."""

    file: str
    sections: list[Section]


# Regex patterns for heading content parsing
# Note: \.? allows optional trailing period (DSM uses "### 2.3.7. Title" format)
_NUMBERED_HEADING = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+(.+)$")
_APPENDIX_HEADING = re.compile(r"^Appendix\s+([A-E]):\s*(.+)$")
_APPENDIX_SUBSECTION = re.compile(r"^([A-E](?:\.\d+)+)\.?\s+(.+)$")


def parse_markdown_file(
    path: Path | str, excerpt_words: int = _DEFAULT_EXCERPT_WORDS
) -> ParsedDocument:
    """Parse a markdown file and extract all sections.

    Args:
        path: Path to the markdown file.
        excerpt_words: Maximum number of words for context_excerpt.

    Returns:
        ParsedDocument with file path and list of sections.
    """
    path = Path(path)

    with path.open(encoding="utf-8") as f:
        lines = f.readlines()

    return _parse_lines(lines, str(path), excerpt_words)


def parse_markdown_content(
    content: str, file_path: str, excerpt_words: int = _DEFAULT_EXCERPT_WORDS
) -> ParsedDocument:
    """Parse markdown content from a string and extract all sections.

    Same logic as parse_markdown_file but accepts content directly,
    useful when file contents come from git show rather than disk.

    Args:
        content: Markdown text content.
        file_path: Virtual file path to store in the ParsedDocument.
        excerpt_words: Maximum number of words for context_excerpt.

    Returns:
        ParsedDocument with file path and list of sections.
    """
    lines = content.splitlines(keepends=True)
    return _parse_lines(lines, file_path, excerpt_words)


def extract_skeleton(
    path: Path | str | None = None,
    *,
    content: str | None = None,
    file_path: str = "<string>",
) -> list[SkeletonEntry]:
    """Extract a lightweight heading skeleton from a markdown file or string.

    Returns heading text, nesting level, and line ranges without
    building full sections or extracting excerpts. Accepts either
    a file path or content string (not both).

    Args:
        path: Path to the markdown file (mutually exclusive with content).
        content: Markdown text content (mutually exclusive with path).
        file_path: Virtual file path when using content parameter.

    Returns:
        List of SkeletonEntry objects representing the document structure.
    """
    if path is not None and content is not None:
        raise ValueError("Provide either path or content, not both")
    if path is not None:
        path = Path(path)
        with path.open(encoding="utf-8") as f:
            lines = f.readlines()
    elif content is not None:
        lines = content.splitlines(keepends=True)
    else:
        raise ValueError("Provide either path or content")

    headings = _detect_headings(lines)
    total_lines = len(lines)
    entries: list[SkeletonEntry] = []

    for i, (idx, level, title, number) in enumerate(headings):
        end_idx = headings[i + 1][0] if i + 1 < len(headings) else total_lines
        entries.append(
            SkeletonEntry(
                heading=title,
                level=level,
                line=idx + 1,
                end_line=end_idx + 1,
                number=number,
            )
        )

    return entries


def _detect_headings(
    lines: list[str],
) -> list[tuple[int, int, str, str | None]]:
    """Detect all markdown headings and return their metadata.

    Returns:
        List of (line_index, level, title, number) tuples.
    """
    headings: list[tuple[int, int, str, str | None]] = []

    for idx, raw_line in enumerate(lines):
        line = raw_line.rstrip("\n")

        if not line.startswith("#"):
            continue

        level = 0
        for ch in line:
            if ch == "#":
                level += 1
            else:
                break

        if level == 0 or level >= len(line) or line[level] != " ":
            continue

        content = line[level + 1 :].strip()
        if not content:
            continue

        number, title = _parse_heading_content(content)
        headings.append((idx, level, title, number))

    return headings


def _parse_lines(
    lines: list[str], file_path: str, excerpt_words: int
) -> ParsedDocument:
    """Core parsing logic operating on pre-read lines."""
    sections: list[Section] = []
    headings = _detect_headings(lines)

    for i, (idx, level, title, number) in enumerate(headings):
        next_heading_idx = (
            headings[i + 1][0] if i + 1 < len(headings) else len(lines)
        )
        excerpt = _extract_excerpt(lines, idx + 1, next_heading_idx, excerpt_words)
        sections.append(
            Section(
                number=number,
                title=title,
                line=idx + 1,
                level=level,
                context_excerpt=excerpt,
            )
        )

    return ParsedDocument(file=file_path, sections=sections)


def _extract_excerpt(
    lines: list[str], start: int, end: int, word_limit: int
) -> str:
    """Extract a prose excerpt from lines between two headings.

    Fallback chain:
    1. First prose paragraph (skip blank lines, headings, code fences, tables)
    2. First list item text (strip bullet prefix)
    3. Empty string if nothing extractable
    """
    in_code_block = False
    prose_words: list[str] = []
    first_list_item: str | None = None

    for i in range(start, end):
        raw = lines[i].rstrip("\n")
        stripped = raw.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        if not stripped:
            if prose_words:
                break
            continue

        if stripped.startswith("#"):
            break

        if stripped.startswith("|") or stripped.startswith("---"):
            continue

        if stripped.startswith(("- ", "* ", "+ ")):
            if first_list_item is None:
                first_list_item = stripped.lstrip("-*+ ").strip()
            continue

        if re.match(r"^\d+\.\s", stripped):
            if first_list_item is None:
                first_list_item = re.sub(r"^\d+\.\s+", "", stripped).strip()
            continue

        words = stripped.split()
        prose_words.extend(words)
        if len(prose_words) >= word_limit:
            break

    if prose_words:
        return " ".join(prose_words[:word_limit])

    if first_list_item:
        return first_list_item

    return ""


def _parse_heading_content(content: str) -> tuple[str | None, str]:
    """Extract section number and title from heading content.

    Handles three formats:
    - Numbered: "1.2.3 Title Text"
    - Appendix heading: "Appendix A: Title Text"
    - Appendix subsection: "A.1.2 Title Text"
    - Unnumbered: "Title Text" (returns number=None)
    """
    # Try numbered section: "1.2.3 Title"
    m = _NUMBERED_HEADING.match(content)
    if m:
        return m.group(1), m.group(2).strip()

    # Try appendix heading: "Appendix A: Title"
    m = _APPENDIX_HEADING.match(content)
    if m:
        return m.group(1), m.group(2).strip()

    # Try appendix subsection: "A.1.2 Title"
    m = _APPENDIX_SUBSECTION.match(content)
    if m:
        return m.group(1), m.group(2).strip()

    # Unnumbered heading
    return None, content.strip()
