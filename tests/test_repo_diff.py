"""Tests for src/graph/repo_diff.py.

RepoDiff is a pure function on two EntityInventory objects. No FalkorDB
dependency, so these tests run without the [graph] extra.

Fixture inventories simulate a private DSM repo and a public (rebranded)
version with overlapping, renamed, modified, added, and removed entities.
"""

import pytest

from inventory.inventory_parser import Entity, EntityInventory, RepoInfo


# ── fixture helpers ──────────────────────────────────────────────────────────


def _entity(
    entity_id: str,
    heading: str,
    path: str = "doc.md",
    entity_type: str = "section",
    level: int = 2,
) -> Entity:
    return Entity(
        id=entity_id,
        type=entity_type,
        path=path,
        heading=heading,
        level=level,
    )


def _inventory(name: str, repo_type: str, entities: list[Entity]) -> EntityInventory:
    return EntityInventory(
        version="1.0",
        repo=RepoInfo(name=name, type=repo_type),
        entities=entities,
    )


@pytest.fixture
def private_inventory() -> EntityInventory:
    """Simulates a private DSM repository inventory."""
    return _inventory(
        "dsm-private",
        "dsm-hub",
        [
            _entity("sec/1.0", "Introduction to the Methodology"),
            _entity("sec/2.0", "Sprint Boundary Checklist", entity_type="protocol"),
            _entity("sec/3.0", "Data Leakage Prevention Guidelines"),
            _entity("sec/4.0", "Internal Review Process"),  # no public equivalent
        ],
    )


@pytest.fixture
def public_inventory() -> EntityInventory:
    """Simulates a public (rebranded) DSM repository inventory."""
    return _inventory(
        "dsm-public",
        "dsm-hub",
        [
            _entity("sec/1.0", "Introduction to the Methodology"),  # identical
            _entity("sec/2.0", "Sprint Boundary Checklist", entity_type="protocol"),  # identical
            _entity("sec/3.0", "Data Leakage Prevention Best Practices"),  # modified heading
            _entity("sec/5.0", "Community Contribution Guide"),  # added, no private equivalent
        ],
    )


@pytest.fixture
def renamed_inventory() -> EntityInventory:
    """Inventory with a renamed entity (different ID, similar heading)."""
    return _inventory(
        "dsm-public-renamed",
        "dsm-hub",
        [
            _entity("pub/intro", "Introduction to the Methodology"),  # renamed ID
        ],
    )


# ── compare_inventories ─────────────────────────────────────────────────────


class TestCompareInventories:
    """Test the main comparison function."""

    def test_identical_entities_matched(self, private_inventory, public_inventory):
        from graph.repo_diff import MatchType, compare_inventories

        results = compare_inventories(private_inventory, public_inventory)
        identical = [r for r in results if r.match_type == MatchType.IDENTICAL]

        assert len(identical) == 2
        ids = {r.entity_a.id for r in identical}
        assert ids == {"sec/1.0", "sec/2.0"}

    def test_identical_has_score_one(self, private_inventory, public_inventory):
        from graph.repo_diff import MatchType, compare_inventories

        results = compare_inventories(private_inventory, public_inventory)
        identical = [r for r in results if r.match_type == MatchType.IDENTICAL]

        for r in identical:
            assert r.similarity_score == 1.0

    def test_modified_entity_detected(self, private_inventory, public_inventory):
        from graph.repo_diff import MatchType, compare_inventories

        results = compare_inventories(private_inventory, public_inventory)
        modified = [r for r in results if r.match_type == MatchType.MODIFIED]

        assert len(modified) == 1
        assert modified[0].entity_a.id == "sec/3.0"
        assert modified[0].entity_b.id == "sec/3.0"
        assert modified[0].similarity_score < 1.0
        assert modified[0].similarity_score > 0.0

    def test_removed_entity_detected(self, private_inventory, public_inventory):
        from graph.repo_diff import MatchType, compare_inventories

        results = compare_inventories(private_inventory, public_inventory)
        removed = [r for r in results if r.match_type == MatchType.REMOVED]

        assert len(removed) == 1
        assert removed[0].entity_a.id == "sec/4.0"
        assert removed[0].entity_b is None
        assert removed[0].similarity_score == 0.0

    def test_added_entity_detected(self, private_inventory, public_inventory):
        from graph.repo_diff import MatchType, compare_inventories

        results = compare_inventories(private_inventory, public_inventory)
        added = [r for r in results if r.match_type == MatchType.ADDED]

        assert len(added) == 1
        assert added[0].entity_a is None
        assert added[0].entity_b.id == "sec/5.0"
        assert added[0].similarity_score == 0.0

    def test_total_results_cover_all_entities(
        self, private_inventory, public_inventory
    ):
        from graph.repo_diff import compare_inventories

        results = compare_inventories(private_inventory, public_inventory)

        # 2 identical + 1 modified + 1 removed + 1 added = 5
        assert len(results) == 5

    def test_renamed_entity_detected(self, private_inventory, renamed_inventory):
        """Different ID but similar heading → RENAMED."""
        from graph.repo_diff import MatchType, compare_inventories

        # private has sec/1.0 "Introduction to the Methodology"
        # renamed has pub/intro "Introduction to the Methodology" (different ID)
        inv_a = _inventory(
            "private",
            "dsm-hub",
            [_entity("sec/1.0", "Introduction to the Methodology")],
        )

        results = compare_inventories(inv_a, renamed_inventory)
        renamed = [r for r in results if r.match_type == MatchType.RENAMED]

        assert len(renamed) == 1
        assert renamed[0].entity_a.id == "sec/1.0"
        assert renamed[0].entity_b.id == "pub/intro"
        assert renamed[0].similarity_score > 0.8


# ── empty inventories ────────────────────────────────────────────────────────


class TestEmptyInventories:
    """Test behavior with empty entity lists."""

    def test_both_empty(self):
        from graph.repo_diff import compare_inventories

        inv_a = _inventory("a", "dsm-spoke", [])
        inv_b = _inventory("b", "dsm-spoke", [])

        results = compare_inventories(inv_a, inv_b)
        assert results == []

    def test_a_empty_all_added(self):
        from graph.repo_diff import MatchType, compare_inventories

        inv_a = _inventory("a", "dsm-spoke", [])
        inv_b = _inventory(
            "b",
            "dsm-spoke",
            [_entity("sec/1.0", "Something")],
        )

        results = compare_inventories(inv_a, inv_b)
        assert len(results) == 1
        assert results[0].match_type == MatchType.ADDED

    def test_b_empty_all_removed(self):
        from graph.repo_diff import MatchType, compare_inventories

        inv_a = _inventory(
            "a",
            "dsm-spoke",
            [_entity("sec/1.0", "Something")],
        )
        inv_b = _inventory("b", "dsm-spoke", [])

        results = compare_inventories(inv_a, inv_b)
        assert len(results) == 1
        assert results[0].match_type == MatchType.REMOVED


# ── threshold behavior ───────────────────────────────────────────────────────


class TestThreshold:
    """Test that the similarity threshold controls fuzzy match sensitivity."""

    def test_high_threshold_fewer_renamed(self):
        """With threshold=0.99, only near-perfect heading matches qualify."""
        from graph.repo_diff import MatchType, compare_inventories

        inv_a = _inventory(
            "a",
            "dsm-hub",
            [_entity("sec/1.0", "Data Leakage Prevention Guidelines")],
        )
        inv_b = _inventory(
            "b",
            "dsm-hub",
            [_entity("pub/1.0", "Data Leakage Prevention Best Practices")],
        )

        results = compare_inventories(inv_a, inv_b, similarity_threshold=0.99)

        # High threshold: not similar enough → each is unmatched
        renamed = [r for r in results if r.match_type == MatchType.RENAMED]
        assert len(renamed) == 0

    def test_low_threshold_more_renamed(self):
        """With a low threshold, moderately similar headings match."""
        from graph.repo_diff import MatchType, compare_inventories

        inv_a = _inventory(
            "a",
            "dsm-hub",
            [_entity("sec/1.0", "Data Leakage Prevention Guidelines")],
        )
        inv_b = _inventory(
            "b",
            "dsm-hub",
            [_entity("pub/1.0", "Data Leakage Prevention Best Practices")],
        )

        results = compare_inventories(inv_a, inv_b, similarity_threshold=0.1)

        renamed = [r for r in results if r.match_type == MatchType.RENAMED]
        assert len(renamed) == 1


# ── MatchResult fields ───────────────────────────────────────────────────────


class TestMatchResultFields:
    """Verify MatchResult dataclass structure."""

    def test_match_result_has_expected_fields(self, private_inventory, public_inventory):
        from graph.repo_diff import compare_inventories

        results = compare_inventories(private_inventory, public_inventory)
        r = results[0]

        assert hasattr(r, "entity_a")
        assert hasattr(r, "entity_b")
        assert hasattr(r, "match_type")
        assert hasattr(r, "similarity_score")