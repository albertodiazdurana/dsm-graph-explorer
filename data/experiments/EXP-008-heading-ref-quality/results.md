# EXP-008: Heading Reference Detection Quality

**Date:** 2026-03-18
**Session:** 39
**Status:** COMPLETE
**Verdict:** FAIL (false positive rate exceeds threshold; pre-filter required)

---

## Setup

**Target repository:** DSM Central (`~/dsm-agentic-ai-data-science-methodology/`)
**Files scanned:** 498 markdown files
**Tool version:** `--heading-refs` flag (Session 39 implementation)

## Baseline (without --heading-refs)

```
Scanned 498 file(s) in 0.32s. Found 12 error(s), 645 warning(s), 0 info(s), 0 version mismatch(es).
```

## With --heading-refs (no filter)

```
Scanned 498 file(s) in 35.88s. Found 12 error(s), 645 warning(s), 0 info(s), 0 version mismatch(es).
```

**No regression:** error/warning counts identical. All 84,052 heading refs resolved successfully (matched existing headings), so no new warnings were produced.

### Raw Detection Metrics

| Metric | Value |
|--------|-------|
| Unique known headings | 3,668 |
| Total heading refs found | 84,052 |
| Files with heading refs | 498 (100%) |
| Extraction time | 35.88s (vs 0.32s baseline) |

**Top matches (unfiltered):** "or" (19,054), "backlog" (2,007), "reference" (1,897), "research" (1,697), "low" (1,689). All are single-word headings that match common English words. Catastrophic noise.

## Heading Word-Count Distribution

| Word count | Unique headings | Noise risk |
|------------|----------------|------------|
| 1 word | 242 | Extreme (common words: "or", "backlog", "files") |
| 2 words | 762 | High (generic phrases: "when to", "how to") |
| 3 words | 951 | Moderate (some specific: "session transcript protocol"; some generic: "when to use") |
| 4+ words | 1,713 | Low (mostly specific protocol/concept names) |

## With 3+ Word Filter

| Metric | Value |
|--------|-------|
| Known headings (3+ words) | 2,664 |
| Total heading refs found | 2,065 |
| Files with heading refs | 375 |
| Extraction time | 25.44s |

**Top matches (3+ words):** "take a bite" (134), "readme change notification" (121), "sprint boundary checklist" (86), "session transcript protocol" (68), "pre-generation brief protocol" (56). Much more meaningful.

## Quality Assessment (Random Sample, n=30, 3+ word filter)

**True positives (~22/30, ~73%):** Meaningful references to named protocols, concepts, or sections. Examples: "Pre-Generation Brief Protocol", "Session Transcript Protocol", "Project Type Detection", "file naming standards".

**False positives (~8/30, ~27%):** Three categories:
1. **Generic short phrases** (3 words but common): "When to Use" (72 hits), "Call to action ideas"
2. **Template/checkpoint phrases:** "Deferred to next full session" (61 hits combined)
3. **Incidental entity matches:** "EU AI Act" (matches a heading but the prose mention is not a cross-reference to that heading)

## Success Criteria Assessment

| Criterion | Threshold | Result | Status |
|-----------|-----------|--------|--------|
| Detection: heading refs found | >0 meaningful refs | 2,065 (3+ filter) | PASS |
| True positive rate | ≥80% | ~73% | FAIL |
| False positive rate | ≤20% | ~27% | FAIL |
| Cross-file resolution | ≥90% | 100% (all resolved) | PASS |
| No regressions | Exact match | 12 errors, 645 warnings (identical) | PASS |

## Decision Gate

False positive rate (27%) exceeds the 20% threshold. Per the experiment definition, scope a pre-filter before promoting the feature.

### Recommended Pre-Filter

**Minimum heading length:** 3+ words AND ≥20 characters. This would eliminate:
- Short generic phrases: "when to use" (11 chars), "out of scope" (12 chars)
- Keep specific names: "session transcript protocol" (28 chars), "pre-generation brief protocol" (30 chars), "take a bite" (11 chars, 3 words but short)

**Alternative:** Word-count minimum of 4 would be simpler but loses valuable 3-word matches like "take a bite" (DSM principle name).

**Recommended approach:** Implement the filter in `extract_heading_references()` as a `min_heading_words` parameter (default=3) and add a `min_heading_length` parameter (default=20 characters). The CLI passes these through. This is a targeted fix, not the deferred TF-IDF fuzzy matching.

## Performance Note

Extraction time with 3+ word filter: 25.44s for 498 files (2,664 headings). The O(lines x headings) substring scan is inherently expensive. For large repos, consider caching the heading index or offering a `--heading-refs-cache` option. Not critical for current use but worth noting for Sprint 15+ planning.
