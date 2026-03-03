"""Report formatting for convention lint results.

Produces Rich console output and markdown text from LintResult lists.
"""

from collections import defaultdict

from rich.console import Console
from rich.table import Table

from linter.models import LintResult, RULE_DESCRIPTIONS
from validator.cross_ref_validator import Severity


def _group_by_file(results: list[LintResult]) -> dict[str, list[LintResult]]:
    """Group lint results by file path, preserving order."""
    grouped: dict[str, list[LintResult]] = defaultdict(list)
    for r in results:
        grouped[r.file].append(r)
    return dict(grouped)


def _count_by_severity(results: list[LintResult]) -> dict[Severity, int]:
    """Count results by severity level."""
    counts: dict[Severity, int] = {s: 0 for s in Severity}
    for r in results:
        counts[r.severity] += 1
    return counts


def _severity_style(severity: Severity) -> str:
    """Return Rich style string for a severity level."""
    if severity == Severity.ERROR:
        return "red bold"
    if severity == Severity.WARNING:
        return "yellow"
    return "blue"


def print_lint_results(results: list[LintResult]) -> None:
    """Print lint results to the console using Rich formatting."""
    console = Console()
    counts = _count_by_severity(results)
    grouped = _group_by_file(results)

    # Header
    console.print()
    console.print("[bold]DSM Convention Lint Report[/bold]")
    console.print()

    # Summary
    error_style = "red bold" if counts[Severity.ERROR] else "green"
    warn_style = "yellow" if counts[Severity.WARNING] else "green"
    info_style = "blue" if counts[Severity.INFO] else "green"

    console.print(f"  Errors:   [{error_style}]{counts[Severity.ERROR]}[/{error_style}]")
    console.print(f"  Warnings: [{warn_style}]{counts[Severity.WARNING]}[/{warn_style}]")
    console.print(f"  Info:     [{info_style}]{counts[Severity.INFO]}[/{info_style}]")
    console.print(f"  Files:    {len(grouped)}")
    console.print()

    if not results:
        console.print("[green]No lint issues found.[/green]")
        console.print()
        return

    # Results table grouped by file
    table = Table(title="Lint Findings", title_style="bold")
    table.add_column("File", style="cyan")
    table.add_column("Line:Col", justify="right")
    table.add_column("Rule", style="bold")
    table.add_column("Severity")
    table.add_column("Message")

    for file_path, file_results in grouped.items():
        for i, r in enumerate(file_results):
            sev_style = _severity_style(r.severity)
            table.add_row(
                file_path if i == 0 else "",
                f"{r.line}:{r.column}",
                r.rule.value,
                f"[{sev_style}]{r.severity.value.upper()}[/{sev_style}]",
                r.message,
            )

    console.print(table)
    console.print()


def format_lint_markdown(results: list[LintResult]) -> str:
    """Format lint results as a markdown string."""
    counts = _count_by_severity(results)
    grouped = _group_by_file(results)

    lines: list[str] = []
    lines.append("# DSM Convention Lint Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Errors:** {counts[Severity.ERROR]}")
    lines.append(f"- **Warnings:** {counts[Severity.WARNING]}")
    lines.append(f"- **Info:** {counts[Severity.INFO]}")
    lines.append(f"- **Files scanned:** {len(grouped)}")
    lines.append("")

    if not results:
        lines.append("No lint issues found.")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Findings")
    lines.append("")
    lines.append("| File | Line:Col | Rule | Severity | Message |")
    lines.append("|------|----------|------|----------|---------|")

    for file_results in grouped.values():
        for r in file_results:
            lines.append(
                f"| {r.file} | {r.line}:{r.column} | {r.rule.value} | "
                f"{r.severity.value.upper()} | {r.message} |"
            )

    lines.append("")

    # Rule reference
    lines.append("## Rule Reference")
    lines.append("")
    for rule, desc in RULE_DESCRIPTIONS.items():
        lines.append(f"- **{rule.value}:** {desc}")
    lines.append("")

    return "\n".join(lines)