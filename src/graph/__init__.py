"""Graph construction, query, and persistence modules for DSM reference networks."""

try:
    from graph.graph_builder import build_reference_graph
    from graph.graph_queries import (
        most_referenced_sections,
        orphan_sections,
        reference_chain,
    )
except ImportError:
    # networkx not installed; graph building/query features unavailable
    build_reference_graph = None  # type: ignore[assignment]
    most_referenced_sections = None  # type: ignore[assignment]
    orphan_sections = None  # type: ignore[assignment]
    reference_chain = None  # type: ignore[assignment]

from graph.graph_store import FALKORDB_AVAILABLE, GraphStore

__all__ = [
    "build_reference_graph",
    "most_referenced_sections",
    "orphan_sections",
    "reference_chain",
    "GraphStore",
    "FALKORDB_AVAILABLE",
]
