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
- [ ] Python 3.12 upgrade and zero test regressions (Sprint 9)
- [ ] FalkorDBLite integration: persistent graph store (Sprint 9)
- [ ] EXP-005: validate FalkorDBLite with existing graph data (Sprint 9)
- [ ] Git-ref temporal compilation: `--git-ref` flag (Sprint 10)
- [ ] Entity inventory format: per-repo referenceable entity manifest (Sprint 11)
- [ ] Cross-repo edges: typed edges for inbox, @-imports, ecosystem paths (Sprint 12)
- [ ] BL-156: private-to-public repo mapping with drift detection (Sprint 12)

**SHOULD (Epoch 3 Enhancements):**
- [ ] Incremental graph updates (avoid full rebuild on unchanged files)
- [ ] Temporal diff query: "what changed between two git refs?"
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
- [ ] FalkorDBLite stores and persists the existing NetworkX graph (EXP-005)
- [ ] Graph survives CLI restarts (data persists on disk)
- [ ] `--git-ref` produces a correct historical snapshot of the graph
- [ ] Entity inventory format is machine-readable and human-editable
- [ ] Cross-repo node matching works via entity inventory lookup
- [ ] BL-156: private DSM and public DSM can be modeled as separate graphs with cross-repo edges

**Process:**
- [ ] Each sprint produces a working increment
- [ ] Feedback files updated at sprint boundaries
- [ ] Blog material captured for Epoch 3 writeup
- [ ] Experiments documented with results

**Deliverable:**
- [ ] Persistent graph CLI with `--graph-db PATH --git-ref REF`
- [ ] Entity inventory spec and parser
- [ ] Cross-repo mapping support for DSM Central (BL-156)

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

**Duration:** 1-2 sessions
**Objective:** Upgrade Python, validate FalkorDBLite, and build the persistence layer.
**Status:** PLANNED

#### Phase 9.0: Python 3.12 Upgrade (DEC-007)

**Tasks:**
1. [ ] Update `pyproject.toml`:
   - [ ] `requires-python = ">=3.12"`
   - [ ] Drop Python 3.10/3.11 classifiers
   - [ ] Add `falkordblite>=0.9` to `[graph]` optional extra
   - [ ] Update `[tool.black] target-version = ['py312']`
   - [ ] Update `[tool.ruff] target-version = "py312"`
   - [ ] Version bump: `0.2.0 → 0.3.0`
2. [ ] Run `pytest tests/` and confirm 331 tests pass, 96% coverage maintained
3. [ ] Commit: "Sprint 9: Python 3.12 upgrade (DEC-007)"

**Gate:** Zero test regressions before proceeding to EXP-005.

#### Phase 9.1: EXP-005 (Integration Validation Experiment)

**Tasks:**
1. [ ] Install `falkordblite` in dev environment
2. [ ] Run EXP-005 test matrix (see above) as an exploratory script in `data/experiments/`
3. [ ] Document results in `data/experiments/EXP-005-falkordb-integration/`
4. [ ] If any test fails: resolve before Phase 9.2 (escalate to DEC-006 or DEC-007 revision if needed)

**Gate:** All EXP-005 acceptance criteria met before building `graph_store.py`.

#### Phase 9.2: Graph Store Module

**Tasks:**
1. [ ] Create `src/graph/graph_store.py`:
   - [ ] `GraphStore` class wrapping FalkorDBLite connection
   - [ ] `open(path)` / `close()` lifecycle management
   - [ ] `write_graph(networkx_graph, repo_name, git_ref)`: imports NetworkX DiGraph into FalkorDB
   - [ ] `query(cypher, params)` and `ro_query(cypher, params)`: thin wrappers
   - [ ] `graph_exists(repo_name)`: check before rebuilding
   - [ ] Parameterized queries throughout (no string interpolation)
2. [ ] Create Cypher schema: indexes on `path` (Document), `heading` (Section)
3. [ ] Write `tests/test_graph_store.py`:
   - [ ] Session-scoped FalkorDBLite fixture (`tmp_path_factory`)
   - [ ] Per-test graph isolation (unique graph names via UUID)
   - [ ] `g.delete()` cleanup in fixture teardown
   - [ ] Tests: write, query, persist simulation, multi-graph isolation

#### Phase 9.3: CLI Integration

**Tasks:**
1. [ ] Add `--graph-db PATH` option to CLI (path to FalkorDB storage file)
2. [ ] When `--graph-db` is provided: after graph build, persist via `GraphStore`
3. [ ] If graph already exists at path: skip rebuild (use cached), unless `--rebuild` flag
4. [ ] Graceful error if `falkordblite` not installed (same pattern as networkx/scikit-learn)
5. [ ] Update `--graph-stats` to query FalkorDB when `--graph-db` is set
6. [ ] Write CLI integration tests

#### Sprint 9 Deliverables

- [ ] Python 3.12 minimum, all tests green
- [ ] `falkordblite` in `[graph]` optional extra
- [ ] `src/graph/graph_store.py` with full test coverage
- [ ] `--graph-db PATH` CLI option
- [ ] EXP-005 results documented
- [ ] Version 0.3.0

**Sprint boundary checklist:**
- [ ] Checkpoint document (`docs/checkpoints/`)
- [ ] Feedback files updated (`docs/feedback/`)
- [ ] Blog journal entry
- [ ] README updated

---

### Sprint 10: Git-Ref Temporal Compilation

**Duration:** 1-2 sessions
**Objective:** Accept a git ref parameter and compile the graph at a historical point,
enabling temporal queries and diff-based analysis.
**Status:** PLANNED

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
1. [ ] Identify two historical refs in DSM repository (a tag and an older commit)
2. [ ] Run EXP-006 test matrix manually before building the feature
3. [ ] Document results in `data/experiments/EXP-006-git-ref-temporal/`

**Gate:** Confirm historical snapshot approach is feasible before full implementation.

#### Phase 10.1: Git-Ref Compilation

**Tasks:**
1. [ ] Add `--git-ref REF` CLI option (commit SHA, tag, or branch name)
2. [ ] Create `src/git_ref/git_resolver.py`:
   - [ ] `resolve_ref(repo_path, ref)` → validated commit SHA
   - [ ] `list_files_at_ref(repo_path, sha)` → list of markdown files at that ref
   - [ ] `read_file_at_ref(repo_path, sha, filepath)` → file contents as string
   - [ ] Uses `subprocess` (git show, git ls-tree) rather than gitpython dependency
3. [ ] Update compilation pipeline: when `--git-ref` is set, feed historical file contents
   to the parser instead of current disk state
4. [ ] Store `git_ref` as a property on Document nodes in FalkorDB
5. [ ] Write tests for git resolver (using current repo as test data)

#### Phase 10.2: Temporal Diff

**Tasks:**
1. [ ] Create `src/graph/graph_diff.py`:
   - [ ] `diff_graphs(store, ref_a, ref_b, repo_name)` → DiffResult
   - [ ] `DiffResult`: added nodes, removed nodes, changed nodes (property changes)
2. [ ] Add `--graph-diff REF_A REF_B` CLI option
3. [ ] Reporter: show diff as a Rich table (added/removed/changed)
4. [ ] Write tests for diff logic

#### Sprint 10 Deliverables

- [ ] `--git-ref REF` CLI option with historical compilation
- [ ] `src/git_ref/git_resolver.py` (subprocess-based, no gitpython)
- [ ] `git_ref` property on Document nodes
- [ ] `--graph-diff REF_A REF_B` CLI option
- [ ] EXP-006 results documented

**Sprint boundary checklist:**
- [ ] Checkpoint document
- [ ] Feedback files updated
- [ ] Blog journal entry
- [ ] README updated

---

### Sprint 11: Entity Inventory

**Duration:** 1 session
**Objective:** Define and implement an entity inventory format so each repository can
publish a machine-readable manifest of its referenceable entities, enabling cross-repo
reference resolution.
**Status:** PLANNED

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
1. [ ] Define final `dsm-entity-inventory.yml` schema (Pydantic model)
2. [ ] Create `src/inventory/inventory_parser.py`:
   - [ ] `EntityInventory` Pydantic model
   - [ ] `Entity` model: id, type, path, heading, level, stable
   - [ ] `load_inventory(path)` → EntityInventory
   - [ ] `discover_inventory(repo_path)` → optional path to inventory file
3. [ ] Write `tests/test_inventory.py` with fixture inventory files

#### Phase 11.2: Cross-Repo Reference Resolution

**Tasks:**
1. [ ] Update `src/validator/cross_ref_validator.py`:
   - [ ] Accept optional list of `EntityInventory` objects (external repos)
   - [ ] When a reference cannot be resolved locally, check external inventories
   - [ ] Flag: EXTERNAL (resolved via inventory) vs UNKNOWN (unresolved)
2. [ ] Add `--inventory PATH` CLI option to load an external repo's inventory
3. [ ] Update reporter to show EXTERNAL references distinctly

#### Phase 11.3: Inventory Export

**Tasks:**
1. [ ] Add `--export-inventory PATH` CLI option:
   - [ ] Scan current repo and generate a `dsm-entity-inventory.yml`
   - [ ] Include all sections, protocols (heuristic: headings matching known patterns)
2. [ ] Write tests for inventory export

#### Sprint 11 Deliverables

- [ ] `dsm-entity-inventory.yml` spec (Pydantic model)
- [ ] `src/inventory/inventory_parser.py`
- [ ] `--inventory PATH` CLI option for cross-repo resolution
- [ ] `--export-inventory PATH` for inventory generation
- [ ] EXTERNAL reference classification in reporter

**Sprint boundary checklist:**
- [ ] Checkpoint document
- [ ] Feedback files updated
- [ ] Blog journal entry
- [ ] README updated

---

### Sprint 12: Cross-Repo Edges + BL-156

**Duration:** 1-2 sessions
**Objective:** Build cross-repo graph support with typed edges for existing DSM
cross-repo mechanisms, and fulfill BL-156 (private-to-public repo mapping).
**Status:** PLANNED

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
1. [ ] Define cross-repo edge types:
   - `INBOX_NOTIFICATION`: source sends inbox entry to target repo
   - `AT_IMPORT`: source imports a file from target repo
   - `ECOSYSTEM_LINK`: Ecosystem Path Registry entry between repos
2. [ ] Create `src/graph/cross_repo.py`:
   - [ ] `CrossRepoBridge`: manages the `_cross_repo` graph in FalkorDB
   - [ ] `add_edge(source_repo, target_repo, edge_type, properties)`: creates cross-repo edge
   - [ ] `edges_for_repo(repo_name)`: all cross-repo edges involving a repo
3. [ ] Update `--graph-db` pipeline to detect and store cross-repo references
4. [ ] Write tests for cross-repo edge operations

#### Phase 12.2: BL-156 Private-to-Public Mapping

**Tasks:**
1. [ ] Add `--compare-repo INVENTORY_PATH` CLI option:
   - [ ] Loads a second repo's entity inventory
   - [ ] Matches nodes by entity ID or heading similarity
   - [ ] Classifies match types: IDENTICAL, RENAMED, MODIFIED, ADDED, REMOVED
2. [ ] Create `src/graph/repo_diff.py`:
   - [ ] `RepoDiff`: match results between two repos
   - [ ] `MatchResult`: entity_a, entity_b, match_type, similarity_score
   - [ ] Uses entity IDs for exact matching; TF-IDF for fuzzy matching (reuses Sprint 6)
3. [ ] Store mapping results in `_cross_repo` bridge graph as `MAPS_TO` edges
4. [ ] Reporter: show mapping table with match types and similarity scores
5. [ ] Write tests with fixture inventories (private-like and public-like)

#### Phase 12.3: Drift Detection

**Tasks:**
1. [ ] Add `--drift-report` CLI option:
   - [ ] Queries `_cross_repo` graph for MODIFIED nodes
   - [ ] Shows sections present in both repos with content divergence
   - [ ] Uses similarity threshold from DEC-005 (0.35)
2. [ ] Write drift detection tests

#### Sprint 12 Deliverables

- [ ] Typed cross-repo edges (INBOX_NOTIFICATION, AT_IMPORT, ECOSYSTEM_LINK)
- [ ] `_cross_repo` bridge graph in FalkorDB
- [ ] `--compare-repo INVENTORY_PATH` with match classification
- [ ] `MAPS_TO` cross-repo edges with match type properties
- [ ] `--drift-report` for divergence analysis
- [ ] BL-156 fulfilled: private/public DSM comparison supported

**Sprint boundary checklist:**
- [ ] Checkpoint document
- [ ] Feedback files updated
- [ ] Blog journal entry
- [ ] README updated (major feature)

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

**Plan Status:** ACTIVE (Epoch 3, pre-Sprint 9)
**Last Updated:** 2026-03-10
**Previous:** [epoch-2-plan.md](epoch-2-plan.md)
**Research:** [epoch-3-neo4j-landscape-research.md](../research/epoch-3-neo4j-landscape-research.md), [epoch-3-falkordblite-deep-dive.md](../research/epoch-3-falkordblite-deep-dive.md)
**Decisions:** [DEC-006](../decisions/DEC-006-graph-database-selection.md), [DEC-007](../decisions/DEC-007-python-312-upgrade.md)