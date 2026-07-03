"""Knowledge summary generation for DSM reference networks.

Produces agent-consumable markdown (~150-200 lines) derived from graph
topology. Four components:
    P1: Document hierarchy (tree view)
    P1: Hub documents (top-N files by incoming references)
    P2: Cross-reference hotspots (sections with many incoming refs)
    P2: Orphan files (files with zero incoming references)

Origin: DSM Central BL-302 (agent-consumable-knowledge-graph-export),
BL-303 (navigation architecture vision, P1-P4 priority guidance).

TOON Schema (BL-302 Phase 1.5, DEC-010)
---------------------------------------
Emitted when ``--format toon``. **Flat tabular arrays only** (no nested
sub-arrays), so per-record cost stays linear and the DEC-010 C3 token
measurement remains comparable to Central BL-367's -14.6% projection.
Delimiter: comma. A field is double-quoted iff it contains the delimiter, a
double-quote, or a newline; embedded double-quotes are doubled (CSV-style).
Empty sections emit a zero-cardinality header (e.g. ``hub[0]{...}:``) with no
rows, preserving the schema contract. The document hierarchy is split into two
flat arrays (``directories`` aggregates + ``hierarchy`` shown files) because a
nested dir->files form is not flat-tabular::

    summary:
      files: <int>
      sections: <int>
      cross_references: <int>

    directories[D]{path,files,sections,shown,more}:
      <dir>,<file_count>,<total_sections>,<files_shown>,<files_remaining>

    hierarchy[F]{dir,title,sections,path}:
      <dir>,<file_title>,<section_count>,<file_path>

    hub[H]{rank,file,incoming_refs,top_section}:
      <rank>,<file_path>,<incoming_ref_count>,<"number: title">

    hotspots[S]{refs,file,section,title}:
      <incoming_refs>,<file_path>,<section_number_or_(unnumbered)>,<title>

    orphans[O]{file,sections}:
      <file_path>,<section_count>

where ``shown = min(top_files_per_dir, file_count)`` and
``more = max(0, file_count - top_files_per_dir)``. The ``file`` columns carry
the file path (node id), not the display title, for navigability.
"""

import os
from collections import defaultdict

import networkx as nx


def _quote(value, delim: str = ",") -> str:
    """Quote a field for TOON output, CSV-style.

    Returns the bare string form unless it contains the delimiter, a
    double-quote, or a newline, in which case it is wrapped in double-quotes
    with embedded double-quotes doubled.
    """
    s = str(value)
    if delim in s or '"' in s or "\n" in s:
        return '"' + s.replace('"', '""') + '"'
    return s


def emit_table(name: str, fields, rows, delim: str = ",") -> str:
    """Emit a flat tabular TOON array.

    The ``name[N]{f1,f2,...}:`` header declares cardinality and field names
    once; each row follows on its own 2-space-indented line with
    delimiter-joined, quoted values. Empty ``rows`` emits the header alone
    (``name[0]{...}:``), preserving the schema contract.
    """
    header = f"{name}[{len(rows)}]{{{delim.join(fields)}}}:"
    if not rows:
        return header
    lines = [header]
    for row in rows:
        lines.append("  " + delim.join(_quote(v, delim) for v in row))
    return "\n".join(lines)


def emit_summary(files: int, sections: int, cross_references: int) -> str:
    """Emit the non-tabular TOON ``summary:`` header block."""
    return (
        "summary:\n"
        f"  files: {files}\n"
        f"  sections: {sections}\n"
        f"  cross_references: {cross_references}"
    )


def _hierarchy_rows(G: nx.DiGraph, top_files_per_dir: int = 3):
    """Extract directory-hierarchy data as flat tabular rows.

    Returns ``(directories_rows, hierarchy_rows)``:
        directories_rows: ``(path, files, sections, shown, more)`` per directory,
            ordered by directory name, where ``shown = min(top, files)`` and
            ``more = max(0, files - top)``.
        hierarchy_rows: ``(dir, title, sections, path)`` per shown file, in the
            same directory order, files sorted by section count descending.

    Both the markdown and TOON paths consume these rows so the traversal logic
    lives in one place.
    """
    file_nodes = sorted(
        [n for n, d in G.nodes(data=True) if d.get("type") == "FILE"]
    )

    # Group files by directory
    dirs: dict[str, list[tuple[str, str, int]]] = defaultdict(list)
    for file_node in file_nodes:
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

    directories_rows = []
    hierarchy_rows = []
    for directory in sorted(dirs.keys()):
        files = dirs[directory]
        file_count = len(files)
        total_sections = sum(f[2] for f in files)
        shown = min(top_files_per_dir, file_count)
        more = max(0, file_count - top_files_per_dir)
        directories_rows.append(
            (directory, file_count, total_sections, shown, more)
        )
        for file_node, title, sec_count in files[:top_files_per_dir]:
            hierarchy_rows.append((directory, title, sec_count, file_node))

    return directories_rows, hierarchy_rows


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
    directories_rows, hierarchy_rows = _hierarchy_rows(G, top_files_per_dir)
    if not directories_rows:
        return "No files in graph."

    # Index shown files by directory for the nested markdown layout.
    files_by_dir: dict[str, list[tuple[str, int, str]]] = defaultdict(list)
    for directory, title, sec_count, file_node in hierarchy_rows:
        files_by_dir[directory].append((title, sec_count, file_node))

    lines = []
    for directory, file_count, total_sections, _shown, more in directories_rows:
        lines.append(
            f"**{directory}/** ({file_count} file{'s' if file_count != 1 else ''}"
            f", {total_sections} sections)"
        )
        for title, sec_count, file_node in files_by_dir[directory]:
            lines.append(f"  - {title} | {sec_count} sections | path: {file_node}")
        if more > 0:
            lines.append(f"  - ... and {more} more")

    return "\n".join(lines)


def _hub_rows(G: nx.DiGraph, n: int = 10):
    """Extract hub-document data as flat tabular rows.

    Returns ``(rank, file_path, title, incoming_refs, top_section)`` for the
    top-``n`` files by aggregated incoming REFERENCES count, excluding files
    with zero incoming refs. ``title`` is carried for the markdown column; the
    TOON path uses ``file_path`` per the schema.
    """
    file_nodes = [
        node for node, data in G.nodes(data=True)
        if data.get("type") == "FILE"
    ]

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

    rows = []
    for i, (file_node, count) in enumerate(top, 1):
        title = G.nodes[file_node].get("title", file_node)
        top_section = _top_section_for_file(G, file_node)
        rows.append((i, file_node, title, count, top_section))
    return rows


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

    rows = _hub_rows(G, n)
    if not rows:
        return "No hub documents found (no cross-references in graph)."

    lines = []
    lines.append("| # | File | Incoming refs | Top section |")
    lines.append("|---|------|--------------|-------------|")
    for rank, _file_node, title, count, top_section in rows:
        lines.append(f"| {rank} | {title} | {count} | {top_section} |")

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


def _hotspot_rows(G: nx.DiGraph, threshold: int = 10, max_items: int = 20):
    """Extract cross-reference hotspot data as flat tabular rows.

    Returns ``(rows, total)`` where ``rows`` are ``(refs, file, section_label,
    title)`` for the top ``max_items`` sections (by incoming REFERENCES,
    descending) at or above ``threshold``, and ``total`` is the count above
    threshold before capping. ``section_label`` is the section number or
    ``"(unnumbered)"``. ``total`` lets the markdown path render its overflow
    note; the flat TOON schema drops it.
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

    hotspots.sort(key=lambda x: x[0], reverse=True)
    total = len(hotspots)
    hotspots = hotspots[:max_items]

    rows = [
        (count, file, number if number else "(unnumbered)", title)
        for count, file, number, title in hotspots
    ]
    return rows, total


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
    rows, total = _hotspot_rows(G, threshold, max_items)

    if total == 0:
        return f"No sections with {threshold}+ incoming references."

    lines = []
    lines.append("| Refs | File | Section | Title |")
    lines.append("|------|------|---------|-------|")
    for count, file, sec_label, title in rows:
        lines.append(f"| {count} | {file} | {sec_label} | {title} |")

    if total > max_items:
        lines.append(f"\n... and {total - max_items} more above threshold.")

    return "\n".join(lines)


def _orphan_rows(G: nx.DiGraph, max_items: int = 15):
    """Extract orphan-file data as flat tabular rows.

    A file is an orphan if none of its sections have incoming REFERENCES edges
    from sections in other files. Returns ``(rows, total)`` where ``rows`` are
    ``(file_path, title, sections)`` for the first ``max_items`` orphans
    (sorted by path), and ``total`` is the orphan count before capping.
    ``title`` is carried for the markdown display; the TOON path uses
    ``file_path``.
    """
    file_nodes = [
        node for node, data in G.nodes(data=True)
        if data.get("type") == "FILE"
    ]

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

    orphans.sort(key=lambda x: x[0])
    total = len(orphans)
    return orphans[:max_items], total


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

    orphans, total = _orphan_rows(G, max_items)

    if not orphans:
        return "No orphan files (all files have incoming cross-references)."

    lines = []
    for file_id, title, section_count in orphans:
        lines.append(f"- **{title}** ({section_count} section{'s' if section_count != 1 else ''})")

    if total > max_items:
        lines.append(f"- ... and {total - max_items} more")

    return "\n".join(lines)


def _generate_toon_summary(G: nx.DiGraph) -> str:
    """Assemble the complete knowledge summary in TOON format.

    Emits the ``summary:`` header block followed by the six flat tabular
    arrays in schema order (``directories``, ``hierarchy``, ``hub``,
    ``hotspots``, ``orphans``), blank-line separated. Empty sections emit a
    zero-cardinality header per the schema contract. See the module docstring
    for the full schema.
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

    directories_rows, hierarchy_rows = _hierarchy_rows(G)
    hub_rows = [
        (rank, file_node, refs, top_section)
        for rank, file_node, _title, refs, top_section in _hub_rows(G)
    ]
    hotspot_rows, _hotspot_total = _hotspot_rows(G)
    orphan_rows_raw, _orphan_total = _orphan_rows(G)
    orphan_rows = [(file_node, sections) for file_node, _title, sections in orphan_rows_raw]

    blocks = [
        emit_summary(file_count, section_count, ref_count),
        emit_table(
            "directories",
            ["path", "files", "sections", "shown", "more"],
            directories_rows,
        ),
        emit_table(
            "hierarchy", ["dir", "title", "sections", "path"], hierarchy_rows
        ),
        emit_table(
            "hub", ["rank", "file", "incoming_refs", "top_section"], hub_rows
        ),
        emit_table(
            "hotspots", ["refs", "file", "section", "title"], hotspot_rows
        ),
        emit_table("orphans", ["file", "sections"], orphan_rows),
    ]
    return "\n\n".join(blocks)


def generate_knowledge_summary(G: nx.DiGraph, fmt: str = "markdown") -> str:
    """Generate the complete knowledge summary.

    Combines all four components into a single document suitable for LLM
    consumption.

    Args:
        G: The reference graph.
        fmt: Output format, ``"markdown"`` (default) or ``"toon"``.

    Returns:
        Complete summary string (markdown ~150-200 lines for large repos, or
        TOON flat-tabular arrays).
    """
    if fmt == "toon":
        return _generate_toon_summary(G)

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
