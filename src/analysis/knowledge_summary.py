"""Knowledge summary generation for DSM reference networks.

Produces agent-consumable markdown (~150-200 lines) derived from graph
topology. Four components:
    P1: Document hierarchy (tree view)
    P1: Hub documents (top-N files by incoming references)
    P2: Cross-reference hotspots (sections with many incoming refs)
    P2: Orphan files (files with zero incoming references)

Origin: DSM Central BL-302 (agent-consumable-knowledge-graph-export),
BL-303 (navigation architecture vision, P1-P4 priority guidance).
"""

from collections import defaultdict

import networkx as nx


def generate_hierarchy(
    G: nx.DiGraph, top_files_per_dir: int = 3
) -> str:
    """Generate a directory-level document hierarchy.

    Groups files by directory, shows file count and total sections per
    directory, and lists the top files (by section count) as examples.
    Bounded output regardless of repository size.

    Args:
        G: The reference graph.
        top_files_per_dir: Max files to list per directory (rest summarized).

    Returns:
        Markdown string with the directory-level hierarchy.
    """
    file_nodes = sorted(
        [n for n, d in G.nodes(data=True) if d.get("type") == "FILE"]
    )
    if not file_nodes:
        return "No files in graph."

    # Group files by directory
    dirs: dict[str, list[tuple[str, str, int]]] = defaultdict(list)
    for file_node in file_nodes:
        import os
        directory = os.path.dirname(file_node) or "."
        title = G.nodes[file_node].get("title", file_node)
        section_count = sum(
            1 for _, _, d in G.out_edges(file_node, data=True)
            if d.get("type") == "CONTAINS"
        )
        dirs[directory].append((file_node, title, section_count))

    # Sort files within each directory by section count (descending)
    for directory in dirs:
        dirs[directory].sort(key=lambda x: x[2], reverse=True)

    lines = []
    for directory in sorted(dirs.keys()):
        files = dirs[directory]
        total_sections = sum(f[2] for f in files)
        file_count = len(files)
        lines.append(
            f"**{directory}/** ({file_count} file{'s' if file_count != 1 else ''}"
            f", {total_sections} sections)"
        )
        for file_node, title, sec_count in files[:top_files_per_dir]:
            lines.append(f"  - {title} | {sec_count} sections | path: {file_node}")
        remaining = file_count - top_files_per_dir
        if remaining > 0:
            lines.append(f"  - ... and {remaining} more")

    return "\n".join(lines)


def generate_hub_documents(G: nx.DiGraph, n: int = 10) -> str:
    """Generate a list of hub documents ranked by incoming references.

    Aggregates incoming REFERENCES edges at the file level: for each file,
    counts how many REFERENCES edges target any of its sections.

    Returns:
        Markdown string with top-N hub files and their reference counts.
    """
    file_nodes = [
        node for node, data in G.nodes(data=True)
        if data.get("type") == "FILE"
    ]
    if not file_nodes:
        return "No files in graph."

    file_ref_counts = {}
    for file_node in file_nodes:
        count = 0
        for _, target, edge_data in G.out_edges(file_node, data=True):
            if edge_data.get("type") == "CONTAINS":
                in_refs = sum(
                    1 for _, _, d in G.in_edges(target, data=True)
                    if d.get("type") == "REFERENCES"
                )
                count += in_refs
        file_ref_counts[file_node] = count

    ranked = sorted(file_ref_counts.items(), key=lambda x: x[1], reverse=True)
    top = [(f, c) for f, c in ranked[:n] if c > 0]

    if not top:
        return "No hub documents found (no cross-references in graph)."

    lines = []
    lines.append("| # | File | Incoming refs | Top section |")
    lines.append("|---|------|--------------|-------------|")
    for i, (file_node, count) in enumerate(top, 1):
        title = G.nodes[file_node].get("title", file_node)
        top_section = _top_section_for_file(G, file_node)
        lines.append(f"| {i} | {title} | {count} | {top_section} |")

    return "\n".join(lines)


def _top_section_for_file(G: nx.DiGraph, file_node: str) -> str:
    """Find the most-referenced section within a file."""
    best_title = ""
    best_count = 0
    for _, target, edge_data in G.out_edges(file_node, data=True):
        if edge_data.get("type") == "CONTAINS":
            in_refs = sum(
                1 for _, _, d in G.in_edges(target, data=True)
                if d.get("type") == "REFERENCES"
            )
            if in_refs > best_count:
                best_count = in_refs
                sec_data = G.nodes[target]
                number = sec_data.get("number", "")
                title = sec_data.get("title", "")
                best_title = f"{number}: {title}" if number else title
    return best_title or "-"


def generate_hotspots(
    G: nx.DiGraph, threshold: int = 10, max_items: int = 20
) -> str:
    """Generate a list of cross-reference hotspots.

    Finds SECTION nodes with incoming REFERENCES count >= threshold.
    Capped at max_items to bound output length.

    Args:
        G: The reference graph.
        threshold: Minimum incoming reference count to qualify.
        max_items: Maximum hotspot entries to show.

    Returns:
        Markdown string listing hotspot sections with their reference counts.
    """
    section_nodes = [
        node for node, data in G.nodes(data=True)
        if data.get("type") == "SECTION"
    ]
    hotspots = []
    for node in section_nodes:
        in_refs = sum(
            1 for _, _, d in G.in_edges(node, data=True)
            if d.get("type") == "REFERENCES"
        )
        if in_refs >= threshold:
            data = G.nodes[node]
            hotspots.append((
                in_refs,
                data.get("file", ""),
                data.get("number", ""),
                data.get("title", ""),
            ))

    if not hotspots:
        return f"No sections with {threshold}+ incoming references."

    hotspots.sort(key=lambda x: x[0], reverse=True)
    total = len(hotspots)
    hotspots = hotspots[:max_items]

    lines = []
    lines.append("| Refs | File | Section | Title |")
    lines.append("|------|------|---------|-------|")
    for count, file, number, title in hotspots:
        sec_label = number if number else "(unnumbered)"
        lines.append(f"| {count} | {file} | {sec_label} | {title} |")

    if total > max_items:
        lines.append(f"\n... and {total - max_items} more above threshold.")

    return "\n".join(lines)


def generate_orphans(G: nx.DiGraph, max_items: int = 15) -> str:
    """Generate a list of orphan files.

    A file is an orphan if none of its sections have incoming REFERENCES
    edges from sections in other files. Capped at max_items.

    Args:
        G: The reference graph.
        max_items: Maximum orphan entries to show.

    Returns:
        Markdown string listing orphan files.
    """
    file_nodes = [
        node for node, data in G.nodes(data=True)
        if data.get("type") == "FILE"
    ]
    if not file_nodes:
        return "No files in graph."

    orphans = []
    for file_node in file_nodes:
        has_incoming = False
        for _, target, edge_data in G.out_edges(file_node, data=True):
            if edge_data.get("type") == "CONTAINS":
                for source, _, d in G.in_edges(target, data=True):
                    if d.get("type") == "REFERENCES":
                        source_file = G.nodes[source].get("file", "")
                        if source_file != file_node:
                            has_incoming = True
                            break
            if has_incoming:
                break
        if not has_incoming:
            title = G.nodes[file_node].get("title", file_node)
            section_count = sum(
                1 for _, _, d in G.out_edges(file_node, data=True)
                if d.get("type") == "CONTAINS"
            )
            orphans.append((file_node, title, section_count))

    if not orphans:
        return "No orphan files (all files have incoming cross-references)."

    orphans.sort(key=lambda x: x[0])
    total = len(orphans)
    orphans = orphans[:max_items]

    lines = []
    for file_id, title, section_count in orphans:
        lines.append(f"- **{title}** ({section_count} section{'s' if section_count != 1 else ''})")

    if total > max_items:
        lines.append(f"- ... and {total - max_items} more")

    return "\n".join(lines)


def generate_knowledge_summary(G: nx.DiGraph) -> str:
    """Generate the complete knowledge summary.

    Combines all four components into a single markdown document
    suitable for LLM consumption.

    Returns:
        Complete markdown string (~150-200 lines for large repos).
    """
    file_count = sum(
        1 for _, d in G.nodes(data=True) if d.get("type") == "FILE"
    )
    section_count = sum(
        1 for _, d in G.nodes(data=True) if d.get("type") == "SECTION"
    )
    ref_count = sum(
        1 for _, _, d in G.edges(data=True) if d.get("type") == "REFERENCES"
    )

    parts = [
        f"# Knowledge Summary\n",
        f"**Files:** {file_count} | **Sections:** {section_count} "
        f"| **Cross-references:** {ref_count}\n",
        "## Document Hierarchy\n",
        generate_hierarchy(G),
        "\n## Hub Documents\n",
        generate_hub_documents(G),
        "\n## Cross-Reference Hotspots\n",
        generate_hotspots(G),
        "\n## Orphan Files\n",
        generate_orphans(G),
    ]

    return "\n".join(parts)
