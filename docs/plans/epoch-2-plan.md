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
- [x] CI workflow template for GitHub Actions
- [x] Remediation documentation

**SHOULD (Epoch 2 Enhancements):**
- [x] Semantic cross-reference validation (TF-IDF keyword similarity)
- [x] NetworkX graph prototype (before Neo4j)
- [ ] Section rename tracking (`section-renames.yml`)
- [x] Pre-commit hook script
- [ ] Convention linting mode (`--lint` flag) — emoji, TOC, em-dash, CRLF, mojibake, backlog metadata checks

**COULD (Future Epoch 3+):**
- Neo4j graph database integration
- Cypher query library for navigation
- Web visualization (Neo4j Browser, pyvis)
- spaCy NER for advanced reference extraction
- Sentence transformer embeddings for deep semantic alignment

### Success Criteria

**Technical:**
- [x] Exclusion patterns reduce 6 → 0 actionable errors on DSM repo
- [x] CI workflow passes on clean core docs
- [x] Semantic validation detects renamed sections (TF-IDF)
- [x] Graph prototype enables navigation queries

**Process:**
- [x] Each sprint produces working increment
- [x] Feedback files updated at sprint boundaries
- [x] Blog material captured for Epoch 2 writeup
- [x] Experiments documented with results

**Deliverable:**
- [x] Production-ready CLI with exclusion and CI support
- [x] Remediation guide for DSM maintainers
- [x] Graph prototype demonstrating future potential

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

### Sprint 5: CI Integration & Remediation Docs ✅

**Duration:** 1 session
**Objective:** Provide ready-to-use CI workflow and documentation for fixing broken references.
**Status:** COMPLETE (2026-02-10)

#### Phase 5.1: GitHub Actions Workflow

**Tasks:**
1. [x] Create `.github/workflows/dsm-validate.yml`:
   - [x] Trigger on `**/*.md` changes (PR and push)
   - [x] Setup Python 3.12
   - [x] Install dsm-graph-explorer
   - [x] Run with `--strict --config`
2. [x] Create example config for DSM repository
3. [ ] Test workflow locally with `act` (optional)

#### Phase 5.2: Pre-commit Hook

**Tasks:**
1. [x] Create `scripts/pre-commit-hook.sh`
2. [x] Document pre-commit framework integration
3. [x] Add installation instructions to README

#### Phase 5.3: Documentation

**Tasks:**
1. [x] Create `docs/guides/remediation-guide.md`:
   - [x] Common error types and fixes
   - [x] How to use exclusions
   - [x] Best practices for cross-references
2. [x] Create `docs/guides/config-reference.md`:
   - [x] All config options documented
   - [x] Example configurations
3. [x] Update README with new features

#### Sprint 5 Deliverables

- [x] `.github/workflows/dsm-validate.yml`
- [x] Pre-commit hook script
- [x] `docs/guides/remediation-guide.md`
- [x] `docs/guides/config-reference.md`
- [x] Updated README

**Sprint boundary:**
- [x] Blog entry (CI integration story)
- [x] Checkpoint document

---

### Sprint 6: Semantic Validation (TF-IDF) ✅

**Duration:** 1-2 sessions (actual: 5 sessions)
**Objective:** Detect meaning drift when sections are rewritten but keep their numbers.
**Status:** COMPLETE (2026-02-23)
**Design source:** DSM Central inbox entry ([2026-02-10_dsm-central-tfidf-context-design.md](../inbox/done/2026-02-10_dsm-central-tfidf-context-design.md))

#### Design: Context Extraction Approach (Option B + C)

The original plan compared `CrossReference.context` (single line) vs `Section.title`.
DSM Central's structural analysis of 937 H2+H3 sections showed many titles are too
short or generic ("Expected Outcomes" x4, "Deliverables" x2) for reliable TF-IDF
matching. The revised approach enriches both sides:

- **Target side:** `Section.title` + `Section.context_excerpt` (first ~50 words of prose after heading)
- **Reference side:** `CrossReference.context` + `context_before` + `context_after` (3-line window)

Robustness measures:
- Strip section numbers (`\d+\.\d+`) before vectorization (no semantic value)
- Corpus-scoped IDF weighting (build vocabulary from all sections, not pairwise)
- Minimum token gate (~3 tokens after stopwords; below this, flag "insufficient context")

#### Phase 6.0: Experiment (Pre-implementation)

**Tasks:**
1. [x] Run EXP-003: TF-IDF Threshold Tuning
2. [x] Document results in decision document (DEC-005)
3. [x] Confirm approach before implementation

#### Phase 6.1: Parser Context Extraction

**Tasks:**
1. [x] Add `context_excerpt` field to `Section` dataclass (first ~50 words of prose)
2. [x] Implement prose extraction with fallback chain:
   - First: prose paragraph (skip headings, tables, code fences, lists)
   - Fallback: first list item text (strip `- ` prefix)
   - Last resort: title-only, flag lower confidence
3. [x] Add `context_before` / `context_after` fields to `CrossReference` dataclass
4. [x] Update parser to populate new fields during extraction
5. [x] Write tests for context extraction (prose, list, table-first, empty sections)

#### Phase 6.2: TF-IDF Implementation

**Tasks:**
1. [x] Add `scikit-learn>=1.3.0` to optional dependencies (`[semantic]`)
2. [x] Create `src/semantic/similarity.py`:
   - [x] `preprocess_text(text)` — strip section numbers, normalize
   - [x] `build_corpus_vectorizer(sections)` — fit TF-IDF on all section texts
   - [x] `compute_similarity(ref_text, target_text, vectorizer)` — cosine similarity
   - [x] Minimum token gate: skip comparison if <3 meaningful tokens
3. [x] Make excerpt word count a config parameter (default: 50)
4. [x] Write tests with synthetic examples (aligned, drifted, insufficient context)

#### Phase 6.3: Integration

**Tasks:**
1. [x] Add `--semantic` flag to CLI (opt-in)
2. [x] Update validator to compute similarity for each reference
3. [x] Add WARNING for low-similarity references (below threshold)
4. [x] Update reporter to show similarity scores
5. [x] Graceful fallback when scikit-learn not installed

#### Sprint 6 Deliverables

- [x] Parser context extraction (`Section.context_excerpt`, `CrossReference.context_before/after`)
- [x] TF-IDF similarity computation with corpus-scoped IDF
- [x] Configurable similarity threshold and excerpt word count
- [x] WARNING for low-similarity references
- [x] Tests with synthetic drift examples
- [x] Graceful degradation without scikit-learn

**Sprint boundary:**
- [x] Decision document (DEC-005: Semantic Validation Approach)
- [x] Checkpoint document
- [x] EXP-003 results documented

**Acceptance criteria:**
- [x] References to renamed sections flagged with low similarity
- [x] False positive rate <10% (0% in EXP-003b)
- [x] Performance acceptable for 100+ file repositories
- [x] Insufficient-context sections flagged rather than producing unreliable scores

---

### Sprint 7: Graph Prototype (NetworkX) ✅

**Duration:** 1 session (actual)
**Objective:** Build a graph representation of the reference network for analysis.
**Status:** COMPLETE (2026-02-25)

#### Phase 7.0: Experiment (Pre-implementation)

**Tasks:**
1. [x] Run EXP-004: Graph Query Performance
2. [x] Verify memory/performance targets achievable

#### Phase 7.1: Graph Construction

**Tasks:**
1. [x] Add `networkx>=3.2.0` to optional dependencies (`[graph]`)
2. [x] Create `src/graph/graph_builder.py`:
   - [x] `build_reference_graph(documents, references)` → DiGraph
   - [x] Node types: FILE, SECTION
   - [x] Edge types: CONTAINS, REFERENCES
   - [x] Node attributes: type, title, file, line, number, level, context_excerpt
3. [x] Write tests for graph construction

#### Phase 7.2: Graph Queries

**Tasks:**
1. [x] Create `src/graph/graph_queries.py`:
   - [x] `most_referenced_sections(G, n=10)`
   - [x] `orphan_sections(G)` — never referenced
   - [x] `reference_chain(G, section)` — what references this?
2. [x] Write tests for each query

#### Phase 7.3: Export & CLI

**Tasks:**
1. [x] Add `--graph-export PATH` CLI option
2. [x] Export to GraphML format
3. [x] Add `--graph-stats` flag for summary output
4. [x] Document visualization with Gephi/yEd

#### Sprint 7 Deliverables

- [x] NetworkX graph builder
- [x] Basic graph queries (most-referenced, orphans)
- [x] Export to GraphML for visualization
- [x] Graceful degradation without networkx

**Sprint boundary:**
- [x] Blog entry (graph visualization story)
- [x] Checkpoint document
- [x] EXP-004 results documented

**Acceptance criteria:**
- [x] Graph accurately represents DSM reference structure
- [x] Can identify most-referenced sections
- [x] Can identify unreferenced sections
- [x] Export works with Gephi

---

### Sprint 8: Convention Linting (`--lint`)

**Duration:** 1-2 sessions
**Objective:** Add convention linting mode that checks surface-level DSM style violations without running the cross-reference pipeline.
**Source:** DSM Central inbox entry ([2026-02-09_dsm-central-feedback-convention-linting.md](../inbox/done/2026-02-09_dsm-central-feedback-convention-linting.md))

#### Checks

| Rule | Severity | Description |
|------|----------|-------------|
| E001 | ERROR | Emoji/symbol usage (should be WARNING:/OK:/ERROR: text) |
| E002 | ERROR | TOC headings (DSM uses hierarchical numbering) |
| W001 | WARNING | Em-dash punctuation (use commas/semicolons) |
| W002 | WARNING | CRLF line endings (use Unix LF) |
| E003 | ERROR | Mojibake encoding (double-encoded UTF-8) |
| W003 | WARNING | Backlog metadata validation (required fields) |

#### Architecture

- New module: `src/linter/` with per-check submodules
- Reuse existing `collect_markdown_files()` and `filter_files()`
- New `LintResult` dataclass, `lint_reporter.py`
- Extend `.dsm-graph-explorer.yml` with `lint:` config section
- `--lint` flag runs independently from `--strict`

#### Sprint 8 Deliverables

- [ ] `src/linter/` module with 6 checks
- [ ] `--lint` CLI flag
- [ ] Config section for lint rule overrides
- [ ] Tests for each check
- [ ] README updated with lint mode

**Sprint boundary:**
- [ ] Checkpoint document
- [ ] Feedback files updated

**Full spec:** See source inbox entry for implementation order and architecture guidance.

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
- **Git ref parameter for temporal compilation:** accept a commit/tag to compile the graph at a historical point, enabling diff-based graph queries ("what changed between v1.3.0 and v1.3.25?"). Git as event store; compilation pipeline as projection function.
- **Entity inventory format:** each repo publishes an inventory of referenceable entities (sections, protocols, backlog items). Design the format now so multi-repo extension is additive. DSM's existing cross-repo mechanisms (inbox, @ imports, Ecosystem Path Registry) map to typed cross-repo edges.
- **Typed cross-repo edges:** formalize inbox notifications, @ imports, and ecosystem path references as edge types in the graph.

### Advanced NLP (Epoch 4)

- spaCy NER for entity extraction (tool names, section titles in prose)
- Sentence transformer embeddings for deep semantic alignment
- Lightweight LLM second-pass: confirm TF-IDF-flagged references via contextual reasoning (tiered: TF-IDF filters, LLM confirms)
- Reference: [tfidf-to-transformers-with-disaster-tweets](https://github.com/albertodiazdurana/tfidf-to-transformers-with-disaster-tweets)
- **Bi-temporal model:** adopt event time (when authored) vs transaction time (when compiled) for temporal queries. Reference: Graphiti's bi-temporal approach, adapted for human-authored markdown.
- **Graphiti differentiation:** Graph Explorer is human-centric (deterministic compilation from authored markdown with git provenance), not agent-centric (LLM extraction from conversation). This positioning informs architecture choices.

**Source:** Literate CQRS Knowledge Architecture research (5 threads, 25+ sources). Full research at `~/dsm-agentic-ai-data-science-methodology/docs/research/Literate-CQRS-Knowledge/`. Acknowledged in Session 18 from DSM Central inbox.

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
│   ├── guides/
│   │   ├── remediation-guide.md   # NEW (Sprint 5)
│   │   └── config-reference.md    # NEW (Sprint 5)
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

**Plan Status:** Sprint 7 complete, ready for Sprint 8
**Last Updated:** 2026-02-28
**Previous:** [epoch-1-plan.md](epoch-1-plan.md)
**Research:** [e2_handoff_graph_explorer_research.md](../research/e2_handoff_graph_explorer_research.md)
