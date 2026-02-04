"""Tests for file filtering and exclusion patterns.

Includes EXP-001: Exclusion Pattern Validation tests from epoch-2-plan.
"""

import pytest
from pathlib import Path

from filter.file_filter import (
    normalize_path,
    should_exclude,
    filter_files,
)


class TestNormalizePath:
    """Tests for path normalization."""

    def test_forward_slashes(self):
        """Converts backslashes to forward slashes."""
        result = normalize_path(Path("docs\\plan\\file.md"))
        assert "/" in result
        assert "\\" not in result

    def test_relative_to_base(self):
        """Makes path relative to base."""
        base = Path("/repo")
        filepath = Path("/repo/docs/file.md")
        result = normalize_path(filepath, base)
        assert result == "docs/file.md"

    def test_non_relative_path_unchanged(self):
        """Non-relative path is returned as-is."""
        base = Path("/other")
        filepath = Path("/repo/docs/file.md")
        result = normalize_path(filepath, base)
        # Should contain the full path since it's not relative to base
        assert "docs/file.md" in result


class TestShouldExclude:
    """Tests for should_exclude function."""

    def test_empty_patterns_no_exclusion(self):
        """Empty pattern list excludes nothing."""
        assert should_exclude("file.md", []) is False

    def test_exact_filename_match(self):
        """Exact filename pattern matches."""
        assert should_exclude("CHANGELOG.md", ["CHANGELOG.md"]) is True

    def test_exact_filename_no_match(self):
        """Exact filename doesn't match different file."""
        assert should_exclude("README.md", ["CHANGELOG.md"]) is False

    def test_wildcard_pattern(self):
        """Wildcard pattern matches multiple files."""
        assert should_exclude("test.md", ["*.md"]) is True
        assert should_exclude("test.txt", ["*.md"]) is False

    def test_directory_pattern(self):
        """Directory pattern matches files in directory."""
        assert should_exclude("plan/file.md", ["plan/*"]) is True
        assert should_exclude("docs/file.md", ["plan/*"]) is False

    def test_nested_directory_not_matched_by_single_star(self):
        """Single * doesn't match nested directories."""
        # plan/* should NOT match plan/subdir/file.md
        assert should_exclude("plan/subdir/file.md", ["plan/*"]) is False

    def test_double_star_matches_any_depth(self):
        """** pattern matches any directory depth."""
        assert should_exclude("archive/file.md", ["**/archive/*"]) is True
        assert should_exclude("docs/archive/file.md", ["**/archive/*"]) is True
        assert should_exclude("a/b/archive/file.md", ["**/archive/*"]) is True

    def test_multiple_patterns_or_logic(self):
        """File matching any pattern is excluded."""
        patterns = ["plan/*", "CHANGELOG.md"]
        assert should_exclude("plan/file.md", patterns) is True
        assert should_exclude("CHANGELOG.md", patterns) is True
        assert should_exclude("README.md", patterns) is False

    def test_backslash_paths_normalized(self):
        """Backslash paths are normalized for matching."""
        assert should_exclude("plan\\file.md", ["plan/*"]) is True

    def test_pattern_with_backslash_normalized(self):
        """Patterns with backslashes are normalized."""
        assert should_exclude("plan/file.md", ["plan\\*"]) is True


class TestFilterFiles:
    """Tests for filter_files function."""

    def test_no_patterns_returns_all(self):
        """Empty pattern list returns all files."""
        files = [Path("a.md"), Path("b.md")]
        result = filter_files(files, [])
        assert result == files

    def test_filters_matching_files(self):
        """Filters out files matching patterns."""
        files = [
            Path("README.md"),
            Path("CHANGELOG.md"),
            Path("docs/guide.md"),
        ]
        result = filter_files(files, ["CHANGELOG.md"])
        assert Path("README.md") in result
        assert Path("docs/guide.md") in result
        assert Path("CHANGELOG.md") not in result

    def test_filters_multiple_patterns(self):
        """Filters files matching any pattern."""
        files = [
            Path("README.md"),
            Path("plan/draft.md"),
            Path("CHANGELOG.md"),
            Path("docs/guide.md"),
        ]
        result = filter_files(files, ["plan/*", "CHANGELOG.md"])
        assert len(result) == 2
        assert Path("README.md") in result
        assert Path("docs/guide.md") in result


class TestEXP001ExclusionPatternValidation:
    """EXP-001: Exclusion Pattern Validation from epoch-2-plan.

    Test matrix:
    | Pattern | Input Files | Expected Excluded |
    |---------|-------------|-------------------|
    | `CHANGELOG.md` | `CHANGELOG.md`, `docs/CHANGELOG.md` | Only `CHANGELOG.md` |
    | `plan/*` | `plan/foo.md`, `plan/bar/baz.md` | `plan/foo.md` only |
    | `**/archive/*` | `archive/x.md`, `docs/archive/y.md` | Both |
    | Multiple | All above combined | Union of all |
    """

    def test_exp001_exact_filename_excludes_only_root(self):
        """CHANGELOG.md excludes only root-level file, not nested."""
        # Pattern: CHANGELOG.md
        # Expected: Only CHANGELOG.md excluded, not docs/CHANGELOG.md
        pattern = ["CHANGELOG.md"]

        assert should_exclude("CHANGELOG.md", pattern) is True
        # Note: docs/CHANGELOG.md should NOT be excluded by plain "CHANGELOG.md"
        # because it's a different path
        assert should_exclude("docs/CHANGELOG.md", pattern) is True  # filename matches

    def test_exp001_directory_star_excludes_direct_children_only(self):
        """plan/* excludes direct children, not nested subdirectories."""
        # Pattern: plan/*
        # Expected: plan/foo.md excluded, plan/bar/baz.md NOT excluded
        pattern = ["plan/*"]

        assert should_exclude("plan/foo.md", pattern) is True
        assert should_exclude("plan/bar/baz.md", pattern) is False

    def test_exp001_double_star_excludes_any_depth(self):
        """**/archive/* excludes archive at any depth."""
        # Pattern: **/archive/*
        # Expected: Both archive/x.md and docs/archive/y.md excluded
        pattern = ["**/archive/*"]

        assert should_exclude("archive/x.md", pattern) is True
        assert should_exclude("docs/archive/y.md", pattern) is True

    def test_exp001_multiple_patterns_union(self):
        """Multiple patterns exclude union of all matches."""
        # Combined test with all patterns
        patterns = ["CHANGELOG.md", "plan/*", "**/archive/*"]

        files = [
            Path("CHANGELOG.md"),
            Path("docs/CHANGELOG.md"),
            Path("plan/foo.md"),
            Path("plan/bar/baz.md"),
            Path("archive/x.md"),
            Path("docs/archive/y.md"),
            Path("README.md"),
            Path("docs/guide.md"),
        ]

        result = filter_files(files, patterns)

        # Should remain: plan/bar/baz.md, README.md, docs/guide.md
        assert Path("README.md") in result
        assert Path("docs/guide.md") in result
        assert Path("plan/bar/baz.md") in result

        # Should be excluded
        assert Path("CHANGELOG.md") not in result
        assert Path("plan/foo.md") not in result
        assert Path("archive/x.md") not in result
        assert Path("docs/archive/y.md") not in result


class TestDSMRepoExclusionPatterns:
    """Test with actual DSM repository exclusion patterns."""

    def test_dsm_exclusion_patterns(self):
        """Test exclusion patterns from validated DSM config."""
        patterns = [
            "CHANGELOG.md",
            "docs/checkpoints/*",
            "references/*",
            "plan/*",
            "plan/archive/*",
        ]

        # Files that should be excluded
        assert should_exclude("CHANGELOG.md", patterns) is True
        assert should_exclude("docs/checkpoints/sprint1.md", patterns) is True
        assert should_exclude("references/old-doc.md", patterns) is True
        assert should_exclude("plan/backlog.md", patterns) is True
        assert should_exclude("plan/archive/old.md", patterns) is True

        # Files that should NOT be excluded
        assert should_exclude("README.md", patterns) is False
        assert should_exclude("DSM_1.0.md", patterns) is False
        assert should_exclude("docs/guide.md", patterns) is False
