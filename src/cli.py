"""CLI interface for DSM integrity validation.

Wires the full pipeline: find files → parse → extract refs → validate → report.
Provides both Rich console output and optional markdown report file.
"""

import sys
import time
from pathlib import Path

import click

from config.config_loader import ConfigError, load_config, merge_config_with_cli
from filter.file_filter import filter_files
from linter.checks import run_all_checks
from linter.lint_reporter import format_lint_markdown, print_lint_results
from linter.models import LintRule
from parser.cross_ref_extractor import (
    extract_cross_references,
    extract_cross_references_from_content,
)
from parser.markdown_parser import parse_markdown_content, parse_markdown_file
from reporter.report_generator import generate_markdown_report, print_rich_report
from graph.graph_store import FALKORDB_AVAILABLE
from semantic.similarity import SKLEARN_AVAILABLE, SemanticResult
from validator.cross_ref_validator import (
    Severity,
    apply_severity_overrides,
    build_section_lookup,
    validate_cross_references,
)
from validator.version_validator import validate_version_consistency


def collect_markdown_files(
    paths: tuple[str, ...],
    glob_pattern: str = "**/*.md",
) -> list[Path]:
    """Resolve paths to a list of markdown files.

    For each path:
    - If it's a file, include it directly.
    - If it's a directory, recursively find files matching the glob pattern.

    Raises click.BadParameter if a path does not exist.
    """
    files: list[Path] = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            raise click.BadParameter(f"Path does not exist: {p}")
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.glob(glob_pattern)))
    return files


def _print_diff_report(result: "DiffResult", elapsed: float) -> None:
    """Print a Rich-formatted graph diff report."""
    from rich.console import Console
    from rich.table import Table

    from graph.graph_diff import DiffResult  # noqa: F811

    console = Console()

    if not result.has_changes:
        console.print(
            f"\nNo differences between {result.ref_a} and {result.ref_b} "
            f"({elapsed:.2f}s)"
        )
        return

    console.print(
        f"\n[bold]Graph Diff:[/bold] {result.ref_a} → {result.ref_b} "
        f"({elapsed:.2f}s)\n"
    )

    if result.added_files or result.removed_files:
        table = Table(title="Files", show_lines=False)
        table.add_column("Status", style="bold", width=8)
        table.add_column("File")

        for f in result.added_files:
            table.add_row("[green]+added[/green]", f)
        for f in result.removed_files:
            table.add_row("[red]-removed[/red]", f)

        console.print(table)
        console.print()

    if result.added_sections or result.removed_sections:
        table = Table(title="Sections", show_lines=False)
        table.add_column("Status", style="bold", width=8)
        table.add_column("Section")

        for s in result.added_sections:
            table.add_row("[green]+added[/green]", s)
        for s in result.removed_sections:
            table.add_row("[red]-removed[/red]", s)

        console.print(table)
        console.print()

    if result.changed:
        table = Table(title="Changed", show_lines=False)
        table.add_column("Node", min_width=20)
        table.add_column("Field")
        table.add_column("Old")
        table.add_column("New")

        for c in result.changed:
            table.add_row(c.node_id, c.field, c.old_value, c.new_value)

        console.print(table)
        console.print()

    # Summary
    summary_parts = []
    if result.added_files:
        summary_parts.append(f"{len(result.added_files)} file(s) added")
    if result.removed_files:
        summary_parts.append(f"{len(result.removed_files)} file(s) removed")
    if result.added_sections:
        summary_parts.append(f"{len(result.added_sections)} section(s) added")
    if result.removed_sections:
        summary_parts.append(f"{len(result.removed_sections)} section(s) removed")
    if result.changed:
        summary_parts.append(f"{len(result.changed)} node(s) changed")

    console.print(f"Summary: {', '.join(summary_parts)}")


@click.command()
@click.version_option(version="0.3.0", prog_name="dsm-validate")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default=None,
    help="Write markdown report to this file path.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with code 1 if any ERROR-level issues are found (for CI).",
)
@click.option(
    "--glob",
    "glob_pattern",
    default="**/*.md",
    show_default=True,
    help="Glob pattern for finding files in directories.",
)
@click.option(
    "--version-files",
    multiple=True,
    type=click.Path(exists=True),
    help="Files to check for version consistency (repeatable).",
)
@click.option(
    "-e",
    "--exclude",
    "exclude_patterns",
    multiple=True,
    help="Exclude files matching pattern (repeatable). E.g., --exclude 'plan/*'",
)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True),
    default=None,
    help="Path to config file. Default: searches for .dsm-graph-explorer.yml",
)
@click.option(
    "--semantic",
    is_flag=True,
    default=False,
    help="Enable TF-IDF semantic drift detection for cross-references.",
)
@click.option(
    "--graph-export",
    "graph_export_path",
    type=click.Path(),
    default=None,
    help="Build reference graph and export to GraphML file.",
)
@click.option(
    "--graph-stats",
    is_flag=True,
    default=False,
    help="Build reference graph and print summary statistics.",
)
@click.option(
    "--lint",
    is_flag=True,
    default=False,
    help="Run convention linting checks (emoji, TOC, mojibake, em-dash, CRLF, backlog metadata).",
)
@click.option(
    "--graph-db",
    "graph_db_path",
    type=click.Path(),
    default=None,
    help="Persist reference graph to a FalkorDB database file.",
)
@click.option(
    "--rebuild",
    is_flag=True,
    default=False,
    help="Force graph rebuild even if cached (requires --graph-db).",
)
@click.option(
    "--git-ref",
    "git_ref",
    default=None,
    help="Compile graph from a historical git ref (commit SHA, tag, or branch).",
)
@click.option(
    "--graph-diff",
    "graph_diff_refs",
    nargs=2,
    default=None,
    help="Compare graphs at two git refs. Usage: --graph-diff REF_A REF_B",
)
def main(
    paths: tuple[str, ...],
    output: str | None,
    strict: bool,
    glob_pattern: str,
    version_files: tuple[str, ...],
    exclude_patterns: tuple[str, ...],
    config_path: str | None,
    semantic: bool,
    graph_export_path: str | None,
    graph_stats: bool,
    lint: bool,
    graph_db_path: str | None,
    rebuild: bool,
    git_ref: str | None,
    graph_diff_refs: tuple[str, str] | None,
) -> None:
    """Validate cross-references and version consistency in DSM markdown files.

    PATHS can be markdown files or directories. Directories are scanned
    recursively for *.md files (customisable with --glob).

    If no PATHS are given, validates the current directory.

    \b
    Examples:
      dsm-validate .                           # Validate current directory
      dsm-validate docs/ --strict              # Strict mode for CI
      dsm-validate . --exclude 'plan/*'        # Exclude plan folder
      dsm-validate . -c myconfig.yml           # Use custom config file
    """
    if not paths:
        paths = (".",)

    # Graph diff mode: independent early-exit path
    if graph_diff_refs:
        try:
            import networkx  # noqa: F401
        except ImportError:
            click.echo(
                "Error: --graph-diff requires networkx. "
                "Install with: pip install dsm-graph-explorer[graph]",
                err=True,
            )
            sys.exit(2)

        from graph.graph_diff import diff_graphs
        from git_ref.git_resolver import GitRefError

        base_path = Path(paths[0]).resolve() if paths else Path.cwd()
        ref_a, ref_b = graph_diff_refs
        click.echo(f"Comparing graphs: {ref_a} vs {ref_b}")

        try:
            start = time.perf_counter()
            result = diff_graphs(base_path, ref_a, ref_b)
            elapsed = time.perf_counter() - start
        except GitRefError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)

        _print_diff_report(result, elapsed)
        return

    # Load configuration
    try:
        base_config = load_config(
            config_path=config_path,
            start_path=Path(paths[0]) if paths else None,
        )
    except ConfigError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(2)

    # Merge CLI options with config (CLI wins)
    config = merge_config_with_cli(
        base_config,
        cli_exclude=exclude_patterns,
        cli_strict=strict if strict else None,
    )

    base_path = Path(paths[0]).resolve() if paths else Path.cwd()

    # Git-ref mode: collect and parse files from a historical commit
    git_ref_sha: str | None = None
    git_file_contents: dict[str, str] | None = None
    if git_ref:
        from git_ref.git_resolver import (
            GitRefError,
            find_repo_root,
            list_files_at_ref,
            read_file_at_ref,
            resolve_ref,
        )

        try:
            repo_root = find_repo_root(base_path)
            git_ref_sha = resolve_ref(repo_root, git_ref)
            git_files = list_files_at_ref(repo_root, git_ref_sha)
            click.echo(
                f"Resolved --git-ref '{git_ref}' to {git_ref_sha[:12]} "
                f"({len(git_files)} markdown file(s))"
            )
        except GitRefError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)

        if not git_files:
            click.echo("No markdown files found at the given git ref.", err=True)
            sys.exit(2)

        # Apply exclusion filters to git file paths
        original_count = len(git_files)
        if config.exclude:
            from filter.file_filter import should_exclude
            git_files = [
                f for f in git_files
                if not should_exclude(f, config.exclude, base_path)
            ]
        excluded_count = original_count - len(git_files)

        if not git_files:
            click.echo("All files excluded by patterns. Nothing to validate.", err=True)
            sys.exit(2)

        # Read all file contents from git
        git_file_contents = {}
        for gf in git_files:
            try:
                git_file_contents[gf] = read_file_at_ref(repo_root, git_ref_sha, gf)
            except GitRefError as e:
                click.echo(f"Warning: skipping {gf}: {e}", err=True)

        # Use git_files as the file list (as strings, not Paths)
        md_files = git_files  # type: ignore[assignment]
    else:
        # Disk-based file collection
        try:
            md_files = collect_markdown_files(paths, glob_pattern)
        except click.BadParameter as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)

        if not md_files:
            click.echo("No markdown files found.", err=True)
            sys.exit(2)

        # Apply exclusion filters
        original_count = len(md_files)
        md_files = filter_files(md_files, config.exclude, base_path)
        excluded_count = original_count - len(md_files)

        if not md_files:
            click.echo("All files excluded by patterns. Nothing to validate.", err=True)
            sys.exit(2)

    # Lint mode (independent from validation pipeline, disk-only)
    if lint and git_ref:
        click.echo("Error: --lint cannot be combined with --git-ref.", err=True)
        sys.exit(2)

    if lint:
        start = time.perf_counter()

        # Build severity overrides from config
        lint_overrides: dict[LintRule, Severity] | None = None
        if config.lint.severity_overrides:
            lint_overrides = {}
            for rule_code, sev_str in config.lint.severity_overrides.items():
                lint_overrides[LintRule(rule_code)] = Severity(sev_str.lower())

        all_lint_results = []
        for f in md_files:
            raw = f.read_text(encoding="utf-8")
            results = run_all_checks(str(f), raw, lint_overrides)
            all_lint_results.extend(results)

        elapsed = time.perf_counter() - start

        print_lint_results(all_lint_results)

        lint_errors = [r for r in all_lint_results if r.severity == Severity.ERROR]
        lint_warnings = [r for r in all_lint_results if r.severity == Severity.WARNING]
        click.echo(
            f"\nScanned {len(md_files)} file(s) in {elapsed:.2f}s. "
            f"Found {len(lint_errors)} error(s), {len(lint_warnings)} warning(s)."
        )

        if output:
            report = format_lint_markdown(all_lint_results)
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            Path(output).write_text(report, encoding="utf-8")
            click.echo(f"Lint report written to {output}")

        if config.strict and lint_errors:
            sys.exit(1)
        return

    # Parse and extract
    start = time.perf_counter()
    documents = []
    references = {}

    if git_file_contents is not None:
        # Git-ref mode: parse from in-memory content
        for file_path, content in git_file_contents.items():
            doc = parse_markdown_content(content, file_path)
            documents.append(doc)
            refs = extract_cross_references_from_content(content, file_path)
            if refs:
                references[doc.file] = refs
    else:
        # Disk mode: parse from filesystem
        for f in md_files:
            doc = parse_markdown_file(f)
            documents.append(doc)
            refs = extract_cross_references(f)
            if refs:
                references[doc.file] = refs

    # Validate cross-references
    cross_ref_results = validate_cross_references(documents, references)

    # Apply severity overrides from config
    cross_ref_results = apply_severity_overrides(
        cross_ref_results, config.severity, config.default_severity
    )

    # Semantic validation (opt-in)
    semantic_results: list[tuple[str, int, str, SemanticResult]] = []
    if semantic:
        if not SKLEARN_AVAILABLE:
            click.echo(
                "Error: --semantic requires scikit-learn. "
                "Install with: pip install dsm-graph-explorer[semantic]",
                err=True,
            )
            sys.exit(2)

        from semantic.similarity import (
            build_corpus_vectorizer,
            check_semantic_alignment,
        )

        # Build corpus from all sections
        all_sections = [s for doc in documents for s in doc.sections]
        if all_sections:
            vectorizer = build_corpus_vectorizer(all_sections)
            section_lookup = build_section_lookup(documents)

            for file_path, refs in references.items():
                for ref in refs:
                    if ref.type in ("section", "appendix"):
                        target_section = section_lookup.get(ref.target)
                        if target_section is not None:
                            result = check_semantic_alignment(
                                ref,
                                target_section,
                                vectorizer,
                                threshold=config.semantic_threshold,
                                min_tokens=config.semantic_min_tokens,
                            )
                            semantic_results.append(
                                (file_path, ref.line, ref.target, result)
                            )

    # Validate version consistency
    version_results = []
    if version_files:
        version_results = validate_version_consistency(
            [Path(vf) for vf in version_files]
        )

    elapsed = time.perf_counter() - start

    # Report
    print_rich_report(cross_ref_results, version_results, semantic_results)

    # Summary line
    errors = [r for r in cross_ref_results if r.severity == Severity.ERROR]
    warnings = [r for r in cross_ref_results if r.severity == Severity.WARNING]
    infos = [r for r in cross_ref_results if r.severity == Severity.INFO]

    # Semantic summary counts
    drift_warnings = [
        (f, l, t, r) for f, l, t, r in semantic_results
        if r.sufficient_context and not r.match
    ]
    insufficient_context = [
        (f, l, t, r) for f, l, t, r in semantic_results
        if not r.sufficient_context
    ]

    summary_parts = [
        f"Scanned {len(md_files)} file(s)",
    ]
    if excluded_count > 0:
        summary_parts.append(f"({excluded_count} excluded)")
    summary_parts.append(f"in {elapsed:.2f}s.")
    summary_parts.append(
        f"Found {len(errors)} error(s), {len(warnings)} warning(s), "
        f"{len(infos)} info(s), {len(version_results)} version mismatch(es)."
    )
    if semantic:
        summary_parts.append(
            f"Semantic: {len(drift_warnings)} drift warning(s), "
            f"{len(insufficient_context)} insufficient context."
        )

    click.echo(f"\n{' '.join(summary_parts)}")

    # Graph operations (opt-in)
    if graph_export_path or graph_stats or graph_db_path:
        # Check falkordblite availability early if --graph-db requested
        if graph_db_path and not FALKORDB_AVAILABLE:
            click.echo(
                "Error: --graph-db requires falkordblite. "
                "Install with: pip install dsm-graph-explorer[graph]",
                err=True,
            )
            sys.exit(2)

        try:
            import networkx as nx  # noqa: F401
        except ImportError:
            click.echo(
                "Error: --graph-export/--graph-stats/--graph-db require networkx. "
                "Install with: pip install dsm-graph-explorer[graph]",
                err=True,
            )
            sys.exit(2)

        from graph.graph_builder import build_reference_graph
        from graph.graph_export import export_graphml
        from graph.graph_queries import most_referenced_sections, orphan_sections

        section_lookup_for_graph = build_section_lookup(documents)
        G = build_reference_graph(documents, references, section_lookup_for_graph)

        if graph_stats:
            file_nodes = sum(
                1 for _, d in G.nodes(data=True) if d.get("type") == "FILE"
            )
            section_nodes = sum(
                1 for _, d in G.nodes(data=True) if d.get("type") == "SECTION"
            )
            contains_edges = sum(
                1 for _, _, d in G.edges(data=True) if d.get("type") == "CONTAINS"
            )
            ref_edges = sum(
                1 for _, _, d in G.edges(data=True) if d.get("type") == "REFERENCES"
            )
            orphans = orphan_sections(G)
            top_refs = most_referenced_sections(G, n=5)

            click.echo("\nGraph Statistics:")
            click.echo(f"  Nodes: {G.number_of_nodes()} ({file_nodes} files, {section_nodes} sections)")
            click.echo(f"  Edges: {G.number_of_edges()} ({contains_edges} contains, {ref_edges} references)")
            click.echo(f"  Orphan sections: {len(orphans)} of {section_nodes}")
            if top_refs:
                click.echo("  Most referenced:")
                for node_id, count in top_refs:
                    data = G.nodes[node_id]
                    click.echo(f"    [{count}x] Section {data.get('number', '?')}: {data.get('title', '?')}")

        if graph_export_path:
            export_graphml(G, graph_export_path)
            click.echo(f"Graph exported to {graph_export_path}")

        # Persist to FalkorDB (opt-in via --graph-db)
        if graph_db_path:
            from graph.graph_store import GraphStore

            graph_name = base_path.name
            ref_label = git_ref_sha[:12] if git_ref_sha else "HEAD"
            store = GraphStore(graph_db_path)
            try:
                if store.graph_exists(graph_name) and not rebuild:
                    click.echo(
                        f"Using cached graph '{graph_name}' "
                        f"from {graph_db_path}"
                    )
                else:
                    store.write_graph(
                        G,
                        graph_name=graph_name,
                        git_ref=git_ref_sha or "HEAD",
                    )
                    click.echo(
                        f"Graph persisted to {graph_db_path} "
                        f"(graph: '{graph_name}', ref: {ref_label})"
                    )
            finally:
                store.close()

    # Write markdown report if requested
    if output:
        generate_markdown_report(
            cross_ref_results, version_results,
            semantic_results=semantic_results,
            output_path=output,
        )
        click.echo(f"Report written to {output}")

    # Exit code based on strict mode and severity
    if config.strict and errors:
        sys.exit(1)
