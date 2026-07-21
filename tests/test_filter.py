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
        filepath = Path("/repo/dsm-docs/file.md")
        result = normalize_path(filepath, base)
        assert result == "dsm-docs/file.md"

    def test_non_relative_path_unchanged(self):
        """Non-relative path is returned as-is."""
        base = Path("/other")
        filepath = Path("/repo/dsm-docs/file.md")
        result = normalize_path(filepath, base)
        # Should contain the full path since it's not relative to base
        assert "dsm-docs/file.md" in result


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
        assert should_exclude("dsm-docs/file.md", ["plan/*"]) is False

    def test_nested_directory_not_matched_by_single_star(self):
        """Single * doesn't match nested directories."""
        # plan/* should NOT match plan/subdir/file.md
        assert should_exclude("plan/subdir/file.md", ["plan/*"]) is False

    def test_double_star_matches_any_depth(self):
        """** pattern matches any directory depth."""
        assert should_exclude("archive/file.md", ["**/archive/*"]) is True
        assert should_exclude("dsm-docs/archive/file.md", ["**/archive/*"]) is True
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
            Path("dsm-docs/guide.md"),
        ]
        result = filter_files(files, ["CHANGELOG.md"])
        assert Path("README.md") in result
        assert Path("dsm-docs/guide.md") in result
        assert Path("CHANGELOG.md") not in result

    def test_filters_multiple_patterns(self):
        """Filters files matching any pattern."""
        files = [
            Path("README.md"),
            Path("plan/draft.md"),
            Path("CHANGELOG.md"),
            Path("dsm-docs/guide.md"),
        ]
        result = filter_files(files, ["plan/*", "CHANGELOG.md"])
        assert len(result) == 2
        assert Path("README.md") in result
        assert Path("dsm-docs/guide.md") in result


class TestEXP001ExclusionPatternValidation:
    """EXP-001: Exclusion Pattern Validation from epoch-2-plan.

    Test matrix:
    | Pattern | Input Files | Expected Excluded |
    |---------|-------------|-------------------|
    | `CHANGELOG.md` | `CHANGELOG.md`, `dsm-docs/CHANGELOG.md` | Only `CHANGELOG.md` |
    | `plan/*` | `plan/foo.md`, `plan/bar/baz.md` | `plan/foo.md` only |
    | `**/archive/*` | `archive/x.md`, `dsm-docs/archive/y.md` | Both |
    | Multiple | All above combined | Union of all |
    """

    def test_exp001_exact_filename_excludes_only_root(self):
        """CHANGELOG.md excludes only root-level file, not nested."""
        # Pattern: CHANGELOG.md
        # Expected: Only CHANGELOG.md excluded, not dsm-docs/CHANGELOG.md
        pattern = ["CHANGELOG.md"]

        assert should_exclude("CHANGELOG.md", pattern) is True
        # Note: dsm-docs/CHANGELOG.md should NOT be excluded by plain "CHANGELOG.md"
        # because it's a different path
        assert should_exclude("dsm-docs/CHANGELOG.md", pattern) is True  # filename matches

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
        # Expected: Both archive/x.md and dsm-docs/archive/y.md excluded
        pattern = ["**/archive/*"]

        assert should_exclude("archive/x.md", pattern) is True
        assert should_exclude("dsm-docs/archive/y.md", pattern) is True

    def test_exp001_multiple_patterns_union(self):
        """Multiple patterns exclude union of all matches."""
        # Combined test with all patterns
        patterns = ["CHANGELOG.md", "plan/*", "**/archive/*"]

        files = [
            Path("CHANGELOG.md"),
            Path("dsm-docs/CHANGELOG.md"),
            Path("plan/foo.md"),
            Path("plan/bar/baz.md"),
            Path("archive/x.md"),
            Path("dsm-docs/archive/y.md"),
            Path("README.md"),
            Path("dsm-docs/guide.md"),
        ]

        result = filter_files(files, patterns)

        # Should remain: plan/bar/baz.md, README.md, dsm-docs/guide.md
        assert Path("README.md") in result
        assert Path("dsm-docs/guide.md") in result
        assert Path("plan/bar/baz.md") in result

        # Should be excluded
        assert Path("CHANGELOG.md") not in result
        assert Path("plan/foo.md") not in result
        assert Path("archive/x.md") not in result
        assert Path("dsm-docs/archive/y.md") not in result


class TestDSMRepoExclusionPatterns:
    """Test with actual DSM repository exclusion patterns."""

    def test_dsm_exclusion_patterns(self):
        """Test exclusion patterns from validated DSM config."""
        patterns = [
            "CHANGELOG.md",
            "dsm-docs/checkpoints/*",
            "references/*",
            "plan/*",
            "plan/archive/*",
        ]

        # Files that should be excluded
        assert should_exclude("CHANGELOG.md", patterns) is True
        assert should_exclude("dsm-docs/checkpoints/sprint1.md", patterns) is True
        assert should_exclude("references/old-doc.md", patterns) is True
        assert should_exclude("plan/backlog.md", patterns) is True
        assert should_exclude("plan/archive/old.md", patterns) is True

        # Files that should NOT be excluded
        assert should_exclude("README.md", patterns) is False
        assert should_exclude("DSM_1.0.md", patterns) is False
        assert should_exclude("dsm-docs/guide.md", patterns) is False


class TestDefaultExcludes:
    """Tests for DEFAULT_EXCLUDES (BL-302 Phase 2, P1).

    The knowledge summary was observed emitting 16 of 57 directories from
    `.venv/` and `.pytest_cache/` (S55). These tests pin the default
    exclusion set and, critically, the pattern form it must use.
    """

    def test_default_excludes_importable(self):
        """DEFAULT_EXCLUDES is exported from config_loader."""
        from config.config_loader import DEFAULT_EXCLUDES

        assert isinstance(DEFAULT_EXCLUDES, list)
        assert len(DEFAULT_EXCLUDES) > 0

    @pytest.mark.parametrize(
        "path",
        [
            ".venv/lib/python3.12/site-packages/numpy-2.4.3.dist-info/licenses/numpy/random/LICENSE.md",
            ".venv/lib/python3.12/site-packages/black-24.10.0.dist-info/licenses/AUTHORS.md",
            ".venv/lib/python3.12/site-packages/scipy/fft/_pocketfft/LICENSE.md",
            ".pytest_cache/README.md",
            ".claude/transcripts/2026-03-13T07:01-ST.md",
        ],
    )
    def test_dependency_noise_is_excluded(self, path):
        """Paths observed polluting the S55 knowledge summary are excluded."""
        from config.config_loader import DEFAULT_EXCLUDES

        assert should_exclude(path, DEFAULT_EXCLUDES) is True

    @pytest.mark.parametrize(
        "path",
        [
            "README.md",
            "dsm-docs/plans/epoch-5-plan.md",
            "dsm-docs/blog/epoch-5/journal.md",
            ".claude/CLAUDE.md",
            "src/analysis/knowledge_summary.py",
            "_inbox/README.md",
        ],
    )
    def test_project_content_survives(self, path):
        """Project content is not caught by the defaults."""
        from config.config_loader import DEFAULT_EXCLUDES

        assert should_exclude(path, DEFAULT_EXCLUDES) is False

    def test_claude_config_survives_while_transcripts_excluded(self):
        """`.claude/` is excluded narrowly: transcripts go, CLAUDE.md stays.

        Resolves BL-302 Phase 2 Open Design Question 3. Agent session
        transcripts are not project knowledge; CLAUDE.md arguably is.
        """
        from config.config_loader import DEFAULT_EXCLUDES

        assert should_exclude(".claude/transcripts/x-ST.md", DEFAULT_EXCLUDES) is True
        assert should_exclude(".claude/CLAUDE.md", DEFAULT_EXCLUDES) is False

    def test_defaults_use_double_star_form(self):
        """Every default uses the `**/X/**` form.

        Regression guard on `_match_segments`, which requires an equal
        segment count. A bare `.venv` or `.venv/*` pattern matches nothing
        nested, so a defaults list written in the natural-looking short form
        would silently exclude nothing at all.
        """
        from config.config_loader import DEFAULT_EXCLUDES

        for pattern in DEFAULT_EXCLUDES:
            assert pattern.startswith("**/"), f"{pattern} must start with **/"
            assert pattern.endswith("/**"), f"{pattern} must end with /**"

    def test_naive_patterns_do_not_match_nested_paths(self):
        """Pins the semantics the `**/X/**` form exists to work around.

        If a future refactor makes bare directory names match recursively,
        this fails and the defaults should be revisited.
        """
        nested = ".venv/lib/python3.12/site-packages/x/LICENSE.md"
        assert should_exclude(nested, [".venv"]) is False
        assert should_exclude(nested, [".venv/*"]) is False
        assert should_exclude(nested, ["**/.venv/**"]) is True


class TestDefaultExcludesConfigIntegration:
    """DEFAULT_EXCLUDES is applied through config merging (BL-302 P2, P1)."""

    def test_merge_applies_defaults(self):
        """merge_config_with_cli folds in the defaults by default."""
        from config.config_loader import Config, merge_config_with_cli

        merged = merge_config_with_cli(Config())
        assert should_exclude(".venv/lib/x/LICENSE.md", merged.exclude) is True

    def test_merge_preserves_config_patterns(self):
        """User patterns survive alongside the defaults."""
        from config.config_loader import Config, merge_config_with_cli

        merged = merge_config_with_cli(Config(exclude=["outputs/*"]))
        assert "outputs/*" in merged.exclude
        assert should_exclude(".venv/lib/x/LICENSE.md", merged.exclude) is True

    def test_merge_preserves_cli_patterns(self):
        """CLI --exclude still merges alongside the defaults."""
        from config.config_loader import Config, merge_config_with_cli

        merged = merge_config_with_cli(Config(), cli_exclude=("scratch/*",))
        assert "scratch/*" in merged.exclude
        assert should_exclude(".venv/lib/x/LICENSE.md", merged.exclude) is True

    def test_opt_out_disables_defaults(self):
        """use_default_excludes=False restores the previous behaviour."""
        from config.config_loader import Config, merge_config_with_cli

        merged = merge_config_with_cli(Config(use_default_excludes=False))
        assert should_exclude(".venv/lib/x/LICENSE.md", merged.exclude) is False
