"""Cross-repo entity matching for private-to-public repository comparison.

Compares two EntityInventory objects and classifies each entity pair by
match type: IDENTICAL, RENAMED, MODIFIED, ADDED, or REMOVED.

Algorithm (three passes)
------------------------
1. **Exact ID match:** Entities with the same ID in both inventories.
   If headings also match → IDENTICAL. If headings differ → MODIFIED.

2. **Fuzzy heading match:** Unmatched entities are compared by heading
   similarity using TF-IDF cosine similarity (reuses the approach from
   Sprint 6 / similarity.py). Pairs above the threshold with different
   IDs → RENAMED.

3. **Leftovers:** Entities only in inventory A → REMOVED.
   Entities only in inventory B → ADDED.

Dependencies
------------
- scikit-learn (optional): required for fuzzy matching (pass 2).
  If not installed, pass 2 is skipped and unmatched entities go
  directly to ADDED/REMOVED.

References
----------
- BL-156: Private-to-public repository mapping
- DEC-005: Similarity threshold (0.35)
- Epoch 3 plan: Phase 12.2
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from inventory.inventory_parser import Entity, EntityInventory

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Default similarity threshold from DEC-005
_DEFAULT_THRESHOLD = 0.35


class MatchType(StrEnum):
    """Classification of entity match between two repositories."""

    IDENTICAL = "IDENTICAL"
    RENAMED = "RENAMED"
    MODIFIED = "MODIFIED"
    ADDED = "ADDED"
    REMOVED = "REMOVED"


@dataclass
class MatchResult:
    """Result of comparing one entity pair across two repositories.

    For IDENTICAL/RENAMED/MODIFIED: both entity_a and entity_b are set.
    For REMOVED: entity_a is set, entity_b is None.
    For ADDED: entity_a is None, entity_b is set.
    """

    entity_a: Entity | None
    entity_b: Entity | None
    match_type: MatchType
    similarity_score: float


def compare_inventories(
    inv_a: EntityInventory,
    inv_b: EntityInventory,
    similarity_threshold: float = _DEFAULT_THRESHOLD,
) -> list[MatchResult]:
    """Compare two inventories and classify entity matches.

    Args:
        inv_a: First inventory (typically the private/source repo).
        inv_b: Second inventory (typically the public/target repo).
        similarity_threshold: Minimum cosine similarity for fuzzy matches.
            Default 0.35 from DEC-005.

    Returns:
        List of MatchResult covering every entity in both inventories.
    """
    results: list[MatchResult] = []

    # Index inventories by entity ID for fast lookup
    a_by_id = {e.id: e for e in inv_a.entities}
    b_by_id = {e.id: e for e in inv_b.entities}

    matched_a: set[str] = set()
    matched_b: set[str] = set()

    # Pass 1: Exact ID match
    for entity_id, entity_a in a_by_id.items():
        if entity_id in b_by_id:
            entity_b = b_by_id[entity_id]
            matched_a.add(entity_id)
            matched_b.add(entity_id)

            if entity_a.heading == entity_b.heading:
                results.append(MatchResult(
                    entity_a=entity_a,
                    entity_b=entity_b,
                    match_type=MatchType.IDENTICAL,
                    similarity_score=1.0,
                ))
            else:
                score = _heading_similarity(entity_a.heading, entity_b.heading)
                results.append(MatchResult(
                    entity_a=entity_a,
                    entity_b=entity_b,
                    match_type=MatchType.MODIFIED,
                    similarity_score=score,
                ))

    # Collect unmatched entities for pass 2
    unmatched_a = [
        e for eid, e in a_by_id.items() if eid not in matched_a
    ]
    unmatched_b = [
        e for eid, e in b_by_id.items() if eid not in matched_b
    ]

    # Pass 2: Fuzzy heading match (requires scikit-learn)
    if unmatched_a and unmatched_b and SKLEARN_AVAILABLE:
        fuzzy_matched_a, fuzzy_matched_b, fuzzy_results = _fuzzy_match(
            unmatched_a, unmatched_b, similarity_threshold
        )
        results.extend(fuzzy_results)
        matched_a.update(fuzzy_matched_a)
        matched_b.update(fuzzy_matched_b)

        # Update unmatched lists
        unmatched_a = [e for e in unmatched_a if e.id not in fuzzy_matched_a]
        unmatched_b = [e for e in unmatched_b if e.id not in fuzzy_matched_b]

    # Pass 3: Leftovers
    for entity in unmatched_a:
        results.append(MatchResult(
            entity_a=entity,
            entity_b=None,
            match_type=MatchType.REMOVED,
            similarity_score=0.0,
        ))

    for entity in unmatched_b:
        results.append(MatchResult(
            entity_a=None,
            entity_b=entity,
            match_type=MatchType.ADDED,
            similarity_score=0.0,
        ))

    return results


def _heading_similarity(heading_a: str, heading_b: str) -> float:
    """Compute cosine similarity between two headings using TF-IDF.

    Falls back to exact string comparison if scikit-learn is unavailable.
    """
    if not SKLEARN_AVAILABLE:
        return 1.0 if heading_a == heading_b else 0.0

    vectorizer = TfidfVectorizer(stop_words="english", min_df=1)
    try:
        matrix = vectorizer.fit_transform([heading_a, heading_b])
    except ValueError:
        # Empty vocabulary (e.g., both headings are only stop words)
        return 0.0
    return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])


def _fuzzy_match(
    unmatched_a: list[Entity],
    unmatched_b: list[Entity],
    threshold: float,
) -> tuple[set[str], set[str], list[MatchResult]]:
    """Find fuzzy heading matches between unmatched entity lists.

    Builds a TF-IDF matrix from all unmatched headings and finds the
    best match for each entity in A from entities in B. Matches above
    the threshold with different IDs are classified as RENAMED.

    Returns:
        Tuple of (matched_a_ids, matched_b_ids, results).
    """
    all_headings = [e.heading for e in unmatched_a] + [
        e.heading for e in unmatched_b
    ]

    vectorizer = TfidfVectorizer(stop_words="english", min_df=1)
    try:
        matrix = vectorizer.fit_transform(all_headings)
    except ValueError:
        return set(), set(), []

    n_a = len(unmatched_a)
    matrix_a = matrix[:n_a]
    matrix_b = matrix[n_a:]

    sim_matrix = cosine_similarity(matrix_a, matrix_b)

    matched_a_ids: set[str] = set()
    matched_b_ids: set[str] = set()
    results: list[MatchResult] = []

    # Greedy best-match: for each entity in A, find best match in B
    import numpy as np

    while True:
        # Mask already-matched rows and columns
        mask = sim_matrix.copy()
        for i, e in enumerate(unmatched_a):
            if e.id in matched_a_ids:
                mask[i, :] = -1
        for j, e in enumerate(unmatched_b):
            if e.id in matched_b_ids:
                mask[:, j] = -1

        best_idx = np.unravel_index(np.argmax(mask), mask.shape)
        best_score = mask[best_idx]

        if best_score < threshold:
            break

        i, j = best_idx
        entity_a = unmatched_a[i]
        entity_b = unmatched_b[j]

        matched_a_ids.add(entity_a.id)
        matched_b_ids.add(entity_b.id)

        results.append(MatchResult(
            entity_a=entity_a,
            entity_b=entity_b,
            match_type=MatchType.RENAMED,
            similarity_score=float(best_score),
        ))

    return matched_a_ids, matched_b_ids, results