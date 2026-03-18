# EXP-007 Results: Multi-File Document Resilience

**Date:** 2026-03-18
**Sprint:** 13 (executed), 38 (documented)
**Status:** COMPLETE

---

## Summary

EXP-007 tested whether GE's parser, validator, and graph builder handle a real-world file split correctly: DSM_0.2 going from a single 2,625-line file (v1.3.59) to a slim core + 4 modules (v1.3.69, 2,573 lines across 5 files).

**Verdict:** PASS with caveats. GE processes both configurations without errors. However, GE's section parser targets numbered references (DSM 1.0/3.0 style), not markdown heading-based sections, so it cannot meaningfully validate inter-module reference integrity introduced by the split.

## Success Criteria Evaluation

| Criterion | Threshold | Result | Verdict |
|-----------|-----------|--------|---------|
| Parsing: split files parse without errors | 100% | 0 errors (baseline: 0, post-split: 0) | **PASS** |
| Sections: total section count comparable (±10%) | Yes | 0 sections in both (GE does not extract markdown heading sections) | **N/A** |
| Cross-refs: intra-file refs still resolve | 100% | No intra-file numbered section refs detected in either configuration | **N/A** |
| Cross-refs: refs between split files resolve | ≥90% | Module Dispatch Table links (`[A](DSM_0.2.A_...)`) not parsed by GE | **NOT TESTABLE** |
| Graph: node/edge counts comparable | ±10% | Baseline: 1 FILE, 0 edges; Post-split: 5 FILE, 0 edges | **PASS** (expected divergence) |

## Quantitative Comparison

| Metric | Baseline (1 file, v1.3.59) | Post-split (5 files, v1.3.69) | Delta |
|--------|---------------------------|-------------------------------|-------|
| Errors | 0 | 0 | 0 |
| Warnings | 70 | 46 | -24 (-34%) |
| FILE nodes | 1 | 5 | +4 (expected) |
| SECTION nodes | 0 | 0 | 0 |
| CONTAINS edges | 0 | 0 | 0 |
| REFERENCES edges | 0 | 0 | 0 |

## Warning Analysis

All warnings in both configurations are **external references**, pointing to DSM documents not included in the scan scope. None are caused by the file split itself.

| Warning Category | Baseline | Post-split | Notes |
|-----------------|----------|------------|-------|
| Broken section refs (DSM_3: 6.6, 6.8, 6.9, 7, etc.) | 34 | 23 | References to DSM_3 sections outside scan scope |
| Unknown DSM docs (5.0, 6.0, 6) | 14 | 12 | DSM 5.0 and DSM 6.0 not in GE's known identifiers |
| Broken appendix refs (A, B, C, D, E, B.2, C.1.3, E.12) | 22 | 11 | Appendix references to DSM_3 not in scope |
| **Total** | **70** | **46** | **-34%** |

The 34% reduction is not caused by the split. Between v1.3.59 and v1.3.69, content was reorganized: some protocol text was consolidated, some redundant cross-references were removed, and appendix-heavy sections at the end of the monolithic file were trimmed during modularization. The split itself is transparent to GE's warning detection.

## Capability Gap Finding

The experiment's most valuable outcome is identifying what GE **cannot** test, rather than confirming what it can:

1. **Markdown heading sections:** GE's parser extracts numbered sections (e.g., "Section 2.3") but not markdown heading-based structure (`## Protocol Name`). DSM_0.2 uses headings exclusively, so GE sees 0 sections in both configurations.

2. **Markdown link cross-references:** The Module Dispatch Table introduced by the split uses `[A](DSM_0.2.A_Session_Lifecycle.md)` style links. GE does not parse these as cross-references. This is the primary inter-module reference pattern, and it is invisible to GE.

3. **Implication:** For document sets that use markdown headings and markdown links (rather than numbered sections and "Section N.N" references), GE provides parsing validation but not structural integrity validation.

These gaps are **pre-existing limitations**, not regressions introduced by the split. They point toward future enhancements: heading-based section extraction and markdown link cross-reference resolution.

## Decision Gate

From `design.md`:

> - If cross-file references break: Phase 13.1 focuses on fixing resolution logic
> - If everything passes: Phase 13.1 reduces to defensive tests confirming current behavior

**Outcome:** Neither gate applies cleanly. Cross-file references did not "break" because GE never parsed them. Defensive tests for current behavior are already covered by the existing test suite (547 tests, 95% coverage).

**Recommended path:** Close EXP-007 as complete. Address the capability gaps (heading section extraction, markdown link resolution) as separate backlog items, not as EXP-007 follow-up work. The cross-reference resolution by heading title matching (already in the deferred backlog) is the natural next step.
