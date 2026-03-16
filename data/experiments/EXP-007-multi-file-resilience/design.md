# EXP-007: Multi-File Document Resilience

**Sprint:** 13
**Date:** 2026-03-16
**Status:** DESIGNED

---

## Goal

Validate that GE's parser, validator, and cross-reference resolution work correctly
when a single large markdown file is split into multiple smaller files with
cross-references between them.

## Context

BL-090 Phase 1 split DSM_0.2 from a single 2,625-line file into a slim core plus
four on-demand modules (v1.3.61, commit c6f8f46 in DSM Central). This experiment
tests GE against the real split, not a simulation.

## Data Sources

### Baseline (pre-split)

- **Source:** `git show fafb8b1:DSM_0.2_Custom_Instructions_v1.1.md` (DSM Central)
- **Version:** v1.3.59 (last version before BL-090 split)
- **Size:** 2,625 lines, single file
- **Location:** `baseline/DSM_0.2_Custom_Instructions_v1.1.md`

### Post-split (current)

- **Source:** Current filesystem, DSM Central repository
- **Version:** v1.3.69
- **Size:** 2,573 lines across 5 files
- **Files:**
  - `DSM_0.2_Custom_Instructions_v1.1.md` (core, 673 lines)
  - `DSM_0.2.A_Session_Lifecycle.md` (860 lines)
  - `DSM_0.2.B_Artifact_Creation.md` (361 lines)
  - `DSM_0.2.C_Security_Safety.md` (242 lines)
  - `DSM_0.2.D_Research_Onboarding.md` (437 lines)
- **Location:** `post-split/` (copies)

## Hypothesis

GE's parser already processes files independently, so parsing should not break.
Cross-reference resolution may surface gaps if references use section numbers
that assumed a single-file context (e.g., "see Section 3.2" now lives in a
different file). The Module Dispatch Table in the core file introduces a new
cross-file reference pattern (markdown links like `[A](DSM_0.2.A_...md)`).

## Methodology

1. Extract pre-split DSM_0.2 into `baseline/`
2. Copy post-split files into `post-split/`
3. Run full GE pipeline on each:
   - `dsm-validate <path> --strict` (parse + validate)
   - `dsm-validate <path> --graph-stats` (graph build + stats)
   - `dsm-validate <path> --graph-export <output>` (graph export for comparison)
4. Compare results:
   - Section count (total numbered sections)
   - Cross-reference count and resolution rate
   - Graph node count and edge count
   - Error/warning counts
5. If discrepancies exist, identify root cause and classify as:
   - Expected (content was restructured, not just split)
   - Bug (GE fails to handle valid cross-file references)
   - Enhancement (new reference pattern GE could support)

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| Parsing: split files parse without errors | 100% |
| Sections: total section count comparable (±10% for restructuring) | Yes |
| Cross-references: intra-file refs still resolve | 100% |
| Cross-references: refs between split files resolve | ≥90% (identify gaps) |
| Graph: node/edge counts comparable | ±10% |

## Decision Gate

- If cross-file references break: Phase 13.1 focuses on fixing resolution logic
- If everything passes: Phase 13.1 reduces to defensive tests confirming current behavior
