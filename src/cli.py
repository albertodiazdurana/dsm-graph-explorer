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
from parser.cross_ref_extractor import extract_cross_references
from parser.markdown_parser import parse_markdown_file
from reporter.report_generator import generate_markdown_report, print_rich_report
from validator.cross_ref_validator import Severity, validate_cross_references
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


@click.command()
@click.version_option(version="0.2.0", prog_name="dsm-validate")
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
def main(
    paths: tuple[str, ...],
    output: str | None,
    strict: bool,
    glob_pattern: str,
    version_files: tuple[str, ...],
    exclude_patterns: tuple[str, ...],
    config_path: str | None,
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

    # Collect files
    try:
        md_files = collect_markdown_files(paths, glob_pattern)
    except click.BadParameter as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)

    if not md_files:
        click.echo("No markdown files found.", err=True)
        sys.exit(2)

    # Apply exclusion filters
    base_path = Path(paths[0]).resolve() if paths else Path.cwd()
    original_count = len(md_files)
    md_files = filter_files(md_files, config.exclude, base_path)
    excluded_count = original_count - len(md_files)

    if not md_files:
        click.echo("All files excluded by patterns. Nothing to validate.", err=True)
        sys.exit(2)

    # Parse and extract
    start = time.perf_counter()
    documents = []
    references = {}

    for f in md_files:
        doc = parse_markdown_file(f)
        documents.append(doc)
        refs = extract_cross_references(f)
        if refs:
            references[doc.file] = refs

    # Validate cross-references
    cross_ref_results = validate_cross_references(documents, references)

    # Validate version consistency
    version_results = []
    if version_files:
        version_results = validate_version_consistency(
            [Path(vf) for vf in version_files]
        )

    elapsed = time.perf_counter() - start

    # Report
    print_rich_report(cross_ref_results, version_results)

    # Summary line
    errors = [r for r in cross_ref_results if r.severity == Severity.ERROR]
    warnings = [r for r in cross_ref_results if r.severity == Severity.WARNING]

    summary_parts = [
        f"Scanned {len(md_files)} file(s)",
    ]
    if excluded_count > 0:
        summary_parts.append(f"({excluded_count} excluded)")
    summary_parts.append(f"in {elapsed:.2f}s.")
    summary_parts.append(
        f"Found {len(errors)} error(s), {len(warnings)} warning(s), "
        f"{len(version_results)} version mismatch(es)."
    )

    click.echo(f"\n{' '.join(summary_parts)}")

    # Write markdown report if requested
    if output:
        generate_markdown_report(
            cross_ref_results, version_results, output_path=output
        )
        click.echo(f"Report written to {output}")

    # Exit code based on strict mode and severity
    if config.strict and errors:
        sys.exit(1)
