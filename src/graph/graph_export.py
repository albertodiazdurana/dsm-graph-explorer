"""GraphML export for DSM reference networks."""

import networkx as nx


def export_graphml(G: nx.DiGraph, path: str) -> None:
    """Export the reference graph to GraphML format.

    Args:
        G: The reference graph to export.
        path: File path for the GraphML output.
    """
    nx.write_graphml(G, path)
