"""Version consistency validator for DSM documentation.

Extracts version declarations from files (e.g., DSM_0, README, CHANGELOG)
and checks that they agree. Reports mismatches as VersionMismatch results.

Recognised version patterns:
- "Version: X.Y.Z" or "**Version:** X.Y.Z"
- "DSM Version: X.Y.Z"
- "vX.Y.Z" standalone prefix
- "[X.Y.Z]" in changelog headings
"""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VersionInfo:
    """A version declaration found in a file."""

    file: str
    version: str
    line: int
    context: str


@dataclass
class VersionMismatch:
    """A version inconsistency across files."""

    versions: list[VersionInfo]
    message: str


# Patterns that capture version strings.
# Order matters: more specific patterns first.
_VERSION_PATTERNS = [
    # "**Version:** 1.3.19" or "Version: 1.3.19"
    re.compile(r"\*{0,2}(?:DSM\s+)?Version\s*:\s*\*{0,2}\s*v?(\d+\.\d+(?:\.\d+)*)"),
    # Changelog bracket: "## [1.3.19]"
    re.compile(r"\[(\d+\.\d+(?:\.\d+)*)\]"),
    # Standalone v-prefix: "v1.2.3" (word boundary)
    re.compile(r"\bv(\d+\.\d+(?:\.\d+)*)\b"),
]


def extract_versions(path: Path | str) -> list[VersionInfo]:
    """Extract all version declarations from a file.

    Args:
        path: Path to the file to scan.

    Returns:
        List of VersionInfo objects, one per version pattern match.
    """
    path = Path(path)
    results: list[VersionInfo] = []
    seen: set[tuple[int, str]] = set()  # (line, version) dedup

    with path.open(encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            context = line.rstrip("\n")
            for pattern in _VERSION_PATTERNS:
                for m in pattern.finditer(line):
                    version = m.group(1)
                    key = (line_num, version)
                    if key not in seen:
                        seen.add(key)
                        results.append(
                            VersionInfo(
                                file=str(path),
                                version=version,
                                line=line_num,
                                context=context,
                            )
                        )

    return results


def validate_version_consistency(
    files: list[Path | str],
) -> list[VersionMismatch]:
    """Check that version declarations are consistent across files.

    Extracts the primary (first) version from each file. If files declare
    different primary versions, returns a VersionMismatch listing all of them.

    Files with no version declarations are silently skipped.

    Args:
        files: List of file paths to check.

    Returns:
        List of VersionMismatch results (empty if consistent).
    """
    primary_versions: list[VersionInfo] = []

    for file_path in files:
        versions = extract_versions(file_path)
        if versions:
            primary_versions.append(versions[0])

    if len(primary_versions) <= 1:
        return []

    # Check if all primary versions agree.
    unique = {v.version for v in primary_versions}
    if len(unique) == 1:
        return []

    # Build mismatch message.
    parts = [f"{v.file} declares {v.version}" for v in primary_versions]
    message = "Version mismatch: " + ", ".join(parts)

    return [VersionMismatch(versions=primary_versions, message=message)]
