"""Integrity report generator for DSM validation results.

Produces both markdown file reports and Rich console output.
"""

from pathlib import Path

from rich.console import Console
from rich.table import Table

from semantic.similarity import SemanticResult
from validator.cross_ref_validator import Severity, ValidationResult
from validator.version_validator import VersionMismatch

# Type alias for semantic results passed from CLI
SemanticEntry = tuple[str, int, str, SemanticResult]


def generate_markdown_report(
    cross_ref_results: list[ValidationResult],
    version_results: list[VersionMismatch],
    semantic_results: list[SemanticEntry] | None = None,
    output_path: Path | str | None = None,
) -> str:
    """Generate a markdown integrity report.

    Args:
        cross_ref_results: Validation findings from cross-reference checks.
        version_results: Version mismatch findings.
        semantic_results: Optional semantic similarity results from --semantic.
        output_path: Optional path to write the report file.

    Returns:
        The report as a markdown string.
    """
    if semantic_results is None:
        semantic_results = []
    errors = [r for r in cross_ref_results if r.severity == Severity.ERROR]
    warnings = [r for r in cross_ref_results if r.severity == Severity.WARNING]
    infos = [r for r in cross_ref_results if r.severity == Severity.INFO]

    lines: list[str] = []
    lines.append("# DSM Integrity Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Errors:** {len(errors)}")
    lines.append(f"- **Warnings:** {len(warnings)}")
    lines.append(f"- **Info:** {len(infos)}")
    lines.append(f"- **Version mismatches:** {len(version_results)}")
    lines.append("")

    if not errors and not warnings and not infos and not version_results:
        lines.append("No issues found. All cross-references and versions are consistent.")
        lines.append("")
    else:
        # Errors section
        if errors:
            lines.append("## Errors")
            lines.append("")
            lines.append("| File | Line | Type | Target | Message |")
            lines.append("|------|------|------|--------|---------|")
            for r in errors:
                lines.append(
                    f"| {r.source_file} | {r.line} | {r.ref_type} | "
                    f"{r.target} | {r.message} |"
                )
            lines.append("")

        # Warnings section
        if warnings:
            lines.append("## Warnings")
            lines.append("")
            lines.append("| File | Line | Type | Target | Message |")
            lines.append("|------|------|------|--------|---------|")
            for r in warnings:
                lines.append(
                    f"| {r.source_file} | {r.line} | {r.ref_type} | "
                    f"{r.target} | {r.message} |"
                )
            lines.append("")

        # Info section
        if infos:
            lines.append("## Info")
            lines.append("")
            lines.append("| File | Line | Type | Target | Message |")
            lines.append("|------|------|------|--------|---------|")
            for r in infos:
                lines.append(
                    f"| {r.source_file} | {r.line} | {r.ref_type} | "
                    f"{r.target} | {r.message} |"
                )
            lines.append("")

        # Version mismatches
        if version_results:
            lines.append("## Version Mismatches")
            lines.append("")
            for mismatch in version_results:
                lines.append(f"**{mismatch.message}**")
                lines.append("")
                lines.append("| File | Version | Line |")
                lines.append("|------|---------|------|")
                for v in mismatch.versions:
                    lines.append(f"| {v.file} | {v.version} | {v.line} |")
                lines.append("")

    # Semantic drift warnings
    drift = [
        (f, l, t, r) for f, l, t, r in semantic_results
        if r.sufficient_context and not r.match
    ]
    if drift:
        lines.append("## Semantic Drift Warnings")
        lines.append("")
        lines.append("| File | Line | Target | Score | Threshold |")
        lines.append("|------|------|--------|-------|-----------|")
        for f, l, t, r in drift:
            lines.append(f"| {f} | {l} | {t} | {r.score:.3f} | {r.threshold:.2f} |")
        lines.append("")

    # Insufficient context
    insufficient = [
        (f, l, t, r) for f, l, t, r in semantic_results
        if not r.sufficient_context
    ]
    if insufficient:
        lines.append("## Insufficient Context")
        lines.append("")
        lines.append("| File | Line | Target | Ref Tokens | Target Tokens |")
        lines.append("|------|------|--------|------------|---------------|")
        for f, l, t, r in insufficient:
            lines.append(f"| {f} | {l} | {t} | {r.ref_tokens} | {r.target_tokens} |")
        lines.append("")

    report = "\n".join(lines)

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")

    return report


def print_rich_report(
    cross_ref_results: list[ValidationResult],
    version_results: list[VersionMismatch],
    semantic_results: list[SemanticEntry] | None = None,
) -> None:
    """Print a Rich-formatted report to the console.

    Args:
        cross_ref_results: Validation findings from cross-reference checks.
        version_results: Version mismatch findings.
        semantic_results: Optional semantic similarity results from --semantic.
    """
    if semantic_results is None:
        semantic_results = []
    console = Console()

    errors = [r for r in cross_ref_results if r.severity == Severity.ERROR]
    warnings = [r for r in cross_ref_results if r.severity == Severity.WARNING]
    infos = [r for r in cross_ref_results if r.severity == Severity.INFO]

    # Header
    console.print()
    console.print("[bold]DSM Integrity Report[/bold]")
    console.print()

    # Summary
    error_style = "red bold" if errors else "green"
    warn_style = "yellow" if warnings else "green"
    info_style = "blue" if infos else "green"
    version_style = "red bold" if version_results else "green"

    console.print(f"  Errors:             [{error_style}]{len(errors)}[/{error_style}]")
    console.print(f"  Warnings:           [{warn_style}]{len(warnings)}[/{warn_style}]")
    console.print(f"  Info:               [{info_style}]{len(infos)}[/{info_style}]")
    console.print(f"  Version mismatches: [{version_style}]{len(version_results)}[/{version_style}]")

    # Semantic summary counts
    drift = [
        (f, l, t, r) for f, l, t, r in semantic_results
        if r.sufficient_context and not r.match
    ]
    insufficient = [
        (f, l, t, r) for f, l, t, r in semantic_results
        if not r.sufficient_context
    ]
    if semantic_results:
        drift_style = "yellow" if drift else "green"
        insuf_style = "dim" if insufficient else "green"
        console.print(f"  Semantic drift:     [{drift_style}]{len(drift)}[/{drift_style}]")
        console.print(f"  Insufficient ctx:   [{insuf_style}]{len(insufficient)}[/{insuf_style}]")

    console.print()

    has_issues = errors or warnings or infos or version_results or drift or insufficient
    if not has_issues:
        console.print("[green]No issues found.[/green]")
        console.print()
        return

    # Errors table
    if errors:
        table = Table(title="Errors", title_style="red bold")
        table.add_column("File", style="cyan")
        table.add_column("Line", justify="right")
        table.add_column("Type")
        table.add_column("Target", style="bold")
        table.add_column("Message")

        for r in errors:
            table.add_row(r.source_file, str(r.line), r.ref_type, r.target, r.message)

        console.print(table)
        console.print()

    # Warnings table
    if warnings:
        table = Table(title="Warnings", title_style="yellow")
        table.add_column("File", style="cyan")
        table.add_column("Line", justify="right")
        table.add_column("Type")
        table.add_column("Target", style="bold")
        table.add_column("Message")

        for r in warnings:
            table.add_row(r.source_file, str(r.line), r.ref_type, r.target, r.message)

        console.print(table)
        console.print()

    # Info table
    if infos:
        table = Table(title="Info", title_style="blue")
        table.add_column("File", style="cyan")
        table.add_column("Line", justify="right")
        table.add_column("Type")
        table.add_column("Target", style="bold")
        table.add_column("Message")

        for r in infos:
            table.add_row(r.source_file, str(r.line), r.ref_type, r.target, r.message)

        console.print(table)
        console.print()

    # Version mismatches
    if version_results:
        for mismatch in version_results:
            table = Table(title="Version Mismatch", title_style="red bold")
            table.add_column("File", style="cyan")
            table.add_column("Version", style="bold")
            table.add_column("Line", justify="right")

            for v in mismatch.versions:
                table.add_row(v.file, v.version, str(v.line))

            console.print(table)
            console.print()

    # Semantic drift warnings
    if drift:
        table = Table(title="Semantic Drift Warnings", title_style="yellow")
        table.add_column("File", style="cyan")
        table.add_column("Line", justify="right")
        table.add_column("Target", style="bold")
        table.add_column("Score", justify="right")
        table.add_column("Threshold", justify="right")

        for f, l, t, r in drift:
            table.add_row(f, str(l), t, f"{r.score:.3f}", f"{r.threshold:.2f}")

        console.print(table)
        console.print()

    # Insufficient context
    if insufficient:
        table = Table(title="Insufficient Context", title_style="dim")
        table.add_column("File", style="cyan")
        table.add_column("Line", justify="right")
        table.add_column("Target", style="bold")
        table.add_column("Ref Tokens", justify="right")
        table.add_column("Target Tokens", justify="right")

        for f, l, t, r in insufficient:
            table.add_row(f, str(l), t, str(r.ref_tokens), str(r.target_tokens))

        console.print(table)
        console.print()
