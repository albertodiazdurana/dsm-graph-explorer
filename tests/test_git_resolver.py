"""Tests for git_ref.git_resolver and content-based parser variants.

Uses the current repository as test data with known historical refs:
- REF_OLD (87d869d): Sprint 1 complete, 12 markdown files
- HEAD: current state, 86+ markdown files
"""

import subprocess
from pathlib import Path

import pytest

from git_ref.git_resolver import GitRefError, list_files_at_ref, read_file_at_ref, resolve_ref
from parser.cross_ref_extractor import (
    extract_cross_references,
    extract_cross_references_from_content,
)
from parser.markdown_parser import parse_markdown_content, parse_markdown_file

REPO_PATH = Path(__file__).resolve().parents[1]
REF_OLD_SHORT = "87d869d"


@pytest.fixture(scope="module")
def head_sha():
    """Resolve HEAD to full SHA once per module."""
    return resolve_ref(REPO_PATH, "HEAD")


@pytest.fixture(scope="module")
def old_sha():
    """Resolve old ref to full SHA once per module."""
    return resolve_ref(REPO_PATH, REF_OLD_SHORT)


# ── resolve_ref ──────────────────────────────────────────────────────


class TestResolveRef:
    def test_head_resolves_to_40_char_sha(self, head_sha):
        assert len(head_sha) == 40
        assert all(c in "0123456789abcdef" for c in head_sha)

    def test_short_sha_resolves_to_full(self, old_sha):
        assert len(old_sha) == 40
        assert old_sha.startswith(REF_OLD_SHORT)

    def test_invalid_ref_raises_error(self):
        with pytest.raises(GitRefError, match="Cannot resolve ref"):
            resolve_ref(REPO_PATH, "nonexistent-ref-xyz-999")

    def test_invalid_repo_path_raises_error(self, tmp_path):
        with pytest.raises(GitRefError):
            resolve_ref(tmp_path, "HEAD")

    def test_accepts_string_path(self, head_sha):
        result = resolve_ref(str(REPO_PATH), "HEAD")
        assert result == head_sha


# ── list_files_at_ref ────────────────────────────────────────────────


class TestListFilesAtRef:
    def test_old_ref_has_expected_md_count(self, old_sha):
        files = list_files_at_ref(REPO_PATH, old_sha)
        assert len(files) == 12

    def test_head_has_more_files_than_old(self, head_sha, old_sha):
        head_files = list_files_at_ref(REPO_PATH, head_sha)
        old_files = list_files_at_ref(REPO_PATH, old_sha)
        assert len(head_files) > len(old_files)

    def test_results_are_sorted(self, head_sha):
        files = list_files_at_ref(REPO_PATH, head_sha)
        assert files == sorted(files)

    def test_readme_present_at_both_refs(self, head_sha, old_sha):
        assert "README.md" in list_files_at_ref(REPO_PATH, head_sha)
        assert "README.md" in list_files_at_ref(REPO_PATH, old_sha)

    def test_custom_pattern_filters(self, head_sha):
        py_files = list_files_at_ref(REPO_PATH, head_sha, pattern="*.py")
        md_files = list_files_at_ref(REPO_PATH, head_sha, pattern="*.md")
        assert all(f.endswith(".py") for f in py_files)
        assert all(f.endswith(".md") for f in md_files)

    def test_no_match_pattern_returns_empty(self, head_sha):
        files = list_files_at_ref(REPO_PATH, head_sha, pattern="*.nonexistent")
        assert files == []

    def test_invalid_sha_raises_error(self):
        with pytest.raises(GitRefError, match="Cannot list files"):
            list_files_at_ref(REPO_PATH, "0" * 40)

    def test_added_file_not_in_old_ref(self, head_sha, old_sha):
        head_files = set(list_files_at_ref(REPO_PATH, head_sha))
        old_files = set(list_files_at_ref(REPO_PATH, old_sha))
        added = head_files - old_files
        assert len(added) > 0


# ── read_file_at_ref ─────────────────────────────────────────────────


class TestReadFileAtRef:
    def test_read_readme_at_old_ref(self, old_sha):
        content = read_file_at_ref(REPO_PATH, old_sha, "README.md")
        assert len(content) > 0
        assert "DSM" in content or "dsm" in content.lower()

    def test_read_readme_at_head(self, head_sha):
        content = read_file_at_ref(REPO_PATH, head_sha, "README.md")
        assert len(content) > 0

    def test_content_differs_between_refs(self, head_sha, old_sha):
        old_content = read_file_at_ref(REPO_PATH, old_sha, "README.md")
        head_content = read_file_at_ref(REPO_PATH, head_sha, "README.md")
        assert old_content != head_content

    def test_nonexistent_file_raises_error(self, head_sha):
        with pytest.raises(GitRefError, match="Cannot read"):
            read_file_at_ref(REPO_PATH, head_sha, "nonexistent/file.md")

    def test_file_only_at_head_not_at_old(self, head_sha, old_sha):
        head_files = set(list_files_at_ref(REPO_PATH, head_sha))
        old_files = set(list_files_at_ref(REPO_PATH, old_sha))
        added = sorted(head_files - old_files)
        assert len(added) > 0
        # Should succeed at HEAD
        content = read_file_at_ref(REPO_PATH, head_sha, added[0])
        assert len(content) > 0
        # Should fail at old ref
        with pytest.raises(GitRefError):
            read_file_at_ref(REPO_PATH, old_sha, added[0])


# ── Content-based parser variants ────────────────────────────────────


class TestParseMarkdownContent:
    def test_matches_file_based_parser(self, tmp_path):
        """Content-based parser produces same sections as file-based."""
        md = "# Title\n\nSome text.\n\n## 1.2 Subsection\n\nMore text.\n"
        md_file = tmp_path / "test.md"
        md_file.write_text(md, encoding="utf-8")

        from_file = parse_markdown_file(md_file)
        from_content = parse_markdown_content(md, "test.md")

        assert len(from_file.sections) == len(from_content.sections)
        for sf, sc in zip(from_file.sections, from_content.sections):
            assert sf.number == sc.number
            assert sf.title == sc.title
            assert sf.line == sc.line
            assert sf.level == sc.level

    def test_virtual_file_path_stored(self):
        md = "# Hello\n"
        doc = parse_markdown_content(md, "virtual/path.md")
        assert doc.file == "virtual/path.md"

    def test_empty_content(self):
        doc = parse_markdown_content("", "empty.md")
        assert doc.sections == []

    def test_excerpt_preserved(self):
        md = "## 1.1 Title\n\nThis is the excerpt text.\n"
        doc = parse_markdown_content(md, "test.md")
        assert doc.sections[0].context_excerpt == "This is the excerpt text."


class TestExtractCrossReferencesFromContent:
    def test_matches_file_based_extractor(self, tmp_path):
        """Content-based extractor produces same refs as file-based."""
        md = "See Section 2.3.7 for details.\n\nAlso DSM_1.0 applies.\n"
        md_file = tmp_path / "test.md"
        md_file.write_text(md, encoding="utf-8")

        from_file = extract_cross_references(md_file)
        from_content = extract_cross_references_from_content(md, "test.md")

        assert len(from_file) == len(from_content)
        for rf, rc in zip(from_file, from_content):
            assert rf.type == rc.type
            assert rf.target == rc.target
            assert rf.line == rc.line

    def test_empty_content(self):
        refs = extract_cross_references_from_content("", "empty.md")
        assert refs == []

    def test_code_blocks_skipped(self):
        md = "```\nSection 1.2.3 in code\n```\nSection 4.5.6 outside\n"
        refs = extract_cross_references_from_content(md, "test.md")
        assert len(refs) == 1
        assert refs[0].target == "4.5.6"

    def test_multiple_ref_types(self):
        md = "Section 1.2 and Appendix A and DSM_2.0 here.\n"
        refs = extract_cross_references_from_content(md, "test.md")
        types = {r.type for r in refs}
        assert types == {"section", "appendix", "dsm"}


# ── Integration: git show → content parser ───────────────────────────


class TestGitShowToParser:
    def test_parse_historical_readme(self, old_sha):
        """Read README.md at old ref via git show, parse it."""
        content = read_file_at_ref(REPO_PATH, old_sha, "README.md")
        doc = parse_markdown_content(content, "README.md")
        assert len(doc.sections) > 0
        assert doc.file == "README.md"

    def test_extract_refs_from_historical_file(self, old_sha):
        """Read a file at old ref, extract cross-refs from content."""
        files = list_files_at_ref(REPO_PATH, old_sha)
        # Find a file likely to have cross-refs
        for f in files:
            content = read_file_at_ref(REPO_PATH, old_sha, f)
            refs = extract_cross_references_from_content(content, f)
            if refs:
                assert refs[0].type in ("section", "appendix", "dsm")
                return
        # If no cross-refs found at all, that's okay for this small ref
        pytest.skip("No cross-references found at old ref")