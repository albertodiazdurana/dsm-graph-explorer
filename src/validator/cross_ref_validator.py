"""Cross-reference validator for DSM documentation.

Validates that cross-references (Section X.Y.Z, Appendix X.Y, DSM X.Y)
found in markdown files point to actual sections defined in parsed documents.

Uses severity levels:
- ERROR: Section or appendix reference not found in any parsed document.
- WARNING: DSM document reference not in the known identifiers list.
"""

from dataclasses import dataclass
from enum import Enum

from parser.cross_ref_extractor import CrossReference
from parser.markdown_parser import ParsedDocument


class Severity(Enum):
    """Validation result severity level."""

    ERROR = "error"
    WARNING = "warning"


@dataclass
class ValidationResult:
    """A single validation finding."""

    severity: Severity
    source_file: str
    line: int
    ref_type: str
    target: str
    message: str
    context: str


# Known DSM document identifiers. References to DSM versions not in this
# list produce a WARNING (they may be valid but cannot be verified).
# Includes both short forms (DSM 1) and long forms (DSM 1.0).
KNOWN_DSM_IDS: list[str] = [
    "0",      # START_HERE guide
    "0.1",    # File naming quick reference
    "1",      # DSM 1 (short form)
    "1.0",    # DSM 1.0 methodology
    "1.1",    # DSM 1.1 methodology update
    "2",      # DSM 2 (short form)
    "2.0",    # DSM 2.0 PM guidelines
    "2.1",    # DSM 2.1 PM supplement
    "3",      # DSM 3 multi-agent collaboration
    "4",      # DSM 4 (short form)
    "4.0",    # DSM 4.0 software engineering adaptation
]


def build_section_index(
    documents: list[ParsedDocument],
) -> dict[str, list[str]]:
    """Build an index mapping section numbers to the files they appear in.

    Args:
        documents: Parsed documents with section definitions.

    Returns:
        Dict mapping section number to list of file paths where it is defined.
    """
    index: dict[str, list[str]] = {}
    for doc in documents:
        for section in doc.sections:
            if section.number is not None:
                index.setdefault(section.number, []).append(doc.file)
    return index


def validate_cross_references(
    documents: list[ParsedDocument],
    references: dict[str, list[CrossReference]],
    known_dsm_ids: list[str] | None = None,
) -> list[ValidationResult]:
    """Validate all cross-references against the section index.

    Args:
        documents: Parsed documents containing section definitions.
        references: Map of file path to cross-references found in that file.
        known_dsm_ids: Optional list of recognised DSM document identifiers.
            Defaults to KNOWN_DSM_IDS.

    Returns:
        List of validation results (errors and warnings).
    """
    if known_dsm_ids is None:
        known_dsm_ids = KNOWN_DSM_IDS

    index = build_section_index(documents)
    results: list[ValidationResult] = []

    for file_path, refs in references.items():
        for ref in refs:
            if ref.type in ("section", "appendix"):
                if ref.target not in index:
                    results.append(
                        ValidationResult(
                            severity=Severity.ERROR,
                            source_file=file_path,
                            line=ref.line,
                            ref_type=ref.type,
                            target=ref.target,
                            message=(
                                f"Broken {ref.type} reference: "
                                f"{ref.target} not found in any document"
                            ),
                            context=ref.context,
                        )
                    )
            elif ref.type == "dsm":
                if ref.target not in known_dsm_ids:
                    results.append(
                        ValidationResult(
                            severity=Severity.WARNING,
                            source_file=file_path,
                            line=ref.line,
                            ref_type=ref.type,
                            target=ref.target,
                            message=(
                                f"Unknown DSM document: DSM {ref.target} "
                                f"not in known identifiers list"
                            ),
                            context=ref.context,
                        )
                    )

    return results
