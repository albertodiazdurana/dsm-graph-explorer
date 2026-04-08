# Research: Similarity Network Analysis for Text Similarity

**Purpose/Question:** How do different embedding models agree/disagree on document similarity, and what strategies handle model disagreement?
**Target Outcome:** Epoch 4 architecture input (LLM second-pass design, similarity edge methodology)
**Status:** Done
**Date Created:** 2026-02-25
**Date Completed:** 2026-02-25
**Outcome Reference:** Informs Epoch 4 roadmap (LLM second-pass) and deferred Sprint 7 feature (similarity edges on graph)

---

## Source

Witschard, D., Kucher, K., Jusufi, I., & Kerren, A. (2025). Using similarity network analysis to improve text similarity calculations. *Applied Network Science*, 10(8). https://doi.org/10.1007/s41109-025-00699-7

**Open Access:** CC BY 4.0
**Tool:** SN-Comparator (https://gitlab.com/dwitschard/sn-comparator)

---

## Key Findings

### 1. Inter-Model Agreement Is Surprisingly Low

Three state-of-the-art embedding models (USE, BERT/Sentence-BERT, SPECTER) tested on three corpora (IEEE VIS ~3,500 papers, CNN ~4,000 articles, Quora 2,500 question pairs):

| Metric | CNN | IEEE |
|--------|-----|------|
| Links unique to one model | 80% | 87% |
| Unanimous (all 3 models) | 6% | 2% |
| Rank alignment | Chaotic | Chaotic |

### 2. Binary vs Continuous Agreement Gap

On Quora data with human-annotated ground truth:
- Binary classification agreement: 73% (models agree on similar/dissimilar)
- Continuous similarity agreement: 25% link overlap (same data, continuous scores)

Implication: a model performing well on binary benchmarks may still produce very different similarity rankings than another model.

### 3. Ground Truth Ambiguity

Manual inspection of 273 cases where all models disagreed with human annotation revealed 51 cases (2% of ground truth) where the annotation itself was debatable. Similarity is inherently subjective, even for human annotators.

### 4. Combination Strategies

| Strategy | CNN links | IEEE links | Trade-off |
|----------|-----------|------------|-----------|
| Unanimous vote | 136 (6%) | 60 (2%) | High precision, very low recall |
| Majority vote | 487 (20%) | 330 (13%) | Moderate precision/recall |
| Two-step (majority + validated singles) | 1,531 (64%) | 849 (33%) | Balanced |
| Single vote (union) | 2,377 (100%) | 2,610 (100%) | Low precision, high recall |

Two-step strategy: include majority-vote links, plus single-model links validated by external signals (author similarity, time proximity, citation network).

---

## Relevance to DSM Graph Explorer

### Direct (Epoch 4: LLM Second-Pass)

Our planned tiered architecture (TF-IDF filters, LLM confirms) maps to the two-step strategy. TF-IDF acts as a broad, cheap first pass; LLM provides a "second opinion" on candidates. The paper validates this multi-model approach: single models miss true positives, combination strategies capture more of the similarity distribution.

**Design implication:** When adding LLM similarity, do not treat any single model as ground truth. Build the pipeline for model combination from the start.

### Confirming (Sprint 6: TF-IDF Threshold)

Our EXP-003b results (Precision=1.000, Recall=0.496 at threshold 0.08) mirror the precision/recall tension in the paper. Our conservative threshold behaves like their unanimous vote: high confidence in detected links, but misses many valid connections. The paper confirms this is a fundamental property of similarity thresholds, not a flaw in our implementation.

### Deferred (Sprint 7: Similarity Edges)

Sprint 7 DSM Central inbox deferred "similarity scores on REFERENCES edges." The paper provides methodology for constructing such edges: pairwise similarity computation, threshold-based or top-N filtering, network construction. Their link occurrence and rank alignment metrics could serve as quality indicators for our similarity edges.

### Future (Epoch 3: Graph Visualization)

SN-Comparator's visual design is relevant to our Neo4j visualization plans:
- Connected component display with keyword extraction per cluster
- Node-link layout with edge weight encoding (vote count)
- Close reading mode for comparing linked documents
- Overlay networks (author similarity, citation) for correlation analysis

### Methodological (Cosine Similarity Concerns)

Paper references Steck et al. (2024), "Is cosine-similarity of embeddings really about similarity?" (WWW '24). Worth tracking: our TF-IDF module uses cosine similarity via scikit-learn. The concern is more relevant to dense embeddings than sparse TF-IDF vectors, but worth revisiting when adding embedding-based similarity in Epoch 4.

---

## Secondary References Worth Tracking

- Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity? *WWW '24*. https://doi.org/10.1145/3589335.3651526
- Benito-Santos, A. & Theron Sanchez, R. (2019). Cross-domain visual exploration of academic corpora via latent meaning of user-authored keywords. *IEEE Access*, 7, 98144-98160.