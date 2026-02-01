"""Markdown parser for extracting sections from DSM documentation.

Reads markdown files and extracts section headings with their hierarchical
numbering, titles, line numbers, and heading levels. Handles both numbered
sections (1.2.3) and appendix sections (A.1.2).
"""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Section:
    """A section extracted from a markdown document."""

    number: str | None
    title: str
    line: int
    level: int


@dataclass
class ParsedDocument:
    """Result of parsing a markdown file."""

    file: str
    sections: list[Section]


# Regex patterns for heading content parsing
_NUMBERED_HEADING = re.compile(r"^(\d+(?:\.\d+)*)\s+(.+)$")
_APPENDIX_HEADING = re.compile(r"^Appendix\s+([A-E]):\s*(.+)$")
_APPENDIX_SUBSECTION = re.compile(r"^([A-E](?:\.\d+)+)\s+(.+)$")


def parse_markdown_file(path: Path | str) -> ParsedDocument:
    """Parse a markdown file and extract all sections.

    Args:
        path: Path to the markdown file.

    Returns:
        ParsedDocument with file path and list of sections.
    """
    path = Path(path)
    sections: list[Section] = []

    with path.open(encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.rstrip("\n")

            if not line.startswith("#"):
                continue

            # Count heading level (number of # characters)
            level = 0
            for ch in line:
                if ch == "#":
                    level += 1
                else:
                    break

            # Must have a space after the # characters
            if level == 0 or level >= len(line) or line[level] != " ":
                continue

            content = line[level + 1 :].strip()
            if not content:
                continue

            number, title = _parse_heading_content(content)
            sections.append(
                Section(number=number, title=title, line=line_num, level=level)
            )

    return ParsedDocument(file=str(path), sections=sections)


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
