"""EXP-003b: Real Data Validation of Semantic Drift Detection.

Purpose: Validate DEC-005 threshold (0.10) against the real DSM methodology
repository (~346 cross-references, ~937 sections). EXP-003 used 25 synthetic
cases; this experiment uses the actual corpus to measure real-world precision
and recall.

Two-phase workflow:
  Phase A (generate): Parse DSM repo, run semantic alignment, output CSV.
  Phase B (score):    Read back labeled CSV, compute precision/recall/F1.

Usage:
  # Phase A: generate results for manual labeling
  python experiments/exp003b_real_data_validation.py ~/dsm-agentic-ai-data-science-methodology/

  # Phase B: score labeled CSV
  python experiments/exp003b_real_data_validation.py --score experiments/exp003b_results.csv
"""

import csv
import sys
from pathlib import Path

# Add src to path so we can import project modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from parser.cross_ref_extractor import extract_cross_references
from parser.markdown_parser import parse_markdown_file
from semantic.similarity import (
    SKLEARN_AVAILABLE,
    build_corpus_vectorizer,
    check_semantic_alignment,
)
from validator.cross_ref_validator import build_section_lookup


def collect_md_files(repo_path: Path) -> list[Path]:
    """Collect all markdown files from the repository."""
    return sorted(repo_path.glob("**/*.md"))


def truncate(text: str, max_len: int = 80) -> str:
    """Truncate text for display, replacing newlines with spaces."""
    clean = " ".join(text.split())
    if len(clean) > max_len:
        return clean[: max_len - 3] + "..."
    return clean


def phase_a(repo_path: Path, output_csv: Path) -> None:
    """Phase A: Parse repo, run semantic alignment, output CSV for labeling."""
    if not SKLEARN_AVAILABLE:
        print("Error: scikit-learn required. Install with: pip install scikit-learn")
        sys.exit(1)

    print(f"Scanning: {repo_path}")
    md_files = collect_md_files(repo_path)
    print(f"Found {len(md_files)} markdown files")

    # Parse all documents
    documents = []
    references = {}
    for f in md_files:
        doc = parse_markdown_file(f)
        documents.append(doc)
        refs = extract_cross_references(f)
        if refs:
            references[doc.file] = refs

    all_sections = [s for doc in documents for s in doc.sections]
    print(f"Parsed {len(all_sections)} sections, {sum(len(r) for r in references.values())} cross-references")

    # Build vectorizer and lookup
    vectorizer = build_corpus_vectorizer(all_sections)
    section_lookup = build_section_lookup(documents)
    print(f"Section lookup has {len(section_lookup)} entries")

    # Run semantic alignment on every resolved section/appendix ref
    rows = []
    resolved = 0
    unresolved = 0

    for file_path, refs in references.items():
        for ref in refs:
            if ref.type not in ("section", "appendix"):
                continue

            target_section = section_lookup.get(ref.target)
            if target_section is None:
                unresolved += 1
                continue

            resolved += 1
            result = check_semantic_alignment(ref, target_section, vectorizer)

            # Classify the result
            if not result.sufficient_context:
                category = "insufficient"
            elif result.match:
                category = "match"
            else:
                category = "drift"

            rows.append({
                "file": Path(file_path).name,
                "line": ref.line,
                "ref_type": ref.type,
                "target": ref.target,
                "ref_context": truncate(ref.context),
                "target_title": target_section.title,
                "target_excerpt": truncate(target_section.context_excerpt),
                "score": f"{result.score:.4f}",
                "ref_tokens": result.ref_tokens,
                "target_tokens": result.target_tokens,
                "sufficient": result.sufficient_context,
                "auto_category": category,
                "manual_label": "",  # To be filled by human reviewer
            })

    print(f"\nResolved: {resolved}, Unresolved: {unresolved}")
    print(f"Results: {sum(1 for r in rows if r['auto_category'] == 'match')} match, "
          f"{sum(1 for r in rows if r['auto_category'] == 'drift')} drift, "
          f"{sum(1 for r in rows if r['auto_category'] == 'insufficient')} insufficient")

    # Write CSV
    fieldnames = list(rows[0].keys()) if rows else []
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV written to: {output_csv}")
    print(f"Total rows: {len(rows)}")
    print("\nNext step: Open the CSV, fill the 'manual_label' column with")
    print("  'match'  = reference context genuinely relates to target section")
    print("  'drift'  = reference context does NOT relate to target section")
    print("  'skip'   = ambiguous or not classifiable")
    print("Then run: python experiments/exp003b_real_data_validation.py --score <csv>")


def phase_b(csv_path: Path) -> None:
    """Phase B: Read labeled CSV, compute precision/recall/F1."""
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Filter to labeled rows (exclude 'skip' and empty)
    labeled = [r for r in rows if r.get("manual_label") in ("match", "drift")]
    unlabeled = [r for r in rows if r.get("manual_label") not in ("match", "drift", "skip")]
    skipped = [r for r in rows if r.get("manual_label") == "skip"]
    insufficient = [r for r in rows if r.get("auto_category") == "insufficient"]

    print(f"Total rows: {len(rows)}")
    print(f"Labeled: {len(labeled)}, Skipped: {skipped}, Insufficient: {len(insufficient)}, Unlabeled: {len(unlabeled)}")

    if not labeled:
        print("\nNo labeled rows found. Fill the 'manual_label' column first.")
        return

    # Compute metrics: auto_category vs manual_label
    # "match" at threshold is a positive prediction, "drift" is negative
    tp = fp = tn = fn = 0
    disagreements = []

    for r in labeled:
        auto = r["auto_category"]
        manual = r["manual_label"]

        if auto == "match" and manual == "match":
            tp += 1
        elif auto == "match" and manual == "drift":
            fp += 1
            disagreements.append(r)
        elif auto == "drift" and manual == "drift":
            tn += 1
        elif auto == "drift" and manual == "match":
            fn += 1
            disagreements.append(r)

    total = tp + fp + tn + fn
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / total if total > 0 else 0.0

    print(f"\n{'=' * 60}")
    print(f"  EXP-003b Results (threshold = 0.10)")
    print(f"{'=' * 60}")
    print(f"  True Positives (auto=match, manual=match):   {tp}")
    print(f"  False Positives (auto=match, manual=drift):  {fp}")
    print(f"  True Negatives (auto=drift, manual=drift):   {tn}")
    print(f"  False Negatives (auto=drift, manual=match):  {fn}")
    print(f"  {'─' * 50}")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall:    {recall:.3f}")
    print(f"  F1:        {f1:.3f}")
    print(f"  Accuracy:  {accuracy:.3f}")

    if disagreements:
        print(f"\n  Disagreements ({len(disagreements)}):")
        for r in disagreements:
            print(f"    {r['file']}:{r['line']} -> {r['target']} "
                  f"(auto={r['auto_category']}, manual={r['manual_label']}, "
                  f"score={r['score']})")

    # Compare with EXP-003 synthetic results
    print(f"\n{'=' * 60}")
    print(f"  Comparison with EXP-003 (synthetic)")
    print(f"{'=' * 60}")
    print(f"  EXP-003:  F1=0.889, Precision=1.000, Recall=0.800 (25 cases)")
    print(f"  EXP-003b: F1={f1:.3f}, Precision={precision:.3f}, Recall={recall:.3f} ({len(labeled)} cases)")
    print(f"\n  Corpus size: EXP-003=25 synthetic, EXP-003b={len(rows)} real")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--score":
        if len(sys.argv) < 3:
            print("Usage: python exp003b_real_data_validation.py --score <csv>")
            sys.exit(1)
        phase_b(Path(sys.argv[2]))
    else:
        repo_path = Path(sys.argv[1])
        if not repo_path.is_dir():
            print(f"Error: {repo_path} is not a directory")
            sys.exit(1)
        output_csv = Path("experiments/exp003b_results.csv")
        phase_a(repo_path, output_csv)


if __name__ == "__main__":
    main()
