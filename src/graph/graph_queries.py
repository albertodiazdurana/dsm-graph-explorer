"""Graph query functions for DSM reference networks.

Provides analytical queries over the DiGraph built by graph_builder:
- most_referenced_sections: hub sections with highest incoming references
- orphan_sections: sections never referenced by other sections
- reference_chain: BFS traversal following REFERENCES edges
"""

from collections import deque

import networkx as nx


def most_referenced_sections(
    G: nx.DiGraph, n: int = 10
) -> list[tuple[str, int]]:
    """Find the n most-referenced SECTION nodes.

    Counts incoming REFERENCES edges (ignoring CONTAINS edges) for each
    SECTION node and returns the top n sorted by count descending.

    Returns:
        List of (node_id, reference_count) tuples, sorted descending.
        Only includes sections with at least one incoming reference.
    """
    section_nodes = [
        node for node, data in G.nodes(data=True)
        if data.get("type") == "SECTION"
    ]
    ref_counts = []
    for node in section_nodes:
        in_refs = sum(
            1
            for _, _, data in G.in_edges(node, data=True)
            if data.get("type") == "REFERENCES"
        )
        if in_refs > 0:
            ref_counts.append((node, in_refs))

    ref_counts.sort(key=lambda x: x[1], reverse=True)
    return ref_counts[:n]


def orphan_sections(G: nx.DiGraph) -> list[str]:
    """Find SECTION nodes that are never referenced by other sections.

    A section is an orphan if it has zero incoming REFERENCES edges.
    CONTAINS edges (from FILE nodes) are ignored.

    Returns:
        List of orphan section node IDs.
    """
    section_nodes = [
        node for node, data in G.nodes(data=True)
        if data.get("type") == "SECTION"
    ]
    orphans = []
    for node in section_nodes:
        in_refs = sum(
            1
            for _, _, data in G.in_edges(node, data=True)
            if data.get("type") == "REFERENCES"
        )
        if in_refs == 0:
            orphans.append(node)
    return orphans


def reference_chain(
    G: nx.DiGraph, section_id: str, max_depth: int = 10
) -> list[str]:
    """Follow the reference chain from a section using BFS.

    Traverses outgoing REFERENCES edges from the given section,
    collecting all reachable sections up to max_depth levels.

    Args:
        G: The reference graph.
        section_id: Starting section node ID.
        max_depth: Maximum BFS depth to prevent unbounded traversal.

    Returns:
        Ordered list of visited section node IDs (source excluded).
        Empty list if section_id does not exist in the graph.
    """
    if section_id not in G:
        return []

    visited = []
    seen = {section_id}
    queue: deque[tuple[str, int]] = deque([(section_id, 0)])

    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            continue

        for _, target, data in G.out_edges(current, data=True):
            if data.get("type") == "REFERENCES" and target not in seen:
                seen.add(target)
                visited.append(target)
                queue.append((target, depth + 1))

    return visited
