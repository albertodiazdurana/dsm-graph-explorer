# DSM Central EXP-001: Document Reachability

**Date reviewed:** 2026-04-02
**Source:** DSM Central Session 162, `data/experiments/EXP-001-reachability/results.md`
**DSM Central BL:** BACKLOG-230
**Origin:** GE Session 39, Entry 53 (experiment templates "architecturally invisible")

---

## Summary

EXP-001 tested whether every section in every DSM document is reachable from
DSM_0.2 (agent entry point) within 3 reference hops. A Python BFS script
parsed 6 reference types across 35 DSM files.

**Result: FAIL on pre-registered 3-hop threshold, PASS on reachability.**

## Key Findings (GE-relevant)

### Reachability: 100%

All 35 DSM files and 1,310 sections are reachable from DSM_0.2. No orphaned
documents, no broken reference chains.

### Hop Distribution

| Hop | Files | Sections | Cumulative % (files) |
|-----|-------|----------|---------------------|
| 0   | 1     | 62       | 2.9%                |
| 1   | 6     | 145      | 20.0%               |
| 2   | 12    | 632      | 54.3%               |
| 3   | 5     | 145      | 68.6%               |
| 4   | 7     | 195      | 88.6%               |
| 5   | 4     | 102      | 100.0%              |

11 files exceed the 3-hop threshold (7 at hop 4, 4 at hop 5). All are modules
of files within threshold. The modular architecture (post-threshold) adds
expected depth.

### Two-Tier Threshold Model

The flat 3-hop rule penalizes the modular architecture. Revised model:
- **Core files (DSM_X.Y):** reachable within 3 hops
- **Module files (DSM_X.Y.Z):** reachable within 1 hop from their core file

Under this model, all 35 files pass.

### Reference Graph Properties

- 286 file-to-file directed edges
- Strongly connected core: DSM_0.2, its 4 modules, DSM_0.1, DSM_6.0
- Hub files: DSM_0.2 (most outgoing), DSM_1.0 + DSM_2.0 modules (densest cluster)
- Leaf files: DSM_3.0 modules and DSM_6.1 modules (few outgoing refs)

## GE Relevance

### Parser Validation Dataset

The reachability script detects 6 reference types:
1. Markdown links `[text](file.md)`
2. `@` references
3. Module dispatch table links `[A](DSM_0.2.A...)`
4. Prose references ("See DSM_X.Y")
5. DSM file-name mentions without `.md`
6. `§N` section references

GE's parser is more comprehensive (handles section-level refs, cross-repo,
inventory classification). The `reference-graph.md` artifact (286 edges) could
serve as a ground truth dataset for validating GE's file-level cross-reference
extraction against an independent implementation.

### Reachability Metrics

The two-tier threshold model (core vs module) could inform GE if it exposes
hop distance calculations. Currently GE computes graph topology but does not
surface per-node hop distance from a designated entry point.

### Scope

No immediate action required. Two deferred opportunities:
1. **Parser validation:** Compare GE's cross-ref output against EXP-001's
   reference-graph.md for the same 35 files (low priority, quality assurance)
2. **Hop distance feature:** Add entry-point-relative hop distance to
   `--graph-stats` output (low priority, future sprint)

## Artifacts

- Full experiment report: DSM Central `data/experiments/EXP-001-reachability/results.md`
- Reachability script: DSM Central `data/experiments/EXP-001-reachability/reachability.py`
- Reference graph: DSM Central `data/experiments/EXP-001-reachability/reference-graph.md`
