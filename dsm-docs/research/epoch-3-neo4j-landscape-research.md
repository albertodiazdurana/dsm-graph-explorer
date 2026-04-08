# Epoch 3 Research: Graph Database Landscape for Python CLI Projects

**Date:** 2026-03-09
**Project:** DSM Graph Explorer
**Scope:** Neo4j deployment, Python driver landscape, embedded alternatives, testing strategies, migration patterns
**Purpose:** Ground Epoch 3 planning with evidence-based technology choices
**Status:** Complete

---

## 1. Neo4j Deployment Options

### Docker (Standard Approach)
- Official images: `neo4j:community` and `neo4j:enterprise`
- Ports: 7474 (HTTP/Browser), 7687 (Bolt protocol)
- Default auth: `neo4j/neo4j`, prompts password change on first connect
- Data persistence via volume mount to `/data`

**Minimal docker-compose.yml:**
```yaml
services:
  neo4j:
    image: neo4j:community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/testpassword
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "testpassword", "RETURN 1"]
      interval: 10s
      timeout: 5s
      retries: 5
volumes:
  neo4j_data:
  neo4j_logs:
```

### Community vs Enterprise
- **Community (free, open source):** Single node, no clustering, no hot backups. Core engine + ACID + Cypher identical to Enterprise.
- **Enterprise:** Clustering, hot backups, RBAC, monitoring.
- **For this project:** Community Edition is sufficient. Single-user CLI tool with local graph storage.

### AuraDB (Cloud)
- Free tier: up to 200k nodes, 400k relationships, no credit card required
- Databases deleted after 30 days of inactivity
- Python driver connects identically (different URI)

### Embedded Mode
- **Neo4j does NOT support embedded/in-process mode in Python.** Embedded exists only for Java (JVM-based).
- The old `neo4j-embedded` Python package (via JPype) is abandoned.
- For Python, Neo4j always requires a separate server process.
- This is a significant architectural consideration for a CLI tool.

---

## 2. Python Driver Landscape

### Official `neo4j` Driver (Recommended)
- **Version:** 6.1.0 (January 2026)
- **Python support:** 3.10-3.14
- **Protocol:** Bolt (binary, efficient)
- **Features:** Connection pooling, automatic retries, cluster-aware routing, transaction management
- **Async support:** Full async/await via `AsyncGraphDatabase.driver()`
- **Install:** `pip install neo4j`

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
with driver.session() as session:
    result = session.run("MATCH (n) RETURN count(n) AS count")
    print(result.single()["count"])
driver.close()
```

### py2neo (DEPRECATED)
- **Status: End-of-life.** Neo4j officially announced EOL.
- Do not use for new projects.

### neomodel (OGM)
- **Version:** 6.0.1, actively maintained (Neo4j Labs)
- Object-Graph Mapper (OGM), class-based model definitions
- Adds convenience but introduces abstraction overhead
- Better suited for application development than CLI tools

### Recommendation
Use the official `neo4j` driver. Direct Cypher control suits a validation/exploration CLI. Avoid py2neo entirely. neomodel adds unnecessary OGM overhead for this use case.

---

## 3. Development & Testing Workflow

### Local Development
- Docker-compose for Neo4j server
- Environment variables for connection details (never hardcode)
- `docker-compose up -d` to start, `docker-compose down` to stop

### CI/CD with GitHub Actions
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      neo4j:
        image: neo4j:community
        env:
          NEO4J_AUTH: neo4j/testpassword
        ports:
          - 7474:7474
          - 7687:7687
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[test]"
      - run: pytest tests/ -v
```

### Testing Strategies

**testcontainers-python:**
- `pip install testcontainers[neo4j]`
- Spins up real Neo4j Docker container per test session
- Disposable containers, clean state each run

```python
import pytest
from testcontainers.neo4j import Neo4jContainer

@pytest.fixture(scope="session")
def neo4j_container():
    container = Neo4jContainer("neo4j:community")
    container.start()
    yield container
    container.stop()

@pytest.fixture(autouse=True)
def clean_db(neo4j_driver):
    yield
    with neo4j_driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
```

**Isolation strategies:**
1. Per-test cleanup: `MATCH (n) DETACH DELETE n` after each test
2. Transaction rollback: run each test in a transaction that rolls back (faster, limited)
3. Session-scoped container + per-test cleanup: best balance

**Recommended split:**
- Unit tests: mock the Neo4j driver/session (fast, no Docker dependency)
- Integration tests: testcontainers or CI service container, marked with `@pytest.mark.integration`

---

## 4. Lighter Alternatives to Neo4j

### Kuzu (ARCHIVED, October 2025)
- Was an excellent embedded, in-process graph database (like SQLite for graphs)
- Columnar storage, Cypher-compatible, very fast
- **Status: ARCHIVED.** GitHub repository set to read-only October 2025.
- **Not recommended for new projects.**

### FalkorDBLite (Strong Alternative)
- Successor to RedisGraph (EOL January 2025)
- **FalkorDBLite:** Embedded, zero-config Python graph database
  - `pip install falkordblite`
  - Forks a lightweight subprocess, communicates via Unix sockets
  - No Docker or port management needed
  - Cypher-compatible query language
  - **Closest thing to "SQLite for graphs" currently available in Python**
- Switch to full FalkorDB server for production/multi-tenant workloads
- Best for: integration tests, local prototyping, CLI tools, notebooks

### Memgraph
- In-memory, Cypher-compatible, runs as a server (Docker)
- Graph algorithms via MAGE library
- Heavier than needed for a CLI tool

### DuckPGQ (DuckDB Graph Extension)
- Graph queries via SQL/PGQ standard (not Cypher)
- Research project, work in progress
- Interesting long-term option given DuckDB's Python ecosystem presence

### Comparison

| Database       | Embedded? | Cypher? | Python Status     | Fit for CLI? |
|---------------|-----------|---------|-------------------|-------------|
| Neo4j         | No (Java only) | Yes | Driver v6.1, active | Good (with Docker) |
| FalkorDBLite  | Yes (subprocess) | Yes | Active | Excellent |
| Kuzu          | Yes | Yes | ARCHIVED | No |
| Memgraph      | No (server) | Yes | Active | Moderate |
| DuckPGQ       | Yes (DuckDB) | No (SQL/PGQ) | Research | Watch |

---

## 5. NetworkX to Graph Database Migration

### Import Pattern
```python
def import_networkx_graph(driver, G, node_label="Node", rel_type="CONNECTS"):
    with driver.session() as session:
        for node, attrs in G.nodes(data=True):
            props = {k: v for k, v in attrs.items()}
            props["id"] = str(node)
            session.run(f"CREATE (n:{node_label} $props)", props=props)

        for u, v, attrs in G.edges(data=True):
            session.run(
                f"MATCH (a:{node_label} {{id: $u}}), (b:{node_label} {{id: $v}}) "
                f"CREATE (a)-[r:{rel_type} $props]->(b)",
                u=str(u), v=str(v), props=attrs
            )
```

### Data Model Mapping
- NetworkX node -> Graph DB node (with label)
- NetworkX node attributes -> Node properties
- NetworkX edge -> Relationship (with type)
- NetworkX edge attributes -> Relationship properties
- DiGraph -> Directed relationships (natural fit)

### Performance Tips
- Use `UNWIND` with batched parameters instead of individual `CREATE` statements
- Create indexes/constraints on identifier properties before import
- Use `CALL { ... } IN TRANSACTIONS OF 1000 ROWS` for large imports

### Existing Tools
- **nxneo4j:** NetworkX-like API backed by Neo4j. Updated for Neo4j 4.x + GDS library.
- **Manual Cypher:** Most projects write custom import scripts (above pattern). Full control over labeling and properties.

---

## 6. Graph Data Modeling for Documentation References

### Proposed Node Labels
- `(:Document {path, name, type, last_modified})` — Files in the repository
- `(:Section {id, title, level, number, context_excerpt})` — Sections within documents
- `(:Reference {raw_text, target_path, target_section})` — Cross-references
- `(:Convention {code, severity, description})` — Linting rules

### Proposed Relationship Types
- `(:Document)-[:CONTAINS]->(:Section)` — Document structure
- `(:Section)-[:CONTAINS]->(:Section)` — Nested sections
- `(:Section)-[:REFERENCES]->(:Section)` — Cross-references
- `(:Reference)-[:FROM]->(:Section)` — Reference origin
- `(:Reference)-[:TO]->(:Section)` — Reference target
- `(:Reference)-[:VIOLATES]->(:Convention)` — Validation findings

### Modeling Best Practices
1. **Specific relationship names:** `REFERENCES`, `CONTAINS`, `VIOLATES` rather than generic `RELATES_TO`
2. **Unique identifiers:** Uniqueness constraints on `path` (Document), `id` (Section)
3. **Query-driven design:** Model based on queries needed ("find broken references", "most referenced sections")
4. **Temporal properties:** `last_validated`, `created_at` on relationships for audit trail

### Queries This Model Enables
- Find all broken references (References with no valid TO target)
- Show reference graph for a specific document
- Most-referenced sections (count incoming REFERENCES)
- Circular reference chains (cycle detection)
- Convention violation hotspots

---

## 7. Key Takeaways for Epoch 3

1. **Driver choice is clear:** Official `neo4j` Python driver v6.1. No alternatives worth considering.

2. **Deployment requires Docker:** Neo4j has no embedded mode for Python. This adds infrastructure complexity for a CLI tool. Users must run `docker-compose up` before using graph features.

3. **FalkorDBLite is a viable embedded alternative:** Cypher-compatible, zero-config, pip-installable. Avoids Docker dependency entirely for basic usage. Younger project, smaller ecosystem.

4. **Testing is well-supported:** testcontainers-python + pytest fixtures for integration tests, mocks for unit tests. CI via GitHub Actions service containers.

5. **Migration is straightforward:** The existing NetworkX graph (FILE/SECTION nodes, CONTAINS/REFERENCES edges) maps directly to the proposed data model. Import is a simple Cypher script.

6. **Architecture decision needed (DEC-006):**
   - **Option A: Full Neo4j** — Industry standard, rich ecosystem, Cypher, web browser UI. Requires Docker.
   - **Option B: FalkorDBLite** — Embedded, zero-config, Cypher-compatible. No Docker needed. Younger project.
   - **Option C: Dual backend** — Abstract the graph layer, support both. More engineering effort, maximum flexibility.
   - **Option D: Keep NetworkX + add persistence** — Serialize NetworkX graphs (pickle/JSON). No new dependency. Limited query power.

---

## Sources

- Neo4j Docker Documentation (operations-manual/current/docker/)
- Neo4j Python Driver Manual (dsm-docs/python-manual/current/)
- Neo4j Python Driver 6.1 API (dsm-docs/api/python-driver/current/)
- py2neo EOL Migration Guide (neo4j.com/blog/developer/py2neo-end-migration-guide/)
- neomodel Documentation (neomodel.readthedocs.io/)
- testcontainers-neo4j (pypi.org/project/testcontainers-neo4j/)
- Kuzu GitHub (archived October 2025)
- FalkorDBLite (github.com/FalkorDB/falkordblite)
- DuckPGQ Extension (duckdb.org/community_extensions/extensions/duckpgq)
- Neo4j Graph Data Modeling (dsm-docs/getting-started/data-modeling/)

---

**Last Updated:** 2026-03-09
**Next Step:** DEC-006 (Graph Database Selection) → Epoch 3 Plan