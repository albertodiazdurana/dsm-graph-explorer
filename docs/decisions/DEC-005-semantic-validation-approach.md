# DEC-005: Semantic Validation Approach

**Date:** 2026-02-10
**Status:** ACCEPTED
**Sprint:** 6 (Phase 6.0)
**Experiment:** EXP-003 (TF-IDF Threshold Tuning)

---

## Context

Sprint 6 adds semantic drift detection: TF-IDF cosine similarity to flag when a
cross-reference's surrounding prose doesn't match the target section's content.
DSM Central's structural analysis (937 H2+H3 sections) showed many section titles
are too short or generic for reliable title-only matching.

## Decision

Use **title + context excerpt** mode with the following parameters:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Comparison mode | Title + excerpt (Option B + C) | Title-only cannot disambiguate generic titles (EXP-003 Part 2) |
| Default threshold | 0.10 | Best F1 in both modes (0.947 title-only, 0.889 title+excerpt) |
| Minimum token gate | 3 tokens after stopword removal | Sections with <3 tokens produce unreliable scores (Part 3) |
| Section number stripping | Yes (`\d+\.\d+` patterns removed) | No semantic value, could inflate similarity artificially |
| IDF scope | Corpus-level (all sections) | Proper downweighting of common DSM vocabulary |
| Excerpt length | ~50 words of prose | Tunable config parameter, balances vocabulary richness vs noise |

## EXP-003 Results

### Part 1: Standard Cases (10 match + 10 drift)

Drift cases all scored 0.000 (completely unrelated domains), giving perfect
precision in both modes. Recall varied by threshold:

| Threshold | Title-only F1 | Title+excerpt F1 |
|-----------|--------------|------------------|
| 0.10 | 0.947 | 0.889 |
| 0.15 | 0.889 | 0.750 |
| 0.20 | 0.824 | 0.750 |
| 0.30 | 0.750 | 0.462 |

Title-only has higher recall on standard cases because the excerpt dilutes signal
when comparing a short reference line against a longer target text.

### Part 2: Ambiguous Cases (generic titles, the critical test)

Same title ("Expected Outcomes", "Deliverables"), different content underneath.

| Mode | Avg match score | Avg drift score | Gap |
|------|----------------|----------------|-----|
| Title-only | 0.331 | 0.364 | **-0.033** (cannot separate) |
| Title+excerpt | 0.380 | 0.116 | **+0.264** (clear separation) |

Title-only produces identical scores for correct and wrong instances of the same
generic title. Title+excerpt creates a 0.264 gap, enabling disambiguation.

### Part 3: Token Gate Validation

| Input | Tokens | Similarity | Gate |
|-------|--------|-----------|------|
| "Overview" vs "Overview" | 1 | 1.000 | SKIP (insufficient) |
| "Deliverables" vs "Produce deliverables..." | 1 | 0.502 | SKIP (insufficient) |
| "Expected Outcomes" vs "Expected Outcomes" | 2 | 1.000 | SKIP (insufficient) |

The 3-token gate correctly flags all short-text cases as unreliable.

## Alternatives Considered

1. **Title-only comparison:** Simpler but fails on generic titles (Part 2 gap = -0.033)
2. **Add summaries to documentation:** 937 summaries to write, ongoing maintenance burden
3. **Higher threshold (0.3+):** Drops recall below 0.5 in title+excerpt mode

## Experiment Limitations

EXP-003 used 25 synthetic test cases modeled on real DSM content. The test set has
known limitations that should be addressed during implementation:

- **No train/test split:** All cases used for both fitting and evaluation
- **No cross-validation:** Single-run evaluation, no variance estimate
- **No hyperparameter search:** Threshold sweep is manual, not optimized
- **Synthetic data:** Test cases are hand-crafted, not sampled from real repository
- **Small corpus for IDF:** 25 pairs produce a narrow vocabulary; real corpus has 937 sections

These limitations are acceptable for a threshold-selection experiment on a
rule-based tool (not a trained model). The threshold will be validated against real
DSM repository data during Phase 6.2 integration testing.

## Implementation Notes

- Phase 6.1: Add `context_excerpt` to Section, `context_before`/`context_after` to CrossReference
- Phase 6.2: Implement `src/semantic/similarity.py` with corpus-scoped TF-IDF
- Phase 6.3: Wire into CLI with `--semantic` flag, graceful fallback without scikit-learn
- Threshold is a config parameter, user-tunable via `.dsm-graph-explorer.yml`

## References

- Experiment script: `data/experiments/exp003_tfidf_threshold.py`
- Design source: `_inbox/done/2026-02-10_dsm-central-tfidf-context-design.md`
- Sprint plan: `docs/plans/epoch-2-plan.md` (Sprint 6)

---

## Amendment: Threshold Lowered to 0.08 (EXP-003b)

**Date:** 2026-02-23
**Experiment:** EXP-003b (Real Data Validation)

EXP-003b validated the 0.10 threshold against 1,191 real cross-references from the
DSM methodology repository (128 manually labeled in the near-threshold zone 0.08-0.12).

### Results

| Metric | EXP-003 (synthetic, 25 cases) | EXP-003b (real, 128 cases) |
|--------|-------------------------------|---------------------------|
| Precision | 1.000 | 1.000 |
| Recall | 0.800 | 0.496 |
| F1 | 0.889 | 0.663 |

The 0.10 threshold produces 63 false negatives (auto=drift, manual=match), all with
scores between 0.08 and 0.10. Root causes: empty target excerpts (3-4 tokens),
vocabulary mismatch in backlog proposals, and short generic section titles.

### Updated Parameter

| Parameter | Previous | Updated | Rationale |
|-----------|----------|---------|-----------|
| Default threshold | 0.10 | **0.08** | Recovers false negatives while maintaining perfect precision (0 false positives at 0.08) |

All 63 false negatives have scores >= 0.08 and were confirmed as genuine matches by
human review. Lowering the threshold to 0.08 recovers these cases without introducing
false positives.
