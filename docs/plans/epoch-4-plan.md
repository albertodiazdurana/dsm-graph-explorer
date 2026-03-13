# DSM Graph Explorer - Epoch 4 Plan

**Project Type:** Software Engineering (DSM 4.0 Track)
**Start Date:** 2026-03-13
**Status:** PLANNING
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
- [ ] BL-090 resilience: parser handles multi-file document sets (Sprint 13)
- [ ] EXP-007: validate current parser behavior against simulated DSM_0.2 split (Sprint 13)
- [ ] Incremental graph updates: skip unchanged files on rebuild (Sprint 14)

**SHOULD (Epoch 4 Enhancements):**
- [ ] Index creation for `path` and `heading` properties in FalkorDB (Sprint 14)
- [ ] `--graph-export` updated to export from FalkorDB (Sprint 14)
- [ ] Protocol usage frequency analysis: which DSM_0.2 sections are used by which spokes (Sprint 15)

**COULD (Future / Conditional):**
- [ ] LLM second-pass validation (TF-IDF filters, LLM confirms)
- [ ] spaCy NER for entity extraction
- [ ] Sentence transformer embeddings
- [ ] Section rename tracking (`section-renames.yml`)
- [ ] Web visualization (pyvis or similar)
- [ ] FalkorDBLite documentation PR (from issue #85)

### Success Criteria

**Technical:**
- [ ] Parser processes a simulated multi-file DSM_0.2 split with zero regressions (EXP-007)
- [ ] Incremental rebuild skips unchanged files (measured by timestamp or hash)
- [ ] FalkorDB indexes created on `path` and `heading` properties
- [ ] `--graph-export` produces GraphML from FalkorDB store

**Process:**
- [ ] Each sprint produces a working increment
- [ ] Feedback files updated at sprint boundaries
- [ ] Blog material captured for Epoch 4 writeup
- [ ] Open Source Contribution Pipeline executed (FalkorDBLite blog post)

**Ecosystem:**
- [ ] GE resilient to DSM_0.2 structural changes before BL-090 Phase 1 lands
- [ ] Protocol usage analysis available to inform BL-090 splitting decisions (if Sprint 15 reached)

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

---

## Sprint Structure

### Sprint 13: BL-090 Resilience (Multi-File Documents)

**Duration:** 1-2 sessions
**Objective:** Ensure GE handles the upcoming DSM_0.2 split without regressions.
This is defensive work: validate current behavior, fix gaps, add resilience tests.
**Status:** PLANNED

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
1. [ ] Create a simulated split: take an existing large test fixture and split it
       into 3-4 files with cross-references between them
2. [ ] Run the full pipeline (parse, validate, cross-ref, graph build) on the split
3. [ ] Compare results against the original single-file version
4. [ ] Document gaps in `data/experiments/EXP-007-multi-file-resilience/`

**Gate:** Identify which (if any) pipeline stages break on split files.

#### Phase 13.1: Cross-Reference Resolution Across Split Files

**Tasks:**
1. [ ] If EXP-007 reveals cross-reference gaps: update `cross_ref_validator.py` to
       resolve references across a file group (files that were originally one document)
2. [ ] If EXP-007 reveals no gaps: add defensive tests confirming current behavior
3. [ ] Update entity inventory export to handle split-file repos correctly
4. [ ] Write tests for split-file scenarios

#### Phase 13.2: Defensive Test Suite

**Tasks:**
1. [ ] Add test fixtures simulating DSM_0.2 split structure
2. [ ] Integration test: full pipeline on split fixtures
3. [ ] Regression gate: ensure single-file behavior unchanged

#### Sprint 13 Deliverables

- [ ] EXP-007 results documented
- [ ] Cross-reference resolution updated (if needed)
- [ ] Defensive test suite for multi-file document scenarios
- [ ] Confirmation: GE is resilient to BL-090 Phase 1

**Sprint boundary checklist:**
- [ ] Checkpoint document (`docs/checkpoints/`)
- [ ] Feedback files updated (`docs/feedback/`)
- [ ] Decision log updated (`docs/decisions/`)
- [ ] Blog journal entry (`docs/blog/epoch-4/journal.md`)
- [ ] README updated
- [ ] Epoch plan updated (completed tasks checked off)
- [ ] Hub/portfolio notified (`_inbox/` in DSM Central and portfolio)

---

### Sprint 14: Performance & Completeness (Carry-Forward SHOULDs)

**Duration:** 1-2 sessions
**Objective:** Deliver the three Epoch 3 carry-forward SHOULDs: incremental graph
updates, FalkorDB index creation, and FalkorDB export.
**Status:** PLANNED

#### Phase 14.1: Incremental Graph Updates

**Tasks:**
1. [ ] Add file-level change detection: compare file timestamps or content hashes
       against the stored graph's metadata
2. [ ] Update `graph_store.py`: `write_graph()` accepts a set of changed files
       and updates only those nodes/edges
3. [ ] Add `--incremental` flag to CLI (default behavior when graph exists)
4. [ ] Write tests: unchanged files skipped, changed files updated, new files added,
       deleted files removed

#### Phase 14.2: FalkorDB Index Creation

**Tasks:**
1. [ ] Create indexes on `path` (Document nodes) and `heading` (Section nodes)
       during `write_graph()`
2. [ ] Verify index usage via `EXPLAIN` on common queries
3. [ ] Write tests confirming index existence and query plan improvement

#### Phase 14.3: FalkorDB Export

**Tasks:**
1. [ ] Update `--graph-export` to export from FalkorDB when `--graph-db` is set
2. [ ] Export format: GraphML (matching existing NetworkX export)
3. [ ] Write tests comparing FalkorDB export against NetworkX export

#### Sprint 14 Deliverables

- [ ] Incremental graph updates with change detection
- [ ] FalkorDB indexes on `path` and `heading`
- [ ] `--graph-export` from FalkorDB
- [ ] All three Epoch 3 carry-forward SHOULDs resolved

**Sprint boundary checklist:**
- [ ] Checkpoint document
- [ ] Feedback files updated
- [ ] Decision log updated
- [ ] Blog journal entry
- [ ] README updated
- [ ] Epoch plan updated
- [ ] Hub/portfolio notified

---

### Sprint 15: Protocol Usage Analysis (Ecosystem Value)

**Duration:** 1-2 sessions
**Objective:** Build analysis tooling that measures which DSM_0.2 sections are
referenced by spoke projects, informing BL-090's splitting strategy.
**Status:** PLANNED

#### Design

BL-090 Phase 1 Step 2 requires classifying DSM_0.2 sections as "always-load" vs
"on-demand." This classification needs data: which sections are actually used by
which spokes? GE already parses markdown and resolves cross-references; extending
this to analyze spoke CLAUDE.md files for DSM_0.2 section references is a natural
extension.

The output is a usage frequency report: per section, which spokes reference it,
how often, and in what context (reinforcement block, @-import, inline reference).

#### Phase 15.1: Spoke CLAUDE.md Scanner

**Tasks:**
1. [ ] Create `src/analysis/protocol_usage.py`:
   - [ ] `scan_spoke_references(spoke_path)`: extract DSM_0.2 section references
         from CLAUDE.md reinforcement blocks
   - [ ] `scan_at_imports(spoke_path)`: extract @-import paths targeting DSM files
   - [ ] Handle different reference formats: section numbers, protocol names,
         template references
2. [ ] Write tests with fixture CLAUDE.md files

#### Phase 15.2: Usage Frequency Report

**Tasks:**
1. [ ] Create `src/analysis/usage_report.py`:
   - [ ] `generate_usage_report(spoke_paths)`: aggregate across all spokes
   - [ ] Per-section output: reference count, referencing spokes, reference context
   - [ ] Classification suggestion: always-load (referenced by ≥50% of spokes) vs
         on-demand (referenced by <50%)
2. [ ] Add `--protocol-usage PATH [PATH...]` CLI option
3. [ ] Rich table output for the report
4. [ ] Write tests

#### Phase 15.3: Cross-Reference Density Mapping

**Tasks:**
1. [ ] Extend `protocol_usage.py` to measure intra-DSM_0.2 cross-references:
       which sections reference each other most?
2. [ ] Identify natural module boundaries: clusters of sections with high internal
       cross-reference density and low external density
3. [ ] Report: suggested module groupings for BL-090 splitting

#### Sprint 15 Deliverables

- [ ] `src/analysis/protocol_usage.py` (spoke scanner)
- [ ] `src/analysis/usage_report.py` (frequency aggregation)
- [ ] `--protocol-usage` CLI option
- [ ] Classification suggestions for BL-090 splitting
- [ ] Cross-reference density mapping

**Sprint boundary checklist:**
- [ ] Checkpoint document
- [ ] Feedback files updated
- [ ] Decision log updated
- [ ] Blog journal entry
- [ ] README updated
- [ ] Epoch plan updated
- [ ] Hub/portfolio notified

---

### Sprint 16: Reserved

**Duration:** 1-2 sessions
**Objective:** TBD at Sprint 15 boundary. Candidates:
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
│   ├── protocol_usage.py       # Spoke CLAUDE.md scanner
│   └── usage_report.py         # Frequency aggregation + classification
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

- `docs/blog/epoch-4/materials.md`
- `docs/blog/epoch-4/journal.md`

---

**Plan Status:** PLANNING (awaiting approval)
**Last Updated:** 2026-03-13
**Previous:** [epoch-3-plan.md](epoch-3-plan.md)
**Alignment Source:** `_inbox/dsm-central.md` (2026-03-13)
