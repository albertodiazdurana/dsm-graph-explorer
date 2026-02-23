"""EXP-003: TF-IDF Threshold Tuning for Semantic Drift Detection.

Purpose: Find optimal cosine similarity threshold for detecting semantic drift
in DSM cross-references. Compares title-only vs title+excerpt approaches.

Usage: python data/experiments/exp003_tfidf_threshold.py
"""

import re
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------------------------
# Test case definitions (from real DSM content)
# ---------------------------------------------------------------------------

@dataclass
class TestCase:
    """A reference-target pair for testing similarity."""
    label: str
    ref_context: str       # 1-line or 3-line reference context
    target_title: str      # Section title
    target_excerpt: str    # First ~50 words of prose after heading
    expected_match: bool   # True = should match, False = drift/unrelated


# 10 TRUE MATCH cases: reference context aligns with target section
TRUE_MATCHES = [
    TestCase(
        label="blog process (full name in ref)",
        ref_context="Section 2.5.6 (Blog/Communication Deliverable Process) specifies the overall blog process but does not include a standard metadata format.",
        target_title="Blog/Communication Deliverable Process",
        target_excerpt="When a project includes a public communication deliverable (blog post, article, presentation), follow this structured process. Create one materials file per blog post.",
        expected_match=True,
    ),
    TestCase(
        label="environment setup (see-reference)",
        ref_context="Base packages installed, see Methodology Section 2.1 (Phase 0: Environment Setup) for details. Jupyter kernel registered and functional.",
        target_title="Phase 0: Environment Setup",
        target_excerpt="Establish a reproducible Python environment with base packages and VS Code configuration before beginning analysis work. This ensures consistency across all projects.",
        expected_match=True,
    ),
    TestCase(
        label="data-driven decisions (parenthetical)",
        ref_context="Document decisions: Every significant choice needs rationale and evidence (See Section 4.1). Honest limitations: Better to remove uncertain features.",
        target_title="Data-Driven Decision Making",
        target_excerpt="Validate assumptions: Never trust predetermined business expectations without verification. Pivot when necessary: Statistical validity overrides initial hypotheses. Document decisions.",
        expected_match=True,
    ),
    TestCase(
        label="communication style (short ref)",
        ref_context="Follow the communication guidelines in Section 1.3.1 for all agent interactions.",
        target_title="Communication Style",
        target_excerpt="Concise responses: Direct answers without unnecessary elaboration. Clarifying questions first: Before generating artifacts or lengthy outputs, confirm understanding.",
        expected_match=True,
    ),
    TestCase(
        label="EDA objectives (context overlap)",
        ref_context="During exploratory analysis, follow the objectives outlined in Section 2.2.1 to ensure thorough data understanding.",
        target_title="Objectives",
        target_excerpt="Primary Goals: Understand data quality, completeness, and structure. Define analytical cohort based on business requirements. Identify data limitations and potential issues.",
        expected_match=True,
    ),
    TestCase(
        label="deliverables (generic title, context helps)",
        ref_context="The EDA phase must produce the deliverables specified in Section 2.2.3, including notebooks and cohort definitions.",
        target_title="Deliverables",
        target_excerpt="Required Outputs: EDA Notebooks, typically 1-2 notebooks with data quality assessment, cohort definition, key visualizations and statistics. Cohort Definition Document.",
        expected_match=True,
    ),
    TestCase(
        label="NLP packages (appendix ref)",
        ref_context="For text analysis projects, install the NLP packages listed in Appendix A.3.2 before starting feature engineering.",
        target_title="NLP Packages",
        target_excerpt="nltk, Purpose: Natural Language Toolkit. Use Cases: Tokenization, stemming, POS tagging. spacy, Purpose: Industrial-strength NLP. Use Cases: Named entity recognition.",
        expected_match=True,
    ),
    TestCase(
        label="base environment (setup ref)",
        ref_context="Start with the minimal base environment from Section A.1 to keep the installation lightweight.",
        target_title="Base Environment (Minimal)",
        target_excerpt="Core Data Science Stack: jupyter, Purpose: Notebook interface for interactive analysis. Why Essential: Primary development environment for data science.",
        expected_match=True,
    ),
    TestCase(
        label="notebook structure (stage-based)",
        ref_context="Use stage-based naming with sequential numbers and descriptive names (See Section 3.3 for details). Section structure per notebook.",
        target_title="Notebook Organization & Naming",
        target_excerpt="Consistent naming conventions ensure notebooks are easily navigable. Use sequential numbering with descriptive suffixes that indicate the analysis stage.",
        expected_match=True,
    ),
    TestCase(
        label="pivot example (evidence-based)",
        ref_context="Be ready to pivot based on analysis (Section 4.2). Example: TravelTide pivoted from K=5 to K=3 based on statistical evidence.",
        target_title="Statistical Validation & Pivots",
        target_excerpt="When analysis results contradict initial hypotheses, pivot rather than force-fit. Document the evidence that triggered the pivot and the statistical tests used.",
        expected_match=True,
    ),
]

# 10 DRIFT/UNRELATED cases: reference context does NOT align with target
DRIFT_CASES = [
    TestCase(
        label="drift: blog ref -> data leakage target",
        ref_context="Section 2.5.6 specifies the overall blog process and metadata format for posts.",
        target_title="Data Leakage Prevention",
        target_excerpt="Validate assumptions about temporal data. Never use future information to predict past events. Implement strict train-test separation.",
        expected_match=False,
    ),
    TestCase(
        label="drift: environment ref -> stakeholder target",
        ref_context="Set up the Python environment according to Section 2.1 with base packages and Jupyter.",
        target_title="Stakeholder Communication",
        target_excerpt="Present findings to both technical and non-technical audiences. Use clear visualizations and avoid jargon in executive summaries.",
        expected_match=False,
    ),
    TestCase(
        label="drift: NLP ref -> visualization target",
        ref_context="Install NLP packages from Appendix A.3.2 for tokenization and named entity recognition.",
        target_title="Visualization Best Practices",
        target_excerpt="Choose chart types appropriate to the data. Use consistent color palettes across notebooks. Label axes clearly and include titles.",
        expected_match=False,
    ),
    TestCase(
        label="drift: deliverables ref -> gateway review target",
        ref_context="Produce the EDA deliverables including notebooks and cohort definitions per Section 2.2.3.",
        target_title="Gateway Review Process",
        target_excerpt="At each project gateway, conduct a structured review with the project lead. Assess completion of sprint objectives and alignment with methodology.",
        expected_match=False,
    ),
    TestCase(
        label="drift: communication ref -> experiment tracking",
        ref_context="Follow the communication guidelines in Section 1.3.1 for concise responses and clarifying questions.",
        target_title="Experiment Tracking",
        target_excerpt="Log all experiment parameters, metrics, and outcomes. Use structured templates for reproducibility. Compare results across runs systematically.",
        expected_match=False,
    ),
    TestCase(
        label="drift: decision ref -> package management",
        ref_context="Document decisions with rationale and evidence as described in Section 4.1 for data-driven choices.",
        target_title="Package Management",
        target_excerpt="Use pip for package installation. Pin versions in requirements.txt for reproducibility. Separate development and production dependencies.",
        expected_match=False,
    ),
    TestCase(
        label="drift: objectives ref -> blog writing",
        ref_context="During exploratory analysis, follow the objectives in Section 2.2.1 for data quality assessment.",
        target_title="Blog Writing Process",
        target_excerpt="Create a materials file with working title options, hook paragraph, story arc, and key insights. Draft iteratively with peer review.",
        expected_match=False,
    ),
    TestCase(
        label="drift: notebook ref -> CI integration",
        ref_context="Organize notebooks using stage-based naming per Section 3.3 with sequential numbers.",
        target_title="CI/CD Integration",
        target_excerpt="Configure GitHub Actions workflow to run validation on pull requests. Set up pre-commit hooks for automated checking before each commit.",
        expected_match=False,
    ),
    TestCase(
        label="drift: pivot ref -> file naming",
        ref_context="Be ready to pivot based on statistical evidence (Section 4.2). Document the reasoning.",
        target_title="File Naming Conventions",
        target_excerpt="Use YYYY-MM-DD prefix for date-stamped files. Separate words with hyphens. Use lowercase consistently across the project.",
        expected_match=False,
    ),
    TestCase(
        label="drift: base env ref -> cross-ref validation",
        ref_context="Start with the minimal base environment from Section A.1 for a lightweight installation.",
        target_title="Cross-Reference Validation",
        target_excerpt="Parse markdown files to extract section headings. Build a section index. Extract cross-references and validate each resolves to an actual heading.",
        expected_match=False,
    ),
]


# 5 AMBIGUOUS cases: generic titles where excerpt is critical for disambiguation
AMBIGUOUS_MATCHES = [
    TestCase(
        label="ambig: 'Expected Outcomes' (correct instance)",
        ref_context="After completing the exploratory analysis, verify the expected outcomes from Section 3.4 including cohort metrics.",
        target_title="Expected Outcomes",
        target_excerpt="Cohort metrics validated against business thresholds. Data quality assessment complete with documented limitations. Feature candidates identified for modeling phase.",
        expected_match=True,
    ),
    TestCase(
        label="ambig: 'Expected Outcomes' (wrong instance)",
        ref_context="After completing the exploratory analysis, verify the expected outcomes from Section 3.4 including cohort metrics.",
        target_title="Expected Outcomes",
        target_excerpt="Sprint velocity stabilized within 20% of planned capacity. Stakeholder feedback incorporated into next iteration. Release candidate approved by product owner.",
        expected_match=False,
    ),
    TestCase(
        label="ambig: 'Deliverables' (correct instance)",
        ref_context="Submit the EDA deliverables from Section 2.2.3 including notebooks with visualizations and the cohort definition document.",
        target_title="Deliverables",
        target_excerpt="Required Outputs: EDA Notebooks, typically 1-2 notebooks with data quality assessment, cohort definition, key visualizations and statistics. Cohort Definition Document.",
        expected_match=True,
    ),
    TestCase(
        label="ambig: 'Deliverables' (wrong instance)",
        ref_context="Submit the EDA deliverables from Section 2.2.3 including notebooks with visualizations and the cohort definition document.",
        target_title="Deliverables",
        target_excerpt="Sprint deliverables: Updated CI/CD pipeline configuration. Pre-commit hook installation guide. Remediation documentation for broken cross-references.",
        expected_match=False,
    ),
    TestCase(
        label="ambig: 'Quality Standards' (wrong instance)",
        ref_context="Code must meet the quality standards in Section 3.2 for documentation coverage and test requirements.",
        target_title="Quality Standards",
        target_excerpt="Data quality dimensions: completeness, accuracy, consistency, timeliness. Measure each dimension with quantitative metrics. Flag records below threshold.",
        expected_match=False,
    ),
]


# ---------------------------------------------------------------------------
# Preprocessing and similarity computation
# ---------------------------------------------------------------------------

def strip_section_numbers(text: str) -> str:
    """Remove section number patterns (e.g., '2.5.6', 'A.3.2') from text."""
    return re.sub(r'\b[A-Z]?\d+(?:\.\d+)+\.?\b', '', text)


def compute_similarities(
    test_cases: list[TestCase],
    use_excerpt: bool,
) -> list[float]:
    """Compute TF-IDF cosine similarity for each test case.

    When use_excerpt=True, uses title+excerpt for target and full ref context.
    When use_excerpt=False, uses title-only for target and ref context line.
    """
    ref_texts = []
    target_texts = []

    for tc in test_cases:
        ref_text = strip_section_numbers(tc.ref_context)

        if use_excerpt:
            target_text = strip_section_numbers(
                f"{tc.target_title} {tc.target_excerpt}"
            )
        else:
            target_text = strip_section_numbers(tc.target_title)

        ref_texts.append(ref_text)
        target_texts.append(target_text)

    # Build corpus-scoped vectorizer from ALL texts (both sides)
    all_texts = ref_texts + target_texts
    vectorizer = TfidfVectorizer(stop_words="english", min_df=1)
    vectorizer.fit(all_texts)

    scores = []
    for ref_text, target_text in zip(ref_texts, target_texts):
        ref_vec = vectorizer.transform([ref_text])
        target_vec = vectorizer.transform([target_text])
        sim = cosine_similarity(ref_vec, target_vec)[0][0]
        scores.append(sim)

    return scores


def evaluate_threshold(
    scores: list[float],
    labels: list[bool],
    threshold: float,
) -> dict:
    """Compute precision, recall, F1 at a given threshold."""
    tp = fp = tn = fn = 0
    for score, expected_match in zip(scores, labels):
        predicted_match = score >= threshold
        if predicted_match and expected_match:
            tp += 1
        elif predicted_match and not expected_match:
            fp += 1
        elif not predicted_match and not expected_match:
            tn += 1
        else:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "threshold": threshold,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 70)
    print("  PART 1: Standard Cases (10 match + 10 drift)")
    print("=" * 70)

    all_cases = TRUE_MATCHES + DRIFT_CASES
    labels = [tc.expected_match for tc in all_cases]
    thresholds = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5]

    for mode_label, use_excerpt in [("TITLE-ONLY", False), ("TITLE + EXCERPT", True)]:
        scores = compute_similarities(all_cases, use_excerpt=use_excerpt)

        print(f"\n{'=' * 70}")
        print(f"  Mode: {mode_label}")
        print(f"{'=' * 70}")

        # Per-case scores
        print(f"\n{'Label':<50} {'Score':>6} {'Expected':>9}")
        print("-" * 70)
        for tc, score in zip(all_cases, scores):
            marker = "MATCH" if tc.expected_match else "DRIFT"
            print(f"{tc.label:<50} {score:>6.3f} {marker:>9}")

        # Threshold sweep
        print(f"\n{'Thresh':>7} {'TP':>4} {'FP':>4} {'TN':>4} {'FN':>4} {'Prec':>7} {'Rec':>7} {'F1':>7}")
        print("-" * 55)
        best = None
        for t in thresholds:
            r = evaluate_threshold(scores, labels, t)
            print(f"{r['threshold']:>7.2f} {r['tp']:>4} {r['fp']:>4} {r['tn']:>4} {r['fn']:>4} {r['precision']:>7.3f} {r['recall']:>7.3f} {r['f1']:>7.3f}")
            if best is None or r["f1"] > best["f1"]:
                best = r

        print(f"\nBest threshold: {best['threshold']:.2f} (F1={best['f1']:.3f}, P={best['precision']:.3f}, R={best['recall']:.3f})")

    # Part 2: Ambiguous cases (generic titles)
    print(f"\n{'=' * 70}")
    print("  PART 2: Ambiguous Cases (generic titles, excerpt critical)")
    print(f"{'=' * 70}")

    ambig_labels = [tc.expected_match for tc in AMBIGUOUS_MATCHES]

    for mode_label, use_excerpt in [("TITLE-ONLY", False), ("TITLE + EXCERPT", True)]:
        scores = compute_similarities(AMBIGUOUS_MATCHES, use_excerpt=use_excerpt)

        print(f"\n--- {mode_label} ---")
        print(f"{'Label':<55} {'Score':>6} {'Expected':>9}")
        print("-" * 75)
        for tc, score in zip(AMBIGUOUS_MATCHES, scores):
            marker = "MATCH" if tc.expected_match else "DRIFT"
            print(f"{tc.label:<55} {score:>6.3f} {marker:>9}")

        match_scores = [s for s, l in zip(scores, ambig_labels) if l]
        drift_scores = [s for s, l in zip(scores, ambig_labels) if not l]
        avg_match = sum(match_scores) / len(match_scores) if match_scores else 0
        avg_drift = sum(drift_scores) / len(drift_scores) if drift_scores else 0
        gap = avg_match - avg_drift
        print(f"\n  Avg match: {avg_match:.3f}, Avg drift: {avg_drift:.3f}, Gap: {gap:.3f}")

    # Part 3: Token gate test
    print(f"\n{'=' * 70}")
    print("  PART 3: Minimum Token Gate Test")
    print(f"{'=' * 70}")
    short_cases = [
        ("Overview", "Overview"),
        ("Deliverables", "Produce deliverables per Section 2.2.3"),
        ("Expected Outcomes", "Expected Outcomes"),
    ]
    vectorizer = TfidfVectorizer(stop_words="english", min_df=1)
    vectorizer.fit([t for pair in short_cases for t in pair])
    for target, ref in short_cases:
        ref_clean = strip_section_numbers(ref)
        target_clean = strip_section_numbers(target)
        # Count meaningful tokens (non-stopword)
        stop_words = vectorizer.get_stop_words() or set()
        ref_tokens = [w for w in ref_clean.split() if w.lower() not in stop_words]
        target_tokens = [w for w in target_clean.split() if w.lower() not in stop_words]
        min_tokens = min(len(ref_tokens), len(target_tokens))
        ref_vec = vectorizer.transform([ref_clean])
        target_vec = vectorizer.transform([target_clean])
        sim = cosine_similarity(ref_vec, target_vec)[0][0]
        gate = "SKIP (insufficient)" if min_tokens < 3 else "OK"
        print(f"  '{target}' vs '{ref}': tokens={min_tokens}, sim={sim:.3f} -> {gate}")


if __name__ == "__main__":
    main()
