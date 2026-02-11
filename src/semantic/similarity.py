"""TF-IDF semantic similarity for cross-reference validation.

Computes cosine similarity between cross-reference context and target
section content using TF-IDF vectorization with corpus-scoped IDF.
Parameters follow DEC-005 (EXP-003 threshold tuning results).

Requires scikit-learn (optional dependency). Functions raise ImportError
with a helpful message when scikit-learn is not installed.
"""

import re
from dataclasses import dataclass

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from parser.cross_ref_extractor import CrossReference
from parser.markdown_parser import Section

_DEFAULT_THRESHOLD = 0.10
_DEFAULT_MIN_TOKENS = 3
_SECTION_NUMBER_RE = re.compile(r"\b[A-Z]?\d+(?:\.\d+)+\.?\b")


@dataclass
class SemanticResult:
    """Result of a semantic similarity check for one cross-reference."""

    score: float
    ref_tokens: int
    target_tokens: int
    threshold: float
    sufficient_context: bool
    match: bool


def _require_sklearn() -> None:
    if not SKLEARN_AVAILABLE:
        raise ImportError(
            "scikit-learn is required for semantic validation. "
            "Install it with: pip install dsm-graph-explorer[semantic]"
        )


def preprocess_text(text: str) -> str:
    """Strip section numbers and normalize whitespace.

    Removes patterns like '2.5.6', 'A.3.2', and '1.0.' that carry no
    semantic value and could inflate similarity artificially.
    """
    cleaned = _SECTION_NUMBER_RE.sub("", text)
    return " ".join(cleaned.split())


def build_corpus_vectorizer(
    sections: list[Section],
) -> "TfidfVectorizer":
    """Fit a TF-IDF vectorizer on all section texts.

    Builds combined text (title + context_excerpt) for each section and
    fits the vectorizer on the full corpus. This gives corpus-scoped IDF
    weighting, which properly downweights common DSM vocabulary.

    Args:
        sections: All sections from all parsed documents.

    Returns:
        Fitted TfidfVectorizer ready for transform calls.
    """
    _require_sklearn()

    corpus = []
    for section in sections:
        combined = f"{section.title} {section.context_excerpt}"
        corpus.append(preprocess_text(combined))

    vectorizer = TfidfVectorizer(stop_words="english", min_df=1)
    vectorizer.fit(corpus)
    return vectorizer


def _count_meaningful_tokens(text: str, vectorizer: "TfidfVectorizer") -> int:
    """Count tokens remaining after stopword removal."""
    stop_words = vectorizer.get_stop_words() or set()
    words = text.lower().split()
    return sum(1 for w in words if w not in stop_words)


def compute_similarity(
    ref_text: str,
    target_text: str,
    vectorizer: "TfidfVectorizer",
) -> float:
    """Compute cosine similarity between two preprocessed texts.

    Args:
        ref_text: Preprocessed reference context text.
        target_text: Preprocessed target section text.
        vectorizer: Fitted TfidfVectorizer.

    Returns:
        Cosine similarity score between 0.0 and 1.0.
    """
    _require_sklearn()

    ref_vec = vectorizer.transform([ref_text])
    target_vec = vectorizer.transform([target_text])
    return float(cosine_similarity(ref_vec, target_vec)[0][0])


def check_semantic_alignment(
    ref: CrossReference,
    section: Section,
    vectorizer: "TfidfVectorizer",
    threshold: float = _DEFAULT_THRESHOLD,
    min_tokens: int = _DEFAULT_MIN_TOKENS,
) -> SemanticResult:
    """Check whether a cross-reference aligns semantically with its target.

    Combines the reference's context window (before + line + after) and
    compares against the section's title + excerpt. Applies the minimum
    token gate before computing similarity.

    Args:
        ref: The cross-reference to check.
        section: The target section it points to.
        vectorizer: Fitted corpus-scoped TfidfVectorizer.
        threshold: Minimum similarity score to consider a match.
        min_tokens: Minimum meaningful tokens required on both sides.

    Returns:
        SemanticResult with score, token counts, and verdict.
    """
    _require_sklearn()

    ref_text = preprocess_text(
        f"{ref.context_before} {ref.context} {ref.context_after}"
    )
    target_text = preprocess_text(
        f"{section.title} {section.context_excerpt}"
    )

    ref_token_count = _count_meaningful_tokens(ref_text, vectorizer)
    target_token_count = _count_meaningful_tokens(target_text, vectorizer)
    sufficient = (
        ref_token_count >= min_tokens and target_token_count >= min_tokens
    )

    if not sufficient:
        return SemanticResult(
            score=0.0,
            ref_tokens=ref_token_count,
            target_tokens=target_token_count,
            threshold=threshold,
            sufficient_context=False,
            match=False,
        )

    score = compute_similarity(ref_text, target_text, vectorizer)

    return SemanticResult(
        score=score,
        ref_tokens=ref_token_count,
        target_tokens=target_token_count,
        threshold=threshold,
        sufficient_context=True,
        match=score >= threshold,
    )
