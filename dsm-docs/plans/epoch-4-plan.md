# DSM Graph Explorer - Epoch 4 Plan

**Project Type:** Software Engineering (DSM 4.0 Track)
**Start Date:** 2026-03-13
**Status:** IN PROGRESS (Sprint 15 implementation complete, EXP-009 pending)
**Prerequisite:** Epoch 3 Complete ([epoch-3-plan.md](epoch-3-plan.md))
**Project Lead:** Alberto Diaz Durana (with AI assistance)
**Alignment:** DSM Central response received 2026-03-13 (v1.3.36-v1.3.39)

---

## Epoch 4 Overview

### Context

Epoch 3 delivered persistent graph storage (FalkorDBLite), git-ref temporal compilation,
entity inventories, and cross-repo edges including BL-156 drift detection. The project
now has 513 tests at 95% coverage across 12 sprints.

Epoch 4 is driven by two forces:

1. **Ecosystem resilience (BL-090):** DSM_0.2 has grown to 2,458 lines (111 KB),
   consuming ~16-20% of context windows. DSM Central will split it into a slim core
   plus module files. GE's parser and validators must handle this structural change
   without regressions.

2. **Performance and completeness:** Three SHOULDs carried forward from Epoch 3
   (incremental graph updates, FalkorDB export, index creation) improve the tool's
   production readiness.

A secondary opportunity exists: GE's cross-repo analysis features can measure protocol
usage frequency across the DSM ecosystem, directly informing BL-090's splitting strategy.
This positions GE as an ecosystem optimization tool, not just a validator.

### Key Inputs

| Source | Input |
|--------|-------|
| DSM Central alignment response | BL-090 priority, version updates v1.3.36-39 |
| Epoch 3 carry-forwards | 3 SHOULDs not completed |
| Epoch 3 COULDs | LLM/NLP features (deferred) |
| Open Source Contribution Pipeline | FalkorDBLite issue #85 open, blog + PR pending |

### Scope (MoSCoW)

**MUST (Epoch 4 Core):**
- [x] BL-090 resilience: parser handles multi-file document sets (Sprint 13)
- [x] EXP-007: validate current parser behavior against real DSM_0.2 split (Sprint 13)
- [x] Incremental graph updates: skip unchanged files on rebuild (Sprint 14)

**SHOULD (Epoch 4 Enhancements):**
- [x] Index creation for `node_id` and `heading` properties in FalkorDB (Sprint 14)
- [x] `to_networkx()` roundtrip export from FalkorDB (Sprint 14)
- [x] Heading reference detection: `--heading-refs` CLI flag, cross-ref extraction by heading title (Sessions 38-39)
- [x] Heading reference graph edges: `ref.type == "heading"` resolution in graph builder (Session 39)
- [x] EXP-008: validate heading reference detection quality on real DSM data (Session 39, FAIL -> pre-filter applied)
- [x] Protocol usage frequency analysis: which DSM_0.2 sections are used by which spokes (Sprint 15)

**COULD (Future / Conditional):**
- [ ] LLM second-pass validation (TF-IDF filters, LLM confirms)
- [ ] spaCy NER for entity extraction
- [ ] Sentence transformer embeddings
- [ ] Section rename tracking (`section-renames.yml`)
- [ ] Web visualization (pyvis or similar)
- [ ] FalkorDBLite documentation PR (from issue #85)
- [ ] Agent-consumable knowledge summary: `--knowledge-summary` (BACKLOG-302, from EXP-002)
- [ ] Parser validation against EXP-001 reference graph (286 edges, ground truth dataset)
- [ ] Hop distance from entry point in `--graph-stats` (informed by EXP-001 two-tier threshold model)

### Success Criteria

**Technical:**
- [x] Parser processes real multi-file DSM_0.2 split with zero regressions (EXP-007)
- [x] Incremental rebuild via `update_files()` (file-level granularity, ref-change detection)
- [x] FalkorDB indexes created on `node_id` and `heading` properties
- [x] `to_networkx()` roundtrip: FalkorDB → NetworkX DiGraph

**Process:**
- [x] Each sprint produces a working increment
- [x] Feedback files updated at sprint boundaries
- [x] Blog material captured for Epoch 4 writeup
- [ ] Open Source Contribution Pipeline executed (FalkorDBLite blog post)

**Ecosystem:**
- [x] GE resilient to DSM_0.2 structural changes (BL-090 Phase 1 already landed)
- [x] Protocol usage analysis available to inform BL-090 splitting decisions (Sprint 15)

---

## Experiment Definitions

### EXP-007: Multi-File Document Resilience

**Sprint:** 13 (pre-implementation gate)
**Goal:** Validate that GE's parser, validator, and cross-reference resolution work
correctly when a single large markdown file is split into multiple smaller files with
cross-references between them.

**Justification:** BL-090 Phase 1 will split DSM_0.2 (~2,458 lines) into a slim core
plus module files. GE currently parses files independently and resolves cross-references
across files. The question is: does the current pipeline handle the split gracefully,
or do references that assumed a single-file context break?

**Hypothesis:** GE's parser already processes files independently, so the split should
not break parsing. Cross-reference resolution may need adjustment if references use
section numbers (e.g., "Section 3.2") that assume a specific file context.

**Success Criteria:**
| Criterion | Threshold |
|-----------|-----------|
| Parsing: split files parse without errors | 100% |
| Sections: total section count matches pre-split | Exact match |
| Cross-references: intra-file refs still resolve | 100% |
| Cross-references: refs between split files resolve | ≥90% (identify gaps) |
| Graph: node/edge count matches pre-split graph | Exact match |

**Environment:** Python 3.12, existing test fixtures, simulated split of a large test file.

**Decision gate:** If cross-file references break, Sprint 13 implementation focuses on
fixing the resolution logic. If everything passes, Sprint 13 scope reduces to
documentation and defensive tests.

### EXP-008: Heading Reference Detection Quality

**Sprint:** Between 14 and 15 (post-implementation gate)
**Goal:** Validate that `--heading-refs` produces useful, low-noise signal when run
against real DSM documents. Heading reference detection was implemented in Sessions
38-39 as a follow-on to EXP-007 findings (GE could not detect heading-only sections
or resolve heading title mentions in prose).

**Justification:** Unit tests validate correctness with synthetic fixtures, but cannot
answer whether the feature is useful on real data. Common heading titles like
"Overview" or "Summary" may produce excessive false positives. Cross-file resolution
may behave differently when many files share similar heading titles. This experiment
validates signal quality before the feature is promoted to production use.

**Hypothesis:** Heading reference detection will find meaningful cross-references in
DSM documents where section numbering is absent. False positive rate will be
acceptable for specific, multi-word headings (e.g., "Session Transcript Protocol")
but may be problematic for generic single-word headings (e.g., "Overview").

**Success Criteria:**
| Criterion | Threshold |
|-----------|-----------|
| Detection: heading refs found in real DSM documents | >0 meaningful refs |
| True positive rate: detected mentions are actual references | ≥80% |
| False positive rate: spurious matches from generic titles | ≤20% |
| Cross-file resolution: heading refs resolve across files | ≥90% |
| No regressions: existing validation results unchanged | Exact match |

**Environment:** Python 3.12, DSM repository (`~/dsm-agentic-ai-data-science-methodology/`),
real DSM_0.2 split (v1.3.69 modular format).

**Decision gate:** If false positive rate exceeds 20%, scope TF-IDF fuzzy filtering
or heading length threshold as a pre-filter before the feature is promoted. If true
positive rate is below 80%, revisit the extraction heuristic.

---

## Sprint Structure

### Sprint 13: BL-090 Resilience (Multi-File Documents)

**Duration:** 1-2 sessions
**Objective:** Ensure GE handles the upcoming DSM_0.2 split without regressions.
This is defensive work: validate current behavior, fix gaps, add resilience tests.
**Status:** COMPLETE (531 tests, 95% coverage)

#### Design

The risk from BL-090 is not that GE's parser breaks (it already processes files
independently), but that:

1. **Cross-references between split files:** A reference like "see Section 3.2" in
   DSM_0.2 currently resolves within the same file. After splitting, "Section 3.2"
   may live in a different file. The cross-reference validator needs to resolve
   these across the split file set.

2. **Entity inventories:** The DSM Central entity inventory will change. Sections
   that were in one file path will move to new paths. GE's inventory-based resolution
   (Sprint 11) should handle this if inventories are regenerated, but needs verification.

3. **Convention linting:** Naming convention checks (Sprint 8) may need path pattern
   updates if DSM_0.2 modules follow a new naming convention.

#### Phase 13.0: EXP-007 (Resilience Experiment)

**Tasks:**
1. [x] Tested against real DSM_0.2 split (pre-split v1.3.59 vs post-split v1.3.69)
2. [x] Run the full pipeline (parse, validate, cross-ref, graph build) on both
3. [x] Compared results: 0 errors both cases, warning delta explained by content redistribution
4. [x] Documented in `data/experiments/EXP-007-multi-file-resilience/`

**Gate:** Identify which (if any) pipeline stages break on split files.

#### Phase 13.1: Heading-Based Section Detection (BL-042)

EXP-007 revealed GE detected 0 sections in DSM_0.2 (heading-only format). Scoped BL-042 into this sprint.

**Tasks:**
1. [x] TDD: 18 new tests for heading-based section detection
2. [x] Updated `graph_builder.py`: `_slugify()`, `_section_id()`, removed `if section.number:` guard
3. [x] Updated existing test for new behavior
4. [x] DEC-008: heading-based section ID format (`h:slug`)

#### Sprint 13 Deliverables

- [x] EXP-007 results documented
- [x] Heading-based section detection implemented (BL-042)
- [x] 18 new tests for heading-based scenarios
- [x] Confirmation: GE is resilient to BL-090 Phase 1
- [x] BL-170 Part B architecture audit complete

**Sprint boundary checklist:**
- [x] Checkpoint document (`dsm-docs/checkpoints/`)
- [x] Feedback files updated (`dsm-docs/feedback-to-dsm/`)
- [x] Decision log updated (`dsm-docs/decisions/`)
- [x] Blog journal entry (`dsm-docs/blog/epoch-4/journal.md`)
- [x] README updated
- [x] Epoch plan updated (completed tasks checked off)
- [x] Hub/portfolio notified (`_inbox/` in DSM Central and portfolio)

---

### Sprint 14: Performance & Completeness (Carry-Forward SHOULDs)

**Duration:** 1-2 sessions
**Objective:** Deliver the three Epoch 3 carry-forward SHOULDs: incremental graph
updates, FalkorDB index creation, and FalkorDB export.
**Status:** COMPLETE (547 tests, 95% coverage)

#### Phase 14.1: Incremental Graph Updates

**Tasks:**
1. [x] `GraphStore.update_files()`: file-level selective delete/reinsert
2. [x] `GraphStore.get_stored_ref()`: detect ref staleness for cache decisions
3. [x] CLI ref-change detection: triggers incremental path when stored ref differs
4. [x] 8 tests: single-file update, reference preservation, no duplicates, git_ref stamping, fallback

#### Phase 14.2: FalkorDB Index Creation

**Tasks:**
1. [x] Added indexes on `Section.node_id` and `Section.heading` in `_create_indexes()`
2. [x] 3 tests: lookup by node_id, lookup by heading, heading section by node_id

#### Phase 14.3: FalkorDB Export

**Tasks:**
1. [x] `GraphStore.to_networkx()`: roundtrip FalkorDB → NetworkX DiGraph
2. [x] Full schema preservation (FILE, SECTION, CONTAINS, REFERENCES with all properties)
3. [x] 5 tests: roundtrip node/edge counts, property preservation, error handling

#### Sprint 14 Deliverables

- [x] Incremental graph updates with ref-change detection
- [x] FalkorDB indexes on `node_id` and `heading`
- [x] `to_networkx()` roundtrip export
- [x] All three Epoch 3 carry-forward SHOULDs resolved

**Sprint boundary checklist:**
- [x] Checkpoint document
- [x] Feedback files: no new entries (implementation-only session)
- [x] Decision log: no new decisions (enhancements to existing DEC-006 architecture)
- [x] Blog journal entry
- [x] README updated
- [x] Epoch plan updated
- [x] Hub/portfolio notified

---

### Sprint 15: Protocol Usage Analysis (Ecosystem Value)

**Duration:** 1-2 sessions
**Objective:** Build analysis tooling that measures which DSM_0.2 sections are
referenced by spoke projects, informing BL-090's splitting strategy.
**Status:** IN PROGRESS (implementation complete, EXP-009 pending, boundary checklist pending)

#### Design

BL-090 Phase 1 Step 2 requires classifying DSM_0.2 sections as "always-load" vs
"on-demand." This classification needs data: which sections are actually used by
which spokes? GE already parses markdown and resolves cross-references; extending
this to analyze spoke CLAUDE.md files for DSM_0.2 section references is a natural
extension.

Implementation evolved beyond the original plan into a four-layer methodology
(Declared, Prescribed, Observed, Designed) with 6 new source modules and 6 new
test files, reaching 664 tests at 91% coverage.

#### Phase 15.1: Section Index + Declared References

**Tasks:**
1. [x] Create `src/analysis/section_index.py`: build section inventory from DSM_0.2
2. [x] Create `src/analysis/declared_refs.py`: extract declared references from spoke CLAUDE.md
3. [x] Write tests for both modules

#### Phase 15.2: Prescribed + Observed References

**Tasks:**
1. [x] Create `src/analysis/prescribed_refs.py`: extract prescribed protocol references
2. [x] Create `src/analysis/observed_refs.py`: extract observed usage patterns
3. [x] Write tests for both modules

#### Phase 15.3: Usage Report + CLI

**Tasks:**
1. [x] Create `src/analysis/usage_report.py`: aggregate all layers into frequency report
2. [x] Create `src/analysis/usage_diff.py`: compare usage across spokes
3. [x] Add `--protocol-usage` and `--usage-compare` CLI options
4. [x] Rich table output for reports
5. [x] Write tests for both modules

#### Phase 15.4: EXP-009 (Protocol Usage Validation)

Defined with DSM Central input (Session 141): fourth layer (Designed), ground
truth validation (7 sections), ≥60% threshold.

**Tasks:**
1. [ ] EXP-009 Stage A: run all 4 layers against real data (including transcripts)
2. [ ] EXP-009 Stage B: transcript validation
3. [ ] Document results in `data/experiments/EXP-009-*/`

#### Sprint 15 Deliverables

- [x] `src/analysis/section_index.py` (section inventory)
- [x] `src/analysis/declared_refs.py` (declared layer)
- [x] `src/analysis/prescribed_refs.py` (prescribed layer)
- [x] `src/analysis/observed_refs.py` (observed layer)
- [x] `src/analysis/usage_report.py` (frequency aggregation)
- [x] `src/analysis/usage_diff.py` (cross-spoke comparison)
- [x] `--protocol-usage` and `--usage-compare` CLI options
- [ ] EXP-009 execution and results

**Sprint boundary checklist:**
- [ ] Checkpoint document
- [ ] Feedback files updated
- [ ] Decision log updated
- [ ] Blog journal entry
- [ ] README updated
- [x] Epoch plan updated
- [ ] Hub/portfolio notified

---

### Sprint 16: Reserved

**Duration:** 1-2 sessions
**Objective:** TBD at Sprint 15 boundary. Candidates:
- **`--knowledge-summary` (BACKLOG-302, from DSM Central EXP-002):** Agent-consumable
  markdown export (~150-200 lines) derived from graph topology. Presentation layer
  over existing graph infrastructure. See `dsm-docs/research/dsm-central-exp-002-knowledge-graph-feasibility.md`.
- **GraphML None-value bug fix:** `export_graphml()` crashes on `None` attributes
  (unnumbered headings). Small fix, independent of feature work.
- LLM second-pass validation (if ecosystem priority shifts)
- FalkorDBLite documentation PR (if maintainers respond to issue #85)
- spaCy NER / sentence embeddings (if analysis features create demand)
- Epoch 4 close-out (if scope is satisfied by Sprints 13-15)
**Status:** RESERVED

**Decision gate:** At Sprint 15 boundary, evaluate:
1. Did Sprints 13-15 complete on schedule?
2. Is there demand for LLM/NLP features from DSM Central or portfolio?
3. Did FalkorDBLite maintainers respond to issue #85?
4. Is the epoch scope satisfied?
5. Does `--knowledge-summary` (BACKLOG-302) justify a Sprint 16, or carry to Epoch 5?

If scope is satisfied, close Epoch 4 at Sprint 15 and carry remaining COULDs to Epoch 5.

---

## Architecture Evolution

### Epoch 3 Pipeline

```
markdown files (or git ref) → parser → validator → NetworkX DiGraph → FalkorDB
                                                                    → graph-stats
                                                                    → temporal diff
entity inventories (external repos) → cross-repo resolver → bridge graph
```

### Epoch 4 Pipeline (additions marked with *)

```
markdown files (or git ref) → parser → validator → NetworkX DiGraph → FalkorDB
                                     ↓                               → graph-stats
                              * multi-file                           → temporal diff
                                resolution                           → * incremental update
                                                                     → * FalkorDB export

entity inventories → cross-repo resolver → bridge graph

* spoke CLAUDE.md files → protocol usage scanner → usage frequency report
                                                 → cross-ref density map
                                                 → BL-090 splitting suggestions
```

### New Modules (Epoch 4)

```
src/
├── analysis/                    # NEW (Sprint 15)
│   ├── __init__.py
│   ├── section_index.py        # DSM_0.2 section inventory
│   ├── declared_refs.py        # Declared references (CLAUDE.md)
│   ├── prescribed_refs.py      # Prescribed protocol references
│   ├── observed_refs.py        # Observed usage patterns
│   ├── usage_report.py         # Four-layer frequency aggregation
│   └── usage_diff.py           # Cross-spoke comparison
```

---

## Dependencies

No new mandatory dependencies anticipated. Sprint 15's analysis features use
existing parsing and cross-reference infrastructure. Sprint 14's incremental
updates use file hashing (stdlib `hashlib`).

If Sprint 16 pursues LLM features, a new optional dependency group would be
needed (e.g., `[llm]` with `ollama` for local inference + RAG pipeline).
This decision is deferred to the Sprint 16 planning gate.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| BL-090 split lands before Sprint 13 completes | Low | High | EXP-007 runs first; defensive tests catch regressions early |
| DSM_0.2 split format unknown | Medium | Medium | EXP-007 uses simulated split; adapt when actual format is known |
| Incremental updates introduce cache staleness bugs | Medium | Medium | Content hashing (not timestamps) as primary change detection |
| Protocol usage analysis produces noisy results | Medium | Low | Start with exact section number matches; add fuzzy matching if needed |
| FalkorDBLite maintainers unresponsive to issue #85 | Medium | Low | Blog post proceeds regardless; PR is optional |
| Sprint 16 scope unclear | Expected | Low | Decision gate at Sprint 15 boundary; acceptable to close epoch early |

---

## Blog Integration

### Epoch 4 Blog Topics

1. **Sprint 13:** "Preparing for Structural Change: How to Validate Parser Resilience"
   - Testing against anticipated upstream changes
   - Experiment-as-insurance pattern

2. **Sprint 14:** "Incremental Graph Updates: From Full Rebuild to Surgical Precision"
   - Change detection strategies (hash vs timestamp)
   - FalkorDB index creation and query optimization

3. **Sprint 15:** "Measuring Protocol Usage: When Your Validator Becomes an Ecosystem Tool"
   - From validation to analysis
   - Cross-reference density as a module boundary signal
   - Contributing measurement data to ecosystem decisions

4. **Cross-cutting:** "When Your Experiment Becomes Upstream Documentation"
   - The Open Source Contribution Pipeline (Entry 42 / Proposal #37)
   - FalkorDBLite issue #85 → blog post → PR sequence

### Materials Location

- `dsm-docs/blog/epoch-4/materials.md`
- `dsm-docs/blog/epoch-4/journal.md`

---

**Plan Status:** IN PROGRESS (Sprint 15 implementation complete, EXP-009 pending)
**Last Updated:** 2026-04-02
**Previous:** [epoch-3-plan.md](epoch-3-plan.md)
**Alignment Source:** `_inbox/dsm-central.md` (2026-03-13)
