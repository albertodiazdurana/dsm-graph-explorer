"""Tests for semantic similarity module (Phase 6.2).

Uses synthetic test cases modeled on EXP-003 to verify TF-IDF cosine
similarity, token gating, and the check_semantic_alignment pipeline.
"""

import pytest

from parser.cross_ref_extractor import CrossReference
from parser.markdown_parser import Section
from semantic.similarity import (
    SKLEARN_AVAILABLE,
    SemanticResult,
    build_corpus_vectorizer,
    check_semantic_alignment,
    compute_similarity,
    preprocess_text,
)

pytestmark = pytest.mark.skipif(
    not SKLEARN_AVAILABLE, reason="scikit-learn not installed"
)


# ---------------------------------------------------------------------------
# Synthetic test data (modeled on EXP-003 cases)
# ---------------------------------------------------------------------------

# A small corpus of sections for vectorizer fitting
CORPUS_SECTIONS = [
    Section(number="2.1", title="Phase 0: Environment Setup", line=10, level=2,
            context_excerpt="Establish a reproducible Python environment with base packages and VS Code configuration before beginning analysis work."),
    Section(number="2.5.6", title="Blog/Communication Deliverable Process", line=50, level=3,
            context_excerpt="When a project includes a public communication deliverable follow this structured process. Create one materials file per blog post."),
    Section(number="2.3.7", title="Data Leakage Prevention", line=80, level=3,
            context_excerpt="Validate assumptions about temporal data. Never use future information to predict past events. Implement strict train-test separation."),
    Section(number="4.1", title="Data-Driven Decision Making", line=120, level=2,
            context_excerpt="Validate assumptions. Never trust predetermined business expectations without verification. Pivot when necessary. Document decisions."),
    Section(number="2.2.3", title="Deliverables", line=160, level=3,
            context_excerpt="Required Outputs: EDA Notebooks, typically 1-2 notebooks with data quality assessment, cohort definition, key visualizations and statistics."),
    Section(number="3.4", title="Expected Outcomes", line=200, level=2,
            context_excerpt="Cohort metrics validated against business thresholds. Data quality assessment complete with documented limitations."),
    Section(number="A.3.2", title="NLP Packages", line=300, level=3,
            context_excerpt="nltk, Purpose: Natural Language Toolkit. spacy, Purpose: Industrial-strength NLP. Use Cases: Named entity recognition."),
    Section(number="1.3.1", title="Communication Style", line=30, level=3,
            context_excerpt="Concise responses: Direct answers without unnecessary elaboration. Clarifying questions first: Before generating artifacts, confirm understanding."),
]


def _make_ref(context: str, target: str, ref_type: str = "section",
              context_before: str = "", context_after: str = "") -> CrossReference:
    """Helper to create a CrossReference with context fields."""
    return CrossReference(
        type=ref_type, target=target, line=1, context=context,
        context_before=context_before, context_after=context_after,
    )


@pytest.fixture
def vectorizer():
    """Corpus-scoped vectorizer fitted on CORPUS_SECTIONS."""
    return build_corpus_vectorizer(CORPUS_SECTIONS)


# ---------------------------------------------------------------------------
# preprocess_text tests
# ---------------------------------------------------------------------------


class TestPreprocessText:
    def test_strips_section_numbers(self):
        result = preprocess_text("See Section 2.5.6 for blog process details")
        assert "2.5.6" not in result
        assert "blog process details" in result

    def test_strips_appendix_numbers(self):
        result = preprocess_text("Appendix A.3.2 lists NLP packages")
        assert "A.3.2" not in result
        assert "NLP packages" in result

    def test_normalizes_whitespace(self):
        result = preprocess_text("  extra   spaces   here  ")
        assert result == "extra spaces here"

    def test_empty_input(self):
        assert preprocess_text("") == ""


# ---------------------------------------------------------------------------
# build_corpus_vectorizer tests
# ---------------------------------------------------------------------------


class TestBuildCorpusVectorizer:
    def test_returns_fitted_vectorizer(self):
        vectorizer = build_corpus_vectorizer(CORPUS_SECTIONS)
        assert hasattr(vectorizer, "vocabulary_")

    def test_vocabulary_contains_domain_terms(self):
        vectorizer = build_corpus_vectorizer(CORPUS_SECTIONS)
        vocab = vectorizer.vocabulary_
        assert "python" in vocab
        assert "blog" in vocab
        assert "data" in vocab


# ---------------------------------------------------------------------------
# compute_similarity tests
# ---------------------------------------------------------------------------


class TestComputeSimilarity:
    def test_identical_texts_score_high(self, vectorizer):
        text = preprocess_text("Data leakage prevention using train-test separation")
        score = compute_similarity(text, text, vectorizer)
        assert score > 0.99

    def test_unrelated_texts_score_low(self, vectorizer):
        ref = preprocess_text("Install NLP packages for tokenization and entity recognition")
        target = preprocess_text("Establish a reproducible Python environment with base packages")
        score = compute_similarity(ref, target, vectorizer)
        assert score < 0.3


# ---------------------------------------------------------------------------
# check_semantic_alignment tests
# ---------------------------------------------------------------------------


class TestCheckSemanticAlignment:
    def test_matching_pair_above_threshold(self, vectorizer):
        """Reference about blog process should match blog section."""
        ref = _make_ref(
            context="Section 2.5.6 specifies the blog process and metadata format.",
            target="2.5.6",
            context_before="The blog deliverable process is documented.",
            context_after="Create materials files for each post.",
        )
        section = CORPUS_SECTIONS[1]  # Blog/Communication Deliverable Process
        result = check_semantic_alignment(ref, section, vectorizer)
        assert result.sufficient_context
        assert result.match
        assert result.score >= 0.10

    def test_drifted_pair_below_threshold(self, vectorizer):
        """Reference about blog process should NOT match data leakage section."""
        ref = _make_ref(
            context="Section 2.5.6 specifies the blog process and metadata format.",
            target="2.3.7",
            context_before="The blog deliverable process is documented.",
            context_after="Create materials files for each post.",
        )
        section = CORPUS_SECTIONS[2]  # Data Leakage Prevention
        result = check_semantic_alignment(ref, section, vectorizer)
        assert result.sufficient_context
        assert not result.match
        assert result.score < 0.10

    def test_insufficient_tokens_flagged(self, vectorizer):
        """Very short context should be flagged as insufficient."""
        ref = _make_ref(
            context="Section 3.4",
            target="3.4",
        )
        section = Section(
            number="3.4", title="Overview", line=1, level=2,
            context_excerpt="",
        )
        result = check_semantic_alignment(ref, section, vectorizer)
        assert not result.sufficient_context
        assert not result.match
        assert result.score == 0.0

    def test_ambiguous_title_with_excerpt_disambiguates(self, vectorizer):
        """Same title 'Deliverables', excerpt content should disambiguate."""
        ref = _make_ref(
            context="Submit the EDA deliverables from Section 2.2.3",
            target="2.2.3",
            context_before="including notebooks with visualizations",
            context_after="and the cohort definition document.",
        )
        correct_section = CORPUS_SECTIONS[4]  # Deliverables (EDA)
        result = check_semantic_alignment(ref, correct_section, vectorizer)
        assert result.sufficient_context
        assert result.score > 0.0

    def test_result_dataclass_fields(self, vectorizer):
        """SemanticResult should have all expected fields."""
        ref = _make_ref(
            context="Follow communication guidelines in Section 1.3.1",
            target="1.3.1",
            context_before="For all agent interactions",
            context_after="use concise responses.",
        )
        section = CORPUS_SECTIONS[7]  # Communication Style
        result = check_semantic_alignment(ref, section, vectorizer)
        assert isinstance(result, SemanticResult)
        assert isinstance(result.score, float)
        assert isinstance(result.ref_tokens, int)
        assert isinstance(result.target_tokens, int)
        assert isinstance(result.threshold, float)
        assert isinstance(result.sufficient_context, bool)
        assert isinstance(result.match, bool)

    def test_custom_threshold(self, vectorizer):
        """Higher threshold should make borderline cases fail."""
        ref = _make_ref(
            context="Follow communication guidelines in Section 1.3.1",
            target="1.3.1",
            context_before="For all agent interactions",
            context_after="use concise responses.",
        )
        section = CORPUS_SECTIONS[7]  # Communication Style
        result_low = check_semantic_alignment(ref, section, vectorizer, threshold=0.01)
        result_high = check_semantic_alignment(ref, section, vectorizer, threshold=0.99)
        assert result_low.match
        assert not result_high.match
        assert result_low.score == result_high.score
