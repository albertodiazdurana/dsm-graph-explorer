# DSM Central Feedback: Convention Linting Mode

**Date:** 2026-02-09
**From:** DSM Central Session 19 (BACKLOG-076 self-compliance audit)
**To:** Graph Explorer development planning
**Type:** Feature request, cross-project alignment feedback

---

## Summary

DSM Central ran a full self-compliance audit (BACKLOG-076) across all methodology
files. Graph Explorer's cross-reference validation handled the structural checks
well, but a separate manual pass was needed for surface-level convention violations.
This document requests a `--lint` mode that automates those convention checks.

---

## Audit Findings That Motivate This Feature

BACKLOG-076 manual audit found across 8 DSM files:

| Category | Violations | Example |
|----------|-----------|---------|
| Emoji/symbol usage | 34 | Checkmarks, cross marks, warning triangles instead of WARNING:/OK:/ERROR: text |
| TOC presence | 3 | `## Table of Contents` headings in DSM_2.0, DSM_2.1, DSM_4.0 |
| Em-dash punctuation | 4 | `—` instead of commas/semicolons |
| Mojibake encoding | 6 files | Double-encoded UTF-8: `âœ—` (cross mark), `âœ"` (checkmark), `âš` (warning) |
| CRLF line endings | 2 files | DSM_2.0 and DSM_2.1 had Windows `\r\n` |

These were all fixed manually. The convention linting mode would catch regressions
automatically and eliminate the need for manual passes.

---

## Feature Specification

### CLI Interface

Add `--lint` flag to existing `main()` command. When set, run convention checks
only (skip cross-reference validation) and exit early.

```bash
# Lint only
dsm-validate ~/dsm-agentic-ai-data-science-methodology --lint

# Full validation (existing behavior, unchanged)
dsm-validate ~/dsm-agentic-ai-data-science-methodology --strict
```

### Checks to Implement (Priority Order)

1. **Emoji/symbol detection (E001):** Flag Unicode emoji and common symbols
   (checkmarks, cross marks, warning triangles, chart symbols). DSM convention:
   use WARNING:/OK:/ERROR: text instead. Exception: skip content inside fenced
   code blocks (Streamlit examples legitimately use emoji).

2. **TOC detection (E002):** Flag `## Table of Contents` or similar headings.
   DSM uses self-documenting hierarchical numbering; explicit TOCs are prohibited.

3. **Em-dash detection (W001):** Flag `—` (U+2014) characters. DSM convention:
   use commas or semicolons for clause separation.

4. **CRLF detection (W002):** Flag files containing `\r\n` line endings. DSM
   uses Unix `\n` only.

5. **Mojibake detection (E003):** Flag common double-encoded UTF-8 byte patterns:
   `âœ—` (was cross mark), `âœ"` (was checkmark), `âš` followed by non-ASCII
   (was warning emoji), `Ã` followed by unexpected characters. These indicate
   Windows editor encoding corruption.

6. **Backlog metadata validation (W003):** For files matching `BACKLOG-*.md`,
   validate required fields: Status, Priority, Date Created, Origin, Author.

### Architecture Guidance

- New module: `src/linter/` with submodules per check category
- Reuse existing `collect_markdown_files()` and `filter_files()`
- New dataclass `LintResult` with: file, line, column, rule, severity, message, context
- Extend `.dsm-graph-explorer.yml` config with optional `lint:` section for rule overrides
- New `src/linter/lint_reporter.py` modeled on existing `src/reporter/report_generator.py`
- New `tests/test_linter.py` following existing pytest patterns

### Implementation Order (TDD)

1. Create `src/linter/` module structure with `LintResult` dataclass
2. Implement emoji detection (E001) with tests
3. Implement TOC detection (E002) with tests
4. Implement em-dash detection (W001) with tests
5. Implement CRLF detection (W002) with tests
6. Implement mojibake detection (E003) with tests
7. Implement backlog metadata validation (W003) with tests
8. Wire into CLI with `--lint` flag
9. Add lint config section to config loader
10. Update README with lint mode documentation

---

## Relationship to Existing Pipeline

```
Current:  collect_files -> filter -> parse -> extract_refs -> validate -> report
New lint: collect_files -> filter -> lint_checks -> lint_report -> exit
```

Lint checks do not need document parsing or cross-reference resolution. They
operate on raw text patterns, so they're fast and independent. The two pipelines
share file collection and filtering but diverge after that.

Long-term, both pipelines could run together (`dsm-validate --strict --lint`),
but for the initial implementation, `--lint` runs independently.

---

## Action Items for Graph Explorer

| # | Action | Priority | Status |
|---|--------|----------|--------|
| 1 | Plan epoch/sprint for lint mode implementation | High | Pending |
| 2 | Implement `--lint` flag with 6 checks (spec above) | High | Pending |
| 3 | Add test fixtures with known convention violations | Medium | Pending |
| 4 | Update README with lint mode documentation | Medium | Pending |
| 5 | Update docs/feedback/backlogs.md proposal #16 when implemented | Low | Pending |

---

## Agent Prompt

Use this prompt when starting a Graph Explorer session to implement this feature:

```
Read .claude/CLAUDE.md for project conventions and interaction protocols.

Read docs/backlog/2026-02-09_dsm-central-feedback-convention-linting.md for the
full feature specification. This is a hub-to-spoke feature request from DSM Central.

The feature: add a --lint flag to the CLI that runs convention checks (emoji usage,
TOC detection, em-dash punctuation, CRLF line endings, mojibake encoding, backlog
metadata) without running the full cross-reference validation pipeline.

Architecture: new src/linter/ module, reuse existing file collection/filtering,
new LintResult dataclass, extend config with lint section.

Follow TDD: implement one check at a time with tests. Present each step for my
review before implementing. Start by reading the existing cli.py, validator/, and
reporter/ modules to understand the patterns to follow.
```

---

**Feedback Status:** Ready for Graph Explorer planning
**Created by:** DSM Central (Alberto + Claude)
