# DSM Central: TF-IDF Context Design for Semantic Drift Detection

**Date:** 2026-02-10
**From:** DSM Central Session 27 (document structure analysis)
**To:** Graph Explorer Sprint 6 planning (semantic drift detection)
**Type:** Design recommendation, data-backed analysis

---

## Summary

Sprint 6 adds semantic drift detection: TF-IDF cosine similarity to flag when a
cross-reference's surrounding prose doesn't match the target section's title,
indicating the section was renamed but the reference wasn't updated.

Key Design Decision 1 proposed comparing `CrossReference.context` (full line) vs
`Section.title`. DSM Central conducted a full structural analysis of all DSM
documents to evaluate whether section titles alone carry enough semantic signal
for reliable TF-IDF matching, and whether adding per-section summaries to the
documentation would be feasible.

**Conclusion:** Titles alone are likely insufficient for many sections. Adding
summaries to the documentation is feasible but creates maintenance burden.
The recommended approach is **parse-time context extraction**, where the parser
automatically captures the first paragraph after each heading. This provides
richer comparison text with zero documentation changes.

---

## DSM Document Structure Metrics (v1.3.30 baseline)

| Document | Lines | H1 | H2 | H3 | H4 |
|----------|------:|---:|---:|---:|---:|
| DSM_0 (Start Here) | 1,030 | 2 | 16 | 45 | 18 |
| DSM_0.1 (File Naming) | 164 | 1 | 8 | 0 | 0 |
| DSM_0.2 (Custom Instructions) | 661 | 4 | 28 | 24 | 0 |
| DSM_1.0 (Methodology) | 4,562 | 114 | 69 | 176 | 19 |
| DSM_1.0 (Appendices) | 5,860 | 207 | 114 | 202 | 30 |
| DSM_2.0 (PM Guidelines) | 1,491 | 6 | 42 | 88 | 6 |
| DSM_2.1 (PM Production) | 404 | 1 | 11 | 20 | 0 |
| DSM_3 (Implementation Guide) | 968 | 6 | 42 | 59 | 12 |
| DSM_4.0 (Software Engineering) | 847 | 5 | 25 | 49 | 1 |
| DSM_5.0 (Documentation) | 337 | 5 | 11 | 28 | 0 |
| **TOTAL** | **16,154** | **356** | **376** | **561** | **86** |

**Key numbers for Sprint 6:**
- 937 H2+H3 headers are the primary cross-reference targets
- 376 H2 "chapter-level" sections (most referenced in cross-refs)
- High H1 counts in DSM_1.0 files reflect hierarchical numbering (e.g., `# 2.2.3.1`), not true top-level sections

---

## Design Problem: Why Titles Alone May Be Insufficient

Many section titles in DSM documents are short and generic:

| Example Title | Semantic Content |
|---------------|-----------------|
| `### 3.2 Quality Standards` | Could be about code, data, or documentation quality |
| `### Expected Outcomes` | Appears 4 times across DSM_2.0 with different content |
| `## Communication & Style` | Repeated in DSM_3 across multiple domain examples |
| `## Deliverables` | Appears twice in DSM_2.0, different sprint contexts |

TF-IDF cosine similarity on short, generic titles will produce:
- **False positives:** Unrelated references flagged because titles share common words
- **False negatives:** Stale references not flagged because the new title is equally generic
- **Ambiguity:** Duplicate titles (e.g., "Expected Outcomes" x4) make matching unreliable

The first paragraph after a heading almost always explains the section's specific purpose, adding discriminating vocabulary that TF-IDF needs.

---

## Approaches Considered

### Option A: Add summaries to documentation headers

Add a 10-15 word summary line under each heading in the DSM documents.

| Metric | Value |
|--------|-------|
| Headers needing summaries | 937 (H2+H3) |
| Additional words | ~14,000 (~700 lines) |
| Bloat on 16,154 lines | ~4.3% |
| Maintenance burden | Every structural edit requires updating both title and summary |
| Retroactive effort | 937 summaries to write for existing content |

**Verdict:** Feasible but creates ongoing maintenance burden disproportionate to the
benefit. The documentation exists for human readers; adding metadata lines for tooling
degrades readability.

### Option B: Parse-time context extraction (recommended)

The parser automatically extracts the first N words of prose following each heading
and stores it as `Section.context_excerpt`. No documentation changes needed.

| Metric | Value |
|--------|-------|
| Documentation changes | Zero |
| Maintenance burden | Zero (extraction is automatic) |
| Parser changes | New field on `Section` dataclass + extraction logic |
| Works retroactively | Yes, on all existing documents |

**Verdict:** Recommended. Achieves richer semantic signal without touching documentation.

### Option C: Expand reference context only

Expand `CrossReference.context` from 1 line to 3 lines (previous + current + next)
but keep the target comparison as title-only.

**Verdict:** Helpful as a complement but doesn't solve the generic-title problem on
the target side. Best combined with Option B.

### Recommended combination: Option B + Option C

- **Reference side:** `CrossReference.context` expanded to 3 lines (previous + current + next line), providing surrounding prose that describes why the reference is made
- **Target side:** `Section.title` + `Section.context_excerpt` (first N words after heading), providing discriminating vocabulary about the section's content

Compare: `3-line reference context` vs `title + first-paragraph excerpt`

---

## Open Design Questions

### 1. How many words to extract per section?

The excerpt length affects TF-IDF vocabulary richness vs noise.

| Option | Trade-off |
|--------|-----------|
| First sentence only | Variable length; semantically dense but may be very short ("See below.") |
| First 30 words | Consistent size; captures most opening statements |
| First 50 words | Richer vocabulary; may include transitional text |
| First non-empty paragraph | Natural boundary; could be very long in some sections |

**Suggestion:** Start with first 50 words of prose (skip blank lines, skip sub-headings,
skip code fences, skip table rows). This is a tunable parameter; start conservative
and adjust based on precision/recall testing against known stale references.

### 2. What about sections that start with non-prose content?

Not every section has a paragraph immediately after the heading. Patterns found in
DSM documents:

| Pattern | Frequency | Example |
|---------|-----------|---------|
| Prose paragraph | Most common | `## 1.1 Overview` followed by explanatory text |
| Immediate sub-heading | Common in DSM_1.0 | `## 2.2 Exploration` followed by `### 2.2.1 Three-Layer Framework` |
| Table | Common in DSM_2.0 | `## Success Criteria` followed by a markdown table |
| Code block | Rare in headings | Template sections with fenced code |
| List | Moderate | `## Deliverables` followed by bullet points |

**Suggestion:** Implement a fallback chain:
1. First: extract prose paragraph (lines not starting with `#`, `|`, `` ` ``, `-`, `*`, or digits followed by `.`)
2. If no prose found before next heading: extract first list item text (strip `- ` prefix)
3. If still nothing: fall back to title-only matching and flag lower confidence

### 3. Three-line reference context: implementation detail

Expanding `CrossReference.context` from 1 to 3 lines requires the parser to track
line numbers and access surrounding lines during extraction.

**Suggestion:** Store `context_before` (line N-1) and `context_after` (line N+1) as
separate fields on `CrossReference`. The TF-IDF comparison concatenates them:

```python
ref_text = f"{ref.context_before} {ref.context} {ref.context_after}"
target_text = f"{section.title} {section.context_excerpt}"
similarity = cosine_similarity(tfidf(ref_text), tfidf(target_text))
```

This keeps the data model clean and allows future tuning of context window size.

---

## Performance Consideration

With 937 sections and potentially hundreds of cross-references, the TF-IDF matrix
will be modest (well under 10K documents). scikit-learn's `TfidfVectorizer` handles
this in milliseconds. The context extraction during parsing adds negligible overhead
(one scan through lines already being read).

---

## Action Items for Graph Explorer

| # | Action | Priority | Status |
|---|--------|----------|--------|
| 1 | Decide on excerpt length (30 vs 50 words) | High | Pending |
| 2 | Add `context_excerpt` field to `Section` dataclass | High | Pending |
| 3 | Implement prose extraction with fallback chain in parser | High | Pending |
| 4 | Add `context_before` / `context_after` fields to `CrossReference` | Medium | Pending |
| 5 | Build TF-IDF comparison using combined context | High | Pending |
| 6 | Test against known stale references for precision/recall tuning | Medium | Pending |
| 7 | Make excerpt word count a config parameter (default: 50) | Low | Pending |

---

## Related

- BACKLOG-103 (DSM Central): Document Structure Metrics Tracking, provides the baseline numbers used in this analysis
- Graph Explorer Sprint 6: Semantic drift detection design
- DSM Central v1.3.30: 16,154 lines, 937 H2+H3 section targets

---

**Feedback Status:** Ready for Graph Explorer Sprint 6 planning
**Created by:** DSM Central (Alberto + Claude)
