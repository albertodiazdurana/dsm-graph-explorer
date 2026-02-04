"""File filtering based on exclusion patterns.

Uses fnmatch for glob-style pattern matching to filter files
for validation based on exclusion patterns from config or CLI.
"""

import fnmatch
from pathlib import Path


def normalize_path(path: Path | str, base_path: Path | None = None) -> str:
    """Normalize path to forward slashes for consistent pattern matching.

    Args:
        path: Path to normalize.
        base_path: If provided, make path relative to this base.

    Returns:
        Normalized path string with forward slashes.
    """
    path = Path(path)

    if base_path is not None:
        try:
            path = path.relative_to(base_path)
        except ValueError:
            # Path is not relative to base_path, use as-is
            pass

    # Convert to forward slashes for consistent matching
    return str(path).replace("\\", "/")


def should_exclude(
    filepath: Path | str,
    patterns: list[str],
    base_path: Path | None = None,
) -> bool:
    """Check if a file should be excluded based on patterns.

    Supports glob patterns:
    - `*` matches any characters except /
    - `**` matches any characters including /
    - `?` matches single character
    - `[seq]` matches any character in seq

    Args:
        filepath: Path to check.
        patterns: List of exclusion patterns.
        base_path: Base path for relative matching.

    Returns:
        True if file matches any exclusion pattern.
    """
    if not patterns:
        return False

    # Normalize the filepath
    normalized = normalize_path(filepath, base_path)
    path_parts = normalized.split("/")

    # Also get just the filename for basename-only patterns
    filename = Path(filepath).name

    for pattern in patterns:
        # Normalize pattern to forward slashes
        pattern = pattern.replace("\\", "/")

        # Check if pattern matches just the filename
        # (for patterns like "CHANGELOG.md" without path)
        if "/" not in pattern and fnmatch.fnmatch(filename, pattern):
            return True

        # Handle ** patterns (match any depth)
        if "**" in pattern:
            if _match_double_star(normalized, pattern):
                return True
        else:
            # For patterns without **, match segment by segment
            # This ensures plan/* matches plan/foo.md but NOT plan/bar/baz.md
            pattern_parts = pattern.split("/")
            if _match_segments(path_parts, pattern_parts):
                return True

    return False


def _match_segments(path_parts: list[str], pattern_parts: list[str]) -> bool:
    """Match path segments against pattern segments.

    Single * in a segment only matches that segment, not path separators.

    Args:
        path_parts: Path split by /
        pattern_parts: Pattern split by /

    Returns:
        True if all segments match.
    """
    # Must have same number of segments
    if len(path_parts) != len(pattern_parts):
        return False

    for path_seg, pattern_seg in zip(path_parts, pattern_parts):
        if not fnmatch.fnmatch(path_seg, pattern_seg):
            return False

    return True


def _match_double_star(normalized: str, pattern: str) -> bool:
    """Match path against pattern containing **.

    ** matches zero or more path segments.

    Args:
        normalized: Normalized path string.
        pattern: Pattern containing **.

    Returns:
        True if path matches pattern.
    """
    # Handle **/suffix patterns (match at any depth)
    if pattern.startswith("**/"):
        suffix_pattern = pattern[3:]  # Remove **/
        parts = normalized.split("/")

        # Check if any suffix of the path matches
        for i in range(len(parts)):
            subpath = "/".join(parts[i:])
            # Recursively handle the suffix (which may or may not have **)
            if "**" in suffix_pattern:
                if _match_double_star(subpath, suffix_pattern):
                    return True
            else:
                suffix_parts = suffix_pattern.split("/")
                subpath_parts = subpath.split("/")
                if _match_segments(subpath_parts, suffix_parts):
                    return True

        return False

    # Handle prefix/**/ patterns
    if "/**/" in pattern:
        before, after = pattern.split("/**/", 1)
        before_parts = before.split("/") if before else []
        path_parts = normalized.split("/")

        # Check if path starts with before
        if before_parts:
            if len(path_parts) < len(before_parts):
                return False
            if not _match_segments(path_parts[: len(before_parts)], before_parts):
                return False
            # Continue matching the rest
            remaining = "/".join(path_parts[len(before_parts) :])
            return _match_double_star(remaining, "**/" + after)
        else:
            return _match_double_star(normalized, "**/" + after)

    # Simple expansion for other cases (e.g., trailing **)
    expanded = pattern.replace("**", "*")
    return fnmatch.fnmatch(normalized, expanded)


def filter_files(
    files: list[Path],
    exclude_patterns: list[str],
    base_path: Path | None = None,
) -> list[Path]:
    """Filter a list of files based on exclusion patterns.

    Args:
        files: List of file paths to filter.
        exclude_patterns: Patterns to exclude.
        base_path: Base path for relative matching.

    Returns:
        List of files not matching any exclusion pattern.
    """
    if not exclude_patterns:
        return files

    return [
        f for f in files
        if not should_exclude(f, exclude_patterns, base_path)
    ]
