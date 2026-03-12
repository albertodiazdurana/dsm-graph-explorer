"""Git resolver: historical file access via subprocess.

Provides functions to resolve git refs, list files at a given commit,
and read file contents at a given commit. Uses subprocess calls to git
rather than gitpython, keeping the dependency footprint minimal.
"""

import fnmatch
import subprocess
from pathlib import Path


class GitRefError(Exception):
    """Raised when a git ref cannot be resolved or a git command fails."""


def _run_git(repo_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command in the given repository.

    Args:
        repo_path: Path to the git repository.
        *args: Git subcommand and arguments.

    Returns:
        CompletedProcess with stdout/stderr captured as text.

    Raises:
        GitRefError: If the git command fails.
    """
    result = subprocess.run(
        ["git", "-C", str(repo_path), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result


def find_repo_root(path: Path | str) -> Path:
    """Find the git repository root for a given path.

    Args:
        path: Any path within a git repository.

    Returns:
        Path to the repository root.

    Raises:
        GitRefError: If the path is not within a git repository.
    """
    path = Path(path)
    result = _run_git(path, "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        raise GitRefError(f"Not a git repository: {path}")
    return Path(result.stdout.strip())


def resolve_ref(repo_path: Path | str, ref: str) -> str:
    """Resolve a git ref (SHA, tag, branch) to a full commit SHA.

    Args:
        repo_path: Path to the git repository.
        ref: Git ref string (commit SHA, tag name, branch name, HEAD, etc.).

    Returns:
        Full 40-character commit SHA.

    Raises:
        GitRefError: If the ref cannot be resolved.
    """
    repo_path = Path(repo_path)
    result = _run_git(repo_path, "rev-parse", "--verify", ref)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise GitRefError(f"Cannot resolve ref '{ref}': {stderr}")
    return result.stdout.strip()


def list_files_at_ref(
    repo_path: Path | str, sha: str, pattern: str = "*.md"
) -> list[str]:
    """List files at a given commit, filtered by glob pattern.

    Args:
        repo_path: Path to the git repository.
        sha: Full commit SHA (from resolve_ref).
        pattern: Glob pattern for filtering file paths (default: "*.md").

    Returns:
        Sorted list of file paths matching the pattern.

    Raises:
        GitRefError: If the git command fails.
    """
    repo_path = Path(repo_path)
    result = _run_git(repo_path, "ls-tree", "-r", "--name-only", sha)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise GitRefError(f"Cannot list files at {sha[:12]}: {stderr}")

    all_files = result.stdout.strip().split("\n")
    if all_files == [""]:
        return []

    matched = [f for f in all_files if fnmatch.fnmatch(f, pattern)]
    return sorted(matched)


def read_file_at_ref(repo_path: Path | str, sha: str, filepath: str) -> str:
    """Read a file's contents at a given commit.

    Args:
        repo_path: Path to the git repository.
        sha: Full commit SHA (from resolve_ref).
        filepath: Path to the file within the repository.

    Returns:
        File contents as a string.

    Raises:
        GitRefError: If the file does not exist at the given ref.
    """
    repo_path = Path(repo_path)
    result = _run_git(repo_path, "show", f"{sha}:{filepath}")
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise GitRefError(
            f"Cannot read '{filepath}' at {sha[:12]}: {stderr}"
        )
    return result.stdout