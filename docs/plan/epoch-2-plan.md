# DSM Graph Explorer - Epoch 2 Plan

**Project Type:** Software Engineering (DSM 4.0 Track)
**Start Date:** 2026-02-04
**Status:** IN PROGRESS
**Prerequisite:** Epoch 1 Complete ([epoch-1-plan.md](epoch-1-plan.md))
**Project Lead:** Alberto Diaz Durana (with AI assistance)

---

## Epoch 2 Overview

### Context

Epoch 1 delivered a working CLI validator that found 448 broken cross-references in the DSM repository. After fixing a parser bug (trailing periods), this reduced to 6 genuine errors. Epoch 2 focuses on:

1. **Productionization** — Exclusion patterns, severity levels, CI integration
2. **Semantic validation** — TF-IDF similarity for detecting meaning drift
3. **Graph exploration** — NetworkX prototype for navigating reference networks

### Scope (MoSCoW)

**MUST (Epoch 2 Core):**
- [x] File exclusion patterns (`--exclude` flag)
- [x] YAML configuration file (`.dsm-graph-explorer.yml`)
- [x] Severity levels by file pattern (ERROR/WARNING/INFO)
- [x] `--strict` respects severity (only fails on ERROR)
- [ ] CI workflow template for GitHub Actions
- [ ] Remediation documentation

**SHOULD (Epoch 2 Enhancements):**
- [ ] Semantic cross-reference validation (TF-IDF keyword similarity)
- [ ] NetworkX graph prototype (before Neo4j)
- [ ] Section rename tracking (`section-renames.yml`)
- [ ] Pre-commit hook script

**COULD (Future Epoch 3+):**
- Neo4j graph database integration
- Cypher query library for navigation
- Web visualization (Neo4j Browser, pyvis)
- spaCy NER for advanced reference extraction
- Sentence transformer embeddings for deep semantic alignment

### Success Criteria

**Technical:**
- [x] Exclusion patterns reduce 6 → 0 actionable errors on DSM repo
- [ ] CI workflow passes on clean core docs
- [ ] Semantic validation detects renamed sections (TF-IDF)
- [ ] Graph prototype enables navigation queries

**Process:**
- [x] Each sprint produces working increment
- [x] Feedback files updated at sprint boundaries
- [x] Blog material captured for Epoch 2 writeup
- [x] Experiments documented with results

**Deliverable:**
- [ ] Production-ready CLI with exclusion and CI support
- [ ] Remediation guide for DSM maintainers
- [ ] Graph prototype demonstrating future potential

---

## Experiment Definitions

### EXP-001: Exclusion Pattern Validation

**Sprint:** 4 (early)
**Goal:** Verify exclusion logic correctly filters files.

**Test matrix:**
| Pattern | Input Files | Expected Excluded |
|---------|-------------|-------------------|
| `CHANGELOG.md` | `CHANGELOG.md`, `docs/CHANGELOG.md` | Only `CHANGELOG.md` |
| `plan/*` | `plan/foo.md`, `plan/bar/baz.md` | `plan/foo.md` only |
| `**/archive/*` | `archive/x.md`, `docs/archive/y.md` | Both |
| Multiple | All above combined | Union of all |

**Acceptance:** All cases pass in pytest.

### EXP-002: Severity Classification

**Sprint:** 4 (mid)
**Goal:** Validate severity assignment by pattern.

**Test matrix:**
| File | Config Pattern | Expected Severity |
|------|----------------|-------------------|
| `DSM_1.0.md` | `DSM_*.md: ERROR` | ERROR |
| `plan/draft.md` | `plan/*: INFO` | INFO |
| `docs/guide.md` | (no match, default) | WARNING |
| `plan/DSM_draft.md` | Both patterns match | Most specific wins |

**Acceptance:** Severity enum correctly assigned.

### EXP-003: TF-IDF Threshold Tuning

**Sprint:** 6 (pre-implementation)
**Goal:** Find optimal similarity threshold for semantic drift.

**Test cases:**
1. True match: "Section 2.3.7 data leakage" ↔ "Data Leakage Prevention" → Expected >0.6
2. Semantic drift: "Section 2.3.7 data leakage" ↔ "Reproducibility Practices" → Expected <0.3
3. Unrelated: "Section 2.3.7 data leakage" ↔ "Appendix Contents" → Expected <0.1

**Approach:**
1. Create 20 synthetic test cases (10 true, 10 drift)
2. Test thresholds: 0.2, 0.3, 0.4, 0.5
3. Measure precision/recall at each threshold
4. Select threshold with best F1 score

**Deliverable:** Decision document (DEC-005) with chosen threshold.

### EXP-004: Graph Query Performance

**Sprint:** 7 (early)
**Goal:** Verify graph queries work efficiently on DSM-sized repos.

**Metrics to measure:**
| Operation | Target | Actual |
|-----------|--------|--------|
| Build graph (30 files, 500 sections) | <5s | |
| Most-referenced query | <100ms | |
| Orphan sections query | <100ms | |
| GraphML export | <2s | |
| Memory usage | <100MB | |

**Acceptance:** All metrics met on DSM repository.

---

## Sprint Structure

### Sprint 4: Exclusion & Severity ✅

**Duration:** 1-2 sessions
**Objective:** Implement file exclusion and severity classification to focus validation on actionable errors.
**Status:** COMPLETE (2026-02-06)

#### Phase 4.1: Config Infrastructure

**Tasks:**
1. [x] Add `pydantic>=2.0` and `pyyaml>=6.0` to dependencies
2. [x] Create `src/config/config_loader.py`:
   - [x] `Config` Pydantic model (exclude, severity, strict)
   - [x] `SeverityMapping` model (pattern, level)
   - [x] `load_config()` function (YAML → Config)
   - [x] Config file discovery (`.dsm-graph-explorer.yml`)
3. [x] Write `tests/test_config.py`:
   - [x] Valid config parsing
   - [x] Missing file (returns defaults)
   - [x] Invalid YAML (clear error)
   - [x] Invalid patterns (validation error)

**Tests:** EXP-001 pattern tests PASSED

#### Phase 4.2: Exclusion Logic

**Tasks:**
1. [x] Update `src/cli.py`:
   - [x] Add `--exclude` option (`multiple=True`)
   - [x] Add `--config` option for config file path
   - [x] Merge CLI options with config file (CLI wins)
2. [x] Create `src/filter/file_filter.py`:
   - [x] `should_exclude(filepath, patterns)` using fnmatch
   - [x] Handle relative paths correctly
3. [x] Update `collect_markdown_files()` to apply exclusions
4. [x] Write tests for exclusion logic

**Validation:** DSM repo with exclusions reduces to actionable errors only.

#### Phase 4.3: Severity Levels

**Tasks:**
1. [x] Update `src/validator/cross_ref_validator.py`:
   - [x] `Severity` enum already exists (ERROR, WARNING)
   - [x] Add INFO level
   - [x] `assign_severity(filepath, mappings)` function
2. [x] Update `--strict` to only fail on ERROR
3. [x] Update reporter to group by severity
4. [x] Write tests for severity assignment

**Tests:** EXP-002 severity tests PASSED

#### Sprint 4 Deliverables

- [x] `--exclude` CLI flag working
- [x] `.dsm-graph-explorer.yml` config file support
- [x] Severity levels (ERROR/WARNING/INFO)
- [x] `--strict` respects severity
- [x] 73 new tests for config, exclusion, and severity (218 total)

**Sprint boundary:**
- [x] DSM feedback update (methodology.md Entry 17)
- [ ] Decision document (DEC-005: Exclusion and Severity Design)
- [x] Checkpoint document (2026-02-06_sprint4-complete)
- [x] Blog journal entry
- [x] README updated

---

### Sprint 5: CI Integration & Remediation Docs

**Duration:** 1 session
**Objective:** Provide ready-to-use CI workflow and documentation for fixing broken references.

#### Phase 5.1: GitHub Actions Workflow

**Tasks:**
1. [ ] Create `.github/workflows/dsm-validate.yml`:
   - [ ] Trigger on `**/*.md` changes (PR and push)
   - [ ] Setup Python 3.12
   - [ ] Install dsm-graph-explorer
   - [ ] Run with `--strict --config`
2. [ ] Create example config for DSM repository
3. [ ] Test workflow locally with `act` (optional)

#### Phase 5.2: Pre-commit Hook

**Tasks:**
1. [ ] Create `scripts/pre-commit-hook.sh`
2. [ ] Document pre-commit framework integration
3. [ ] Add installation instructions to README

#### Phase 5.3: Documentation

**Tasks:**
1. [ ] Create `docs/remediation-guide.md`:
   - [ ] Common error types and fixes
   - [ ] How to use exclusions
   - [ ] Best practices for cross-references
2. [ ] Create `docs/config-reference.md`:
   - [ ] All config options documented
   - [ ] Example configurations
3. [ ] Update README with new features

#### Sprint 5 Deliverables

- [ ] `.github/workflows/dsm-validate.yml`
- [ ] Pre-commit hook script
- [ ] `docs/remediation-guide.md`
- [ ] `docs/config-reference.md`
- [ ] Updated README

**Sprint boundary:**
- [ ] Blog entry (CI integration story)
- [ ] Checkpoint document

---

### Sprint 6: Semantic Validation (TF-IDF)

**Duration:** 1-2 sessions
**Objective:** Detect meaning drift when sections are rewritten but keep their numbers.

#### Phase 6.0: Experiment (Pre-implementation)

**Tasks:**
1. [ ] Run EXP-003: TF-IDF Threshold Tuning
2. [ ] Document results in decision document
3. [ ] Confirm approach before implementation

#### Phase 6.1: TF-IDF Implementation

**Tasks:**
1. [ ] Add `scikit-learn>=1.3.0` to optional dependencies (`[semantic]`)
2. [ ] Create `src/semantic/similarity.py`:
   - [ ] `compute_similarity(text1, text2)` using TfidfVectorizer
   - [ ] `extract_context(reference, document)` — 1-2 sentences around ref
   - [ ] `get_section_text(section)` — title + first paragraph
3. [ ] Write tests with synthetic examples

#### Phase 6.2: Integration

**Tasks:**
1. [ ] Add `--semantic` flag to CLI (opt-in)
2. [ ] Update validator to compute similarity for each reference
3. [ ] Add WARNING for low-similarity references (below threshold)
4. [ ] Update reporter to show similarity scores
5. [ ] Graceful fallback when scikit-learn not installed

#### Sprint 6 Deliverables

- [ ] TF-IDF similarity computation
- [ ] Configurable similarity threshold
- [ ] WARNING for low-similarity references
- [ ] Tests with synthetic drift examples
- [ ] Graceful degradation without scikit-learn

**Sprint boundary:**
- [ ] Decision document (DEC-005: Semantic Validation Approach)
- [ ] Checkpoint document
- [ ] EXP-003 results documented

**Acceptance criteria:**
- [ ] References to renamed sections flagged with low similarity
- [ ] False positive rate <10%
- [ ] Performance acceptable for 100+ file repositories

---

### Sprint 7: Graph Prototype (NetworkX)

**Duration:** 1-2 sessions
**Objective:** Build a graph representation of the reference network for analysis.

#### Phase 7.0: Experiment (Pre-implementation)

**Tasks:**
1. [ ] Run EXP-004: Graph Query Performance
2. [ ] Verify memory/performance targets achievable

#### Phase 7.1: Graph Construction

**Tasks:**
1. [ ] Add `networkx>=3.2.0` to optional dependencies (`[graph]`)
2. [ ] Create `src/graph/graph_builder.py`:
   - [ ] `build_reference_graph(documents, references)` → DiGraph
   - [ ] Node types: FILE, SECTION
   - [ ] Edge types: CONTAINS, REFERENCES
   - [ ] Node attributes: type, title, file, line
3. [ ] Write tests for graph construction

#### Phase 7.2: Graph Queries

**Tasks:**
1. [ ] Create `src/graph/graph_queries.py`:
   - [ ] `most_referenced_sections(G, n=10)`
   - [ ] `orphan_sections(G)` — never referenced
   - [ ] `reference_chain(G, section)` — what references this?
2. [ ] Write tests for each query

#### Phase 7.3: Export & CLI

**Tasks:**
1. [ ] Add `--graph-export PATH` CLI option
2. [ ] Export to GraphML format
3. [ ] Add `--graph-stats` flag for summary output
4. [ ] Document visualization with Gephi/yEd

#### Sprint 7 Deliverables

- [ ] NetworkX graph builder
- [ ] Basic graph queries (most-referenced, orphans)
- [ ] Export to GraphML for visualization
- [ ] Graceful degradation without networkx

**Sprint boundary:**
- [ ] Blog entry (graph visualization story)
- [ ] Checkpoint document
- [ ] EXP-004 results documented

**Acceptance criteria:**
- [ ] Graph accurately represents DSM reference structure
- [ ] Can identify most-referenced sections
- [ ] Can identify unreferenced sections
- [ ] Export works with Gephi

---

## Dependencies

### Updated pyproject.toml

```toml
[project]
name = "dsm-graph-explorer"
version = "0.2.0"  # Bump for Epoch 2

dependencies = [
    "click>=8.1.0",      # CLI framework
    "rich>=13.7.0",      # Terminal formatting
    "pydantic>=2.0",     # Config validation (NEW)
    "pyyaml>=6.0",       # YAML parsing (NEW)
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
semantic = [
    "scikit-learn>=1.3.0",  # TF-IDF (Sprint 6)
]
graph = [
    "networkx>=3.2.0",      # Graph analysis (Sprint 7)
]
all = [
    "scikit-learn>=1.3.0",
    "networkx>=3.2.0",
]
```

---

## Validated Exclusion List (from DSM Central)

Based on real-world validation against DSM repository:

```yaml
# .dsm-graph-explorer.yml
exclude:
  - CHANGELOG.md           # Historical drift (valid when written)
  - docs/checkpoints/*     # Milestone snapshots
  - references/*           # Archive folder
  - plan/*                 # Planning docs with proposals
  - plan/archive/*         # Archived backlog items

severity:
  - pattern: "DSM_*.md"
    level: ERROR
  - pattern: "docs/checkpoints/*"
    level: INFO
  - pattern: "plan/*"
    level: INFO
  - pattern: "*.md"
    level: WARNING  # default
```

**Result with exclusions:** 0 errors in active DSM documentation.

---

## Future Epochs (Deferred)

### Neo4j Integration (Epoch 3)

- Import NetworkX graph into Neo4j
- Cypher query library for navigation
- Web visualization using Neo4j Browser
- Relationship mapping (REFERENCES, CONTAINS, PARENT_OF)

### Advanced NLP (Epoch 4)

- spaCy NER for entity extraction (tool names, section titles in prose)
- Sentence transformer embeddings for deep semantic alignment
- Reference: [tfidf-to-transformers-with-disaster-tweets](https://github.com/albertodiazdurana/tfidf-to-transformers-with-disaster-tweets)

---

## Project Structure (Epoch 2 Additions)

```
dsm-graph-explorer/
├── src/
│   ├── config/                    # NEW
│   │   ├── __init__.py
│   │   └── config_loader.py       # Pydantic config
│   ├── filter/                    # NEW
│   │   ├── __init__.py
│   │   └── file_filter.py         # Exclusion logic
│   ├── semantic/                  # NEW (Sprint 6)
│   │   ├── __init__.py
│   │   └── similarity.py          # TF-IDF
│   ├── graph/                     # NEW (Sprint 7)
│   │   ├── __init__.py
│   │   ├── graph_builder.py
│   │   └── graph_queries.py
│   ├── parser/
│   ├── validator/
│   ├── reporter/
│   └── cli.py
├── tests/
│   ├── test_config.py             # NEW
│   ├── test_filter.py             # NEW
│   ├── test_semantic.py           # NEW (Sprint 6)
│   ├── test_graph.py              # NEW (Sprint 7)
│   └── fixtures/
│       └── sample_config.yml      # NEW
├── docs/
│   ├── remediation-guide.md       # NEW (Sprint 5)
│   ├── config-reference.md        # NEW (Sprint 5)
│   └── research/
│       └── e2_handoff_graph_explorer_research.md  # NEW
├── .github/
│   └── workflows/
│       └── dsm-validate.yml       # NEW (Sprint 5)
└── scripts/
    └── pre-commit-hook.sh         # NEW (Sprint 5)
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Pydantic learning curve** | Low | Low | Well-documented, widespread adoption |
| **TF-IDF false positives** | Medium | Medium | Tunable threshold, opt-in feature |
| **Config complexity** | Medium | Low | Good defaults, clear documentation |
| **NetworkX memory for large repos** | Low | Low | Lazy loading, tested in EXP-004 |
| **fnmatch edge cases** | Low | Low | Comprehensive test coverage (EXP-001) |
| **Scope creep to Neo4j** | Medium | Medium | Strict epoch boundaries, defer explicitly |

---

## Document Health Recommendations

### For DSM Repository Maintainers

Based on Epoch 1 findings, recommendations for maintaining healthy documentation:

1. **Establish validation baseline**
   - Run validator with exclusions to get actionable error count
   - Set target: zero errors in core documentation

2. **Integrate into workflow**
   - Add pre-commit hook for authors
   - Add CI check for PRs touching documentation
   - Review validation report at each release

3. **Handle section renumbering**
   - Search for references to old numbers before renaming
   - Update or deprecate old references
   - Consider maintaining rename history for tooling

4. **Archive strategy**
   - Move deprecated documents to `archive/` folder
   - Exclude archive from strict validation
   - Document that archive references are frozen

5. **Reference style guide**
   - Prefer stable identifiers (section titles) over numbers where possible
   - Use consistent patterns (`Section X.Y.Z` not `see X.Y.Z`)
   - Add context to references ("Section 2.4 (Human Baseline)")

---

## Blog Integration

### Epoch 2 Blog Topics

1. **Sprint 4-5:** "From Prototype to Production: Adding CI to a Documentation Validator"
   - Exclusion patterns and config files
   - GitHub Actions integration
   - The 448→6→0 error journey

2. **Sprint 6:** "Detecting Semantic Drift in Documentation with TF-IDF"
   - Why structural validation isn't enough
   - TF-IDF threshold tuning experiment
   - Real examples of caught drift

3. **Sprint 7:** "Visualizing Documentation as a Graph"
   - NetworkX for reference networks
   - Finding orphan sections
   - GraphML export to Gephi

### Materials Location

- `docs/blog/epoch-2/materials.md` — Observations during sprints
- `docs/blog/epoch-2/journal.md` — Sprint-by-sprint notes

---

## DSM Feedback Plan

### Active Backlog Items (from docs/backlog/)

| # | Action | Priority | Sprint | Status |
|---|--------|----------|--------|--------|
| 1 | Implement `--exclude` flag | High | Sprint 4 | Pending |
| 2 | Add default exclusion config | Medium | Sprint 4 | Pending |
| 3 | Update epoch-2-plan.md with validated exclusion list | Medium | Sprint 4 | DONE |
| 4 | Add fixture validation lesson to blog journal | Low | Sprint 4 | Pending |

### Feedback Files

Updated at every sprint boundary:
- `docs/feedback/backlogs.md` — DSM gaps and improvements
- `docs/feedback/methodology.md` — DSM section effectiveness (1-5)
- `docs/feedback/blog.md` — Blog process effectiveness

---

**Plan Status:** Sprint 4 complete, ready for Sprint 5
**Last Updated:** 2026-02-06
**Previous:** [epoch-1-plan.md](epoch-1-plan.md)
**Research:** [e2_handoff_graph_explorer_research.md](../research/e2_handoff_graph_explorer_research.md)
