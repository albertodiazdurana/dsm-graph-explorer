"""EXP-008: Heading Reference Detection Quality.

Validates that --heading-refs produces useful, low-noise signal when run
against real DSM documents. Measures detection count, true/false positive rate
proxies, cross-file resolution, and performance.

Follows DSM Appendix C.1.3 seven-element framework:
1. Hypothesis
2. Baseline
3. Method
4. Variables
5. Success Criteria
6. Results
7. Decision

Run: python data/experiments/EXP-008-heading-ref-quality/exp008_heading_ref_quality.py

Requires: DSM Central repository at ~/dsm-agentic-ai-data-science-methodology/
"""

import sys
import time
from collections import Counter
from pathlib import Path

# ── Setup ─────────────────────────────────────────────────────────────

REPO_PATH = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_PATH / "src"))

from click.testing import CliRunner
from parser.cross_ref_extractor import extract_heading_references
from parser.markdown_parser import parse_markdown_file

DSM_PATH = Path.home() / "dsm-agentic-ai-data-science-methodology"
if not DSM_PATH.exists():
    print(f"ERROR: DSM repository not found at {DSM_PATH}")
    sys.exit(1)

results: list[tuple[str, bool, str]] = []


def record(name: str, passed: bool, detail: str = "") -> None:
    results.append((name, passed, detail))
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))


# ── 1. Hypothesis ─────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("EXP-008: Heading Reference Detection Quality")
print("=" * 70)
print("""
Hypothesis: Heading reference detection will find meaningful cross-references
in DSM documents where section numbering is absent. False positive rate will be
acceptable for specific, multi-word headings but problematic for generic
single-word headings.
""")

# ── 2. Baseline ───────────────────────────────────────────────────────

print("2. Baseline (without --heading-refs)")
print("-" * 40)

from cli import main

runner = CliRunner()
start = time.perf_counter()
baseline_result = runner.invoke(main, [str(DSM_PATH)])
baseline_time = time.perf_counter() - start

# Extract summary from baseline output
baseline_summary = ""
for line in baseline_result.output.split("\n"):
    if "Scanned" in line:
        baseline_summary = line.strip()
        break

print(f"  {baseline_summary}")
print(f"  Time: {baseline_time:.2f}s")
print(f"  Exit code: {baseline_result.exit_code}")
record("Baseline runs without error", baseline_result.exit_code == 0)

# ── 3. Method ─────────────────────────────────────────────────────────

print("\n3. Method")
print("-" * 40)
print("  a) Parse all markdown files in DSM repository")
print("  b) Collect all unnumbered heading titles as known_headings")
print("  c) Run extract_heading_references per file (unfiltered)")
print("  d) Repeat with 3+ word minimum filter")
print("  e) Analyze detection counts, noise distribution, sample quality")
print("  f) Run CLI with --heading-refs and compare to baseline")

# ── 4. Variables ──────────────────────────────────────────────────────

print("\n4. Variables")
print("-" * 40)
print("  Independent: heading word-count filter (none, 3+)")
print("  Dependent: ref count, FP rate proxy, extraction time")
print("  Controlled: DSM repo version, Python version, tool version")

# ── Parse all documents ───────────────────────────────────────────────

print("\n5. Execution")
print("-" * 40)

md_files = sorted(DSM_PATH.glob("**/*.md"))
print(f"  Files found: {len(md_files)}")

documents = []
for f in md_files:
    try:
        doc = parse_markdown_file(f)
        documents.append(doc)
    except Exception:
        pass

print(f"  Files parsed: {len(documents)}")

# ── 5a. Unfiltered heading extraction ─────────────────────────────────

print("\n  5a. Unfiltered heading extraction")

all_headings = set()
heading_word_dist = Counter()
for doc in documents:
    for section in doc.sections:
        if section.number is None:
            normalized = " ".join(section.title.lower().split())
            all_headings.add(normalized)
            heading_word_dist[len(normalized.split())] += 1

print(f"  Unique known headings: {len(all_headings)}")
print("  Word-count distribution:")
for wc in sorted(heading_word_dist.keys()):
    print(f"    {wc} word(s): {heading_word_dist[wc]}")

start = time.perf_counter()
unfiltered_total = 0
unfiltered_by_file = {}
unfiltered_heading_counts = Counter()
for doc in documents:
    refs = extract_heading_references(doc.file, known_headings=all_headings)
    if refs:
        unfiltered_by_file[doc.file] = refs
        unfiltered_total += len(refs)
        for ref in refs:
            unfiltered_heading_counts[ref.target.lower()] += 1
unfiltered_time = time.perf_counter() - start

print(f"\n  Total refs (unfiltered): {unfiltered_total}")
print(f"  Files with refs: {len(unfiltered_by_file)}")
print(f"  Time: {unfiltered_time:.2f}s")
print("  Top 10 noisiest headings:")
for heading, count in unfiltered_heading_counts.most_common(10):
    print(f"    {count:6d}  \"{heading}\"")

record(
    "Unfiltered detection finds refs",
    unfiltered_total > 0,
    f"{unfiltered_total} refs",
)

# ── 5b. 3+ word filtered extraction ──────────────────────────────────

print("\n  5b. Filtered heading extraction (3+ words)")

headings_3plus = {h for h in all_headings if len(h.split()) >= 3}
print(f"  Known headings (3+ words): {len(headings_3plus)}")

start = time.perf_counter()
filtered_total = 0
filtered_by_file = {}
filtered_heading_counts = Counter()
for doc in documents:
    refs = extract_heading_references(doc.file, known_headings=headings_3plus)
    if refs:
        filtered_by_file[doc.file] = refs
        filtered_total += len(refs)
        for ref in refs:
            filtered_heading_counts[ref.target.lower()] += 1
filtered_time = time.perf_counter() - start

print(f"  Total refs (3+ words): {filtered_total}")
print(f"  Files with refs: {len(filtered_by_file)}")
print(f"  Time: {filtered_time:.2f}s")
print(f"  Noise reduction: {unfiltered_total} -> {filtered_total} ({100 * (1 - filtered_total / max(unfiltered_total, 1)):.1f}% reduction)")
print("  Top 10 most referenced headings:")
for heading, count in filtered_heading_counts.most_common(10):
    print(f"    {count:4d}  \"{heading}\"")

record(
    "3+ word filter reduces noise",
    filtered_total < unfiltered_total * 0.1,
    f"{unfiltered_total} -> {filtered_total}",
)

# ── 5c. CLI with --heading-refs ───────────────────────────────────────

print("\n  5c. CLI with --heading-refs")

start = time.perf_counter()
heading_result = runner.invoke(main, [str(DSM_PATH), "--heading-refs"])
heading_time = time.perf_counter() - start

heading_summary = ""
for line in heading_result.output.split("\n"):
    if "Scanned" in line:
        heading_summary = line.strip()
        break

print(f"  {heading_summary}")
print(f"  Time: {heading_time:.2f}s")
print(f"  Exit code: {heading_result.exit_code}")

record(
    "CLI --heading-refs runs without error",
    heading_result.exit_code == 0,
)

# ── 5d. No regression check ──────────────────────────────────────────

print("\n  5d. Regression check")

# Extract error/warning counts from both summaries
import re


def extract_counts(summary: str) -> tuple[int, int]:
    errors = re.search(r"(\d+) error\(s\)", summary)
    warnings = re.search(r"(\d+) warning\(s\)", summary)
    return (
        int(errors.group(1)) if errors else -1,
        int(warnings.group(1)) if warnings else -1,
    )


base_errors, base_warnings = extract_counts(baseline_summary)
head_errors, head_warnings = extract_counts(heading_summary)

print(f"  Baseline: {base_errors} errors, {base_warnings} warnings")
print(f"  Heading-refs: {head_errors} errors, {head_warnings} warnings")

record(
    "No error regression",
    base_errors == head_errors,
    f"baseline={base_errors}, heading-refs={head_errors}",
)
record(
    "No warning regression (warnings may increase from broken heading refs)",
    head_warnings >= base_warnings,
    f"baseline={base_warnings}, heading-refs={head_warnings}",
)

# ── 5e. Cross-file resolution ────────────────────────────────────────

print("\n  5e. Cross-file resolution")

# Count how many heading refs point to headings defined in a different file
heading_to_files: dict[str, set[str]] = {}
for doc in documents:
    for section in doc.sections:
        if section.number is None:
            normalized = " ".join(section.title.lower().split())
            if len(normalized.split()) >= 3:
                heading_to_files.setdefault(normalized, set()).add(str(doc.file))

cross_file_count = 0
same_file_count = 0
for fpath, refs in filtered_by_file.items():
    for ref in refs:
        target_norm = " ".join(ref.target.lower().split())
        defining_files = heading_to_files.get(target_norm, set())
        if str(fpath) not in defining_files and defining_files:
            cross_file_count += 1
        else:
            same_file_count += 1

total_resolved = cross_file_count + same_file_count
cross_file_pct = (
    100 * cross_file_count / total_resolved if total_resolved > 0 else 0
)
print(f"  Cross-file refs: {cross_file_count}")
print(f"  Same-file refs: {same_file_count}")
print(f"  Cross-file percentage: {cross_file_pct:.1f}%")

record(
    "Cross-file resolution present",
    cross_file_count > 0,
    f"{cross_file_count} cross-file refs ({cross_file_pct:.1f}%)",
)

# ── 6. Success Criteria Assessment ────────────────────────────────────

print("\n\n6. Success Criteria")
print("=" * 70)
print("""
| Criterion                              | Threshold    | Result          |
|----------------------------------------|--------------|-----------------|""")

criteria = [
    ("Detection: heading refs found", ">0", f"{filtered_total}", filtered_total > 0),
    ("Noise reduction: 3+ filter effective", ">90% reduction", f"{100 * (1 - filtered_total / max(unfiltered_total, 1)):.1f}%", filtered_total < unfiltered_total * 0.1),
    ("Cross-file resolution present", ">0 cross-file", f"{cross_file_count}", cross_file_count > 0),
    ("No error regression", "exact match", f"{base_errors}=={head_errors}", base_errors == head_errors),
    ("Performance: CLI completes", "<120s", f"{heading_time:.1f}s", heading_time < 120),
]

for name, threshold, result_val, passed in criteria:
    status = "PASS" if passed else "FAIL"
    print(f"| {name:<38} | {threshold:<12} | {result_val:<7} {status:<6} |")

# Note: true/false positive rate requires manual sample assessment
# (done in results.md, not automatable)
print("""
Note: True/false positive rate assessed via manual sample (n=30) in results.md.
Automated proxy: noise reduction ratio and top heading quality.
""")

# ── 7. Decision ───────────────────────────────────────────────────────

print("7. Decision")
print("=" * 70)

all_auto_pass = all(p for _, p, _ in results)
if all_auto_pass:
    print("  All automated checks PASS.")
else:
    print("  Some automated checks FAILED:")
    for name, passed, detail in results:
        if not passed:
            print(f"    FAIL: {name} ({detail})")

print("""
  Manual assessment (from n=30 random sample):
  - True positive rate: ~73% (below 80% threshold)
  - False positive rate: ~27% (above 20% threshold)
  - Main FP sources: generic 3-word phrases, template phrases, incidental matches

  VERDICT: FAIL (FP rate exceeds threshold)

  Decision gate: Pre-filter required before promoting --heading-refs.
  Recommended: min_heading_words=3 + min_heading_length=20 characters.
""")

# ── Summary ───────────────────────────────────────────────────────────

print("Summary")
print("-" * 40)
total = len(results)
passed = sum(1 for _, p, _ in results if p)
failed = total - passed
print(f"  {passed}/{total} automated checks passed, {failed} failed")
print(f"  Manual quality assessment: ~73% TP, ~27% FP (n=30)")
print(f"  Overall verdict: FAIL (pre-filter needed)")

sys.exit(0 if all_auto_pass else 1)