# Epoch 3 Blog Journal

**Date:** 2026-03-09 (started)
**Project:** DSM Graph Explorer
**Epoch:** 3 (Graph Database Integration)

---

## Sessions: 2026-03-09 — Epoch 3 Pre-Planning & Research

### What Happened

1. **Landscape research** — Surveyed six graph database options for replacing the NetworkX in-memory prototype: Neo4j Community, Neo4j AuraDB Free, FalkorDB (Redis-based), FalkorDBLite (embedded), Memgraph, and Kùzu. Evaluated against five criteria: embeddability, Cypher support, Python API, persistence, and pip-installable. Documented in `docs/research/epoch-3-neo4j-landscape-research.md`.

2. **DEC-006: FalkorDBLite selected** — The embedded option won: no server process, Cypher-compatible, pip-installable, persistent storage to disk. The trade-off: requires Python 3.12+ (project was on 3.10). Mitigated via optional dependency with version gate, matching the pattern used by scikit-learn and networkx.

3. **Deep-dive research** — Detailed investigation of FalkorDBLite's API, Cypher dialect, persistence model, and testing patterns. Documented in `docs/research/epoch-3-falkordblite-deep-dive.md`. Key finding: import path is `redislite.falkordb_client`, not what the docs suggest.

4. **Epoch 3 plan drafted** — Four-sprint roadmap: Sprint 9 (FalkorDB foundation), Sprint 10 (git-ref temporal), Sprint 11 (bridge graph), Sprint 12 (Cypher query library).

### Aha Moments

1. **Embedded beats client-server** — The original plan assumed Neo4j (client-server). But FalkorDBLite provides the same Cypher interface as an embedded library with zero infrastructure. This is the same insight that SQLite brought to relational databases: for single-user tools, embedded is simpler and sufficient.

2. **Tiered research** — The landscape survey (broad) followed by the deep-dive (narrow) was more effective than going deep on the first option that looked promising. The broad pass eliminated 4 options quickly; the deep-dive confirmed the survivor. This became DSM feedback Entry 33 / Proposal #28.

3. **Research Gate** — The sequence Idea → Research → Plan → Action prevented premature implementation. Without the research phase, we would have started with Neo4j Community and discovered the server dependency mid-sprint. This became DSM feedback Entry 32 / Proposal #27.

### Metrics

| Metric | Value |
|--------|-------|
| Options evaluated | 6 |
| Research documents | 2 (landscape + deep-dive) |
| Decisions created | 1 (DEC-006) |
| Sessions | 2 (Sessions 22-23) |

### Blog Material

**Sprint 9 narrative threads:**
- Embedded vs client-server: why SQLite thinking applies to graph databases
- The research funnel: 6 options → 1 selection through structured elimination
- Python version as dependency constraint: when your library choice forces an upgrade

---

## Sessions: 2026-03-10/11 — Sprint 9: FalkorDBLite Integration

### What Happened

1. **Phase 9.0: Python 3.12 Upgrade (DEC-007)** — Installed Python 3.12 via deadsnakes PPA, recreated venv, updated pyproject.toml (6 changes: requires-python, version bump to 0.3.0, classifiers, falkordblite extra, black/ruff target versions). 331 tests passed with zero regressions.

2. **Phase 9.1: EXP-005 FalkorDBLite Validation** — Ran a 16-check capability experiment validating FalkorDBLite's API: import path, graph creation, node/edge insertion, Cypher queries, persistence across sessions, multi-graph isolation, index creation, subprocess startup time (0.119s). All 16 checks passed.

3. **Phase 9.2: graph_store.py Persistence Layer** — Built `src/graph/graph_store.py` with GraphStore class: `write_graph()` imports a NetworkX DiGraph to FalkorDB, `graph_exists()` gates rebuilds, `ro_query()`/`query()` wrap parameterized Cypher, `close()` handles lifecycle. Schema: Document and Section nodes with CONTAINS and REFERENCES edges, matching the NetworkX graph structure. git_ref property on all nodes prepares for Sprint 10 temporal queries. 18 tests in `tests/test_graph_store.py`.

4. **Phase 9.3: CLI --graph-db Integration** — Added `--graph-db PATH` and `--rebuild` flags to `cli.py`. Flow: build NetworkX graph → check if FalkorDB graph exists → write if new or --rebuild → report. Graceful error if falkordblite not installed. 6 tests in `tests/test_cli_graph_db.py`. Total: 355 tests, 96% coverage.

5. **CI Fix (Session 26)** — GitHub Actions workflow failed because `graph/__init__.py` eagerly imported `graph_builder` which does `import networkx` unconditionally. CI installs without optional graph dependencies. Fix: wrapped imports in try/except ImportError. Also removed a duplicate import line in `cli.py`.

6. **DSM Feedback** — Six methodology entries (31-36) and five backlog proposals (27-31):
   - Portfolio path standardization (Entry 31)
   - Research Gate protocol (Entry 32 / Proposal #27)
   - Tiered Research pattern (Entry 33 / Proposal #28)
   - Experiment documentation structure (Entry 34 / Proposal #29)
   - "Challenge Myself to Reason" composition challenge (Entry 35 / Proposal #30)
   - Edit Explanation Stop Protocol (Entry 36 / Proposal #31)

### Aha Moments

1. **Two-layer architecture** — NetworkX handles graph construction (compilation); FalkorDBLite handles persistence and Cypher queries. Keeping them separate means either can be replaced independently. The GraphStore doesn't know about markdown parsing; the graph builder doesn't know about databases. This is the CQRS pattern from Sprint 7 extended with a persistence layer.

2. **Optional dependency cascade** — The CI fix revealed a subtle problem: when module A (graph_store) is optional and module B (graph_builder) is also optional but imported by the package's `__init__.py`, importing A triggers B's dependencies. The fix (try/except in `__init__.py`) is the same pattern Python uses for optional submodules. Lesson: optional dependencies need guarding at every import boundary, not just at the point of use.

3. **EXP-005 as API discovery** — The experiment wasn't just validation; it was the primary means of discovering FalkorDBLite's actual API (import paths, method signatures, Cypher dialect quirks). The documentation was incomplete; the experiment filled the gaps. This is why experiments should run before implementation, not after.

4. **git_ref as forward investment** — Adding `git_ref` to every node in Phase 9.2 cost nothing during implementation but creates the foundation for Sprint 10's temporal queries. Without it, Sprint 10 would require a schema migration. Planning one sprint ahead on schema design paid off.

5. **"Challenge Myself to Reason"** — When presenting 6 test cases for Phase 9.3, the user asked "why these 6 and not more or fewer?" This exposed a gap in the Pre-Generation Brief: it asks What/Why/How but doesn't challenge artifact composition. The new protocol adds Why/What/Why not more or less/How/When as a structured reasoning framework for multi-item artifacts.

### Metrics

| Metric | Value |
|--------|-------|
| New source files | 1 (`graph_store.py`) |
| Modified source files | 2 (`cli.py`, `graph/__init__.py`) |
| New test files | 2 (`test_graph_store.py`, `test_cli_graph_db.py`) |
| Tests added | 24 (18 graph_store + 6 CLI) |
| Total tests | 355 |
| Coverage | 96% |
| Experiments run | 1 (EXP-005, 16/16 checks) |
| Decisions created | 2 (DEC-006, DEC-007) |
| DSM feedback entries | 6 (Entries 31-36) |
| DSM backlog proposals | 5 (Proposals 27-31) |
| Sessions | 4 (Sessions 24-26, plus lightweight Session 24) |

### Blog Material

**Sprint 9 narrative threads:**
- From in-memory to persistent: extending the CQRS architecture with a database layer
- Embedded graph databases: when SQLite thinking applies to Cypher
- Experiment as API discovery: why you run EXP-005 before writing graph_store.py
- The optional dependency cascade: a CI failure that teaches import architecture
- Forward investment in schema design: git_ref costs nothing now, enables everything later

**Title options for Sprint 9 blog:**
1. "Adding Persistence to Your Graph: From NetworkX to FalkorDBLite"
2. "The Embedded Graph Database: Why We Chose SQLite Thinking Over Neo4j"
3. "When Your CI Teaches You About Import Architecture: Optional Dependencies Done Right"

---

## Session: 2026-03-12 — Sprint 10: Git-Ref Temporal Compilation

### What Happened

1. **Phase 10.0: EXP-006 Git-Ref Temporal Accuracy** — Pre-implementation gate experiment validating subprocess-based git commands (`rev-parse`, `ls-tree`, `show`) at historical refs. Used two refs from this repo's history: an early commit (87d869d, 12 markdown files) and HEAD (86+ files). All 19 checks passed, confirming the approach for `git_resolver.py`.

2. **Phase 10.1: git_resolver.py + Content-Based Parsers** — Built `src/git_ref/git_resolver.py` with `resolve_ref()`, `list_markdown_files()`, `read_file_at_ref()`, and `find_repo_root()`. Added content-based variants to the parser (`parse_markdown_content()`, `extract_cross_references_from_content()`) so git-ref content can be parsed without writing temporary files. CLI `--git-ref REF` flag compiles and validates at any historical commit. 35 tests (28 resolver + 7 CLI).

3. **Phase 10.2: graph_diff.py + CLI Integration** — Built `src/graph/graph_diff.py` with `diff_graphs()` comparing two NetworkX DiGraphs: added/removed/modified nodes and edges. `format_diff_report()` produces Rich console output. CLI `--graph-diff REF_A REF_B` compiles both refs and shows structural differences. 12 tests.

4. **Ancillary fixes** — `find_repo_root()` walks up from CWD to find `.git/`, making `--git-ref` work from subdirectories. CLI version bumped from 0.2.0 to 0.3.0. Fixed `test_errors_with_strict_exits_one` to use empty config file.

### Aha Moments

1. **Content-based parsing avoids temp files** — The original parser functions take file paths. For git-ref content (read from `git show`), writing to temp files would add I/O overhead and cleanup complexity. Adding `parse_markdown_content()` and `extract_cross_references_from_content()` keeps the same logic but accepts strings directly. The file-based functions become thin wrappers that read the file and delegate. This is the adapter pattern applied to I/O boundaries.

2. **Graph diff as in-memory comparison** — Instead of diffing Cypher query results (which would couple the diff logic to FalkorDB), the diff operates on NetworkX DiGraphs. Two refs produce two graphs; the diff compares them. This keeps the diff logic database-agnostic, meaning it works whether the user has FalkorDB installed or not. The database is for persistence and querying; the diff is a pure computation.

3. **find_repo_root() for subdirectory safety** — Users may run `dsm-validate --git-ref HEAD` from a subdirectory. Without repo root resolution, `git ls-tree` would fail because relative paths don't resolve against the working directory's `.git/`. Walking up to find `.git/` is the same pattern `git` itself uses internally, and it costs one stat call per directory level.

4. **Experiment as implementation blueprint** — EXP-006's 19 checks mapped almost 1:1 to `git_resolver.py`'s functions. The experiment validated the subprocess commands; the implementation wrapped them with error handling and typing. This confirms the pattern from Sprint 9 (EXP-005 → graph_store.py): experiments are not just validation, they are the implementation's first draft.

### Metrics

| Metric | Value |
|--------|-------|
| New source files | 3 (`git_resolver.py`, `git_ref/__init__.py`, `graph_diff.py`) |
| Modified source files | 3 (`cli.py`, `markdown_parser.py`, `cross_ref_extractor.py`) |
| New test files | 3 (`test_git_resolver.py`, `test_cli_git_ref.py`, `test_graph_diff.py`) |
| Tests added | 47 |
| Total tests | 402 |
| Coverage | 95% |
| Experiments | 1 (EXP-006, 19/19) |

### Blog Material

**Sprint 10 narrative threads:**
- Time travel for documentation: how `--git-ref` lets you validate any historical snapshot
- Content-based parsing: the adapter pattern at I/O boundaries
- Graph diffing without a database: why in-memory comparison beats Cypher queries for structural diff
- Experiment-to-implementation pipeline: EXP-006 checks become git_resolver.py functions

**Title options for Sprint 10 blog:**
1. "Time-Traveling Your Documentation Graph: Git-Ref Temporal Compilation"
2. "From Experiment to Implementation: When Your Validation Checks Become Your API"
3. "Diffing Documentation Graphs Across Git History"

---

## Session: 2026-03-12 — Sprint 11: Entity Inventory

### What Happened

1. **Phase 11.1: Inventory Spec and Parser** — Defined the `dsm-entity-inventory.yml` schema as Pydantic models: `Entity` (id, type, path, heading, level, stable), `RepoInfo` (name, type, url), and `EntityInventory` (version, repo, entities). Built `src/inventory/inventory_parser.py` with `load_inventory()` for parsing and `discover_inventory()` for automatic detection of inventory files at repo roots. 33 tests with YAML fixture files.

2. **Phase 11.2: Cross-Repo Reference Resolution** — Extended the cross-reference validator to accept optional `EntityInventory` objects from external repos. When a reference cannot be resolved locally, the validator checks external inventories and classifies matches as EXTERNAL (distinct from UNKNOWN). Added `--inventory PATH` CLI option (repeatable) to load external inventories. Updated the reporter to show EXTERNAL references with their source inventory. 17 tests.

3. **Phase 11.3: Inventory Export** — Added `--export-inventory PATH` CLI option that scans the current repo and generates a `dsm-entity-inventory.yml`. Type heuristics classify headings as sections, protocols, or backlog items based on pattern matching (e.g., "Sprint Boundary Checklist" → protocol, "BL-156" → backlog-item). 19 tests.

4. **DSM Feedback** — Entries 38-39 (epoch plan update gap, alignment review gap) with Proposals #33-34. Both pushed to DSM Central inbox. CLAUDE.md Sprint Boundary Checklist updated with 6th item (epoch plan).

### Aha Moments

1. **Entity inventories as the bridge abstraction** — The inventory format is the key enabler for Sprint 12's cross-repo edges. By defining a machine-readable manifest per repository, cross-repo references become inventory lookups rather than file system traversals. The format is deliberately additive: Sprint 12 adds cross-repo edge types without changing the per-repo schema. This is the same strategy as database migrations: the schema evolves, but existing data remains valid.

2. **EXTERNAL vs UNKNOWN as a classification insight** — Before entity inventories, unresolved references were binary: found or not found. With inventories, "not found locally" splits into two cases: found in an external inventory (EXTERNAL, expected) or not found anywhere (UNKNOWN, likely broken). This three-state model (LOCAL, EXTERNAL, UNKNOWN) gives users actionable information: EXTERNAL references are correct cross-repo links, not errors to fix.

3. **Type heuristics for export** — Generating an inventory from scratch requires classifying sections by type (section, protocol, backlog-item). Rather than requiring manual tagging, pattern matching on heading text provides reasonable defaults: numbered sections are "section," known protocol names are "protocol," "BL-" prefixes are "backlog-item." The heuristics are imperfect but produce a usable first draft that users can refine.

4. **Checklist-driven process gaps compound** — Entries 37-39 all follow the same pattern: if a step is not in the checklist, it does not happen. Sprint boundary gate (Entry 37), epoch plan update (Entry 38), alignment review (Entry 39). Three process gaps discovered in one session, all with the same root cause. The checklist is not just a convenience; it is the behavioral specification for the agent.

### Metrics

| Metric | Value |
|--------|-------|
| New source files | 2 (`inventory_parser.py`, `inventory/__init__.py`) |
| Modified source files | 3 (`cli.py`, `cross_ref_validator.py`, `reporter.py`) |
| New test files | 1 (`test_inventory.py`) |
| Tests added | 69 (33 parser + 17 resolution + 19 export) |
| Total tests | 471 |
| Coverage | 95% |
| DSM feedback entries | 2 (Entries 38-39) |
| DSM backlog proposals | 2 (Proposals 33-34) |
| Sessions | 1 (Session 29) |

### Blog Material

**Sprint 11 narrative threads:**
- Entity inventories as a federation pattern: how per-repo manifests enable multi-repo graph queries without centralized indexing
- The LOCAL/EXTERNAL/UNKNOWN classification: turning binary validation into actionable cross-repo intelligence
- Type heuristics: generating machine-readable manifests from human-authored markdown
- Checklist as behavioral specification: why three process gaps shared one root cause

**Title options for Sprint 11 blog:**
1. "From Validation to Federation: Entity Inventories for Multi-Repo Documentation Graphs"
2. "Three States of a Cross-Reference: LOCAL, EXTERNAL, and UNKNOWN"
3. "When Your Checklist IS Your Specification: Process Gaps That Compound"

---

## Session: 2026-03-13 — Sprint 12: Cross-Repo Edges + BL-156

### What Happened

1. **Phase 12.1: Typed Cross-Repo Edges** — Created `src/graph/cross_repo.py` with `CrossRepoBridge` class managing a `_cross_repo` bridge graph. Defined four edge types via `EdgeType` enum: `INBOX_NOTIFICATION`, `AT_IMPORT`, `ECOSYSTEM_LINK`, and `MAPS_TO`. The bridge stores cross-repo relationships separately from per-repo graphs, using `store_mapping()` to persist entity matches. 19 tests in `tests/test_cross_repo.py`.

2. **Phase 12.2: BL-156 Private-to-Public Mapping** — Built `src/graph/repo_diff.py` with `compare_inventories()` implementing a three-pass entity matching algorithm: (1) exact ID match, (2) heading match, (3) fuzzy TF-IDF similarity (reusing Sprint 6's threshold). Match types: IDENTICAL, RENAMED, MODIFIED, ADDED, REMOVED. Added `--compare-repo INV_A INV_B` CLI option showing match results as a Rich table. 13 tests in `tests/test_repo_diff.py`.

3. **Phase 12.3: Drift Detection** — Added `--drift-report` CLI option that filters comparison results to show only MODIFIED and RENAMED matches, highlighting sections that diverged between private and public repos. 10 CLI integration tests in `tests/test_cli_compare.py`.

4. **BL-156 Complete** — The combination of entity inventories (Sprint 11) and cross-repo edges (Sprint 12) fulfills BL-156: private and public DSM repositories can be modeled as separate entity inventories, compared via `--compare-repo`, and divergence tracked via `--drift-report`.

### Aha Moments

1. **Bridge graph as separation of concerns** — Cross-repo relationships live in their own graph (`_cross_repo`), not mixed into per-repo graphs. This means per-repo graphs remain self-contained and can be rebuilt independently. The bridge graph is a join table in graph form: it only stores relationships, not entity data. This mirrors the relational pattern of a many-to-many junction table.

2. **Three-pass matching as progressive refinement** — Exact ID match catches the easy cases (same entity ID in both repos). Heading match catches renamed entities where the ID changed but the heading didn't. TF-IDF catches semantic matches where both changed. Each pass is cheaper than the next, so the algorithm exits early when possible. This is the same tiered approach used in Sprint 6's semantic validation: simple checks first, expensive checks only for unresolved cases.

3. **Inventory as the federation layer** — Sprint 11's entity inventories turned out to be the key enabler. Without per-repo manifests, cross-repo comparison would require parsing both repos from scratch. With inventories, comparison is an inventory-to-inventory operation: fast, offline, and independent of the actual markdown files. The inventory is the API contract between repos.

### Metrics

| Metric | Value |
|--------|-------|
| New source files | 2 (`cross_repo.py`, `repo_diff.py`) |
| Modified source files | 2 (`cli.py`, `graph/__init__.py`) |
| New test files | 3 (`test_cross_repo.py`, `test_repo_diff.py`, `test_cli_compare.py`) |
| Tests added | 42 (19 + 13 + 10) |
| Total tests | 513 |
| Coverage | 95% |
| Sessions | 1 (Session 31) |

### Blog Material

**Sprint 12 narrative threads:**
- Bridge graphs as junction tables: modeling cross-repo relationships without contaminating per-repo data
- Three-pass entity matching: progressive refinement from exact to fuzzy
- Entity inventories as a federation API: comparing repos without parsing them
- BL-156 retrospective: from backlog item to working feature across two sprints (11+12)

**Title options for Sprint 12 blog:**
1. "Cross-Repo Knowledge Graphs: Bridge Graphs, Entity Matching, and Drift Detection"
2. "Comparing Documentation Repositories: A Three-Pass Entity Matching Algorithm"
3. "From Backlog to Feature: How BL-156 Became a Two-Sprint Cross-Repo Solution"

---

## Session: 2026-03-13 — FalkorDBLite Documentation Contribution Opportunity

### What Happened

Reviewing the Epoch 3 journal entry about "EXP-005 as API discovery," we identified that our deep-dive research and experiment results constitute a comprehensive user guide for FalkorDBLite that doesn't exist in its official documentation. The experiment wasn't just validation for us; it filled real documentation gaps in the upstream project.

### Contribution-Ready Documentation Gaps

From our research (`docs/research/epoch-3-falkordblite-deep-dive.md`) and EXP-005 (`data/experiments/exp005_falkordb_integration.py`):

1. **Import path confusion** — Package is `falkordblite`, import is `from redislite.falkordb_client import FalkorDB`. The #1 gotcha for new users, buried in heritage from RedisLite/RedisGraph.
2. **Testing patterns** — Session-scoped DB fixture + per-test graph isolation via UUID naming + `g.delete()` cleanup. We validated this across 18+ tests; official docs have no testing guidance.
3. **Complete working example** — EXP-005 covers graph creation, parameterized queries, persistence verification, multi-graph isolation, and index creation in a single runnable script.
4. **Editable installs fail** — `pip install -e .` doesn't work, only `pip install .`. Worth a note in installation docs.
5. **Python 3.12+ requirement** — Not prominently documented; catches users upgrading from 3.10/3.11.

### Blog Material

**Narrative thread:** "When your experiment becomes upstream documentation" — how capability experiments (DSM 4.0 Section 4) can produce contributions to open-source projects. The experiment-as-API-discovery pattern generates documentation that the library maintainers didn't write because they already know their own API. Users discover the gaps; experiments document them systematically.

### Next Action

Open an issue on [FalkorDBLite GitHub](https://github.com/FalkorDB/falkordblite) listing the documentation gaps with specific suggestions. Gauge maintainer responsiveness before investing in a PR.

---

**Last Updated:** 2026-03-13