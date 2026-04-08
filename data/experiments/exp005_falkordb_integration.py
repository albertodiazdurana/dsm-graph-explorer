"""
EXP-005: FalkorDBLite Integration Validation
=============================================

Purpose
-------
Gate experiment before implementing graph_store.py (Sprint 9, Phase 9.2).
Validates that FalkorDBLite works correctly in this environment with
DSM-like graph data before we commit to building the full integration layer.

This experiment was defined in the Epoch 3 plan (dsm-docs/plans/epoch-3-plan.md,
EXP-005 section) and is the acceptance gate for Phase 9.2. If any check fails,
Phase 9.2 does not begin until the issue is resolved.

Background
----------
FalkorDBLite (pip: falkordblite) is an embedded graph database that bundles a
compiled redis-server binary and falkordb.so C module. It forks a lightweight
subprocess communicating via Unix domain sockets. This architecture provides
process isolation (a DB crash does not crash the Python app) at the cost of
subprocess startup overhead (~100-500ms per FalkorDB() instance).

The import path is `redislite.falkordb_client` (reflecting the RedisGraph /
RedisLite heritage), not `falkordblite`. This is a known gotcha documented in
the deep-dive research (dsm-docs/research/epoch-3-falkordblite-deep-dive.md, Section 6).

Graph Architecture Being Validated
-----------------------------------
Sprint 9 will use NetworkX as the in-memory compilation layer and FalkorDBLite
as the persistence layer. This experiment validates only the FalkorDBLite side.
The graph schema mirrors what graph_builder.py (Sprint 7) already produces:

    (:Document {path, repo, git_ref})
        -[:CONTAINS {order}]->
    (:Section {heading, level, document_path})
        -[:REFERENCES]->
    (:Document)

Decisions
---------
- DEC-006: FalkorDBLite selected as graph database
  (dsm-docs/decisions/DEC-006-graph-database-selection.md)
- DEC-007: Python 3.12 upgrade to meet FalkorDBLite requirement
  (dsm-docs/decisions/DEC-007-python-312-upgrade.md)

Test Matrix (from epoch-3-plan.md EXP-005)
-------------------------------------------
  1. Import from redislite.falkordb_client     → Success
  2. Create graph with DSM document nodes      → <2s
     2a. Document node count correct
     2b. Section node count correct
     2c. CONTAINS edge count correct
  3. Persist and reload (restart simulation)   → All nodes present
     3a. Document nodes survive reload
     3b. Section nodes survive reload
     3c. CONTAINS edges survive reload
  4. Multi-graph: two repos coexist            → Correct isolation
     4a. Spoke graph contains only its own documents
     4b. Hub graph unaffected by spoke writes
     4c. Both graphs visible in list_graphs()
  5. Parameterized Cypher query                → Correct results
  6. MATCH (d:Document)-[:CONTAINS]->(s:Section) traversal → Correct
  7. REFERENCES edge traversal                 → Correct
  8. Index creation on Document.path and Section.heading → Success
     (index creation is the first action graph_store.py will take;
      surface syntax failures here before Phase 9.2 begins)

Checks NOT included and why
----------------------------
- Async API: we build a sync CLI tool; AsyncFalkorDB is out of scope for Sprint 9
- GRAPH.EXPLAIN / SLOWLOG: performance profiling tooling, not required for validation
- Unique/mandatory constraints: not planned for Sprint 9 schema
- Variable-length path traversal (REFERENCES*1..3): covered by basic traversal;
  deep path queries are planned for Sprint 12 (cross-repo edges)

Data Source
-----------
Synthetic test data shaped like the DSM repository graph from EXP-004
(data/experiments/exp004_graph_performance.py): 3 documents, 5 sections,
5 CONTAINS edges, 2 REFERENCES edges.

Usage
-----
    python data/experiments/exp005_falkordb_integration.py

Results written to: data/experiments/exp005_results.txt

References
----------
- FalkorDBLite PyPI:     https://pypi.org/project/falkordblite/
- FalkorDBLite GitHub:   https://github.com/FalkorDB/falkordblite
- FalkorDB docs:         https://docs.falkordb.com/
- Cypher coverage:       https://docs.falkordb.com/cypher/cypher-support.html
- RedisLite (heritage):  https://github.com/yahoo/redislite
- Deep-dive research:    dsm-docs/research/epoch-3-falkordblite-deep-dive.md
- Epoch 3 plan:          dsm-docs/plans/epoch-3-plan.md
- DEC-006:               dsm-docs/decisions/DEC-006-graph-database-selection.md
- DEC-007:               dsm-docs/decisions/DEC-007-python-312-upgrade.md
- Prior graph work:      src/graph/graph_builder.py (Sprint 7, Epoch 2)
- EXP-004 results:       data/experiments/exp004_graph_performance.py
"""

import shutil
import sys
import tempfile
import time
from pathlib import Path

# ── result tracking ───────────────────────────────────────────────────────────

# Each entry: (label, passed, note)
results: list[tuple[str, bool, str]] = []


def check(label: str, passed: bool, note: str = "") -> bool:
    """Record a check result and print it immediately."""
    status = "PASS" if passed else "FAIL"
    results.append((label, passed, note))
    marker = "✓" if passed else "✗"
    print(f"  [{status}] {marker} {label}" + (f"  ({note})" if note else ""))
    return passed


def section(title: str) -> None:
    print(f"\n{'─' * 62}")
    print(f"  {title}")
    print(f"{'─' * 62}")


# ── test data ─────────────────────────────────────────────────────────────────
#
# Mirrors the node/edge schema planned for graph_store.py and the data shape
# established by graph_builder.py (Sprint 7). Small enough to run quickly,
# realistic enough to exercise real query patterns.

DOCUMENTS = [
    {"path": "DSM_1.0.md", "repo": "dsm-central", "git_ref": "HEAD"},
    {"path": "DSM_2.0.md", "repo": "dsm-central", "git_ref": "HEAD"},
    {"path": "DSM_4.0.md", "repo": "dsm-central", "git_ref": "HEAD"},
]

SECTIONS = [
    {"heading": "Introduction",                    "level": 1, "document_path": "DSM_1.0.md"},
    {"heading": "Data Science Lifecycle",          "level": 2, "document_path": "DSM_1.0.md"},
    {"heading": "Sprint Boundary Checklist",       "level": 3, "document_path": "DSM_2.0.md"},
    {"heading": "Software Engineering Adaptation", "level": 2, "document_path": "DSM_4.0.md"},
    {"heading": "Test-Driven Development",         "level": 3, "document_path": "DSM_4.0.md"},
]

# (document_path, section_heading, order)
CONTAINS_EDGES = [
    ("DSM_1.0.md", "Introduction",                    1),
    ("DSM_1.0.md", "Data Science Lifecycle",          2),
    ("DSM_2.0.md", "Sprint Boundary Checklist",       1),
    ("DSM_4.0.md", "Software Engineering Adaptation", 1),
    ("DSM_4.0.md", "Test-Driven Development",         2),
]

# (section_heading, target_document_path)
REFERENCE_EDGES = [
    ("Data Science Lifecycle",          "DSM_2.0.md"),
    ("Software Engineering Adaptation", "DSM_1.0.md"),
]


# ── graph population ──────────────────────────────────────────────────────────

def populate_graph(g) -> None:
    """
    Write test data into graph g using parameterized queries throughout.

    Parameterized queries ($param syntax) are used for all writes to:
    - Prevent Cypher injection (important for production graph_store.py)
    - Validate that the parameterized query path works correctly in this version
    - Mirror the pattern that graph_store.py will use

    All CREATE statements are intentionally separate rather than batched into
    a single multi-clause CREATE. This matches how graph_store.py will write
    data incrementally from the NetworkX compilation pipeline.
    """
    # Create Document nodes
    for doc in DOCUMENTS:
        g.query(
            "CREATE (:Document {path: $path, repo: $repo, git_ref: $git_ref})",
            params=doc,
        )

    # Create Section nodes
    for sec in SECTIONS:
        g.query(
            "CREATE (:Section {heading: $heading, level: $level, document_path: $document_path})",
            params=sec,
        )

    # Create CONTAINS edges via MATCH + CREATE (not inline CREATE)
    # This is the pattern graph_store.py will use: nodes are written first,
    # then edges are wired up via MATCH. Avoids duplicate node creation.
    for doc_path, sec_heading, order in CONTAINS_EDGES:
        g.query(
            """
            MATCH (d:Document {path: $doc_path})
            MATCH (s:Section {heading: $sec_heading})
            CREATE (d)-[:CONTAINS {order: $order}]->(s)
            """,
            params={"doc_path": doc_path, "sec_heading": sec_heading, "order": order},
        )

    # Create REFERENCES edges
    for sec_heading, target_path in REFERENCE_EDGES:
        g.query(
            """
            MATCH (s:Section {heading: $sec_heading})
            MATCH (d:Document {path: $target_path})
            CREATE (s)-[:REFERENCES]->(d)
            """,
            params={"sec_heading": sec_heading, "target_path": target_path},
        )


# ── experiment ────────────────────────────────────────────────────────────────

def run_experiment(db_dir: Path) -> None:

    # ── Check 1: Import ───────────────────────────────────────────────────────
    #
    # The import path `redislite.falkordb_client` is not obvious from the
    # package name `falkordblite`. This is the primary installation gotcha
    # documented in the deep-dive (Section 6: Known Gotchas). If this fails,
    # falkordblite is not installed or its internal structure changed.
    section("Check 1: Import")
    try:
        from redislite.falkordb_client import FalkorDB
        check("Import from redislite.falkordb_client", True, "import path confirmed")
    except ImportError as e:
        check("Import from redislite.falkordb_client", False, str(e))
        print("\n  CRITICAL: Import failed. Cannot continue experiment.")
        print("  Run: pip install falkordblite")
        return

    # ── Check 2: Graph creation with DSM document nodes ──────────────────────
    #
    # Validates that FalkorDBLite can create and populate a graph shaped like
    # the DSM repository. The <2s target gives headroom above the expected
    # ~100-500ms subprocess startup time. We verify exact node and edge counts
    # because a silent failure (crash-free but incomplete write) would be worse
    # than an explicit error.
    section("Check 2: Graph creation with DSM document nodes")
    db_path = str(db_dir / "exp005.db")
    t0 = time.perf_counter()
    db = FalkorDB(db_path)
    g = db.select_graph("dsm_central")
    populate_graph(g)
    elapsed = time.perf_counter() - t0

    check(
        "Create graph with DSM nodes and edges (<2s)",
        elapsed < 2.0,
        f"{elapsed:.3f}s",
    )
    doc_count = len(g.ro_query("MATCH (d:Document) RETURN d").result_set)
    sec_count = len(g.ro_query("MATCH (s:Section) RETURN s").result_set)
    edge_count = len(g.ro_query("MATCH ()-[r:CONTAINS]->() RETURN r").result_set)
    check("Document node count correct", doc_count == len(DOCUMENTS),     f"{doc_count}/{len(DOCUMENTS)}")
    check("Section node count correct",  sec_count == len(SECTIONS),      f"{sec_count}/{len(SECTIONS)}")
    check("CONTAINS edge count correct", edge_count == len(CONTAINS_EDGES), f"{edge_count}/{len(CONTAINS_EDGES)}")

    # ── Check 3: Persistence (restart simulation) ─────────────────────────────
    #
    # FalkorDBLite persists via Redis RDB snapshots to the file path provided
    # at construction. We simulate a process restart by deleting the Python
    # objects (forcing garbage collection of the subprocess) and reopening with
    # the same file path. This is the core persistence guarantee that justifies
    # choosing FalkorDBLite over the current NetworkX + JSON approach.
    #
    # Note: `del` followed by re-opening is the closest approximation to a
    # true process restart available within a single Python script. A fully
    # accurate restart test would require a subprocess. For our purposes,
    # garbage collection of the FalkorDB object is sufficient to validate
    # that data was flushed to disk.
    #
    # Reference: deep-dive Section 4 (Persistence Model).
    section("Check 3: Persistence (restart simulation)")
    del g
    del db

    db2 = FalkorDB(db_path)
    g2 = db2.select_graph("dsm_central")

    doc_count_r  = len(g2.ro_query("MATCH (d:Document) RETURN d").result_set)
    sec_count_r  = len(g2.ro_query("MATCH (s:Section) RETURN s").result_set)
    edge_count_r = len(g2.ro_query("MATCH ()-[r:CONTAINS]->() RETURN r").result_set)

    check("Document nodes survive reload", doc_count_r  == len(DOCUMENTS),     f"{doc_count_r}/{len(DOCUMENTS)}")
    check("Section nodes survive reload",  sec_count_r  == len(SECTIONS),      f"{sec_count_r}/{len(SECTIONS)}")
    check("CONTAINS edges survive reload", edge_count_r == len(CONTAINS_EDGES), f"{edge_count_r}/{len(CONTAINS_EDGES)}")

    # ── Check 4: Multi-graph isolation ────────────────────────────────────────
    #
    # FalkorDBLite supports multiple named graphs within a single DB file.
    # Graphs are fully isolated: nodes, edges, labels, indexes, and constraints
    # are scoped per graph. Cross-graph queries are not supported; cross-graph
    # operations must happen at the application level.
    #
    # For BL-156 (Sprint 12), we will use separate graphs per repo (e.g.,
    # "dsm_central" and "dsm_spoke") and a bridge graph ("_cross_repo") for
    # cross-repo edges. This check validates that approach is sound.
    #
    # Reference: deep-dive Section 5 (Multi-Graph Support).
    section("Check 4: Multi-graph isolation (two repos)")
    g_spoke = db2.select_graph("dsm_spoke")
    g_spoke.query(
        "CREATE (:Document {path: $path, repo: $repo, git_ref: $git_ref})",
        params={"path": "SPOKE_README.md", "repo": "dsm-spoke", "git_ref": "HEAD"},
    )

    spoke_docs  = len(g_spoke.ro_query("MATCH (d:Document) RETURN d").result_set)
    hub_docs    = len(g2.ro_query("MATCH (d:Document) RETURN d").result_set)
    graph_list  = db2.list_graphs()

    check(
        "Spoke graph contains only its own documents",
        spoke_docs == 1,
        f"{spoke_docs} doc(s) in spoke (expected 1)",
    )
    check(
        "Hub graph unaffected by spoke writes",
        hub_docs == len(DOCUMENTS),
        f"{hub_docs} doc(s) in hub (expected {len(DOCUMENTS)})",
    )
    check(
        "Both graphs visible in list_graphs()",
        "dsm_central" in graph_list and "dsm_spoke" in graph_list,
        f"graphs: {sorted(graph_list)}",
    )

    # ── Check 5: Parameterized Cypher query ───────────────────────────────────
    #
    # Verifies the $param syntax works for read queries (ro_query). This is
    # the primary query pattern graph_store.py will use. Results are compared
    # against the known expected set (sorted, for determinism).
    #
    # ro_query() is used for all read-only queries as an optimization hint to
    # FalkorDBLite, signalling that no write locks are needed.
    #
    # Reference: deep-dive Section 2 (Python API).
    section("Check 5: Parameterized Cypher query (ro_query)")
    result = g2.ro_query(
        "MATCH (d:Document {repo: $repo}) RETURN d.path ORDER BY d.path",
        params={"repo": "dsm-central"},
    )
    returned_paths = [row[0] for row in result.result_set]
    expected_paths = sorted(d["path"] for d in DOCUMENTS)

    check(
        "Parameterized ro_query returns correct results",
        returned_paths == expected_paths,
        f"got {returned_paths}",
    )

    # ── Check 6: CONTAINS traversal ───────────────────────────────────────────
    #
    # The core query pattern for graph_store.py: navigate from a Document node
    # to its Section nodes via CONTAINS edges. This is the graph equivalent of
    # "give me all sections in this file". The Sprint 9 --graph-stats output
    # will depend on this traversal.
    #
    # Reference: deep-dive Section 9 (Data Model Compatibility, Example Queries).
    section("Check 6: MATCH (d:Document)-[:CONTAINS]->(s:Section) traversal")
    result = g2.ro_query(
        """
        MATCH (d:Document {path: $path})-[:CONTAINS]->(s:Section)
        RETURN s.heading, s.level ORDER BY s.level
        """,
        params={"path": "DSM_4.0.md"},
    )
    headings = [row[0] for row in result.result_set]
    expected = {"Software Engineering Adaptation", "Test-Driven Development"}

    check(
        "CONTAINS traversal returns correct sections for DSM_4.0.md",
        set(headings) == expected,
        f"sections: {headings}",
    )

    # ── Check 7: REFERENCES edge traversal ───────────────────────────────────
    #
    # Validates cross-document reference edges. In the full pipeline, these
    # are created by graph_builder.py from the validator's CrossReference
    # dataclass. Sprint 9 will persist these edges to FalkorDBLite, enabling
    # Cypher queries like "which documents reference DSM_2.0.md?".
    section("Check 7: REFERENCES edge traversal")
    result = g2.ro_query(
        """
        MATCH (s:Section)-[:REFERENCES]->(d:Document)
        RETURN s.heading, d.path ORDER BY s.heading
        """
    )
    ref_pairs = [(row[0], row[1]) for row in result.result_set]

    check(
        "REFERENCES edges traversable",
        len(ref_pairs) == len(REFERENCE_EDGES),
        f"{len(ref_pairs)} reference edge(s) (expected {len(REFERENCE_EDGES)})",
    )

    # ── Check 8: Index creation ───────────────────────────────────────────────
    #
    # graph_store.py will create these indexes as its first action when
    # initializing a new graph. Indexes on path (Document) and heading (Section)
    # enable efficient MATCH lookups. Surfacing a syntax failure here prevents
    # discovering it mid-implementation in Phase 9.2.
    #
    # FalkorDBLite range indexes use the standard Cypher CREATE INDEX syntax.
    # Full-text and vector indexes use procedure calls (not tested here, as we
    # don't plan to use them in Sprint 9).
    #
    # Reference: deep-dive Section 3 (Cypher Subset, Indexes).
    section("Check 8: Index creation")
    try:
        g2.query("CREATE INDEX FOR (d:Document) ON (d.path)")
        check("CREATE INDEX FOR (d:Document) ON (d.path)", True)
    except Exception as e:
        check("CREATE INDEX FOR (d:Document) ON (d.path)", False, str(e))

    try:
        g2.query("CREATE INDEX FOR (s:Section) ON (s.heading)")
        check("CREATE INDEX FOR (s:Section) ON (s.heading)", True)
    except Exception as e:
        check("CREATE INDEX FOR (s:Section) ON (s.heading)", False, str(e))

    # ── cleanup ───────────────────────────────────────────────────────────────
    g2.delete()
    g_spoke.delete()


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 62)
    print("  EXP-005: FalkorDBLite Integration Validation")
    print(f"  Python:  {sys.version.split()[0]}")
    try:
        import importlib.metadata
        version = importlib.metadata.version("falkordblite")
        print(f"  Package: falkordblite {version}")
    except Exception:
        print("  Package: falkordblite (version unknown)")
    print("=" * 62)

    tmp_dir = Path(tempfile.mkdtemp(prefix="exp005_"))
    try:
        run_experiment(tmp_dir)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # ── summary ───────────────────────────────────────────────────────────────
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)

    print(f"\n{'=' * 62}")
    print("  SUMMARY")
    print(f"{'=' * 62}")
    print(f"  Passed: {passed}   Failed: {failed}   Total: {len(results)}")

    if failed:
        print("\n  FAILED checks:")
        for label, ok, note in results:
            if not ok:
                print(f"    ✗ {label}" + (f"  ({note})" if note else ""))
        gate_line = "Gate: NO-GO. Resolve failures before Phase 9.2."
    else:
        gate_line = "Gate: GO for Phase 9.2 (graph_store.py implementation)."
        print(f"\n  {gate_line}")

    # Write results file
    out_path = Path(__file__).parent / "exp005_results.txt"
    with open(out_path, "w") as f:
        f.write("EXP-005: FalkorDBLite Integration Validation\n")
        f.write("=" * 62 + "\n")
        f.write(f"Python:  {sys.version.split()[0]}\n")
        try:
            import importlib.metadata
            f.write(f"Package: falkordblite {importlib.metadata.version('falkordblite')}\n")
        except Exception:
            f.write("Package: falkordblite (version unknown)\n")
        f.write(f"\nPassed: {passed}   Failed: {failed}   Total: {len(results)}\n")
        f.write("\nResults:\n")
        for label, ok, note in results:
            status = "PASS" if ok else "FAIL"
            f.write(f"  [{status}] {label}")
            if note:
                f.write(f"  ({note})")
            f.write("\n")
        f.write(f"\n{gate_line}\n")

    print(f"\n  Results written to: {out_path.relative_to(Path.cwd())}")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()