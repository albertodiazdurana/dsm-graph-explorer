"""Tests for convention linter checks.

Covers all 6 rules (E001-E003, W001-W003) plus the run_all_checks
orchestrator and severity override behaviour.
"""

import pytest

from linter.models import DEFAULT_SEVERITY, LintResult, LintRule
from linter.checks import (
    check_emoji_usage,
    check_toc_headings,
    check_mojibake,
    check_emdash,
    check_crlf,
    check_backlog_metadata,
    run_all_checks,
)
from validator.cross_ref_validator import Severity


# ---------------------------------------------------------------------------
# E001: Emoji/symbol usage
# ---------------------------------------------------------------------------


class TestCheckEmojiUsage:
    def test_flags_checkmark_emoji(self):
        lines = ["All good \u2705 here"]
        results = check_emoji_usage("test.md", lines)
        assert len(results) == 1
        assert results[0].rule == LintRule.E001
        assert results[0].line == 1
        assert "U+2705" in results[0].message

    def test_flags_cross_mark(self):
        lines = ["Failed \u274C badly"]
        results = check_emoji_usage("test.md", lines)
        assert len(results) == 1
        assert results[0].rule == LintRule.E001

    def test_flags_multiple_emoji_on_same_line(self):
        lines = ["\u2705 ok \u274C bad"]
        results = check_emoji_usage("test.md", lines)
        assert len(results) == 2

    def test_clean_line_no_results(self):
        lines = ["WARNING: something happened", "OK: all clear"]
        results = check_emoji_usage("test.md", lines)
        assert results == []

    def test_multiline(self):
        lines = ["line one", "emoji \U0001F534 here", "line three"]
        results = check_emoji_usage("test.md", lines)
        assert len(results) == 1
        assert results[0].line == 2

    def test_default_severity_is_error(self):
        lines = ["\u2705"]
        results = check_emoji_usage("test.md", lines)
        assert results[0].severity == Severity.ERROR


# ---------------------------------------------------------------------------
# E002: TOC headings
# ---------------------------------------------------------------------------


class TestCheckTocHeadings:
    def test_flags_table_of_contents_heading(self):
        lines = ["## Table of Contents"]
        results = check_toc_headings("test.md", lines)
        assert len(results) == 1
        assert results[0].rule == LintRule.E002
        assert "TOC" in results[0].message

    def test_flags_toc_abbreviation(self):
        lines = ["# TOC"]
        results = check_toc_headings("test.md", lines)
        assert len(results) == 1

    def test_case_insensitive(self):
        lines = ["### table of contents"]
        results = check_toc_headings("test.md", lines)
        assert len(results) == 1

    def test_ignores_non_heading_toc_mention(self):
        lines = ["This paragraph mentions TOC in text."]
        results = check_toc_headings("test.md", lines)
        assert results == []

    def test_normal_heading_clean(self):
        lines = ["## 1. Introduction", "### 1.1 Overview"]
        results = check_toc_headings("test.md", lines)
        assert results == []


# ---------------------------------------------------------------------------
# E003: Mojibake encoding
# ---------------------------------------------------------------------------


class TestCheckMojibake:
    def test_flags_common_mojibake_accent(self):
        # \u00c3\u00a9 = mojibake for é
        lines = ["The word caf\u00c3\u00a9 is mojibake"]
        results = check_mojibake("test.md", lines)
        assert len(results) == 1
        assert results[0].rule == LintRule.E003
        assert "Mojibake" in results[0].message

    def test_flags_smart_quote_mojibake(self):
        # \u00e2\u20ac\u2122 = mojibake for right single quote
        lines = ["He said \u00e2\u20ac\u2122hello\u00e2\u20ac\u2122"]
        results = check_mojibake("test.md", lines)
        assert len(results) == 2

    def test_clean_utf8_no_results(self):
        lines = ["Normal text with caf\u00e9 properly encoded"]
        results = check_mojibake("test.md", lines)
        assert results == []

    def test_flags_mojibake_umlaut(self):
        # \u00c3\u00bc = mojibake for ü
        lines = ["M\u00c3\u00bcnchen"]
        results = check_mojibake("test.md", lines)
        assert len(results) == 1


# ---------------------------------------------------------------------------
# W001: Em-dash punctuation
# ---------------------------------------------------------------------------


class TestCheckEmdash:
    def test_flags_em_dash(self):
        lines = ["This \u2014 is wrong"]
        results = check_emdash("test.md", lines)
        assert len(results) == 1
        assert results[0].rule == LintRule.W001
        assert "Em-dash" in results[0].message

    def test_flags_en_dash(self):
        lines = ["Pages 1\u20132"]
        results = check_emdash("test.md", lines)
        assert len(results) == 1
        assert "En-dash" in results[0].message

    def test_both_on_same_line(self):
        lines = ["A \u2014 B \u2013 C"]
        results = check_emdash("test.md", lines)
        assert len(results) == 2

    def test_clean_text(self):
        lines = ["Use commas, like this; or semicolons."]
        results = check_emdash("test.md", lines)
        assert results == []

    def test_default_severity_is_warning(self):
        lines = ["text \u2014 text"]
        results = check_emdash("test.md", lines)
        assert results[0].severity == Severity.WARNING


# ---------------------------------------------------------------------------
# W002: CRLF line endings
# ---------------------------------------------------------------------------


class TestCheckCrlf:
    def test_flags_crlf(self):
        raw = "line one\r\nline two\r\n"
        results = check_crlf("test.md", raw)
        assert len(results) == 2
        assert all(r.rule == LintRule.W002 for r in results)

    def test_unix_lf_clean(self):
        raw = "line one\nline two\n"
        results = check_crlf("test.md", raw)
        assert results == []

    def test_mixed_endings(self):
        raw = "line one\nline two\r\nline three\n"
        results = check_crlf("test.md", raw)
        assert len(results) == 1
        assert results[0].line == 2


# ---------------------------------------------------------------------------
# W003: Backlog metadata validation
# ---------------------------------------------------------------------------


class TestCheckBacklogMetadata:
    def test_flags_missing_fields(self):
        lines = [
            "# Backlog Proposals",
            "",
            "## Proposal #1: Add feature X",
            "**ID:** 1",
            "Description of the proposal.",
        ]
        results = check_backlog_metadata("docs/feedback/backlogs.md", lines)
        assert len(results) == 1
        assert results[0].rule == LintRule.W003
        assert "Priority" in results[0].message
        assert "Status" in results[0].message

    def test_complete_proposal_clean(self):
        lines = [
            "# Backlog",
            "",
            "## Proposal #1: Feature",
            "**ID:** 1",
            "**Status:** Open",
            "**Priority:** High",
        ]
        results = check_backlog_metadata("docs/feedback/backlogs.md", lines)
        assert results == []

    def test_skips_non_backlog_file(self):
        lines = [
            "## Proposal #1: Feature",
            "Missing all fields.",
        ]
        results = check_backlog_metadata("docs/guides/readme.md", lines)
        assert results == []

    def test_dash_list_field_format(self):
        lines = [
            "## Proposal #2: Another",
            "- ID: 2",
            "- Status: Open",
            "- Priority: Medium",
        ]
        results = check_backlog_metadata("backlog/items.md", lines)
        assert results == []

    def test_multiple_proposals_partial(self):
        lines = [
            "## Proposal #1: First",
            "**ID:** 1",
            "**Status:** Open",
            "**Priority:** High",
            "",
            "## Proposal #2: Second",
            "**ID:** 2",
            "No status or priority here.",
        ]
        results = check_backlog_metadata("docs/feedback/backlogs.md", lines)
        assert len(results) == 1
        assert "#2" in results[0].context or "Second" in results[0].context


# ---------------------------------------------------------------------------
# Severity overrides
# ---------------------------------------------------------------------------


class TestSeverityOverrides:
    def test_override_downgrades_error_to_info(self):
        overrides = {LintRule.E001: Severity.INFO}
        lines = ["\u2705 emoji"]
        results = check_emoji_usage("test.md", lines, overrides)
        assert results[0].severity == Severity.INFO

    def test_override_upgrades_warning_to_error(self):
        overrides = {LintRule.W001: Severity.ERROR}
        lines = ["text \u2014 text"]
        results = check_emdash("test.md", lines, overrides)
        assert results[0].severity == Severity.ERROR


# ---------------------------------------------------------------------------
# run_all_checks orchestrator
# ---------------------------------------------------------------------------


class TestRunAllChecks:
    def test_combines_multiple_rules(self):
        raw = "\u2705 good \u2014 bad\n"
        results = run_all_checks("test.md", raw)
        rules_found = {r.rule for r in results}
        assert LintRule.E001 in rules_found
        assert LintRule.W001 in rules_found

    def test_results_sorted_by_line_then_column(self):
        raw = "ok\n\u2014 \u2705\n"
        results = run_all_checks("test.md", raw)
        for i in range(len(results) - 1):
            assert (results[i].line, results[i].column) <= (
                results[i + 1].line,
                results[i + 1].column,
            )

    def test_empty_file_no_results(self):
        results = run_all_checks("test.md", "")
        assert results == []

    def test_crlf_detected_before_line_split(self):
        raw = "line\r\n"
        results = run_all_checks("test.md", raw)
        rules_found = {r.rule for r in results}
        assert LintRule.W002 in rules_found

    def test_overrides_propagate_to_all_checks(self):
        overrides = {LintRule.E001: Severity.INFO, LintRule.W001: Severity.ERROR}
        raw = "\u2705 text \u2014 more\n"
        results = run_all_checks("test.md", raw, overrides)
        for r in results:
            if r.rule == LintRule.E001:
                assert r.severity == Severity.INFO
            elif r.rule == LintRule.W001:
                assert r.severity == Severity.ERROR