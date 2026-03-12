"""Temporal diff: compare graph snapshots at two git refs.

Builds two NetworkX graphs from historical git refs, then compares
node sets to identify added, removed, and changed documents/sections.
"""

from dataclasses import dataclass, field
from pathlib import Path

import networkx as nx

from git_ref.git_resolver import (
    GitRefError,
    find_repo_root,
    list_files_at_ref,
    read_file_at_ref,
    resolve_ref,
)
from parser.cross_ref_extractor import extract_cross_references_from_content
from parser.markdown_parser import parse_markdown_content
from validator.cross_ref_validator import build_section_lookup


@dataclass
class ChangedNode:
    """A node whose properties differ between two refs."""

    node_id: str
    node_type: str
    field: str
    old_value: str
    new_value: str


@dataclass
class DiffResult:
    """Result of comparing two graph snapshots."""

    ref_a: str
    ref_b: str
    added_files: list[str] = field(default_factory=list)
    removed_files: list[str] = field(default_factory=list)
    added_sections: list[str] = field(default_factory=list)
    removed_sections: list[str] = field(default_factory=list)
    changed: list[ChangedNode] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(
            self.added_files
            or self.removed_files
            or self.added_sections
            or self.removed_sections
            or self.changed
        )


def _build_graph_at_ref(repo_path: Path, sha: str) -> nx.DiGraph:
    """Build a NetworkX graph from files at a given git ref.

    Args:
        repo_path: Path to the git repository root.
        sha: Full commit SHA.

    Returns:
        NetworkX DiGraph with FILE and SECTION nodes.
    """
    from graph.graph_builder import build_reference_graph

    files = list_files_at_ref(repo_path, sha)
    documents = []
    references = {}

    for file_path in files:
        try:
            content = read_file_at_ref(repo_path, sha, file_path)
        except GitRefError:
            continue

        doc = parse_markdown_content(content, file_path)
        documents.append(doc)
        refs = extract_cross_references_from_content(content, file_path)
        if refs:
            references[doc.file] = refs

    section_lookup = build_section_lookup(documents)
    return build_reference_graph(documents, references, section_lookup)


def _compare_graphs(
    graph_a: nx.DiGraph, graph_b: nx.DiGraph, ref_a: str, ref_b: str
) -> DiffResult:
    """Compare two NetworkX graphs and produce a DiffResult.

    Args:
        graph_a: Graph at ref_a.
        graph_b: Graph at ref_b.
        ref_a: Label for the first ref.
        ref_b: Label for the second ref.

    Returns:
        DiffResult with added, removed, and changed nodes.
    """
    result = DiffResult(ref_a=ref_a, ref_b=ref_b)

    nodes_a = {n: d for n, d in graph_a.nodes(data=True)}
    nodes_b = {n: d for n, d in graph_b.nodes(data=True)}

    ids_a = set(nodes_a.keys())
    ids_b = set(nodes_b.keys())

    added_ids = sorted(ids_b - ids_a)
    removed_ids = sorted(ids_a - ids_b)
    common_ids = ids_a & ids_b

    for node_id in added_ids:
        node_type = nodes_b[node_id].get("type", "")
        if node_type == "FILE":
            result.added_files.append(node_id)
        elif node_type == "SECTION":
            result.added_sections.append(node_id)

    for node_id in removed_ids:
        node_type = nodes_a[node_id].get("type", "")
        if node_type == "FILE":
            result.removed_files.append(node_id)
        elif node_type == "SECTION":
            result.removed_sections.append(node_id)

    # Check for property changes in common nodes
    compare_fields = ("title",)
    for node_id in sorted(common_ids):
        data_a = nodes_a[node_id]
        data_b = nodes_b[node_id]
        node_type = data_a.get("type", "")

        for fld in compare_fields:
            val_a = data_a.get(fld, "")
            val_b = data_b.get(fld, "")
            if val_a != val_b:
                result.changed.append(
                    ChangedNode(
                        node_id=node_id,
                        node_type=node_type,
                        field=fld,
                        old_value=str(val_a),
                        new_value=str(val_b),
                    )
                )

    return result


def diff_graphs(
    repo_path: Path | str, ref_a: str, ref_b: str
) -> DiffResult:
    """Compare graph snapshots at two git refs.

    Resolves both refs, builds a graph at each, and compares.

    Args:
        repo_path: Path to (or within) the git repository.
        ref_a: First git ref (older).
        ref_b: Second git ref (newer).

    Returns:
        DiffResult with added, removed, and changed nodes.

    Raises:
        GitRefError: If either ref cannot be resolved.
    """
    repo_root = find_repo_root(repo_path)
    sha_a = resolve_ref(repo_root, ref_a)
    sha_b = resolve_ref(repo_root, ref_b)

    graph_a = _build_graph_at_ref(repo_root, sha_a)
    graph_b = _build_graph_at_ref(repo_root, sha_b)

    return _compare_graphs(graph_a, graph_b, sha_a[:12], sha_b[:12])