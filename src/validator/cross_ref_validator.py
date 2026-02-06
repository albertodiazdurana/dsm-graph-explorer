"""Cross-reference validator for DSM documentation.

Validates that cross-references (Section X.Y.Z, Appendix X.Y, DSM X.Y)
found in markdown files point to actual sections defined in parsed documents.

Uses severity levels:
- ERROR: Section or appendix reference not found in any parsed document.
- WARNING: DSM document reference not in the known identifiers list.
- INFO: Issue in a file classified as informational by config.
"""

import fnmatch
from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path

from config.config_loader import SeverityMapping
from parser.cross_ref_extractor import CrossReference
from parser.markdown_parser import ParsedDocument


class Severity(Enum):
    """Validation result severity level."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


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
    "0.1",    # File naming quick reference (deprecated)
    "0.2",    # Custom instructions
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


_SEVERITY_MAP: dict[str, Severity] = {
    "ERROR": Severity.ERROR,
    "WARNING": Severity.WARNING,
    "INFO": Severity.INFO,
}


def assign_severity(
    filepath: str | Path,
    severity_mappings: list[SeverityMapping],
    default_severity: str = "WARNING",
) -> Severity:
    """Assign severity to a file based on config pattern matching.

    First matching pattern wins. Falls back to default_severity.

    Args:
        filepath: Path to the file being validated.
        severity_mappings: Ordered list of pattern → severity mappings.
        default_severity: Severity level when no pattern matches.

    Returns:
        The assigned Severity enum value.
    """
    filename = Path(filepath).name
    normalized = str(filepath).replace("\\", "/")

    for mapping in severity_mappings:
        pattern = mapping.pattern.replace("\\", "/")
        # Match against filename (for patterns without path separator)
        if "/" not in pattern and fnmatch.fnmatch(filename, pattern):
            return _SEVERITY_MAP[mapping.level]
        # Match against full relative path
        if fnmatch.fnmatch(normalized, pattern):
            return _SEVERITY_MAP[mapping.level]

    return _SEVERITY_MAP[default_severity]


def apply_severity_overrides(
    results: list[ValidationResult],
    severity_mappings: list[SeverityMapping],
    default_severity: str = "WARNING",
) -> list[ValidationResult]:
    """Override result severities based on config file patterns.

    Args:
        results: Validation results with base severities.
        severity_mappings: Ordered list of pattern → severity mappings.
        default_severity: Severity level when no pattern matches.

    Returns:
        New list with severities overridden by config patterns.
        If no mappings, returns results unchanged.
    """
    if not severity_mappings:
        return results

    return [
        replace(
            r,
            severity=assign_severity(
                r.source_file, severity_mappings, default_severity
            ),
        )
        for r in results
    ]
