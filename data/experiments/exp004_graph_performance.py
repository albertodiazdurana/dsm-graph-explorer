"""EXP-004: Graph Query Performance Benchmark.

Validates that NetworkX can handle DSM-sized repositories within
the performance targets defined in epoch-2-plan.md.

Targets:
    Build graph (30 files, 500 sections): <5s
    Most-referenced query:                <100ms
    Orphan sections query:                <100ms
    GraphML export:                       <2s
    Memory usage:                         <100MB

Usage:
    python data/experiments/exp004_graph_performance.py --repo ~/dsm-agentic-ai-data-science-methodology
"""

import argparse
import os
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import networkx as nx

from src.parser.cross_ref_extractor import extract_cross_references
from src.parser.markdown_parser import parse_markdown_file
from src.validator.cross_ref_validator import build_section_lookup


def collect_markdown_files(repo_path: str) -> list[str]:
    """Collect all .md files in the repository."""
    md_files = []
    for root, _dirs, files in os.walk(repo_path):
        for f in files:
            if f.endswith(".md"):
                md_files.append(os.path.join(root, f))
    return sorted(md_files)


def build_graph(documents, references, section_lookup):
    """Build a NetworkX DiGraph from parsed documents and references.

    Nodes:
        FILE nodes: one per parsed document
        SECTION nodes: one per section with a number

    Edges:
        CONTAINS: FILE -> SECTION
        REFERENCES: SECTION -> SECTION (resolved cross-references)
    """
    G = nx.DiGraph()

    # Add FILE and SECTION nodes
    for doc in documents:
        file_id = doc.file
        G.add_node(file_id, type="FILE", title=os.path.basename(doc.file))

        for section in doc.sections:
            if section.number:
                section_id = f"{file_id}:{section.number}"
                G.add_node(
                    section_id,
                    type="SECTION",
                    title=section.title,
                    number=section.number,
                    file=file_id,
                    line=section.line,
                    level=section.level,
                )
                G.add_edge(file_id, section_id, type="CONTAINS")

    # Add REFERENCES edges
    for source_file, refs in references.items():
        # Find which section each reference belongs to (by line proximity)
        doc = next((d for d in documents if d.file == source_file), None)
        if not doc:
            continue

        numbered_sections = [s for s in doc.sections if s.number]

        for ref in refs:
            # Find the enclosing section for this reference
            enclosing = None
            for s in reversed(numbered_sections):
                if s.line <= ref.line:
                    enclosing = s
                    break

            if not enclosing:
                continue

            source_id = f"{source_file}:{enclosing.number}"

            # Resolve the reference target
            if ref.type == "section" and ref.target in section_lookup:
                target_section = section_lookup[ref.target]
                # Find which document contains this section
                for d in documents:
                    if any(
                        s.number == target_section.number for s in d.sections
                    ):
                        target_id = f"{d.file}:{target_section.number}"
                        if G.has_node(source_id) and G.has_node(target_id):
                            G.add_edge(
                                source_id,
                                target_id,
                                type="REFERENCES",
                                line=ref.line,
                                ref_type=ref.type,
                            )
                        break

    return G


def query_most_referenced(G, n=10):
    """Find the n most-referenced SECTION nodes."""
    section_nodes = [
        node for node, data in G.nodes(data=True) if data.get("type") == "SECTION"
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


def query_orphan_sections(G):
    """Find SECTION nodes that are never referenced by other sections."""
    section_nodes = [
        node for node, data in G.nodes(data=True) if data.get("type") == "SECTION"
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


def export_graphml(G, path):
    """Export graph to GraphML format."""
    nx.write_graphml(G, path)


def format_time(seconds):
    """Format time with appropriate unit."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.0f}us"
    if seconds < 1:
        return f"{seconds * 1_000:.1f}ms"
    return f"{seconds:.2f}s"


def format_memory(bytes_val):
    """Format memory with appropriate unit."""
    if bytes_val < 1024:
        return f"{bytes_val}B"
    if bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f}KB"
    return f"{bytes_val / (1024 * 1024):.1f}MB"


def main():
    parser = argparse.ArgumentParser(description="EXP-004: Graph Query Performance")
    parser.add_argument(
        "--repo",
        required=True,
        help="Path to DSM repository to benchmark against",
    )
    args = parser.parse_args()

    repo_path = os.path.expanduser(args.repo)
    if not os.path.isdir(repo_path):
        print(f"Error: {repo_path} is not a directory")
        sys.exit(1)

    print("=" * 60)
    print("EXP-004: Graph Query Performance Benchmark")
    print("=" * 60)
    print(f"Repository: {repo_path}")
    print()

    # Phase 1: Parse repository
    print("Phase 1: Parsing repository...")
    md_files = collect_markdown_files(repo_path)
    print(f"  Found {len(md_files)} markdown files")

    documents = []
    references = {}
    for f in md_files:
        doc = parse_markdown_file(f)
        documents.append(doc)
        refs = extract_cross_references(f)
        if refs:
            references[f] = refs

    total_sections = sum(len(d.sections) for d in documents)
    total_refs = sum(len(r) for r in references.values())
    print(f"  Parsed: {len(documents)} documents, {total_sections} sections, {total_refs} cross-references")
    print()

    section_lookup = build_section_lookup(documents)

    # Phase 2: Benchmark
    print("Phase 2: Running benchmarks...")
    print()

    results = []

    # Start memory tracking
    tracemalloc.start()

    # Benchmark: Build graph
    t0 = time.perf_counter()
    G = build_graph(documents, references, section_lookup)
    t_build = time.perf_counter() - t0

    peak_after_build = tracemalloc.get_traced_memory()[1]

    results.append({
        "operation": "Build graph",
        "target": "< 5s",
        "actual": format_time(t_build),
        "raw": t_build,
        "pass": t_build < 5.0,
    })

    print(f"  Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    file_nodes = sum(1 for _, d in G.nodes(data=True) if d.get("type") == "FILE")
    section_nodes = sum(1 for _, d in G.nodes(data=True) if d.get("type") == "SECTION")
    contains_edges = sum(1 for _, _, d in G.edges(data=True) if d.get("type") == "CONTAINS")
    ref_edges = sum(1 for _, _, d in G.edges(data=True) if d.get("type") == "REFERENCES")
    print(f"  Nodes: {file_nodes} FILE, {section_nodes} SECTION")
    print(f"  Edges: {contains_edges} CONTAINS, {ref_edges} REFERENCES")
    print()

    # Benchmark: Most-referenced query
    t0 = time.perf_counter()
    top_refs = query_most_referenced(G, n=10)
    t_most_ref = time.perf_counter() - t0

    results.append({
        "operation": "Most-referenced query",
        "target": "< 100ms",
        "actual": format_time(t_most_ref),
        "raw": t_most_ref,
        "pass": t_most_ref < 0.1,
    })

    # Benchmark: Orphan sections query
    t0 = time.perf_counter()
    orphans = query_orphan_sections(G)
    t_orphans = time.perf_counter() - t0

    results.append({
        "operation": "Orphan sections query",
        "target": "< 100ms",
        "actual": format_time(t_orphans),
        "raw": t_orphans,
        "pass": t_orphans < 0.1,
    })

    # Benchmark: GraphML export
    with tempfile.NamedTemporaryFile(suffix=".graphml", delete=False) as tmp:
        tmp_path = tmp.name

    t0 = time.perf_counter()
    export_graphml(G, tmp_path)
    t_export = time.perf_counter() - t0

    export_size = os.path.getsize(tmp_path)
    os.unlink(tmp_path)

    results.append({
        "operation": "GraphML export",
        "target": "< 2s",
        "actual": format_time(t_export),
        "raw": t_export,
        "pass": t_export < 2.0,
    })

    # Memory measurement
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    results.append({
        "operation": "Peak memory",
        "target": "< 100MB",
        "actual": format_memory(peak_memory),
        "raw": peak_memory,
        "pass": peak_memory < 100 * 1024 * 1024,
    })

    # Phase 3: Report
    print("Phase 3: Results")
    print()
    print(f"{'Operation':<25} {'Target':<12} {'Actual':<12} {'Result':<8}")
    print("-" * 57)

    all_pass = True
    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        if not r["pass"]:
            all_pass = False
        print(f"{r['operation']:<25} {r['target']:<12} {r['actual']:<12} {status:<8}")

    print("-" * 57)
    print()

    # Show top referenced sections
    if top_refs:
        print("Top 10 most-referenced sections:")
        for node, count in top_refs:
            data = G.nodes[node]
            title = data.get("title", "?")
            number = data.get("number", "?")
            print(f"  [{count:>3}x] Section {number}: {title}")
        print()

    # Show orphan count
    print(f"Orphan sections (never referenced): {len(orphans)} of {section_nodes}")
    print(f"GraphML export size: {format_memory(export_size)}")
    print()

    if all_pass:
        print("RESULT: ALL TARGETS MET — NetworkX is viable for Sprint 7")
    else:
        print("RESULT: SOME TARGETS MISSED — review before proceeding")

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
