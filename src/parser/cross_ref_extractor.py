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


@dataclass
class CrossReference:
    """A cross-reference found in a markdown document."""

    type: str  # "section", "appendix", or "dsm"
    target: str
    line: int
    context: str


# Cross-reference patterns
_SECTION_REF = re.compile(r"Section\s+(\d+(?:\.\d+)*)")
_APPENDIX_REF = re.compile(r"Appendix\s+([A-E](?:\.\d+)*)")
_DSM_REF = re.compile(r"DSM[_ ](\d+(?:\.\d+)*)")


def extract_cross_references(path: Path | str) -> list[CrossReference]:
    """Extract all cross-references from a markdown file.

    Iterates line-by-line, tracking fenced code block state to skip
    references inside code blocks. Applies three regex patterns for
    Section, Appendix, and DSM references.

    Args:
        path: Path to the markdown file.

    Returns:
        List of CrossReference objects found in the file.
    """
    path = Path(path)
    references: list[CrossReference] = []
    in_code_block = False

    with path.open(encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            stripped = line.strip()

            # Toggle code block state on fenced delimiters
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            context = line.rstrip("\n")

            # Extract Section X.Y.Z references
            for m in _SECTION_REF.finditer(line):
                references.append(
                    CrossReference(
                        type="section",
                        target=m.group(1),
                        line=line_num,
                        context=context,
                    )
                )

            # Extract Appendix X.Y references
            for m in _APPENDIX_REF.finditer(line):
                references.append(
                    CrossReference(
                        type="appendix",
                        target=m.group(1),
                        line=line_num,
                        context=context,
                    )
                )

            # Extract DSM_X.Y and DSM X.Y references
            for m in _DSM_REF.finditer(line):
                references.append(
                    CrossReference(
                        type="dsm",
                        target=m.group(1),
                        line=line_num,
                        context=context,
                    )
                )

    return references
