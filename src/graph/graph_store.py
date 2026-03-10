"""FalkorDBLite persistence layer for DSM reference networks.

Wraps the FalkorDBLite embedded graph database to provide persistent storage
for the NetworkX DiGraph produced by graph_builder.py.

Architecture
------------
NetworkX (graph_builder.py) is the in-memory compilation layer:
  markdown files → parser → graph_builder → nx.DiGraph

GraphStore (this module) is the persistence layer:
  nx.DiGraph → GraphStore.write_graph() → FalkorDBLite on disk

The two layers are intentionally separate. NetworkX handles graph construction
logic; FalkorDBLite handles persistence, Cypher queries, and multi-repo support.

Schema
------
Nodes:
    (:Document {path, repo, git_ref})
        Corresponds to a FILE node in the NetworkX graph.
    (:Section {heading, number, level, line, document_path,
               context_excerpt, repo, git_ref})
        Corresponds to a SECTION node in the NetworkX graph.

Edges:
    (:Document)-[:CONTAINS {order}]->(:Section)
    (:Section)-[:REFERENCES {line, ref_type}]->(:Section)

Indexes (created on first write):
    Document.path  — enables fast MATCH by file path
    Section.number — enables fast MATCH by section number

Multi-repo support
------------------
Each repository is stored as a separate named graph within a single
FalkorDBLite file. This provides clean isolation while keeping all
repos in one DB file (DEC-006, Sprint 12 bridge graph approach).

Availability
------------
FalkorDBLite is an optional dependency (pip install .[graph]).
If not installed, FALKORDB_AVAILABLE is False and GraphStore raises
ImportError at instantiation time, matching the pattern used by
graph_builder.py (networkx) and similarity.py (scikit-learn).

References
----------
- DEC-006: docs/decisions/DEC-006-graph-database-selection.md
- DEC-007: docs/decisions/DEC-007-python-312-upgrade.md
- EXP-005: data/experiments/exp005_falkordb_integration.py (validated this API)
- Epoch 3 plan: docs/plans/epoch-3-plan.md (Phase 9.2)
- Deep-dive: docs/research/epoch-3-falkordblite-deep-dive.md
"""

from __future__ import annotations

try:
    from redislite.falkordb_client import FalkorDB as _FalkorDB

    FALKORDB_AVAILABLE = True
except ImportError:
    FALKORDB_AVAILABLE = False

try:
    import networkx as nx

    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False


class GraphStore:
    """Persistent graph storage backed by FalkorDBLite.

    Lifecycle::

        store = GraphStore("/path/to/db.falkordb")
        store.write_graph(nx_graph, repo_name="dsm-central", git_ref="HEAD")
        result = store.ro_query(
            "MATCH (d:Document) RETURN d.path",
            graph_name="dsm-central",
        )
        store.close()

    The db_path file persists across process restarts. Pass the same path
    in a new process to reopen the existing graph.
    """

    def __init__(self, db_path: str) -> None:
        """Open (or create) a FalkorDBLite database at db_path.

        Args:
            db_path: Path to the FalkorDB storage file. Created if it does
                not exist. Pass ":memory:" equivalent by omitting path (not
                recommended for production use).

        Raises:
            ImportError: If falkordblite is not installed.
        """
        if not FALKORDB_AVAILABLE:
            raise ImportError(
                "falkordblite is required for graph persistence. "
                "Install with: pip install '.[graph]'"
            )
        self._db = _FalkorDB(db_path)
        self._db_path = db_path

    def close(self) -> None:
        """Release the FalkorDBLite connection.

        After closing, the database file remains on disk and can be reopened
        with a new GraphStore instance. This method is idempotent.
        """
        if self._db is not None:
            del self._db
            self._db = None  # type: ignore[assignment]

    def graph_exists(self, graph_name: str) -> bool:
        """Return True if a named graph already exists in this database.

        Used to skip full rebuilds when the graph is already current.

        Args:
            graph_name: The named graph to check (e.g., repo name).
        """
        return graph_name in self._db.list_graphs()

    def write_graph(
        self,
        nx_graph: "nx.DiGraph",
        graph_name: str,
        git_ref: str = "HEAD",
    ) -> None:
        """Import a NetworkX DiGraph into FalkorDBLite.

        Translates the FILE/SECTION/CONTAINS/REFERENCES schema produced by
        graph_builder.py into FalkorDB :Document/:Section nodes and edges.

        If a graph with graph_name already exists, it is deleted and
        rewritten from scratch (full rebuild). For incremental updates,
        call graph_exists() first and skip the write if up to date.

        Args:
            nx_graph: DiGraph produced by graph_builder.build_reference_graph().
            graph_name: Name of the graph to write (becomes the FalkorDB
                named graph, typically the repo name).
            git_ref: Git ref to stamp on all nodes (e.g., "HEAD", a SHA, or
                a tag). Stored as a property; used for temporal queries
                in Sprint 10.
        """
        if not NETWORKX_AVAILABLE:
            raise ImportError(
                "networkx is required to import graphs. "
                "Install with: pip install '.[graph]'"
            )

        # Delete and recreate for a clean write (idempotent)
        g = self._db.select_graph(graph_name)
        if self.graph_exists(graph_name):
            g.delete()
            g = self._db.select_graph(graph_name)

        # Create indexes first (before any writes, for efficiency)
        self._create_indexes(g)

        # Partition NetworkX nodes by type
        file_nodes = [
            (node_id, attrs)
            for node_id, attrs in nx_graph.nodes(data=True)
            if attrs.get("type") == "FILE"
        ]
        section_nodes = [
            (node_id, attrs)
            for node_id, attrs in nx_graph.nodes(data=True)
            if attrs.get("type") == "SECTION"
        ]

        # Write :Document nodes (FILE → Document)
        for node_id, attrs in file_nodes:
            g.query(
                """
                CREATE (:Document {
                    path:    $path,
                    title:   $title,
                    repo:    $repo,
                    git_ref: $git_ref
                })
                """,
                params={
                    "path": node_id,
                    "title": attrs.get("title", ""),
                    "repo": graph_name,
                    "git_ref": git_ref,
                },
            )

        # Write :Section nodes (SECTION → Section)
        for node_id, attrs in section_nodes:
            g.query(
                """
                CREATE (:Section {
                    node_id:         $node_id,
                    heading:         $heading,
                    number:          $number,
                    level:           $level,
                    line:            $line,
                    document_path:   $document_path,
                    context_excerpt: $context_excerpt,
                    repo:            $repo,
                    git_ref:         $git_ref
                })
                """,
                params={
                    "node_id": node_id,
                    "heading": attrs.get("title", ""),
                    "number": attrs.get("number", ""),
                    "level": attrs.get("level", 0),
                    "line": attrs.get("line", 0),
                    "document_path": attrs.get("file", ""),
                    "context_excerpt": attrs.get("context_excerpt", ""),
                    "repo": graph_name,
                    "git_ref": git_ref,
                },
            )

        # Write CONTAINS edges (FILE → SECTION)
        contains_order: dict[str, int] = {}
        for source_id, target_id, edge_attrs in nx_graph.edges(data=True):
            if edge_attrs.get("type") != "CONTAINS":
                continue
            contains_order[source_id] = contains_order.get(source_id, 0) + 1
            g.query(
                """
                MATCH (d:Document {path: $doc_path})
                MATCH (s:Section {node_id: $sec_id})
                CREATE (d)-[:CONTAINS {order: $order}]->(s)
                """,
                params={
                    "doc_path": source_id,
                    "sec_id": target_id,
                    "order": contains_order[source_id],
                },
            )

        # Write REFERENCES edges (SECTION → SECTION)
        for source_id, target_id, edge_attrs in nx_graph.edges(data=True):
            if edge_attrs.get("type") != "REFERENCES":
                continue
            g.query(
                """
                MATCH (s1:Section {node_id: $src_id})
                MATCH (s2:Section {node_id: $tgt_id})
                CREATE (s1)-[:REFERENCES {line: $line, ref_type: $ref_type}]->(s2)
                """,
                params={
                    "src_id": source_id,
                    "tgt_id": target_id,
                    "line": edge_attrs.get("line", 0),
                    "ref_type": edge_attrs.get("ref_type", ""),
                },
            )

    def query(
        self,
        cypher: str,
        graph_name: str,
        params: dict | None = None,
    ) -> object:
        """Execute a read-write Cypher query against a named graph.

        Args:
            cypher: Cypher query string. Use $param syntax for all values.
            graph_name: Named graph to query.
            params: Optional parameter dict for $param substitutions.

        Returns:
            FalkorDB query result object (iterate result.result_set for rows).
        """
        g = self._db.select_graph(graph_name)
        return g.query(cypher, params=params or {})

    def ro_query(
        self,
        cypher: str,
        graph_name: str,
        params: dict | None = None,
    ) -> object:
        """Execute a read-only Cypher query against a named graph.

        Use this for all MATCH/RETURN queries. FalkorDB uses this as an
        optimization hint (no write locks acquired).

        Args:
            cypher: Cypher query string. Use $param syntax for all values.
            graph_name: Named graph to query.
            params: Optional parameter dict for $param substitutions.

        Returns:
            FalkorDB query result object (iterate result.result_set for rows).
        """
        g = self._db.select_graph(graph_name)
        return g.ro_query(cypher, params=params or {})

    def list_graphs(self) -> list[str]:
        """Return all named graphs in this database."""
        return self._db.list_graphs()

    def _create_indexes(self, g: object) -> None:
        """Create range indexes for efficient MATCH lookups.

        Called once per graph before any writes. Safe to call on a fresh
        graph (indexes do not exist yet).

        Indexes created:
            Document.path  — primary lookup key for documents
            Section.number — lookup by section number
        """
        g.query("CREATE INDEX FOR (d:Document) ON (d.path)")  # type: ignore[union-attr]
        g.query("CREATE INDEX FOR (s:Section) ON (s.number)")  # type: ignore[union-attr]