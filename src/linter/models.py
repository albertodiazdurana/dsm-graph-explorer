"""Data models for convention linting.

Defines LintRule (the 6 checks) and LintResult (a single finding).
Reuses Severity from the validator module to avoid duplication.
"""

from dataclasses import dataclass
from enum import Enum

from validator.cross_ref_validator import Severity


class LintRule(Enum):
    """Convention lint rules.

    Error rules (E0xx) indicate violations that should be fixed.
    Warning rules (W0xx) indicate style issues that should be addressed.
    """

    E001 = "E001"  # Emoji/symbol usage
    E002 = "E002"  # TOC headings
    E003 = "E003"  # Mojibake encoding
    W001 = "W001"  # Em-dash punctuation
    W002 = "W002"  # CRLF line endings
    W003 = "W003"  # Backlog metadata validation


RULE_DESCRIPTIONS: dict[LintRule, str] = {
    LintRule.E001: "Emoji/symbol usage (use WARNING:/OK:/ERROR: text)",
    LintRule.E002: "TOC heading (DSM uses hierarchical numbering)",
    LintRule.E003: "Mojibake encoding (double-encoded UTF-8)",
    LintRule.W001: "Em-dash punctuation (use commas/semicolons)",
    LintRule.W002: "CRLF line endings (use Unix LF)",
    LintRule.W003: "Backlog metadata validation (required fields)",
}

DEFAULT_SEVERITY: dict[LintRule, Severity] = {
    LintRule.E001: Severity.ERROR,
    LintRule.E002: Severity.ERROR,
    LintRule.E003: Severity.ERROR,
    LintRule.W001: Severity.WARNING,
    LintRule.W002: Severity.WARNING,
    LintRule.W003: Severity.WARNING,
}


@dataclass
class LintResult:
    """A single lint finding."""

    file: str
    line: int
    column: int
    rule: LintRule
    severity: Severity
    message: str
    context: str
