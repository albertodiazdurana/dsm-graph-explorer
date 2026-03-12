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

**Last Updated:** 2026-03-12