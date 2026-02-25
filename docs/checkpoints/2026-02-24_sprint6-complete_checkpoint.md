# Sprint 6 Complete Checkpoint

**Date:** 2026-02-24
**Type:** Sprint Boundary
**Status:** Complete
**Previous:** [2026-02-10_sprint5-complete_checkpoint.md](2026-02-10_sprint5-complete_checkpoint.md)

---

## Summary

Sprint 6 (Semantic Validation) is complete. Four implementation phases and one real-data validation experiment delivered TF-IDF cosine similarity for detecting semantic drift in cross-references. The `--semantic` flag is fully integrated into the CLI with graceful fallback when scikit-learn is absent. EXP-003b validated the threshold against 1,191 real cross-references, leading to a DEC-005 amendment lowering the default from 0.10 to 0.08. This is the most technically complex sprint so far, spanning parser enhancements, a new module (`src/semantic/`), CLI wiring, and an experiment that challenged the original synthetic results.

---

## What Was Built

### Phase 6.0: EXP-003 Threshold Tuning
- Capability experiment with 25 synthetic test cases (10 match, 10 drift, 5 ambiguous)
- Evaluated title-only vs title+excerpt modes across thresholds 0.05-0.30
- Result: title+excerpt with threshold 0.10, min 3 tokens, corpus-scoped IDF
- Documented as [DEC-005](../decisions/DEC-005-semantic-validation-approach.md)

### Phase 6.1: Parser Context Extraction
- Added `Section.context_excerpt` (~50 words of prose following each heading)
- Added `CrossReference.context_before` / `context_after` (3 lines surrounding each reference)
- 12 new tests (8 excerpt, 4 context window)

### Phase 6.2: TF-IDF Similarity Module
- `src/semantic/similarity.py` with corpus-scoped TF-IDF vectorization
- Section number stripping before vectorization
- Minimum token gate (3 tokens after stopword removal)
- Configurable threshold via `.dsm-graph-explorer.yml`
- 14 new tests

### Phase 6.3: CLI Integration
- `--semantic` flag on `dsm-validate` command
- Graceful fallback: missing scikit-learn prints clear error, exits with code 2
- `config_loader.py`: `semantic_threshold` + `semantic_min_tokens` fields
- `cross_ref_validator.py`: `build_section_lookup()` for efficient section resolution
- `report_generator.py`: drift warning (yellow) and insufficient context (dim) Rich tables, markdown equivalents
- 6 new CLI integration tests (`tests/test_cli_semantic.py`)

### EXP-003b: Real Data Validation
- Generated 1,191 cross-reference rows from DSM methodology repository
- Agent-assisted labeling of 128 near-threshold rows (0.08-0.12 score zone)
- Results at threshold 0.10: Precision=1.000, Recall=0.496, F1=0.663
- 63 false negatives (all between 0.08-0.10), 0 false positives
- Root causes: empty target excerpts, vocabulary mismatch in backlog proposals, short generic titles
- DEC-005 amended: threshold lowered from 0.10 to 0.08

---

## Test Results

| Metric | Value |
|--------|-------|
| Total tests | 250 |
| Coverage | 95% |
| New tests (Sprint 6) | 32 (12 parser + 14 semantic + 6 CLI) |
| Execution time | ~2s |

---

## Real-World Validation

EXP-003b served as the real-world validation for this sprint. Against the full DSM repository (1,191 cross-references):

| Metric | EXP-003 (synthetic) | EXP-003b (real) |
|--------|---------------------|-----------------|
| Test cases | 25 | 128 (labeled) |
| Precision | 1.000 | 1.000 |
| Recall | 0.800 | 0.496 → recovered at 0.08 |
| F1 | 0.889 | 0.663 → improved at 0.08 |

The tool is perfectly conservative: when it says "match," it is always right. The recall gap between synthetic and real data confirmed the value of real-data validation experiments.

---

## DSM Feedback Generated

| Type | ID | Topic |
|------|----|-------|
| Methodology Entries 22-28 | Proposals 19-23 | Sprint 6 observations across 4 sessions |

Key entries from Sprint 6:
- Entry 22 / Proposal #19: Experiment scripts as first-class artifacts
- Entry 23 / Proposal #20: Agent-assisted labeling protocol
- Entry 24 / Proposal #21: Real-data validation as experiment gate
- Proposal #23: `data/experiments/` as canonical experiment location (accepted, migrated)

**Totals:** methodology.md now has 28 entries, backlogs.md has 23 proposals.

---

## Sprint 6 Deliverables Checklist

- [x] EXP-003 threshold tuning experiment (`data/experiments/exp003_tfidf_threshold.py`)
- [x] DEC-005 semantic validation approach decision
- [x] Parser context extraction (`Section.context_excerpt`, `CrossReference.context_before/after`)
- [x] TF-IDF similarity module (`src/semantic/similarity.py`)
- [x] CLI integration (`--semantic` flag, graceful fallback)
- [x] Config support (`semantic_threshold`, `semantic_min_tokens`)
- [x] Report generator updates (drift + insufficient context tables)
- [x] EXP-003b real data validation (`data/experiments/exp003b_real_data_validation.py`)
- [x] DEC-005 amendment (threshold 0.10 → 0.08)
- [x] README updated with Sprint 6 features and project structure

---

## Sprint Boundary Checklist (DSM 2.0 Template 8)

- [x] Checkpoint document created (this file)
- [x] Feedback files updated (`methodology.md` Entries 22-28, `backlogs.md` Proposals 19-23)
- [x] Decision log updated (DEC-005 created + amended with EXP-003b)
- [x] Blog journal entry written (`docs/blog/epoch-2/journal.md`)
- [x] Repository README updated (features, structure, status)

---

## Next Steps

1. **Sprint 7:** Graph Prototype, NetworkX graph builder, queries, GraphML export
2. **Sprint 8:** Convention Linting, `--lint` flag, 6 style checks (added during Sprint 5)
3. **Epoch 3+:** Neo4j integration, LLM second-pass (tiered: TF-IDF filters, LLM confirms)

---

## Session Context

- **Environment:** WSL2 Ubuntu, Python 3.10.12
- **Tools:** pytest, dsm-validate, pip, git, scikit-learn
- **Sprint sessions:** Sessions 11-15 (2026-02-10 through 2026-02-23)
- **Key commit:** `c2c67f2` (Session 15 wrap-up)

---

**Author:** Alberto Diaz Durana (with AI assistance)
**Created:** 2026-02-24
