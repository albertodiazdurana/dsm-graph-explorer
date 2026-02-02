"""CLI interface for DSM integrity validation.

Wires the full pipeline: find files → parse → extract refs → validate → report.
Provides both Rich console output and optional markdown report file.
"""

import sys
import time
from pathlib import Path

import click

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
@click.version_option(version="0.1.0", prog_name="dsm-validate")
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
    help="Exit with code 1 if any errors are found (for CI).",
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
def main(
    paths: tuple[str, ...],
    output: str | None,
    strict: bool,
    glob_pattern: str,
    version_files: tuple[str, ...],
) -> None:
    """Validate cross-references and version consistency in DSM markdown files.

    PATHS can be markdown files or directories. Directories are scanned
    recursively for *.md files (customisable with --glob).

    If no PATHS are given, validates the current directory.
    """
    if not paths:
        paths = (".",)

    # Collect files
    try:
        md_files = collect_markdown_files(paths, glob_pattern)
    except click.BadParameter as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)

    if not md_files:
        click.echo("No markdown files found.", err=True)
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
    click.echo(
        f"\nScanned {len(md_files)} file(s) in {elapsed:.2f}s. "
        f"Found {len(errors)} error(s), {len(warnings)} warning(s), "
        f"{len(version_results)} version mismatch(es)."
    )

    # Write markdown report if requested
    if output:
        generate_markdown_report(
            cross_ref_results, version_results, output_path=output
        )
        click.echo(f"Report written to {output}")

    # Exit code
    if strict and errors:
        sys.exit(1)
