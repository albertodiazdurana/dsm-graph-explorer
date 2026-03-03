"""Convention lint checks for DSM markdown files.

Each check function takes a file path, lines, and optional severity
overrides, returning a list of LintResult findings.
"""

import re
from pathlib import Path

from linter.models import DEFAULT_SEVERITY, LintResult, LintRule
from validator.cross_ref_validator import Severity

# --- Patterns ---

# E001: Common emoji/symbol characters that should be text labels
_EMOJI_RE = re.compile(
    r"[\u2705\u274C\u26A0\uFE0F\u2139\uFE0F\u2757\u2753\u2B50\u274E"
    r"\U0001F534\U0001F7E2\U0001F7E1\U0001F6A8\U0001F4A1\U0001F4CC]"
)

# E002: TOC-style headings (DSM uses hierarchical numbering)
_TOC_RE = re.compile(r"^#{1,6}\s+.*\b(Table\s+of\s+Contents|TOC)\b", re.IGNORECASE)

# E003: Common mojibake patterns (double-encoded UTF-8)
# When UTF-8 text is re-decoded as Latin-1/CP1252, accented characters become
# \u00c3 + another byte, and smart quotes/dashes become \u00e2\u20ac sequences.
_MOJIBAKE_RE = re.compile(
    "\u00c3[\u00a1\u00a9\u00ad\u00b3\u00ba\u00b1\u00bc\u00b6\u00a4]"  # accented vowels, ñ, ü, ö, ä
    "|\u00e2\u20ac[\u2122\u0153\u009d\u201c]"  # smart quotes and em-dash
)

# W001: Em-dash and en-dash
_EMDASH_RE = re.compile(r"[—–]")

# W003: Required backlog proposal fields
_BACKLOG_REQUIRED_FIELDS = {"ID", "Status", "Priority"}


def _severity(rule: LintRule, overrides: dict[LintRule, Severity] | None) -> Severity:
    """Resolve severity for a rule, applying overrides if present."""
    if overrides and rule in overrides:
        return overrides[rule]
    return DEFAULT_SEVERITY[rule]


def check_emoji_usage(
    file_path: str,
    lines: list[str],
    overrides: dict[LintRule, Severity] | None = None,
) -> list[LintResult]:
    """E001: Flag emoji/symbol characters that should be text labels."""
    results = []
    sev = _severity(LintRule.E001, overrides)
    for i, line in enumerate(lines, start=1):
        for m in _EMOJI_RE.finditer(line):
            results.append(
                LintResult(
                    file=file_path,
                    line=i,
                    column=m.start() + 1,
                    rule=LintRule.E001,
                    severity=sev,
                    message=f"Emoji/symbol U+{ord(m.group()):04X} found; use text labels instead",
                    context=line.rstrip(),
                )
            )
    return results


def check_toc_headings(
    file_path: str,
    lines: list[str],
    overrides: dict[LintRule, Severity] | None = None,
) -> list[LintResult]:
    """E002: Flag TOC headings (DSM uses hierarchical numbering)."""
    results = []
    sev = _severity(LintRule.E002, overrides)
    for i, line in enumerate(lines, start=1):
        m = _TOC_RE.match(line)
        if m:
            results.append(
                LintResult(
                    file=file_path,
                    line=i,
                    column=1,
                    rule=LintRule.E002,
                    severity=sev,
                    message="TOC heading found; DSM uses hierarchical numbering",
                    context=line.rstrip(),
                )
            )
    return results


def check_mojibake(
    file_path: str,
    lines: list[str],
    overrides: dict[LintRule, Severity] | None = None,
) -> list[LintResult]:
    """E003: Flag mojibake (double-encoded UTF-8) patterns."""
    results = []
    sev = _severity(LintRule.E003, overrides)
    for i, line in enumerate(lines, start=1):
        for m in _MOJIBAKE_RE.finditer(line):
            results.append(
                LintResult(
                    file=file_path,
                    line=i,
                    column=m.start() + 1,
                    rule=LintRule.E003,
                    severity=sev,
                    message=f"Mojibake pattern '{m.group()}' found; check encoding",
                    context=line.rstrip(),
                )
            )
    return results


def check_emdash(
    file_path: str,
    lines: list[str],
    overrides: dict[LintRule, Severity] | None = None,
) -> list[LintResult]:
    """W001: Flag em-dash and en-dash usage."""
    results = []
    sev = _severity(LintRule.W001, overrides)
    for i, line in enumerate(lines, start=1):
        for m in _EMDASH_RE.finditer(line):
            char_name = "em-dash" if m.group() == "—" else "en-dash"
            results.append(
                LintResult(
                    file=file_path,
                    line=i,
                    column=m.start() + 1,
                    rule=LintRule.W001,
                    severity=sev,
                    message=f"{char_name.capitalize()} found; use commas or semicolons",
                    context=line.rstrip(),
                )
            )
    return results


def check_crlf(
    file_path: str,
    raw_content: str,
    overrides: dict[LintRule, Severity] | None = None,
) -> list[LintResult]:
    """W002: Flag CRLF line endings.

    Takes raw_content (not split lines) to detect \\r\\n before splitting.
    """
    results = []
    sev = _severity(LintRule.W002, overrides)
    for i, line in enumerate(raw_content.split("\n"), start=1):
        if line.endswith("\r"):
            results.append(
                LintResult(
                    file=file_path,
                    line=i,
                    column=len(line),
                    rule=LintRule.W002,
                    severity=sev,
                    message="CRLF line ending found; use Unix LF",
                    context="(line ending)",
                )
            )
    return results


def check_backlog_metadata(
    file_path: str,
    lines: list[str],
    overrides: dict[LintRule, Severity] | None = None,
) -> list[LintResult]:
    """W003: Validate backlog proposals have required fields.

    Only runs on files in a backlog/ or feedback/ directory whose name
    contains 'backlog'. Checks that each proposal block has ID, Status,
    and Priority fields.
    """
    path = Path(file_path)
    is_backlog = (
        "backlog" in path.name.lower()
        or "backlog" in str(path.parent).lower()
    )
    if not is_backlog:
        return []

    results = []
    sev = _severity(LintRule.W003, overrides)

    # Track proposal blocks: lines starting with "### " or "## Proposal"
    proposal_start = None
    proposal_title = ""
    found_fields: set[str] = set()

    def _emit_missing(start_line: int, title: str, fields: set[str]) -> None:
        missing = _BACKLOG_REQUIRED_FIELDS - fields
        if missing:
            results.append(
                LintResult(
                    file=file_path,
                    line=start_line,
                    column=1,
                    rule=LintRule.W003,
                    severity=sev,
                    message=f"Proposal '{title}' missing fields: {', '.join(sorted(missing))}",
                    context=title,
                )
            )

    for i, line in enumerate(lines, start=1):
        # Detect proposal headings (## or ###)
        if re.match(r"^#{2,3}\s+", line) and ("proposal" in line.lower() or "#" in line):
            # Close previous proposal block
            if proposal_start is not None:
                _emit_missing(proposal_start, proposal_title, found_fields)
            proposal_start = i
            proposal_title = line.strip().lstrip("#").strip()
            found_fields = set()
        elif proposal_start is not None:
            # Look for field markers like "**ID:**", "**Status:**", etc.
            for field in _BACKLOG_REQUIRED_FIELDS:
                if re.search(rf"\*\*{field}[:\s*]", line, re.IGNORECASE):
                    found_fields.add(field)
                elif re.match(rf"^-\s*{field}\s*:", line, re.IGNORECASE):
                    found_fields.add(field)

    # Close last proposal block
    if proposal_start is not None:
        _emit_missing(proposal_start, proposal_title, found_fields)

    return results


def run_all_checks(
    file_path: str,
    raw_content: str,
    overrides: dict[LintRule, Severity] | None = None,
) -> list[LintResult]:
    """Run all 6 lint checks on a file and return combined results."""
    lines = raw_content.replace("\r\n", "\n").split("\n")

    results: list[LintResult] = []
    results.extend(check_emoji_usage(file_path, lines, overrides))
    results.extend(check_toc_headings(file_path, lines, overrides))
    results.extend(check_mojibake(file_path, lines, overrides))
    results.extend(check_emdash(file_path, lines, overrides))
    results.extend(check_crlf(file_path, raw_content, overrides))
    results.extend(check_backlog_metadata(file_path, lines, overrides))

    # Sort by line, then column
    results.sort(key=lambda r: (r.line, r.column))
    return results