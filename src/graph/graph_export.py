"""GraphML export for DSM reference networks."""

import networkx as nx


def _sanitize_none_attrs(G: nx.DiGraph) -> nx.DiGraph:
    """Return a copy of G with None attribute values replaced by empty strings.

    NetworkX's GraphML writer rejects NoneType values. Unnumbered headings
    have number=None in the graph; this function sanitizes them for export.
    """
    H = G.copy()
    for node in H.nodes:
        for key, value in H.nodes[node].items():
            if value is None:
                H.nodes[node][key] = ""
    for u, v, data in H.edges(data=True):
        for key, value in data.items():
            if value is None:
                data[key] = ""
    return H


def export_graphml(G: nx.DiGraph, path: str) -> None:
    """Export the reference graph to GraphML format.

    Sanitizes None attribute values to empty strings before writing,
    since NetworkX's GraphML writer rejects NoneType.

    Args:
        G: The reference graph to export.
        path: File path for the GraphML output.
    """
    H = _sanitize_none_attrs(G)
    nx.write_graphml(H, path)
