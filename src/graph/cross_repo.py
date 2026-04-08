"""Cross-repo bridge graph for typed edges between DSM repositories.

Manages a dedicated named graph (_cross_repo by default) within an existing
GraphStore. The bridge graph stores lightweight :RepoEntity anchor nodes
and :CROSS_REF edges that represent cross-repo relationships.

Edge types
----------
- INBOX_NOTIFICATION: inbox entry sent from one repo to another
- AT_IMPORT: @path/to/external/file.md reference
- ECOSYSTEM_LINK: Ecosystem Path Registry entry between repos
- MAPS_TO: entity mapping from compare_inventories (BL-156)

Schema
------
Nodes:
    (:RepoEntity {repo, entity_id})
        Anchor node representing an entity in a specific repo.
        Created via MERGE to avoid duplicates when the same entity
        participates in multiple edges.

Edges:
    (:RepoEntity)-[:CROSS_REF {type, props_json}]->(:RepoEntity)
        Single edge label with a type property distinguishing the
        relationship kind. Extra properties stored as JSON string
        (FalkorDB does not support nested map properties).

References
----------
- Epoch 3 plan: dsm-docs/plans/epoch-3-plan.md (Phase 12.1)
- DEC-006: dsm-docs/decisions/DEC-006-graph-database-selection.md
"""

from __future__ import annotations

import json
from enum import StrEnum
from typing import TYPE_CHECKING

from graph.graph_store import FALKORDB_AVAILABLE, GraphStore

if TYPE_CHECKING:
    from graph.repo_diff import MatchResult


class EdgeType(StrEnum):
    """Cross-repo edge types."""

    INBOX_NOTIFICATION = "INBOX_NOTIFICATION"
    AT_IMPORT = "AT_IMPORT"
    ECOSYSTEM_LINK = "ECOSYSTEM_LINK"
    MAPS_TO = "MAPS_TO"


# Default bridge graph name (convention from epoch-3 plan)
BRIDGE_GRAPH_NAME = "_cross_repo"


class CrossRepoBridge:
    """Manages cross-repo edges in a dedicated FalkorDB bridge graph.

    Wraps an existing GraphStore instance, using a separate named graph
    for cross-repo relationships. This keeps per-repo graphs clean while
    enabling cross-repo queries.

    Usage::

        store = GraphStore("/path/to/db.falkordb")
        bridge = CrossRepoBridge(store)
        bridge.add_edge(
            source_repo="dsm-central",
            source_entity_id="backlog/BL-156",
            target_repo="dsm-graph-explorer",
            target_entity_id="_inbox/2026-03-01-bl156",
            edge_type=EdgeType.INBOX_NOTIFICATION,
            properties={"date": "2026-03-01"},
        )
        edges = bridge.edges_for_repo("dsm-central")
    """

    def __init__(
        self,
        store: GraphStore,
        graph_name: str = BRIDGE_GRAPH_NAME,
    ) -> None:
        if not FALKORDB_AVAILABLE:
            raise ImportError(
                "falkordblite is required for cross-repo bridge. "
                "Install with: pip install '.[graph]'"
            )
        self._store = store
        self._graph_name = graph_name
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        """Create indexes on the bridge graph for efficient lookups."""
        g = self._store._db.select_graph(self._graph_name)
        g.query("CREATE INDEX FOR (e:RepoEntity) ON (e.repo)")
        g.query("CREATE INDEX FOR (e:RepoEntity) ON (e.entity_id)")

    def add_edge(
        self,
        source_repo: str,
        source_entity_id: str,
        target_repo: str,
        target_entity_id: str,
        edge_type: EdgeType,
        properties: dict | None = None,
    ) -> None:
        """Add a cross-repo edge between two entities.

        Source and target RepoEntity nodes are created via MERGE,
        so the same entity can participate in multiple edges without
        duplication.

        Args:
            source_repo: Name of the source repository.
            source_entity_id: Entity identifier in the source repo.
            target_repo: Name of the target repository.
            target_entity_id: Entity identifier in the target repo.
            edge_type: Type of cross-repo relationship.
            properties: Optional extra properties stored on the edge.
        """
        props_json = json.dumps(properties) if properties else "{}"

        self._store.query(
            """
            MERGE (src:RepoEntity {repo: $src_repo, entity_id: $src_eid})
            MERGE (tgt:RepoEntity {repo: $tgt_repo, entity_id: $tgt_eid})
            CREATE (src)-[:CROSS_REF {
                type: $edge_type,
                props_json: $props_json
            }]->(tgt)
            """,
            graph_name=self._graph_name,
            params={
                "src_repo": source_repo,
                "src_eid": source_entity_id,
                "tgt_repo": target_repo,
                "tgt_eid": target_entity_id,
                "edge_type": str(edge_type),
                "props_json": props_json,
            },
        )

    def all_edges(self) -> list[dict]:
        """Return all cross-repo edges in the bridge graph.

        Returns:
            List of edge dicts with keys: source_repo, source_entity_id,
            target_repo, target_entity_id, edge_type, properties.
        """
        result = self._store.ro_query(
            """
            MATCH (src:RepoEntity)-[r:CROSS_REF]->(tgt:RepoEntity)
            RETURN src.repo, src.entity_id,
                   tgt.repo, tgt.entity_id,
                   r.type, r.props_json
            """,
            graph_name=self._graph_name,
        )
        return self._parse_edges(result)

    def edges_for_repo(self, repo_name: str) -> list[dict]:
        """Return all cross-repo edges involving a specific repository.

        Matches edges where the repo is either source or target.

        Args:
            repo_name: Repository name to filter by.
        """
        result = self._store.ro_query(
            """
            MATCH (src:RepoEntity)-[r:CROSS_REF]->(tgt:RepoEntity)
            WHERE src.repo = $repo OR tgt.repo = $repo
            RETURN src.repo, src.entity_id,
                   tgt.repo, tgt.entity_id,
                   r.type, r.props_json
            """,
            graph_name=self._graph_name,
            params={"repo": repo_name},
        )
        return self._parse_edges(result)

    def edges_by_type(self, edge_type: EdgeType) -> list[dict]:
        """Return all cross-repo edges of a specific type.

        Args:
            edge_type: Edge type to filter by.
        """
        result = self._store.ro_query(
            """
            MATCH (src:RepoEntity)-[r:CROSS_REF]->(tgt:RepoEntity)
            WHERE r.type = $edge_type
            RETURN src.repo, src.entity_id,
                   tgt.repo, tgt.entity_id,
                   r.type, r.props_json
            """,
            graph_name=self._graph_name,
            params={"edge_type": str(edge_type)},
        )
        return self._parse_edges(result)

    def store_mapping(
        self,
        results: list[MatchResult],
        repo_a_name: str,
        repo_b_name: str,
    ) -> int:
        """Store compare_inventories results as MAPS_TO edges.

        Creates a MAPS_TO edge for each matched pair (IDENTICAL, RENAMED,
        MODIFIED). ADDED and REMOVED results are skipped (no counterpart
        entity to link to).

        Args:
            results: Output from compare_inventories().
            repo_a_name: Name of inventory A's repository.
            repo_b_name: Name of inventory B's repository.

        Returns:
            Number of MAPS_TO edges created.
        """
        count = 0
        for r in results:
            if r.entity_a is None or r.entity_b is None:
                continue
            self.add_edge(
                source_repo=repo_a_name,
                source_entity_id=r.entity_a.id,
                target_repo=repo_b_name,
                target_entity_id=r.entity_b.id,
                edge_type=EdgeType.MAPS_TO,
                properties={
                    "match_type": str(r.match_type),
                    "similarity_score": r.similarity_score,
                },
            )
            count += 1
        return count

    def node_count(self) -> int:
        """Return the number of RepoEntity nodes in the bridge graph."""
        result = self._store.ro_query(
            "MATCH (e:RepoEntity) RETURN count(e)",
            graph_name=self._graph_name,
        )
        rows = result.result_set
        if rows:
            return rows[0][0]
        return 0

    @staticmethod
    def _parse_edges(result: object) -> list[dict]:
        """Convert FalkorDB result rows into edge dicts."""
        edges = []
        for row in result.result_set:
            props_json = row[5] if row[5] else "{}"
            props = json.loads(props_json)
            edges.append({
                "source_repo": row[0],
                "source_entity_id": row[1],
                "target_repo": row[2],
                "target_entity_id": row[3],
                "edge_type": row[4],
                "properties": props,
            })
        return edges