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
    extract_heading_references,
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


def _print_compare_report(
    results: list,
    inv_a: "EntityInventory",
    inv_b: "EntityInventory",
    elapsed: float,
) -> None:
    """Print a Rich-formatted repo comparison report."""
    from rich.console import Console
    from rich.table import Table

    from graph.repo_diff import MatchType

    console = Console()
    console.print(
        f"\n[bold]Repo Comparison:[/bold] {inv_a.repo.name} → {inv_b.repo.name} "
        f"({elapsed:.2f}s)\n"
    )

    table = Table(show_lines=False)
    table.add_column("Match", style="bold", width=10)
    table.add_column(f"{inv_a.repo.name}", min_width=20)
    table.add_column(f"{inv_b.repo.name}", min_width=20)
    table.add_column("Score", width=6, justify="right")

    style_map = {
        MatchType.IDENTICAL: "green",
        MatchType.MODIFIED: "yellow",
        MatchType.RENAMED: "cyan",
        MatchType.ADDED: "green",
        MatchType.REMOVED: "red",
    }

    for r in results:
        style = style_map.get(r.match_type, "")
        a_label = r.entity_a.heading if r.entity_a else ""
        b_label = r.entity_b.heading if r.entity_b else ""
        score = f"{r.similarity_score:.2f}" if r.similarity_score > 0 else "-"
        table.add_row(
            f"[{style}]{r.match_type}[/{style}]",
            a_label,
            b_label,
            score,
        )

    console.print(table)

    # Summary by match type
    from collections import Counter
    counts = Counter(r.match_type for r in results)
    parts = []
    for mt in MatchType:
        c = counts.get(mt, 0)
        if c > 0:
            parts.append(f"{c} {mt.lower()}")
    console.print(f"\nSummary: {', '.join(parts)} ({len(results)} total)")


def _print_drift_report_compare(
    results: list,
    inv_a: "EntityInventory",
    inv_b: "EntityInventory",
    elapsed: float,
) -> None:
    """Print a Rich-formatted drift report (MODIFIED entities only)."""
    from rich.console import Console
    from rich.table import Table

    from graph.repo_diff import MatchType

    console = Console()

    modified = [r for r in results if r.match_type == MatchType.MODIFIED]

    if not modified:
        console.print(
            f"\nDrift Report: {inv_a.repo.name} → {inv_b.repo.name}: "
            f"no drift detected ({elapsed:.2f}s)"
        )
        return

    console.print(
        f"\n[bold]Drift Report:[/bold] {inv_a.repo.name} → {inv_b.repo.name} "
        f"({elapsed:.2f}s)\n"
    )

    table = Table(show_lines=False)
    table.add_column("Entity ID", min_width=12)
    table.add_column(f"{inv_a.repo.name}", min_width=20)
    table.add_column(f"{inv_b.repo.name}", min_width=20)
    table.add_column("Similarity", width=10, justify="right")

    for r in modified:
        table.add_row(
            r.entity_a.id,
            r.entity_a.heading,
            r.entity_b.heading,
            f"{r.similarity_score:.2f}",
        )

    console.print(table)
    console.print(f"\n{len(modified)} MODIFIED entity(ies) with content drift")


def _print_usage_report(report: "UsageReport") -> None:
    """Print a Rich-formatted protocol usage report."""
    from rich.console import Console
    from rich.table import Table

    console = Console()

    # Summary.
    s = report.summary
    console.print(
        f"\n[bold]Protocol Usage Report[/bold] "
        f"({report.spoke}, DSM_0.2 {report.version})"
    )
    console.print(
        f"Sections: {s['total_sections']} total, "
        f"{s['high_usage']} high-usage, {s['low_usage']} low-usage, "
        f"{s['gaps']} gaps"
    )

    # Main table: sections sorted by total_score descending.
    table = Table(title="Section Usage (sorted by score)")
    table.add_column("Section", style="cyan", max_width=40)
    table.add_column("Module", style="dim")
    table.add_column("Designed", style="dim")
    table.add_column("D", justify="right")  # declared
    table.add_column("P", justify="right")  # prescribed
    table.add_column("O", justify="right")  # observed
    table.add_column("Score", justify="right", style="bold")
    table.add_column("Inferred", style="bold")

    for sec in sorted(report.sections, key=lambda x: x.total_score, reverse=True):
        style = ""
        if sec.inferred_classification == "high":
            style = "green"
        elif sec.total_score == 0:
            style = "dim"
        table.add_row(
            sec.heading,
            sec.module,
            sec.designed_classification,
            str(sec.declared_count),
            str(sec.prescribed_count),
            str(sec.observed_count),
            str(sec.total_score),
            sec.inferred_classification,
            style=style,
        )

    console.print(table)

    # Gaps.
    if report.gaps:
        gap_table = Table(title="Designed vs Observed Gaps")
        gap_table.add_column("Section", style="cyan")
        gap_table.add_column("Designed")
        gap_table.add_column("Observed")
        gap_table.add_column("Gap Type", style="yellow")
        for gap in report.gaps:
            gap_table.add_row(
                gap.heading, gap.designed, gap.observed, gap.gap_type
            )
        console.print(gap_table)

    # Ground truth.
    if report.ground_truth_results:
        gt_table = Table(title="Ground Truth Validation")
        gt_table.add_column("Section ID", style="cyan")
        gt_table.add_column("Result")
        for sid, result in report.ground_truth_results.items():
            style = "green" if result == "pass" else "red"
            gt_table.add_row(sid, f"[{style}]{result}[/{style}]")
        console.print(gt_table)


def _print_usage_diff(diff: "DiffReport") -> None:
    """Print a Rich-formatted usage diff report."""
    from rich.console import Console
    from rich.table import Table

    console = Console()
    console.print(
        f"\n[bold]Usage Diff[/bold]: {diff.version_old} → {diff.version_new}"
    )

    if diff.structural_changes:
        table = Table(title="Structural Changes")
        table.add_column("Section", style="cyan")
        table.add_column("Change")
        for ch in diff.structural_changes:
            style = "green" if ch.change_type == "added" else "red"
            table.add_row(ch.heading, f"[{style}]{ch.change_type}[/{style}]")
        console.print(table)

    if diff.classification_changes:
        table = Table(title="Classification Changes")
        table.add_column("Section", style="cyan")
        table.add_column("Old")
        table.add_column("New")
        for ch in diff.classification_changes:
            table.add_row(ch.heading, ch.old_classification, ch.new_classification)
        console.print(table)

    if diff.new_gaps:
        table = Table(title="New Gaps")
        table.add_column("Section", style="cyan")
        table.add_column("Gap Type", style="yellow")
        for g in diff.new_gaps:
            table.add_row(g.heading, g.gap_type)
        console.print(table)

    if diff.resolved_gaps:
        table = Table(title="Resolved Gaps")
        table.add_column("Section", style="cyan")
        table.add_column("Gap Type", style="green")
        for g in diff.resolved_gaps:
            table.add_row(g.heading, g.gap_type)
        console.print(table)

    if not any([
        diff.structural_changes,
        diff.classification_changes,
        diff.new_gaps,
        diff.resolved_gaps,
    ]):
        console.print("[dim]No changes detected.[/dim]")


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
    "--knowledge-summary",
    "knowledge_summary_path",
    type=click.Path(),
    default=None,
    help="Build reference graph and write agent-consumable knowledge summary (markdown) to PATH.",
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
    "--inventory",
    "inventory_paths",
    multiple=True,
    type=click.Path(exists=True),
    help="Path to external entity inventory YAML (repeatable).",
)
@click.option(
    "--export-inventory",
    "export_inventory_path",
    type=click.Path(),
    default=None,
    help="Scan repo and export entity inventory to YAML file.",
)
@click.option(
    "--graph-diff",
    "graph_diff_refs",
    nargs=2,
    default=None,
    help="Compare graphs at two git refs. Usage: --graph-diff REF_A REF_B",
)
@click.option(
    "--compare-repo",
    "compare_repo_paths",
    nargs=2,
    type=click.Path(),
    default=None,
    help="Compare two entity inventories. Usage: --compare-repo INV_A INV_B",
)
@click.option(
    "--drift-report",
    is_flag=True,
    default=False,
    help="Show only MODIFIED entities (requires --compare-repo).",
)
@click.option(
    "--heading-refs",
    is_flag=True,
    default=False,
    help="Detect heading title mentions in prose as cross-references.",
)
@click.option(
    "--protocol-usage",
    "protocol_usage_dsm_path",
    type=click.Path(exists=True),
    default=None,
    help="Run protocol usage analysis. Path to DSM_0.2 directory.",
)
@click.option(
    "--dsm-version",
    "dsm_version",
    default=None,
    help="DSM_0.2 version tag for the analysis (e.g., v1.3.69).",
)
@click.option(
    "--commands-dir",
    "commands_dir",
    type=click.Path(exists=True),
    default=None,
    help="Path to skill definition files (dsm-*.md). Requires --protocol-usage.",
)
@click.option(
    "--claude-md",
    "claude_md_path",
    type=click.Path(exists=True),
    default=None,
    help="Path to spoke CLAUDE.md for declared refs. Requires --protocol-usage.",
)
@click.option(
    "--transcripts",
    "transcript_paths",
    multiple=True,
    type=click.Path(exists=True),
    help="Session transcript files to scan (repeatable). Requires --protocol-usage.",
)
@click.option(
    "--usage-output",
    "usage_output_path",
    type=click.Path(),
    default=None,
    help="Write usage report JSON to this path. Requires --protocol-usage.",
)
@click.option(
    "--usage-compare",
    "usage_compare_paths",
    nargs=2,
    type=click.Path(exists=True),
    default=None,
    help="Compare two usage report JSON files. Usage: --usage-compare OLD NEW",
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
    knowledge_summary_path: str | None,
    lint: bool,
    graph_db_path: str | None,
    rebuild: bool,
    inventory_paths: tuple[str, ...],
    export_inventory_path: str | None,
    git_ref: str | None,
    graph_diff_refs: tuple[str, str] | None,
    compare_repo_paths: tuple[str, str] | None,
    drift_report: bool,
    heading_refs: bool,
    protocol_usage_dsm_path: str | None,
    dsm_version: str | None,
    commands_dir: str | None,
    claude_md_path: str | None,
    transcript_paths: tuple[str, ...],
    usage_output_path: str | None,
    usage_compare_paths: tuple[str, str] | None,
) -> None:
    """Validate cross-references and version consistency in DSM markdown files.

    PATHS can be markdown files or directories. Directories are scanned
    recursively for *.md files (customisable with --glob).

    If no PATHS are given, validates the current directory.

    \b
    Examples:
      dsm-validate .                           # Validate current directory
      dsm-validate dsm-docs/ --strict              # Strict mode for CI
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

    # Protocol usage compare mode: independent early-exit path
    if usage_compare_paths:
        import json as _json

        from analysis.usage_diff import compare_reports as _compare_reports
        from analysis.usage_report import UsageReport as _UsageReport

        old_path, new_path = usage_compare_paths
        old_data = _json.loads(Path(old_path).read_text())
        new_data = _json.loads(Path(new_path).read_text())
        old_report = _UsageReport(**old_data)
        new_report = _UsageReport(**new_data)
        diff = _compare_reports(old_report, new_report)
        _print_usage_diff(diff)
        return

    # Protocol usage analysis mode: independent early-exit path
    if protocol_usage_dsm_path:
        from analysis.section_index import build_section_index
        from analysis.declared_refs import extract_declared_references
        from analysis.prescribed_refs import extract_prescribed_references
        from analysis.observed_refs import extract_observed_references
        from analysis.usage_report import aggregate_usage

        dsm_path = Path(protocol_usage_dsm_path)
        version = dsm_version or "unknown"
        spoke_name = Path.cwd().name

        # Build section index.
        index = build_section_index(dsm_path, version)
        click.echo(
            f"Section index: {len(index.sections)} sections, "
            f"{len(index.dispatch_table)} dispatch entries (DSM_0.2 {version})"
        )

        # Layer 1: Declared.
        declared = []
        if claude_md_path:
            declared = extract_declared_references(Path(claude_md_path), index)
            click.echo(f"Layer 1 (Declared): {len(declared)} references")

        # Layer 2: Prescribed.
        prescribed = []
        if commands_dir:
            prescribed = extract_prescribed_references(
                Path(commands_dir), index
            )
            click.echo(f"Layer 2 (Prescribed): {len(prescribed)} references")

        # Layer 3: Observed.
        observed = []
        if transcript_paths:
            observed = extract_observed_references(
                [Path(p) for p in transcript_paths], index
            )
            sessions = {r.session_number for r in observed}
            click.echo(
                f"Layer 3 (Observed): {len(observed)} references "
                f"across {len(sessions)} sessions"
            )

        # Ground truth (hardcoded per DSM Central Session 141).
        ground_truth = [
            "session-transcript-protocol",
            "pre-generation-brief-protocol",
            "three-level-branching-strategy",
            "read-only-access-within-repository",
            "ecosystem-path-registry",
            "inclusive-language",
            "active-suggestion-protocol",
        ]

        # Aggregate.
        report = aggregate_usage(
            index, declared, prescribed, observed,
            spoke=spoke_name,
            ground_truth_ids=ground_truth,
        )

        # Output.
        _print_usage_report(report)

        if usage_output_path:
            Path(usage_output_path).write_text(
                report.model_dump_json(indent=2) + "\n"
            )
            click.echo(f"\nReport written to {usage_output_path}")

        return

    # Compare-repo mode: independent early-exit path
    if drift_report and not compare_repo_paths:
        click.echo(
            "Error: --drift-report requires --compare-repo.",
            err=True,
        )
        sys.exit(2)

    if compare_repo_paths:
        from inventory.inventory_parser import InventoryError, load_inventory
        from graph.repo_diff import compare_inventories

        inv_path_a, inv_path_b = compare_repo_paths

        try:
            inv_a = load_inventory(inv_path_a)
            inv_b = load_inventory(inv_path_b)
        except InventoryError as e:
            click.echo(f"Error loading inventory: {e}", err=True)
            sys.exit(2)

        start = time.perf_counter()
        results = compare_inventories(inv_a, inv_b)
        elapsed = time.perf_counter() - start

        if drift_report:
            _print_drift_report_compare(results, inv_a, inv_b, elapsed)
        else:
            _print_compare_report(results, inv_a, inv_b, elapsed)
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

    # Heading reference extraction (opt-in)
    # Minimum 4 non-stopword tokens to filter generic headings (EXP-008, Proposal #46)
    _HEADING_STOPWORDS = frozenset({
        "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by",
        "from", "and", "or", "but", "is", "are", "was", "were", "be", "been",
        "has", "have", "had", "do", "does", "did", "will", "would", "should",
        "may", "can", "could", "not", "no", "this", "that", "it", "its", "as",
        "so", "if", "when", "where", "how", "what", "which", "who",
    })
    _MIN_NON_STOPWORD_TOKENS = 4
    if heading_refs:
        known_headings: set[str] = set()
        for doc in documents:
            for section in doc.sections:
                if section.number is None:
                    normalized = " ".join(section.title.lower().split())
                    non_stop = [
                        w for w in normalized.split()
                        if w not in _HEADING_STOPWORDS
                    ]
                    if len(non_stop) >= _MIN_NON_STOPWORD_TOKENS:
                        known_headings.add(normalized)

        if known_headings:
            for doc in documents:
                if git_file_contents is not None:
                    content = git_file_contents.get(doc.file, "")
                    heading_cross_refs = extract_heading_references(
                        known_headings=known_headings,
                        content=content,
                        file_path=doc.file,
                    )
                else:
                    heading_cross_refs = extract_heading_references(
                        doc.file,
                        known_headings=known_headings,
                    )
                if heading_cross_refs:
                    references.setdefault(doc.file, []).extend(heading_cross_refs)

    # Load external inventories if provided
    inventories = []
    if inventory_paths:
        from inventory.inventory_parser import InventoryError, load_inventory

        for inv_path in inventory_paths:
            try:
                inv = load_inventory(inv_path)
                inventories.append(inv)
                click.echo(f"Loaded inventory: {inv.repo.name} ({len(inv.entities)} entities)")
            except InventoryError as e:
                click.echo(f"Error loading inventory {inv_path}: {e}", err=True)
                sys.exit(2)

    # Validate cross-references
    cross_ref_results = validate_cross_references(
        documents, references, inventories=inventories if inventories else None,
    )

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
    external_refs = [r for r in cross_ref_results if r.resolution == "external"]
    infos = [
        r for r in cross_ref_results
        if r.severity == Severity.INFO and r.resolution != "external"
    ]

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
    found_parts = [
        f"{len(errors)} error(s)",
        f"{len(warnings)} warning(s)",
        f"{len(infos)} info(s)",
    ]
    if external_refs:
        found_parts.append(f"{len(external_refs)} external ref(s)")
    found_parts.append(f"{len(version_results)} version mismatch(es)")
    summary_parts.append(f"Found {', '.join(found_parts)}.")
    if semantic:
        summary_parts.append(
            f"Semantic: {len(drift_warnings)} drift warning(s), "
            f"{len(insufficient_context)} insufficient context."
        )

    click.echo(f"\n{' '.join(summary_parts)}")

    # Export entity inventory (opt-in)
    if export_inventory_path:
        from inventory.inventory_parser import export_inventory as do_export

        repo_name = base_path.name
        inv = do_export(
            documents,
            repo_name=repo_name,
            output_path=export_inventory_path,
        )
        click.echo(
            f"Inventory exported to {export_inventory_path} "
            f"({len(inv.entities)} entities from {len(documents)} file(s))"
        )

    # Graph operations (opt-in)
    if graph_export_path or graph_stats or graph_db_path or knowledge_summary_path:
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

        if knowledge_summary_path:
            from analysis.knowledge_summary import generate_knowledge_summary
            summary = generate_knowledge_summary(G)
            with open(knowledge_summary_path, "w", encoding="utf-8") as f:
                f.write(summary)
            line_count = len(summary.splitlines())
            click.echo(
                f"Knowledge summary written to {knowledge_summary_path} "
                f"({line_count} lines)"
            )

        # Persist to FalkorDB (opt-in via --graph-db)
        if graph_db_path:
            from graph.graph_store import GraphStore

            graph_name = base_path.name
            current_ref = git_ref_sha or "HEAD"
            ref_label = git_ref_sha[:12] if git_ref_sha else "HEAD"
            store = GraphStore(graph_db_path)
            try:
                if rebuild:
                    store.write_graph(
                        G, graph_name=graph_name, git_ref=current_ref,
                    )
                    click.echo(
                        f"Graph persisted to {graph_db_path} "
                        f"(graph: '{graph_name}', ref: {ref_label})"
                    )
                elif store.graph_exists(graph_name):
                    stored_ref = store.get_stored_ref(graph_name)
                    if stored_ref == current_ref:
                        click.echo(
                            f"Using cached graph '{graph_name}' "
                            f"from {graph_db_path}"
                        )
                    else:
                        all_files = [
                            nid for nid, d in G.nodes(data=True)
                            if d.get("type") == "FILE"
                        ]
                        store.update_files(
                            G,
                            graph_name=graph_name,
                            changed_files=all_files,
                            git_ref=current_ref,
                        )
                        click.echo(
                            f"Graph updated in {graph_db_path} "
                            f"(graph: '{graph_name}', ref: {ref_label}, "
                            f"{len(all_files)} file(s))"
                        )
                else:
                    store.write_graph(
                        G, graph_name=graph_name, git_ref=current_ref,
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
