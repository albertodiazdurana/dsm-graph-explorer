"""EXP-006: Git-Ref Temporal Accuracy Validation.

Pre-implementation gate for Sprint 10. Validates that subprocess-based
git commands (rev-parse, ls-tree, show) produce correct results at
historical refs, confirming the approach for git_resolver.py.

Test refs (this repo):
- Ref A (old): 87d869d — Sprint 1 complete, 12 markdown files
- Ref B (current): HEAD — 86+ markdown files

Run: python data/experiments/exp006_git_ref_temporal.py
"""

import subprocess
import sys
from pathlib import Path

REPO_PATH = Path(__file__).resolve().parents[2]
REF_OLD = "87d869d"
REF_OLD_EXPECTED_MD_COUNT = 12

results: list[tuple[str, bool, str]] = []


def record(name: str, passed: bool, detail: str = "") -> None:
    results.append((name, passed, detail))
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO_PATH), *args],
        capture_output=True,
        text=True,
        timeout=10,
    )


# ── Check 1: resolve_ref (git rev-parse) ────────────────────────────

print("\n1. Ref Resolution (git rev-parse)")

# 1a: HEAD resolves to a 40-char SHA
r = run_git("rev-parse", "HEAD")
head_sha = r.stdout.strip()
record(
    "HEAD resolves to SHA",
    r.returncode == 0 and len(head_sha) == 40,
    head_sha[:12],
)

# 1b: Short SHA resolves to full SHA
r = run_git("rev-parse", REF_OLD)
old_sha = r.stdout.strip()
record(
    "Short SHA resolves to full SHA",
    r.returncode == 0 and len(old_sha) == 40 and old_sha.startswith(REF_OLD),
    old_sha[:12],
)

# 1c: Invalid ref fails cleanly
r = run_git("rev-parse", "--verify", "nonexistent-ref-xyz")
record(
    "Invalid ref returns error",
    r.returncode != 0,
    f"returncode={r.returncode}",
)

# ── Check 2: list_files_at_ref (git ls-tree) ────────────────────────

print("\n2. File Listing (git ls-tree)")

# 2a: List md files at old ref
r = run_git("ls-tree", "-r", "--name-only", old_sha)
old_files = [f for f in r.stdout.strip().split("\n") if f.endswith(".md")]
record(
    f"Old ref has {REF_OLD_EXPECTED_MD_COUNT} md files",
    len(old_files) == REF_OLD_EXPECTED_MD_COUNT,
    f"found {len(old_files)}",
)

# 2b: List md files at HEAD
r = run_git("ls-tree", "-r", "--name-only", head_sha)
head_files = [f for f in r.stdout.strip().split("\n") if f.endswith(".md")]
record(
    "HEAD has more md files than old ref",
    len(head_files) > len(old_files),
    f"HEAD={len(head_files)}, old={len(old_files)}",
)

# 2c: README.md exists at both refs
record(
    "README.md present at old ref",
    "README.md" in old_files,
)
record(
    "README.md present at HEAD",
    "README.md" in head_files,
)

# ── Check 3: File presence/absence between refs ─────────────────────

print("\n3. File Presence/Absence")

old_set = set(old_files)
head_set = set(head_files)

added_files = head_set - old_set
removed_files = old_set - head_set
common_files = head_set & old_set

record(
    "Files added since old ref",
    len(added_files) > 0,
    f"{len(added_files)} added",
)
record(
    "Common files exist in both refs",
    len(common_files) > 0,
    f"{len(common_files)} common",
)

# Pick a file that exists only at HEAD (not at old ref)
if added_files:
    added_example = sorted(added_files)[0]
    record(
        f"Added file '{added_example}' not in old ref",
        added_example not in old_set,
    )

# ── Check 4: read_file_at_ref (git show) ────────────────────────────

print("\n4. File Content (git show)")

# 4a: Read README.md at old ref
r = run_git("show", f"{old_sha}:README.md")
record(
    "Read README.md at old ref",
    r.returncode == 0 and len(r.stdout) > 0,
    f"{len(r.stdout)} bytes",
)

# 4b: Read README.md at HEAD
r = run_git("show", f"{head_sha}:README.md")
head_readme = r.stdout
record(
    "Read README.md at HEAD",
    r.returncode == 0 and len(head_readme) > 0,
    f"{len(head_readme)} bytes",
)

# 4c: Content differs between refs (README evolved)
r_old = run_git("show", f"{old_sha}:README.md")
record(
    "README.md content differs between refs",
    r_old.stdout != head_readme,
    f"old={len(r_old.stdout)}B, head={len(head_readme)}B",
)

# 4d: Reading nonexistent file fails cleanly
r = run_git("show", f"{old_sha}:nonexistent/file.md")
record(
    "Nonexistent file returns error",
    r.returncode != 0,
)

# 4e: Reading a file that only exists at HEAD from old ref fails
if added_files:
    added_example = sorted(added_files)[0]
    r = run_git("show", f"{old_sha}:{added_example}")
    record(
        f"File '{added_example}' not readable at old ref",
        r.returncode != 0,
    )

# ── Check 5: Determinism ────────────────────────────────────────────

print("\n5. Determinism")

# Run ls-tree twice, same result
r1 = run_git("ls-tree", "-r", "--name-only", old_sha)
r2 = run_git("ls-tree", "-r", "--name-only", old_sha)
record(
    "ls-tree is deterministic",
    r1.stdout == r2.stdout,
)

# Read file twice, same content
r1 = run_git("show", f"{old_sha}:README.md")
r2 = run_git("show", f"{old_sha}:README.md")
record(
    "git show is deterministic",
    r1.stdout == r2.stdout,
)

# ── Check 6: Performance ────────────────────────────────────────────

print("\n6. Performance")

import time

# Time listing all files at HEAD
t0 = time.perf_counter()
for _ in range(10):
    run_git("ls-tree", "-r", "--name-only", head_sha)
elapsed_ls = (time.perf_counter() - t0) / 10

record(
    "ls-tree avg < 100ms",
    elapsed_ls < 0.1,
    f"{elapsed_ls*1000:.1f}ms",
)

# Time reading a single file
t0 = time.perf_counter()
for _ in range(10):
    run_git("show", f"{head_sha}:README.md")
elapsed_show = (time.perf_counter() - t0) / 10

record(
    "git show avg < 100ms",
    elapsed_show < 0.1,
    f"{elapsed_show*1000:.1f}ms",
)

# ── Summary ──────────────────────────────────────────────────────────

print("\n" + "=" * 60)
passed = sum(1 for _, p, _ in results if p)
failed = sum(1 for _, p, _ in results if not p)
total = len(results)
print(f"EXP-006 Results: {passed}/{total} passed, {failed} failed")

if failed:
    print("\nFailed checks:")
    for name, p, detail in results:
        if not p:
            print(f"  FAIL: {name}" + (f" — {detail}" if detail else ""))

sys.exit(0 if failed == 0 else 1)