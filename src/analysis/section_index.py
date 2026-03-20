"""DSM_0.2 section index builder.

Parses DSM_0.2 markdown files (core + modules A-D) and produces a structured
inventory of all sections with metadata. This inventory is the reference list
that all four EXP-009 layers compare against.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from pydantic import BaseModel


class SectionEntry(BaseModel):
    """A single section/protocol in the DSM_0.2 document set."""

    section_id: str
    heading: str
    file: str
    module: str  # "core", "A", "B", "C", "D"
    designed_classification: str  # "always-load" or "on-demand"
    level: int  # heading level (2 = ##, 3 = ###, etc.)
    line_number: int


class DispatchEntry(BaseModel):
    """A row from the Module Dispatch Table."""

    protocol: str
    trigger: str
    module: str  # "A", "B", "C", "D"


class SectionIndex(BaseModel):
    """Complete section inventory for a DSM_0.2 version."""

    version: str
    date: str
    sections: list[SectionEntry]
    dispatch_table: list[DispatchEntry]


# Headings to exclude from the section inventory (metadata, not protocols).
_EXCLUDED_HEADINGS = frozenset({"Module Dispatch Table"})

# Pattern for module file H1 titles like "# DSM_0.2 Module A: Session Lifecycle".
_MODULE_TITLE_RE = re.compile(r"^DSM_0\.2 Module [A-D]:")


def _slugify(title: str) -> str:
    """Convert a heading title to a URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug


def _detect_module(filename: str) -> str:
    """Determine module identifier from filename.

    Returns "core" for the main file, or "A"-"D" for module files.
    """
    match = re.search(r"DSM_0\.2\.([A-D])_", filename)
    if match:
        return match.group(1)
    return "core"


def _parse_headings(filepath: Path) -> list[dict]:
    """Extract all markdown headings from a file.

    Returns a list of dicts with keys: heading, level, line_number.
    """
    heading_re = re.compile(r"^(#{1,6})\s+(.+)$")
    results = []
    for line_number, line in enumerate(filepath.read_text().splitlines(), start=1):
        match = heading_re.match(line)
        if match:
            level = len(match.group(1))
            heading = match.group(2).strip()
            results.append({
                "heading": heading,
                "level": level,
                "line_number": line_number,
            })
    return results


def _parse_dispatch_table(filepath: Path) -> list[DispatchEntry]:
    """Parse the Module Dispatch Table from the core file.

    Expects a markdown table with columns: Protocol | Trigger | Module.
    """
    text = filepath.read_text()
    in_table = False
    entries: list[DispatchEntry] = []
    module_link_re = re.compile(r"\[([A-D])\]")

    for line in text.splitlines():
        if "| Protocol |" in line and "| Trigger |" in line:
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")]
            # Split produces empty strings at boundaries: ['', 'Protocol', 'Trigger', 'Module', '']
            cells = [c for c in cells if c]
            if len(cells) >= 3:
                protocol = cells[0]
                trigger = cells[1]
                module_match = module_link_re.search(cells[2])
                module = module_match.group(1) if module_match else cells[2]
                entries.append(DispatchEntry(
                    protocol=protocol,
                    trigger=trigger,
                    module=module,
                ))
        elif in_table:
            break  # end of table

    return entries


def build_section_index(dsm_path: Path, version: str) -> SectionIndex:
    """Build a complete section index from a DSM_0.2 directory.

    Args:
        dsm_path: Directory containing DSM_0.2 core and module files.
        version: Version string to tag the index with (e.g., "v1.3.69").

    Returns:
        SectionIndex with all sections and the dispatch table.
    """
    dsm_path = Path(dsm_path)
    sections: list[SectionEntry] = []
    dispatch_table: list[DispatchEntry] = []

    # Find all DSM_0.2 files.
    dsm_files = sorted(dsm_path.glob("DSM_0.2*.md"))

    for filepath in dsm_files:
        module = _detect_module(filepath.name)
        classification = "always-load" if module == "core" else "on-demand"

        headings = _parse_headings(filepath)
        for h in headings:
            heading_text = h["heading"]

            # Skip excluded headings.
            if heading_text in _EXCLUDED_HEADINGS:
                continue

            # Skip module file H1 titles.
            if h["level"] == 1 and _MODULE_TITLE_RE.match(heading_text):
                continue

            sections.append(SectionEntry(
                section_id=_slugify(heading_text),
                heading=heading_text,
                file=filepath.name,
                module=module,
                designed_classification=classification,
                level=h["level"],
                line_number=h["line_number"],
            ))

        # Parse dispatch table from core file.
        if module == "core":
            dispatch_table = _parse_dispatch_table(filepath)

    return SectionIndex(
        version=version,
        date=date.today().isoformat(),
        sections=sections,
        dispatch_table=dispatch_table,
    )
