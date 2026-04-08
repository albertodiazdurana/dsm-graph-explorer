# Epoch 3 Research: FalkorDBLite Deep-Dive

**Date:** 2026-03-09
**Project:** DSM Graph Explorer
**Scope:** FalkorDBLite implementation details, Cypher subset, persistence, multi-graph, Python API, testing patterns, limitations
**Purpose:** Resolve implementation-level unknowns for the selected graph database (DEC-006)
**Prerequisite:** [Landscape research](epoch-3-neo4j-landscape-research.md), [DEC-006](../decisions/DEC-006-graph-database-selection.md)
**Status:** Complete

---

## 1. Installation and Platform

**Package:** `falkordblite` (PyPI)
**Current version:** 0.9.0 (March 2, 2026)
**License:** BSD (OSI Approved)
**Status:** Beta

```bash
pip install falkordblite
```

### Python Version Requirement

**Python 3.12+ only.** No support for 3.10 or 3.11.

This is a **critical finding**: our project currently targets Python 3.10 (per `pyproject.toml`). See Section 8 for mitigation options.

### Platform Support

| Platform | Status |
|----------|--------|
| Linux x86-64 | Supported |
| Linux ARM64 | Supported |
| macOS x86-64 | Supported (requires `brew install libomp`) |
| macOS ARM64 | Supported (requires `brew install libomp`) |
| Windows | Not supported (must use WSL2) |

### Dependencies

- `redis>=4.5` (Python Redis client)
- `psutil` (process utilities)
- `setuptools>38.0`

### Architecture

FalkorDBLite is **not** a pure Python library. It bundles a compiled `redis-server` binary and `falkordb.so` C module. It forks a lightweight subprocess communicating via Unix domain sockets. This provides process isolation: a crash in the DB does not crash the Python app.

---

## 2. Python API

### Import Path

```python
from redislite.falkordb_client import FalkorDB       # sync
from redislite.async_falkordb_client import AsyncFalkorDB  # async
```

Note: the import path is `redislite`, not `falkordblite`, reflecting the redislite heritage.

### Graph Creation and Selection

```python
# Persistent (file path specified)
db = FalkorDB('/tmp/falkordb.db')

# Ephemeral (no path, uses temp file, lost when process ends)
db = FalkorDB()

# Select or create a named graph
g = db.select_graph('social')
```

### Query Execution

```python
# Read-write queries
result = g.query('CREATE (p:Person {name: "Alice", age: 30}) RETURN p')

# Read-only queries (optimization hint)
result = g.ro_query('MATCH (p:Person) RETURN p.name, p.age')

# Parameterized queries (prevents injection)
result = g.query(
    'CREATE (p:Person {name: $name, age: $age}) RETURN p',
    params={'name': 'Alice', 'age': 30}
)
```

### Result Handling

```python
result = g.query('MATCH (p:Person) RETURN p.name, p.age')
for row in result.result_set:
    print(row)  # each row is a list of values
```

### Database Management

```python
db.list_graphs()    # returns list of all graph names
g.delete()          # deletes the graph and all its data
db.close()          # async version: closes the connection
```

### API Compatibility

The API mirrors `falkordb-py` (the standard FalkorDB Python client) exactly. Migrating to a production FalkorDB server requires changing only the import and connection initialization; all query code stays identical.

---

## 3. Cypher Subset Support

### Fully Supported Clauses

| Clause | Status | Notes |
|--------|--------|-------|
| `CREATE` | Supported | |
| `MATCH` | Supported | |
| `OPTIONAL MATCH` | Supported | |
| `MERGE` | Supported | ON CREATE SET, ON MATCH SET |
| `DELETE` | Supported | DETACH DELETE |
| `SET` | Supported | |
| `REMOVE` | Supported | Property and label removal |
| `WITH` | Supported | |
| `UNWIND` | Supported | |
| `RETURN` / `AS` | Supported | |
| `WHERE` | Supported | |
| `ORDER BY` / `SKIP` / `LIMIT` | Supported | |
| `UNION` / `UNION ALL` | Supported | |
| `FOREACH` | Supported | Updating clauses only |
| `CALL {}` (subqueries) | Supported | Returning and non-returning |
| `CALL` (procedures) | Supported | |

### Supported Types

- **Structural:** nodes, relationships, path variables
- **Composite:** lists, maps
- **Temporal:** Date, DateTime, LocalDateTime, Time, LocalTime, Duration
- **Literal:** 64-bit numerics, strings, booleans, NULL

### Supported Patterns

- Variable-length paths: `(a)-[:KNOWS*1..3]->(b)`
- Path variables (alternating node/relationship sequences)
- Pattern comprehensions

### Operators

- Mathematical operators
- String: `STARTS WITH`, `ENDS WITH`, `CONTAINS`
- Boolean: `AND`, `OR`, `NOT`, `XOR`
- Parameters: `$param_name` syntax

### Indexes

| Type | Description |
|------|-------------|
| Range indexes | Single-property, on node labels and relationship types |
| Full-text indexes | RediSearch-based (stemming, stopwords, phonetic, TF-IDF) |
| Vector indexes | Nearest-neighbor (Euclidean/cosine distance) |

```cypher
CREATE INDEX FOR (p:Person) ON (p.name)
CREATE INDEX FOR ()-[r:KNOWS]-() ON (r.since)
```

### Constraints

- **UNIQUE constraints** (require a supporting index first)
- **MANDATORY constraints** (enforce property existence)
- Created via Redis command: `GRAPH.CONSTRAINT CREATE ...`

### Built-in Procedures

- `db.labels()`, `db.relationshipTypes()`, `db.propertyKeys()`
- `db.indexes()`, `db.constraints()`
- `db.meta.stats()` (label counts, rel counts, node counts)
- `db.idx.fulltext.createNodeIndex()`, `db.idx.fulltext.queryNodes()`
- `algo.pageRank()`, `algo.BFS()`, `algo.MSF()`

### FalkorDB-Specific Extensions

- `GRAPH.EXPLAIN` / `GRAPH.PROFILE` (execution plans)
- `GRAPH.SLOWLOG` (up to 10 slowest queries)
- Rich function library: JSON functions, similarity functions (`jaccard`), text functions (`levenshtein`, `jaroWinkler`), collection functions (`frequencies`, `intersection`, `shuffle`, `union`, `zip`)

### NOT Supported (vs Neo4j)

| Feature | Status |
|---------|--------|
| Label expressions `(n:A\|B)` | Not supported |
| Regex operator `=~` | Not supported |
| Multi-statement ACID transactions | Not supported (single-query atomicity only) |
| APOC library | No equivalent |
| User-defined functions (UDFs) | Not supported |
| Schema retrieval via Cypher | Must use procedures |

---

## 4. Persistence Model

### Storage Mechanism

Data is stored via Redis RDB snapshots to a file specified at construction time. Data lives **in-memory** during operation.

```python
# Persistent: data survives process restarts
db = FalkorDB('/tmp/falkordb.db')

# Ephemeral: lost when process ends
db = FalkorDB()
```

### Configurable Storage Path

Yes, controlled by the constructor argument. Associated metadata files (`.db.settings`, `.pid`) are created alongside.

### Process Restart Behavior

```python
# Session 1
db = FalkorDB('/tmp/data.db')
g = db.select_graph('social')
g.query('CREATE (p:Person {name: "Alice"})')
# Process ends

# Session 2 (new process)
db = FalkorDB('/tmp/data.db')
g = db.select_graph('social')
result = g.query('MATCH (p:Person) RETURN p.name')  # Alice is still there
```

### Backup

The `.db` file is a standard Redis RDB file. Copy it for backup. No built-in export-to-CSV/JSON, but Cypher queries can extract data programmatically.

### Memory Constraint

Dataset must fit in RAM. No disk-based overflow. FalkorDB recommends 4GB RAM minimum.

---

## 5. Multi-Graph Support

**Fully supported.** Multiple named graphs coexist within a single FalkorDBLite instance.

```python
db = FalkorDB('/tmp/multi.db')

repo_a = db.select_graph('repo_alpha')
repo_b = db.select_graph('repo_beta')

repo_a.query('CREATE (d:Document {path: "README.md"})')
repo_b.query('CREATE (d:Document {path: "setup.py"})')

db.list_graphs()  # ['repo_alpha', 'repo_beta']
```

### Isolation

Graphs are independent: nodes, relationships, labels, indexes, and constraints are fully isolated per graph.

### Cross-Graph Queries

**Not supported.** No single Cypher statement can span multiple graphs. Cross-graph operations must happen at the application level.

### Multi-Repo Design Implications (BL-156)

Two approaches for multi-repository support:

| Approach | Pros | Cons |
|----------|------|------|
| Separate graph per repo | Clean isolation, independent lifecycle | No cross-repo edge traversal in Cypher |
| Single graph, `repo` property | Cross-repo edges queryable | Must filter by repo, larger graph |

Recommendation: start with separate graphs per repo (simpler), add a cross-repo "bridge" graph later if cross-repo edges prove valuable.

---

## 6. Known Limitations

### Critical for This Project

1. **Python 3.12+ only** (project currently targets 3.10)
2. **Beta status** (API may change)
3. **No multi-statement transactions** (single-query atomicity only)

### Platform and Performance

- No native Windows support (WSL2 required, which we already use)
- In-memory architecture, RAM-bound
- Single-threaded writes (serialized by Redis event loop)
- Concurrent reads are safe (`ro_query`)

### Missing vs Full FalkorDB Server

- No clustering or replication
- No multi-tenant access control
- No network access (Unix socket only)

### Known Gotchas

- Editable installs (`pip install -e .`) fail; use `pip install .`
- Import path is `redislite.falkordb_client`, not `falkordblite`
- Permission issues with `falkordb.so` may require `chmod +x`
- Bundled `redis-server` binary; version conflicts with system Redis possible

---

## 7. Testing Patterns

### Recommended Fixture: Shared DB, Per-Test Graphs

```python
import pytest
from redislite.falkordb_client import FalkorDB

@pytest.fixture(scope="session")
def falkor_db(tmp_path_factory):
    """Single FalkorDBLite instance for all tests (avoids subprocess overhead)."""
    db_path = str(tmp_path_factory.mktemp("data") / "test.db")
    return FalkorDB(db_path)

@pytest.fixture
def graph(falkor_db):
    """Each test gets a uniquely-named graph for isolation."""
    import uuid
    graph_name = f"test_{uuid.uuid4().hex[:8]}"
    g = falkor_db.select_graph(graph_name)
    yield g
    g.delete()
```

### Alternative: Per-Test DB (Maximum Isolation)

```python
@pytest.fixture
def db(tmp_path):
    """Fresh FalkorDBLite per test. Slower but fully isolated."""
    return FalkorDB(str(tmp_path / "test.db"))
```

### Cleanup

- `g.delete()` removes all nodes, edges, and indexes in a graph
- `tmp_path` / `tmp_path_factory` ensures files are cleaned up after test session
- The subprocess is cleaned up when the FalkorDB object is garbage collected

### Performance Considerations

- Subprocess startup: ~100-500ms per instance
- Node creation: >1 million nodes in <0.5 seconds
- Read queries on small graphs (hundreds of nodes): sub-millisecond
- Use `ro_query()` for read-only queries (optimization hint)

### Async Testing

```python
@pytest.fixture
async def async_db(tmp_path):
    db = AsyncFalkorDB(str(tmp_path / "test.db"))
    yield db
    await db.close()
```

---

## 8. Python Version Mitigation

DEC-006 selected FalkorDBLite assuming it would fit our pip-install CLI model. The Python 3.12+ requirement creates a compatibility gap.

### Options

| Option | Description | Impact |
|--------|-------------|--------|
| **A. Upgrade to 3.12+** | Change `pyproject.toml` minimum to 3.12 | Breaking for 3.10/3.11 users. Simplest technically. |
| **B. Optional dependency** | FalkorDBLite as optional extra (`pip install .[graph]`), gate on Python version | Preserves 3.10 compatibility for non-graph features. Graph features require 3.12+. |
| **C. Docker FalkorDB** | Use `falkordb` client (supports 3.10+) with Docker server | Abandons embedded model. Requires Docker. Contradicts DEC-006 rationale. |
| **D. Alternative DB** | Revisit DEC-006 with a different embedded option | Significant rework. No clear better alternative exists. |

**Recommended: Option B.** Make FalkorDBLite an optional dependency with a clear 3.12+ gate. This preserves the existing CLI for 3.10 users while enabling graph features for 3.12+ users. The import guard pattern:

```python
try:
    from redislite.falkordb_client import FalkorDB
    FALKORDB_AVAILABLE = True
except ImportError:
    FALKORDB_AVAILABLE = False
```

This aligns with how `scikit-learn` and `networkx` are already handled as optional dependencies in the project.

---

## 9. Data Model Compatibility

Our target data model (from Epoch 2 Sprint 7):

| Entity | Graph Element | Key Properties |
|--------|---------------|----------------|
| Document | Node `:Document` | `path`, `repo`, `git_ref` |
| Section | Node `:Section` | `heading`, `level`, `document_path` |
| Reference | Node `:Reference` | `target_path`, `source_section` |
| Contains | Edge `(:Document)-[:CONTAINS]->(:Section)` | `order` |
| References | Edge `(:Section)-[:REFERENCES]->(:Document)` | `line_number` |

### FalkorDBLite Compatibility

All elements are fully supported:
- Node labels: supported
- Edge types: supported
- Properties (strings, integers): supported
- Indexes on `path`, `heading`: supported via `CREATE INDEX`
- Variable-length paths (e.g., finding transitive references): supported
- `MERGE` for idempotent upserts: supported

### Example Queries

```cypher
-- Create a document with sections
CREATE (d:Document {path: 'README.md', repo: 'dsm-graph-explorer'})
CREATE (s1:Section {heading: 'Installation', level: 2})
CREATE (s2:Section {heading: 'Usage', level: 2})
CREATE (d)-[:CONTAINS {order: 1}]->(s1)
CREATE (d)-[:CONTAINS {order: 2}]->(s2)

-- Find all sections in a document
MATCH (d:Document {path: 'README.md'})-[:CONTAINS]->(s:Section)
RETURN s.heading, s.level ORDER BY s.level

-- Find cross-document references
MATCH (s:Section)-[:REFERENCES]->(d:Document)
WHERE s.document_path <> d.path
RETURN s.heading, d.path

-- Variable-length path: transitive reference chains
MATCH p = (d1:Document)-[:CONTAINS]->(:Section)-[:REFERENCES*1..3]->(d2:Document)
RETURN d1.path, d2.path, length(p)
```

---

## 10. Summary

| Question | Answer |
|----------|--------|
| Cypher subset sufficient? | Yes, all needed features supported |
| Persistence? | File-based, survives restarts |
| Multi-graph? | Yes, fully isolated named graphs |
| Python API usable? | Yes, clean sync/async API |
| Testing friendly? | Yes, tmp_path + per-test graphs |
| Data model compatible? | Yes, all node/edge patterns work |
| **Blocker?** | **Python 3.12+ requirement (mitigated by Option B)** |

**Sources:** [PyPI](https://pypi.org/project/falkordblite/), [GitHub](https://github.com/FalkorDB/falkordblite), [FalkorDB docs](https://docs.falkordb.com/), [Cypher coverage](https://docs.falkordb.com/cypher/cypher-support.html)