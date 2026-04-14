# DSM Graph Explorer - Epoch 4 Plan

**Project Type:** Software Engineering (DSM 4.0 Track)
**Start Date:** 2026-03-13
**Status:** COMPLETE (Sprints 13-16 delivered, retrospective in `dsm-docs/checkpoints/epoch-4/epoch-4-retrospective.md`)
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
| Epoch 3 COULDs | ~~LLM/NLP features~~ dropped (DEC-009) |
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
- ~~LLM second-pass validation~~ dropped (DEC-009: no local LLM dependencies)
- ~~spaCy NER for entity extraction~~ dropped (DEC-009)
- ~~Sentence transformer embeddings~~ dropped (DEC-009)
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

**Decision gate:** If false positive rate exceeds 20%, scope heading length
threshold as a pre-filter before the feature is promoted. If true positive rate
is below 80%, revisit the extraction heuristic. (TF-IDF fuzzy filtering
removed per DEC-009.)

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
**Status:** COMPLETE (EXP-009 CONDITIONAL PASS, boundary checklist complete)

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
- [x] Checkpoint document (`dsm-docs/checkpoints/epoch-4/done/session-45-sprint-15-checkpoint.md`)
- [x] Feedback files updated (`dsm-docs/feedback-to-dsm/done/2026-04-02_s45_*.md`)
- [x] Decision log updated (Sprint 15 was analysis-focused, no new DECs, verified)
- [x] Blog journal entry (`dsm-docs/blog/journal.md`, Sprint 15 entry 2026-04-02)
- [x] README updated (Sprint 15 complete, four-layer methodology, EXP-009, 664 tests)
- [x] Epoch plan updated
- [x] Hub/portfolio notified (`2026-04-02_dsm-graph-explorer_sprint-15-complete.md` in both Central and portfolio done/)

---

### Sprint 16: Knowledge Summary Export (DSM Central BL-302 Phase 1)

**Duration:** 1-2 sessions (completed in S47, 1 session)
**Objective:** `--knowledge-summary PATH` CLI command producing agent-consumable
markdown (~150-200 lines) derived from graph topology. Presentation layer over
existing graph infrastructure (Sprint 14).
**Status:** COMPLETE (BL-302 Phase 1 delivered, validated against DSM Central: 811 files → 253-line summary)
**Origin:** DSM Central EXP-002 (PARTIAL PASS), BL-303 (P1-P4 priority guidance)
**Research:** `dsm-docs/research/dsm-central-exp-002-knowledge-graph-feasibility.md`,
DSM Central `dsm-docs/research/2026-04-13_external-repos-deep-research.md` (BL-355)

**Decision gate answers** (from Sprint 15 boundary):
1. Sprints 13-15 complete on schedule ✓
2. No LLM/NLP demand from ecosystem, deferred to Epoch 5
3. FalkorDBLite maintainers have not responded to issue #85, deferred to Epoch 5
4. Epoch scope not yet satisfied, BL-302 justifies Sprint 16
5. `--knowledge-summary` justified as High priority from Central EXP-002 + BL-303

#### Scope: P1 + P2 + GraphML Bug Fix

| Priority | Component | Description | Implementation |
|----------|-----------|-------------|----------------|
| P1 | Document hierarchy | Tree view with module relationships | Walk CONTAINS edges, render indented tree |
| P1 | Hub documents | Top-N by reference connectivity, 1-line purpose | Sort by in-degree, extract title + purpose |
| P2 | Cross-reference hotspots | Sections referenced 10+ times | Filter REFERENCES edges by count |
| P2 | Orphan detection | Files with zero incoming references | Find file nodes with in-degree == 0 |
| Fix | GraphML None-value | `export_graphml()` crashes on `None` attributes | Replace `None` with empty string |

**Design rationale:** "Knowledge compilation over retrieval," pre-synthesize
navigation aids rather than requiring agents to query raw data per session.
Validated independently by Karpathy's LLM Wiki design, PageIndex tree navigation,
and code-review-graph's structured output approach.

#### Deliverables

1. `src/analysis/knowledge_summary.py` — summary generator module (4 components)
2. Markdown formatter — structured output designed for LLM consumption
3. `--knowledge-summary PATH` CLI flag integration
4. GraphML None-value bug fix in `export_graphml()`
5. Tests for all components, validated against DSM Central graph (4,703+ nodes)

#### Acceptance Criteria

- [ ] `--knowledge-summary PATH` produces markdown output (~150-200 lines)
- [ ] Document hierarchy shows file-to-section tree structure
- [ ] Hub documents lists top-10 by connectivity with 1-line descriptions
- [ ] Cross-reference hotspots lists sections with 10+ incoming references
- [ ] Orphan detection lists files with zero incoming references
- [ ] Output is agent-consumable (structured markdown, no visual formatting)
- [ ] GraphML None-value bug is fixed
- [ ] Tests pass, coverage maintained above 80%
- [ ] Validated against DSM Central repository

#### Risks

1. **Output length:** 150-200 line target may be insufficient for large repos.
   Mitigation: configurable top-N thresholds, test with real data early.
2. **Hub scoring stability:** Rankings may shift as repo evolves, causing churn.
   Mitigation: use relative rankings, not absolute counts.

#### Related Work

| Repo | Pattern | Applicable to |
|------|---------|---------------|
| code-review-graph (9.2k stars) | Leiden community detection, MCP integration | Future Phase 2-3 |
| Karpathy LLM Wiki (5k+ stars) | Knowledge compilation, lint operations | Core design, future lint |
| PageIndex (25k stars) | Tree-based hierarchical navigation | P1 hierarchy |

#### Deferred Requirements (organized by theme, for Epoch 5+ planning)

**Theme A: Intrinsic-ToC / Knowledge Summary evolution (BL-302 Phase 2-3+)**
- BL-302 Phase 2: concept clusters via Leiden algorithm (ref: code-review-graph)
- BL-302 Phase 3: navigation by project type (needs DSM-specific config input)
- Data/format separation: split data functions from markdown formatters when a
  second output format is concretely needed (JSON, other). See DEC-009 rationale.
- Cross-repo references in ToC entries (Layer 3 of Intrinsic-ToC vision)
- Non-markdown metadata enrichment: filesystem stats, pyproject.toml, test
  metrics injected into the knowledge summary
- Temporal/methodology metadata: when components were built, which DSM
  principles applied (from git history, session transcripts, decision records)
- Parseable key-value entry format for machine extraction (`refs-in:`, `path:`)
- Full lint operation: expand orphan detection into contradiction detection,
  missing cross-references, stale claims (ref: Karpathy wiki lint concept)
- Research ref: `dsm-docs/research/2026-04-13_intrinsic-toc-vision.md`

**Theme B: Ecosystem graph / Avatar (Layer 3-4 of vision)**
- Avatar materialization: persistent cross-repo graph connecting all spoke ToCs
- Code ontology parsing: AST-based graphs from Python source (ref: code-review-graph Tree-sitter)
- Code-to-document relationships: which code implements which spec section
- Test-to-requirement tracing: which tests validate which requirements
- MCP exposure of knowledge summary as agent tool
- Research ref: `dsm-docs/research/2026-04-13_intrinsic-toc-vision.md` §4, §10

**Theme C: Graph infrastructure**
- Hop distance from entry point in `--graph-stats` (EXP-001 two-tier threshold)
- Parser validation against EXP-001 reference graph (286 edges, ground truth)
- Bidirectional edge analysis (EXP-001 suggestion)
- Web visualization (pyvis or similar)
- Research ref: `_inbox/done/dsm-central-reachability-experiment.md`

**Theme D: Open source contribution pipeline**
- FalkorDBLite documentation PR (awaiting maintainer response to issue #85)
- Blog post for the contribution story ("experiment becomes upstream docs")
- Research ref: `dsm-docs/blog/epoch-3/journal.md` (Contribution-Ready section)

**Theme E: Parser extensions**
- Section rename tracking (`section-renames.yml`)
- TF-IDF fuzzy matching for heading references (pre-filter only, no local LLM per DEC-009)

#### Sprint 16 Deliverables

- [x] `src/analysis/knowledge_summary.py` (5 functions: hierarchy, hub documents, hotspots, orphans, orchestrator)
- [x] `--knowledge-summary PATH` CLI option
- [x] GraphML None-value bug fix in `export_graphml()`
- [x] Tests (25 new, full suite 689 passed, 91% coverage)
- [x] Validated against DSM Central (811 files, 8,991 sections → 253-line summary)

**Sprint boundary checklist:**
- [x] Checkpoint document (`dsm-docs/checkpoints/epoch-4/session-47-sprint-16-checkpoint.md`)
- [x] Feedback files (methodology entries 59-62, backlogs proposals #52-55)
- [x] Decision log (DEC-009: no local LLM dependencies)
- [x] Blog journal entry (`dsm-docs/blog/journal.md`, Sprint 16 entry)
- [x] README updated (Sprint 16 complete, --knowledge-summary, 689 tests)
- [x] Epoch plan updated
- [x] Hub/portfolio notified (Central: `2026-04-14_dsm-graph-explorer_s47-findings.md`, portfolio: `2026-04-14_dsm-graph-explorer_sprint-16-complete.md`)

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

Local LLM/NLP dependencies (spaCy, sentence-transformers, ollama) have been
dropped per DEC-009: the consuming AI agent is the LLM, local models are
redundant. No `[llm]` optional dependency group will be created.

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
