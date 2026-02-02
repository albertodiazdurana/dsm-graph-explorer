"""Integrity report generator for DSM validation results.

Produces both markdown file reports and Rich console output.
"""

from pathlib import Path

from rich.console import Console
from rich.table import Table

from validator.cross_ref_validator import Severity, ValidationResult
from validator.version_validator import VersionMismatch


def generate_markdown_report(
    cross_ref_results: list[ValidationResult],
    version_results: list[VersionMismatch],
    output_path: Path | str | None = None,
) -> str:
    """Generate a markdown integrity report.

    Args:
        cross_ref_results: Validation findings from cross-reference checks.
        version_results: Version mismatch findings.
        output_path: Optional path to write the report file.

    Returns:
        The report as a markdown string.
    """
    errors = [r for r in cross_ref_results if r.severity == Severity.ERROR]
    warnings = [r for r in cross_ref_results if r.severity == Severity.WARNING]

    lines: list[str] = []
    lines.append("# DSM Integrity Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Errors:** {len(errors)}")
    lines.append(f"- **Warnings:** {len(warnings)}")
    lines.append(f"- **Version mismatches:** {len(version_results)}")
    lines.append("")

    if not errors and not warnings and not version_results:
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

    report = "\n".join(lines)

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")

    return report


def print_rich_report(
    cross_ref_results: list[ValidationResult],
    version_results: list[VersionMismatch],
) -> None:
    """Print a Rich-formatted report to the console.

    Args:
        cross_ref_results: Validation findings from cross-reference checks.
        version_results: Version mismatch findings.
    """
    console = Console()

    errors = [r for r in cross_ref_results if r.severity == Severity.ERROR]
    warnings = [r for r in cross_ref_results if r.severity == Severity.WARNING]

    # Header
    console.print()
    console.print("[bold]DSM Integrity Report[/bold]")
    console.print()

    # Summary
    error_style = "red bold" if errors else "green"
    warn_style = "yellow" if warnings else "green"
    version_style = "red bold" if version_results else "green"

    console.print(f"  Errors:             [{error_style}]{len(errors)}[/{error_style}]")
    console.print(f"  Warnings:           [{warn_style}]{len(warnings)}[/{warn_style}]")
    console.print(f"  Version mismatches: [{version_style}]{len(version_results)}[/{version_style}]")
    console.print()

    if not errors and not warnings and not version_results:
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
