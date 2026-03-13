# DSM Graph Explorer - Epoch 3 Plan

**Project Type:** Software Engineering (DSM 4.0 Track)
**Start Date:** 2026-03-10
**Status:** ACTIVE
**Prerequisite:** Epoch 2 Complete ([epoch-2-plan.md](epoch-2-plan.md))
**Project Lead:** Alberto Diaz Durana (with AI assistance)

---

## Epoch 3 Overview

### Context

Epoch 2 delivered a production-ready CLI validator with semantic validation (TF-IDF),
a NetworkX graph prototype, and convention linting. The graph prototype demonstrated that
reference networks can be queried efficiently (104ms build, well within performance targets).

Epoch 3 elevates the graph from an in-memory prototype to a persistent, queryable database.
The primary driver is twofold:

1. **Persistence**: graph data survives CLI restarts; incremental updates replace full rebuilds
2. **Multi-repo support (BL-156)**: DSM Central requires cross-repo comparison, modeling both
   private and public DSM repositories as separate graphs with node matching and drift detection

The graph database selection was decided in DEC-006 (FalkorDBLite). The Python version
upgrade to enable it was decided in DEC-007.

### Key Decisions Entering Epoch 3

| Decision | Record | Summary |
|----------|--------|---------|
| Graph database | DEC-006 | FalkorDBLite: embedded, Cypher-compatible, zero-config |
| Python version | DEC-007 | Upgrade to 3.12+ (FalkorDBLite requirement) |
| Graph architecture | DEC-006 | NetworkX as compilation layer, FalkorDBLite as persistence layer |
| Multi-repo approach | DEC-006 | Separate graph per repo; bridge graph for cross-repo edges |

### Scope (MoSCoW)

**MUST (Epoch 3 Core):**
- [x] Python 3.12 upgrade and zero test regressions (Sprint 9)
- [x] FalkorDBLite integration: persistent graph store (Sprint 9)
- [x] EXP-005: validate FalkorDBLite with existing graph data (Sprint 9)
- [x] Git-ref temporal compilation: `--git-ref` flag (Sprint 10)
- [x] Entity inventory format: per-repo referenceable entity manifest (Sprint 11)
- [x] Cross-repo edges: typed edges for inbox, @-imports, ecosystem paths (Sprint 12)
- [x] BL-156: private-to-public repo mapping with drift detection (Sprint 12)

**SHOULD (Epoch 3 Enhancements):**
- [ ] Incremental graph updates (avoid full rebuild on unchanged files)
- [x] Temporal diff query: "what changed between two git refs?" (Sprint 10)
- [ ] Index creation for `path` and `heading` properties (query performance)
- [ ] `--graph-export` updated to export from FalkorDB (not just NetworkX)

**COULD (Future Epoch 4+):**
- [ ] Section rename tracking (`section-renames.yml`, deferred from Epoch 2 SHOULD)
- [ ] LLM second-pass (TF-IDF filters, LLM confirms), Epoch 4 roadmap item
- [ ] spaCy NER for entity extraction
- [ ] Sentence transformer embeddings (bi-temporal model)
- [ ] Web visualization (Neo4j Browser if migrated, or pyvis)

### Success Criteria

**Technical:**
- [x] FalkorDBLite stores and persists the existing NetworkX graph (EXP-005)
- [x] Graph survives CLI restarts (data persists on disk)
- [x] `--git-ref` produces a correct historical snapshot of the graph
- [x] Entity inventory format is machine-readable and human-editable
- [x] Cross-repo node matching works via entity inventory lookup
- [x] BL-156: private DSM and public DSM can be modeled as separate graphs with cross-repo edges

**Process:**
- [x] Each sprint produces a working increment
- [x] Feedback files updated at sprint boundaries
- [x] Blog material captured for Epoch 3 writeup
- [x] Experiments documented with results

**Deliverable:**
- [x] Persistent graph CLI with `--graph-db PATH --git-ref REF`
- [x] Entity inventory spec and parser
- [x] Cross-repo mapping support for DSM Central (BL-156)

---

## Experiment Definitions

### EXP-005: FalkorDBLite Integration Validation

**Sprint:** 9 (pre-implementation gate)
**Goal:** Confirm FalkorDBLite can store, persist, and query the existing NetworkX graph
before building the full integration layer.

**Test matrix:**

| Operation | Target | Actual |
|-----------|--------|--------|
| Install falkordblite on Python 3.12 | No errors | |
| Import from `redislite.falkordb_client` | Success | |
| Create graph with DSM document nodes | <2s | |
| Persist and reload (process restart simulation) | All nodes present | |
| Multi-graph: two repos coexist | Correct isolation | |
| Parameterized Cypher query | Correct results | |
| `MATCH (d:Document)-[:CONTAINS]->(s:Section)` | Correct traversal | |

**Acceptance:** All operations succeed. If persistence fails, escalate before Sprint 9
integration work begins.

**Data source:** EXP-004 NetworkX graph (30 files, ~500 sections from DSM repository).

### EXP-006: Git-Ref Temporal Accuracy

**Sprint:** 10 (pre-implementation gate)
**Goal:** Verify that compiling the graph at a historical git ref produces an accurate
snapshot distinct from the current HEAD.

**Test matrix:**

| Scenario | Expected |
|----------|----------|
| `--git-ref HEAD` | Matches current graph |
| `--git-ref <tag>` | Documents/sections as of that tag |
| `--git-ref <SHA>` | Deterministic: same SHA, same graph |
| Added file since ref | Not present in historical graph |
| Deleted file since ref | Present in historical graph |
| Diff (HEAD vs old tag) | Correct added/removed/changed nodes |

**Acceptance:** Historical graph matches expected document state at the given ref.
Performance: historical compilation completes within 2x normal compilation time.

---

## Sprint Structure

### Sprint 9: Foundation (Python 3.12 + FalkorDBLite Integration)

**Duration:** 1-2 sessions (actual: 2 sessions)
**Objective:** Upgrade Python, validate FalkorDBLite, and build the persistence layer.
**Status:** COMPLETE

#### Phase 9.0: Python 3.12 Upgrade (DEC-007)

**Tasks:**
1. [x] Update `pyproject.toml`:
   - [x] `requires-python = ">=3.12"`
   - [x] Drop Python 3.10/3.11 classifiers
   - [x] Add `falkordblite>=0.9` to `[graph]` optional extra
   - [x] Update `[tool.black] target-version = ['py312']`
   - [x] Update `[tool.ruff] target-version = "py312"`
   - [x] Version bump: `0.2.0 → 0.3.0`
2. [x] Run `pytest tests/` and confirm 331 tests pass, 96% coverage maintained
3. [x] Commit: "Sprint 9: Python 3.12 upgrade (DEC-007)"

**Gate:** Zero test regressions before proceeding to EXP-005. ✓ Passed

#### Phase 9.1: EXP-005 (Integration Validation Experiment)

**Tasks:**
1. [x] Install `falkordblite` in dev environment
2. [x] Run EXP-005 test matrix (see above) as an exploratory script in `data/experiments/`
3. [x] Document results in `data/experiments/EXP-005-falkordb-integration/`
4. [x] If any test fails: resolve before Phase 9.2 (escalate to DEC-006 or DEC-007 revision if needed)

**Gate:** All EXP-005 acceptance criteria met before building `graph_store.py`. ✓ 16/16 passed

#### Phase 9.2: Graph Store Module

**Tasks:**
1. [x] Create `src/graph/graph_store.py`:
   - [x] `GraphStore` class wrapping FalkorDBLite connection
   - [x] `open(path)` / `close()` lifecycle management
   - [x] `write_graph(networkx_graph, repo_name, git_ref)`: imports NetworkX DiGraph into FalkorDB
   - [x] `query(cypher, params)` and `ro_query(cypher, params)`: thin wrappers
   - [x] `graph_exists(repo_name)`: check before rebuilding
   - [x] Parameterized queries throughout (no string interpolation)
2. [x] Create Cypher schema: indexes on `path` (Document), `heading` (Section)
3. [x] Write `tests/test_graph_store.py`:
   - [x] Session-scoped FalkorDBLite fixture (`tmp_path_factory`)
   - [x] Per-test graph isolation (unique graph names via UUID)
   - [x] `g.delete()` cleanup in fixture teardown
   - [x] Tests: write, query, persist simulation, multi-graph isolation (18 tests)

#### Phase 9.3: CLI Integration

**Tasks:**
1. [x] Add `--graph-db PATH` option to CLI (path to FalkorDB storage file)
2. [x] When `--graph-db` is provided: after graph build, persist via `GraphStore`
3. [x] If graph already exists at path: skip rebuild (use cached), unless `--rebuild` flag
4. [x] Graceful error if `falkordblite` not installed (same pattern as networkx/scikit-learn)
5. [x] Update `--graph-stats` to query FalkorDB when `--graph-db` is set
6. [x] Write CLI integration tests (6 tests)

#### Sprint 9 Deliverables

- [x] Python 3.12 minimum, all tests green
- [x] `falkordblite` in `[graph]` optional extra
- [x] `src/graph/graph_store.py` with full test coverage
- [x] `--graph-db PATH` CLI option
- [x] EXP-005 results documented
- [x] Version 0.3.0

**Sprint boundary checklist:**
- [x] Checkpoint document (`docs/checkpoints/`)
- [x] Feedback files updated (`docs/feedback/`)
- [x] Blog journal entry
- [x] README updated

---

### Sprint 10: Git-Ref Temporal Compilation

**Duration:** 1-2 sessions (actual: 2 sessions)
**Objective:** Accept a git ref parameter and compile the graph at a historical point,
enabling temporal queries and diff-based analysis.
**Status:** COMPLETE

#### Design

Git is treated as the event store. The compilation pipeline is the projection function.
Given a git ref (commit SHA, tag, branch), the tool checks out the tree at that ref,
builds the graph, and stores it with `git_ref` as a property on all Document nodes.

This enables queries like:
```cypher
MATCH (d:Document {git_ref: 'v1.3.0'}) RETURN d.path
MATCH (d:Document {git_ref: 'HEAD'}) RETURN d.path
```

And diffs between two stored snapshots.

#### Phase 10.0: EXP-006 (Temporal Accuracy Experiment)

**Tasks:**
1. [x] Identify two historical refs in DSM repository (a tag and an older commit)
2. [x] Run EXP-006 test matrix manually before building the feature
3. [x] Document results in `data/experiments/EXP-006-git-ref-temporal/`

**Gate:** Confirm historical snapshot approach is feasible before full implementation. ✓ 19/19 passed

#### Phase 10.1: Git-Ref Compilation

**Tasks:**
1. [x] Add `--git-ref REF` CLI option (commit SHA, tag, or branch name)
2. [x] Create `src/git_ref/git_resolver.py`:
   - [x] `resolve_ref(repo_path, ref)` → validated commit SHA
   - [x] `list_files_at_ref(repo_path, sha)` → list of markdown files at that ref
   - [x] `read_file_at_ref(repo_path, sha, filepath)` → file contents as string
   - [x] Uses `subprocess` (git show, git ls-tree) rather than gitpython dependency
   - [x] Added `find_repo_root()` for subdirectory-safe resolution
   - [x] Content-based parser variants for in-memory parsing
3. [x] Update compilation pipeline: when `--git-ref` is set, feed historical file contents
   to the parser instead of current disk state
4. [x] Store `git_ref` as a property on Document nodes in FalkorDB
5. [x] Write tests for git resolver (28 tests)

#### Phase 10.2: Temporal Diff

**Tasks:**
1. [x] Create `src/graph/graph_diff.py`:
   - [x] `diff_graphs(base_path, ref_a, ref_b)` → DiffResult
   - [x] `DiffResult`: added nodes, removed nodes, changed nodes (property changes)
2. [x] Add `--graph-diff REF_A REF_B` CLI option
3. [x] Reporter: show diff as a Rich table (added/removed/changed)
4. [x] Write tests for diff logic (12 tests)

#### Sprint 10 Deliverables

- [x] `--git-ref REF` CLI option with historical compilation
- [x] `src/git_ref/git_resolver.py` (subprocess-based, no gitpython)
- [x] `git_ref` property on Document nodes
- [x] `--graph-diff REF_A REF_B` CLI option
- [x] EXP-006 results documented
- [x] CLI version updated 0.2.0 → 0.3.0

**Sprint boundary checklist:**
- [x] Checkpoint document
- [x] Feedback files updated
- [x] Blog journal entry
- [x] README updated

---

### Sprint 11: Entity Inventory

**Duration:** 1 session (actual: 1 session)
**Objective:** Define and implement an entity inventory format so each repository can
publish a machine-readable manifest of its referenceable entities, enabling cross-repo
reference resolution.
**Status:** COMPLETE

#### Design

Each DSM repository publishes a `dsm-entity-inventory.yml` at its root. The inventory
lists sections, documents, protocols, and backlog items by stable identifier. The format
is designed to be additive: multi-repo extension in Sprint 12 does not require changing
the per-repo format.

DSM's existing cross-repo mechanisms (inbox notifications, @-imports, Ecosystem Path
Registry entries) map to typed cross-repo edges in Sprint 12.

#### Inventory Format (Draft)

```yaml
# dsm-entity-inventory.yml
version: "1.0"
repo:
  name: dsm-agentic-ai-data-science-methodology
  type: dsm-hub          # dsm-hub | dsm-spoke | external
  url: https://github.com/...  # optional

entities:
  - id: "DSM_1.0/section/2.3.7"
    type: section
    path: DSM_1.0_Data_Science_Collaboration_Methodology_v1.1.md
    heading: "2.3.7 Data Leakage Prevention"
    level: 3
    stable: true         # not expected to change

  - id: "DSM_2.0/protocol/sprint-boundary-checklist"
    type: protocol
    path: DSM_2.0_ProjectManagement_Guidelines.md
    heading: "Sprint Boundary Checklist"
    stable: true

  - id: "backlog/BL-156"
    type: backlog-item
    path: plan/backlog.md
    heading: "BL-156: Private-to-public repository mapping"
    stable: false        # may be resolved and removed
```

#### Phase 11.1: Inventory Spec and Parser

**Tasks:**
1. [x] Define final `dsm-entity-inventory.yml` schema (Pydantic model)
2. [x] Create `src/inventory/inventory_parser.py`:
   - [x] `EntityInventory` Pydantic model
   - [x] `Entity` model: id, type, path, heading, level, stable
   - [x] `load_inventory(path)` → EntityInventory
   - [x] `discover_inventory(repo_path)` → optional path to inventory file
3. [x] Write `tests/test_inventory.py` with fixture inventory files

#### Phase 11.2: Cross-Repo Reference Resolution

**Tasks:**
1. [x] Update `src/validator/cross_ref_validator.py`:
   - [x] Accept optional list of `EntityInventory` objects (external repos)
   - [x] When a reference cannot be resolved locally, check external inventories
   - [x] Flag: EXTERNAL (resolved via inventory) vs UNKNOWN (unresolved)
2. [x] Add `--inventory PATH` CLI option to load an external repo's inventory
3. [x] Update reporter to show EXTERNAL references distinctly

#### Phase 11.3: Inventory Export

**Tasks:**
1. [x] Add `--export-inventory PATH` CLI option:
   - [x] Scan current repo and generate a `dsm-entity-inventory.yml`
   - [x] Include all sections, protocols (heuristic: headings matching known patterns)
2. [x] Write tests for inventory export

#### Sprint 11 Deliverables

- [x] `dsm-entity-inventory.yml` spec (Pydantic model)
- [x] `src/inventory/inventory_parser.py`
- [x] `--inventory PATH` CLI option for cross-repo resolution
- [x] `--export-inventory PATH` for inventory generation
- [x] EXTERNAL reference classification in reporter

**Sprint boundary checklist:**
- [x] Checkpoint document
- [x] Feedback files updated
- [x] Blog journal entry
- [x] README updated

---

### Sprint 12: Cross-Repo Edges + BL-156

**Duration:** 1 session (actual: 1 session)
**Objective:** Build cross-repo graph support with typed edges for existing DSM
cross-repo mechanisms, and fulfill BL-156 (private-to-public repo mapping).
**Status:** COMPLETE

#### Design

Cross-repo mechanisms already exist in DSM:
- **Inbox notifications**: notifications sent from one repo to another
- **@-imports**: `@path/to/external/file.md` references
- **Ecosystem Path Registry**: named paths to other repos

These become typed cross-repo edge types in the graph. The bridge graph is a separate
named graph (`_cross_repo`) that stores only cross-repo relationships.

For BL-156 specifically: the private DSM repo and the public (rebranded) DSM repo are
modeled as separate named graphs. Cross-repo node matching identifies equivalent sections
and tracks drift (sections that diverged between private and public versions).

#### Phase 12.1: Typed Cross-Repo Edges

**Tasks:**
1. [x] Define cross-repo edge types:
   - `INBOX_NOTIFICATION`: source sends inbox entry to target repo
   - `AT_IMPORT`: source imports a file from target repo
   - `ECOSYSTEM_LINK`: Ecosystem Path Registry entry between repos
2. [x] Create `src/graph/cross_repo.py`:
   - [x] `CrossRepoBridge`: manages the `_cross_repo` graph in FalkorDB
   - [x] `add_edge(source_repo, target_repo, edge_type, properties)`: creates cross-repo edge
   - [x] `edges_for_repo(repo_name)`: all cross-repo edges involving a repo
3. [x] Update `--graph-db` pipeline to detect and store cross-repo references
4. [x] Write tests for cross-repo edge operations

#### Phase 12.2: BL-156 Private-to-Public Mapping

**Tasks:**
1. [x] Add `--compare-repo INV_A INV_B` CLI option:
   - [x] Loads two repo entity inventories
   - [x] Matches nodes by entity ID or heading similarity
   - [x] Classifies match types: IDENTICAL, RENAMED, MODIFIED, ADDED, REMOVED
2. [x] Create `src/graph/repo_diff.py`:
   - [x] `compare_inventories()`: match results between two repos
   - [x] `MatchResult`: entity_a, entity_b, match_type, similarity_score
   - [x] Uses entity IDs for exact matching; TF-IDF for fuzzy matching (reuses Sprint 6)
3. [x] Store mapping results in `_cross_repo` bridge graph as `MAPS_TO` edges
4. [x] Reporter: show mapping table with match types and similarity scores
5. [x] Write tests with fixture inventories (private-like and public-like)

#### Phase 12.3: Drift Detection

**Tasks:**
1. [x] Add `--drift-report` CLI option:
   - [x] Filters comparison results for MODIFIED/RENAMED matches
   - [x] Shows sections present in both repos with content divergence
   - [x] Uses similarity threshold from DEC-005
2. [x] Write drift detection tests

#### Sprint 12 Deliverables

- [x] Typed cross-repo edges (INBOX_NOTIFICATION, AT_IMPORT, ECOSYSTEM_LINK, MAPS_TO)
- [x] `CrossRepoBridge` bridge graph manager
- [x] `--compare-repo INV_A INV_B` with three-pass match classification
- [x] `MAPS_TO` cross-repo edges with match type properties
- [x] `--drift-report` for divergence analysis
- [x] BL-156 fulfilled: private/public DSM comparison supported

**Sprint boundary checklist:**
- [x] Checkpoint document
- [x] Feedback files updated
- [x] Blog journal entry
- [x] README updated (major feature)

---

## Dependencies

### Updated pyproject.toml (Sprint 9)

```toml
[project]
name = "dsm-graph-explorer"
version = "0.3.0"  # Epoch 3
requires-python = ">=3.12"

classifiers = [
    "Programming Language :: Python :: 3.12",
]

[project.optional-dependencies]
graph = [
    "networkx>=3.2.0",      # In-memory graph compilation
    "falkordblite>=0.9",    # Persistent graph storage (NEW, Epoch 3)
]
```

No new mandatory dependencies. All Epoch 3 features are in optional extras or use
stdlib modules (subprocess for git operations).

---

## Architecture Evolution

### Epoch 2 Pipeline (NetworkX only)

```
markdown files → parser → validator → NetworkX DiGraph → GraphML export
                                                       → graph-stats (in-memory)
```

### Epoch 3 Pipeline (NetworkX + FalkorDBLite)

```
markdown files (or git ref) → parser → validator → NetworkX DiGraph → FalkorDB
                                                                    → graph-stats
                                                                    → temporal diff
entity inventories (external repos) → cross-repo resolver → bridge graph
```

NetworkX remains the in-memory compilation layer. FalkorDBLite is the persistence layer.
Both coexist; FalkorDBLite adds persistence, not replacement.

---

## New Project Structure (Epoch 3 Additions)

```
dsm-graph-explorer/
├── src/
│   ├── graph/
│   │   ├── graph_builder.py       # Existing (Epoch 2)
│   │   ├── graph_queries.py       # Existing (Epoch 2)
│   │   ├── graph_store.py         # NEW (Sprint 9): FalkorDBLite persistence
│   │   ├── graph_diff.py          # NEW (Sprint 10): temporal diff
│   │   └── cross_repo.py          # NEW (Sprint 12): bridge graph
│   ├── git_ref/                   # NEW (Sprint 10)
│   │   ├── __init__.py
│   │   └── git_resolver.py        # Historical file access via subprocess
│   └── inventory/                 # NEW (Sprint 11)
│       ├── __init__.py
│       └── inventory_parser.py    # Entity inventory YAML parser
├── tests/
│   ├── test_graph_store.py        # NEW (Sprint 9)
│   ├── test_git_resolver.py       # NEW (Sprint 10)
│   ├── test_graph_diff.py         # NEW (Sprint 10)
│   ├── test_inventory.py          # NEW (Sprint 11)
│   └── test_cross_repo.py         # NEW (Sprint 12)
├── data/
│   └── experiments/
│       ├── EXP-005-falkordb-integration/  # NEW (Sprint 9)
│       └── EXP-006-git-ref-temporal/      # NEW (Sprint 10)
└── docs/
    └── plans/
        └── epoch-3-plan.md        # This document
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| FalkorDBLite subprocess startup overhead in CI | Medium | Low | Session-scoped fixture (one instance per test session) |
| FalkorDBLite API changes (Beta) | Medium | Medium | Pinned version; isolate in `graph_store.py` facade |
| Git ref checkout complexity | Medium | Medium | subprocess-only (git show, git ls-tree); no gitpython |
| Entity inventory format too rigid | Low | Medium | Version field in YAML; additive design |
| Cross-repo Cypher limitation (no cross-graph queries) | Known | Low | Bridge graph approach; application-level joins |
| BL-156 scope creep | Medium | Medium | Strict sprint 12 boundary; defer advanced matching to Epoch 4 |

---

## Blog Integration

### Epoch 3 Blog Topics

1. **Sprint 9:** "From In-Memory to Persistent: Adding a Graph Database to a CLI Tool"
   - Why embedded databases exist, and when to choose them over a server
   - FalkorDBLite subprocess model
   - Zero-infrastructure Cypher

2. **Sprint 10:** "Git as Event Store: Temporal Graph Snapshots from Markdown"
   - The compilation-as-projection pattern
   - Historical graph queries via git ref
   - Diff-based analysis

3. **Sprint 11-12:** "Multi-Repo Knowledge Graphs: Entity Inventories and Cross-Repo Edges"
   - How cross-repo references work in DSM
   - Mapping private-to-public repository content
   - Drift detection as a graph query

### Materials Location

- `docs/blog/epoch-3/materials.md` (to be created at Sprint 9 start)
- `docs/blog/epoch-3/journal.md`

---

**Plan Status:** ACTIVE (Epoch 3, Sprints 9-12 complete, all MUSTs done)
**Last Updated:** 2026-03-13
**Previous:** [epoch-2-plan.md](epoch-2-plan.md)
**Research:** [epoch-3-neo4j-landscape-research.md](../research/epoch-3-neo4j-landscape-research.md), [epoch-3-falkordblite-deep-dive.md](../research/epoch-3-falkordblite-deep-dive.md)
**Decisions:** [DEC-006](../decisions/DEC-006-graph-database-selection.md), [DEC-007](../decisions/DEC-007-python-312-upgrade.md)