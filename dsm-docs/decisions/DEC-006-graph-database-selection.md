# DEC-006: Graph Database Selection

**Date:** 2026-03-09
**Status:** ACCEPTED
**Epoch:** 3 (pre-planning)
**Research:** `dsm-docs/research/epoch-3-neo4j-landscape-research.md`
**Inbox Input:** `_inbox/dsm-central.md` (BL-156 private-to-public repo mapping)

---

## Context

Epoch 2 built a NetworkX graph prototype for reference network analysis (Sprint 7).
Epoch 3 needs to extend this with persistent storage, temporal queries (git-ref
compilation), cross-repo edges, and entity inventory support. Additionally, DSM
Central's BL-156 (rebranding) requires Graph Explorer to support multi-repo graph
comparison: modeling both private and public DSM repositories as separate graphs
with cross-repo node matching and drift detection.

The research phase (`epoch-3-neo4j-landscape-research.md`) evaluated the graph
database landscape for Python CLI projects. Key constraint: Neo4j has no embedded
mode for Python (Java only); it always requires a separate server process.

## Decision

Use **FalkorDBLite** as the graph database backend for Epoch 3.

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Database | FalkorDBLite | Embedded, zero-config, Cypher-compatible, pip install |
| Python package | `falkordblite` | Subprocess-based, no Docker dependency |
| Query language | Cypher (compatible subset) | Skills transfer to Neo4j if migration needed later |
| Driver | Official `neo4j` driver (v6.1) reserved for future Neo4j migration | Not used in Epoch 3 |
| Testing | Direct FalkorDBLite instances in pytest fixtures | No testcontainers needed for embedded DB |
| NetworkX role | Retained as compilation target; FalkorDBLite as persistence layer | Incremental migration, not full replacement |

## Options Evaluated

### Option A: Full Neo4j (Server)

| Aspect | Assessment |
|--------|------------|
| Ecosystem | Industry standard, massive community, Graph Data Science library |
| Query language | Full Cypher support |
| Visualization | Neo4j Browser (web UI) built-in |
| Deployment | Requires Docker or native install |
| CI/CD | Requires service containers in GitHub Actions |
| User experience | Users must `docker-compose up` before graph features work |
| Scale fit | Overkill for ~500 nodes; designed for millions |

**Verdict:** Rejected for Epoch 3. Transforms a pip-install-and-run CLI tool into
one with infrastructure dependencies. The power is real but the overhead is
disproportionate to current scale. Remains the migration target if/when scale or
multi-user needs justify it.

### Option B: FalkorDBLite (Embedded) -- SELECTED

| Aspect | Assessment |
|--------|------------|
| Ecosystem | Successor to RedisGraph; FalkorDB is actively maintained |
| Query language | Cypher-compatible subset |
| Deployment | `pip install falkordblite`, zero-config |
| CI/CD | No special infrastructure needed |
| User experience | Preserves pip-install-and-run CLI model |
| Scale fit | Appropriate for current scale; handles multi-repo graphs |
| Multi-repo support | Natural via graph labels/properties for repo boundaries |

**Verdict:** Selected. Delivers persistent Cypher queries without Docker dependency.
Preserves the CLI tool model. Cypher skills transfer directly to Neo4j if migration
is needed later.

### Option C: Dual Backend (Abstraction Layer)

| Aspect | Assessment |
|--------|------------|
| Flexibility | Maximum: user chooses backend |
| Engineering cost | Significant: abstraction layer, lowest-common-denominator API |
| Maintenance | Double the test matrix |

**Verdict:** Rejected. Premature abstraction for current needs. If migration to
Neo4j is needed later, the Cypher queries transfer directly; no abstraction layer
required.

### Option D: NetworkX + JSON Persistence

| Aspect | Assessment |
|--------|------------|
| Simplicity | No new dependency |
| Query power | Custom Python functions only, no Cypher |
| Multi-repo | Manual graph management, fragile |
| Persistence | JSON/pickle serialization |

**Verdict:** Rejected. The BL-156 multi-repo mapping requirement (cross-repo node
matching, persistent mappings, diff detection) exceeds what custom Python graph
functions can cleanly support. A proper query language is needed.

## BL-156 Impact Analysis

The DSM Central inbox entry requesting private-to-public repository mapping was the
decisive factor in eliminating Option D. The requirements:

| Requirement | NetworkX+JSON | FalkorDBLite | Neo4j |
|-------------|---------------|--------------|-------|
| Multi-repo graphs | Manual, fragile | Labels/properties | Labels/properties |
| Cross-repo node matching | Custom Python | Cypher queries | Cypher queries |
| Mapping persistence | JSON files | Built-in | Built-in |
| Match type classification | Custom enums | Relationship properties | Relationship properties |
| Drift detection queries | Custom code | Cypher traversals | Cypher traversals |
| Docker dependency | None | None | Required |

FalkorDBLite handles all BL-156 requirements while preserving the zero-infrastructure
CLI model.

## Migration Path

If FalkorDBLite proves insufficient (stability issues, missing Cypher features,
performance at larger scale), migration to Neo4j is straightforward:

1. Same Cypher queries (compatible subset)
2. Change connection string from embedded to `bolt://localhost:7687`
3. Add Docker-compose file and update CI workflow
4. Existing graph schema (nodes, relationships, properties) transfers directly

Estimated migration effort: 1 sprint.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| FalkorDBLite project instability | Medium | Medium | Cypher queries transfer to Neo4j; migration is ~1 sprint |
| Cypher compatibility gaps | Low | Low | Test critical queries against FalkorDBLite during EXP-005 |
| Performance at multi-repo scale | Low | Low | Current scale is ~500 nodes per repo; well within embedded DB capacity |
| FalkorDBLite subprocess model limitations | Low | Medium | Monitor for edge cases; fall back to Neo4j if blocking |

## Success Criteria

- [ ] FalkorDBLite can store and query the existing NetworkX graph (EXP-005)
- [ ] Multi-repo graphs can coexist with clear boundaries
- [ ] Cross-repo node matching queries work in FalkorDBLite's Cypher subset
- [ ] Persistence survives CLI restarts (data stored on disk)
- [ ] Test suite runs without Docker dependency

## Implementation Notes

- Add `falkordblite` to optional dependencies (`[graph]` extra, alongside networkx)
- Create `src/graph/graph_store.py` for FalkorDBLite integration
- Retain `graph_builder.py` (NetworkX) as the compilation step; add a persistence step that writes to FalkorDBLite
- EXP-005: Validate FalkorDBLite with existing graph data before building new features

## References

- Research: `dsm-docs/research/epoch-3-neo4j-landscape-research.md`
- Inbox input: `_inbox/dsm-central.md` (BL-156 private-to-public mapping)
- Prior graph work: `src/graph/` (Sprint 7, Epoch 2)
- EXP-004 results: NetworkX performance benchmarks (104ms build, 12.7MB, 50x margins)
- FalkorDBLite: https://github.com/FalkorDB/falkordblite