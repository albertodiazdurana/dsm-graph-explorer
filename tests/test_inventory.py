"""Tests for entity inventory parsing and models."""

import pytest
from pathlib import Path

from inventory.inventory_parser import (
    Entity,
    EntityInventory,
    InventoryError,
    RepoInfo,
    discover_inventory,
    export_inventory,
    load_inventory,
)
from parser.markdown_parser import ParsedDocument, Section


# --- Fixtures ---

VALID_INVENTORY_YAML = """\
version: "1.0"
repo:
  name: dsm-agentic-ai-data-science-methodology
  type: dsm-hub
  url: https://github.com/example/dsm

entities:
  - id: "DSM_1.0/section/2.3.7"
    type: section
    path: DSM_1.0_Data_Science_Collaboration_Methodology_v1.1.md
    heading: "2.3.7 Data Leakage Prevention"
    level: 3
    stable: true

  - id: "DSM_2.0/protocol/sprint-boundary-checklist"
    type: protocol
    path: DSM_2.0_ProjectManagement_Guidelines.md
    heading: "Sprint Boundary Checklist"
    stable: true

  - id: "backlog/BL-156"
    type: backlog-item
    path: plan/backlog.md
    heading: "BL-156: Private-to-public repository mapping"
    stable: false
"""

MINIMAL_INVENTORY_YAML = """\
version: "1.0"
repo:
  name: my-project
  type: dsm-spoke

entities: []
"""

NO_URL_INVENTORY_YAML = """\
version: "1.0"
repo:
  name: private-repo
  type: external

entities:
  - id: "doc/readme"
    type: section
    path: README.md
    heading: "Introduction"
    stable: true
"""


# --- Entity model tests ---


class TestEntity:
    """Tests for Entity Pydantic model."""

    def test_valid_entity_all_fields(self):
        """Entity with all fields creates successfully."""
        entity = Entity(
            id="DSM_1.0/section/2.3.7",
            type="section",
            path="DSM_1.0.md",
            heading="2.3.7 Data Leakage Prevention",
            level=3,
            stable=True,
        )
        assert entity.id == "DSM_1.0/section/2.3.7"
        assert entity.type == "section"
        assert entity.path == "DSM_1.0.md"
        assert entity.heading == "2.3.7 Data Leakage Prevention"
        assert entity.level == 3
        assert entity.stable is True

    def test_entity_level_optional(self):
        """Entity without level defaults to None."""
        entity = Entity(
            id="backlog/BL-156",
            type="backlog-item",
            path="backlog.md",
            heading="BL-156",
            stable=False,
        )
        assert entity.level is None

    def test_entity_stable_defaults_true(self):
        """Entity without stable defaults to True."""
        entity = Entity(
            id="doc/readme",
            type="section",
            path="README.md",
            heading="Introduction",
        )
        assert entity.stable is True

    def test_entity_valid_types(self):
        """All valid entity types are accepted."""
        for entity_type in ["section", "protocol", "backlog-item"]:
            entity = Entity(
                id=f"test/{entity_type}",
                type=entity_type,
                path="test.md",
                heading="Test",
            )
            assert entity.type == entity_type

    def test_entity_empty_id_rejected(self):
        """Empty id raises validation error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Entity(id="", type="section", path="test.md", heading="Test")

    def test_entity_empty_path_rejected(self):
        """Empty path raises validation error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Entity(id="test/1", type="section", path="", heading="Test")

    def test_entity_empty_heading_rejected(self):
        """Empty heading raises validation error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Entity(id="test/1", type="section", path="test.md", heading="")

    def test_entity_invalid_type_rejected(self):
        """Invalid entity type raises validation error."""
        with pytest.raises(ValueError):
            Entity(id="test/1", type="invalid", path="test.md", heading="Test")

    def test_entity_negative_level_rejected(self):
        """Negative level raises validation error."""
        with pytest.raises(ValueError):
            Entity(
                id="test/1", type="section", path="test.md",
                heading="Test", level=-1,
            )


# --- RepoInfo model tests ---


class TestRepoInfo:
    """Tests for RepoInfo Pydantic model."""

    def test_valid_repo_info_all_fields(self):
        """RepoInfo with all fields creates successfully."""
        repo = RepoInfo(
            name="dsm-methodology",
            type="dsm-hub",
            url="https://github.com/example/dsm",
        )
        assert repo.name == "dsm-methodology"
        assert repo.type == "dsm-hub"
        assert repo.url == "https://github.com/example/dsm"

    def test_repo_info_url_optional(self):
        """RepoInfo without url defaults to None."""
        repo = RepoInfo(name="private-repo", type="dsm-spoke")
        assert repo.url is None

    def test_repo_info_valid_types(self):
        """All valid repo types are accepted."""
        for repo_type in ["dsm-hub", "dsm-spoke", "external"]:
            repo = RepoInfo(name="test", type=repo_type)
            assert repo.type == repo_type

    def test_repo_info_invalid_type_rejected(self):
        """Invalid repo type raises validation error."""
        with pytest.raises(ValueError):
            RepoInfo(name="test", type="unknown")

    def test_repo_info_empty_name_rejected(self):
        """Empty name raises validation error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            RepoInfo(name="", type="dsm-hub")


# --- EntityInventory model tests ---


class TestEntityInventory:
    """Tests for EntityInventory Pydantic model."""

    def test_valid_inventory_with_entities(self):
        """Inventory with entities creates successfully."""
        inv = EntityInventory(
            version="1.0",
            repo=RepoInfo(name="dsm", type="dsm-hub"),
            entities=[
                Entity(
                    id="test/1", type="section",
                    path="test.md", heading="Test",
                ),
            ],
        )
        assert inv.version == "1.0"
        assert inv.repo.name == "dsm"
        assert len(inv.entities) == 1

    def test_empty_entities_list_valid(self):
        """Inventory with empty entities list is valid."""
        inv = EntityInventory(
            version="1.0",
            repo=RepoInfo(name="dsm", type="dsm-spoke"),
            entities=[],
        )
        assert inv.entities == []

    def test_duplicate_entity_ids_rejected(self):
        """Inventory with duplicate entity IDs raises validation error."""
        with pytest.raises(ValueError, match="Duplicate entity"):
            EntityInventory(
                version="1.0",
                repo=RepoInfo(name="dsm", type="dsm-hub"),
                entities=[
                    Entity(
                        id="test/1", type="section",
                        path="a.md", heading="A",
                    ),
                    Entity(
                        id="test/1", type="section",
                        path="b.md", heading="B",
                    ),
                ],
            )

    def test_entity_lookup_by_id(self):
        """Inventory provides entity lookup by ID."""
        entities = [
            Entity(id="a/1", type="section", path="a.md", heading="A"),
            Entity(id="b/2", type="protocol", path="b.md", heading="B"),
        ]
        inv = EntityInventory(
            version="1.0",
            repo=RepoInfo(name="dsm", type="dsm-hub"),
            entities=entities,
        )
        assert inv.get_entity("a/1") is not None
        assert inv.get_entity("a/1").heading == "A"
        assert inv.get_entity("b/2").type == "protocol"
        assert inv.get_entity("nonexistent") is None


# --- load_inventory tests ---


class TestLoadInventory:
    """Tests for load_inventory function."""

    def test_load_valid_inventory(self, tmp_path):
        """Load a valid inventory YAML file."""
        path = tmp_path / "dsm-entity-inventory.yml"
        path.write_text(VALID_INVENTORY_YAML, encoding="utf-8")

        inv = load_inventory(path)
        assert inv.version == "1.0"
        assert inv.repo.name == "dsm-agentic-ai-data-science-methodology"
        assert inv.repo.type == "dsm-hub"
        assert inv.repo.url == "https://github.com/example/dsm"
        assert len(inv.entities) == 3

    def test_load_minimal_inventory(self, tmp_path):
        """Load a minimal inventory with no entities."""
        path = tmp_path / "dsm-entity-inventory.yml"
        path.write_text(MINIMAL_INVENTORY_YAML, encoding="utf-8")

        inv = load_inventory(path)
        assert inv.repo.name == "my-project"
        assert inv.entities == []

    def test_load_inventory_no_url(self, tmp_path):
        """Load inventory without optional URL field."""
        path = tmp_path / "dsm-entity-inventory.yml"
        path.write_text(NO_URL_INVENTORY_YAML, encoding="utf-8")

        inv = load_inventory(path)
        assert inv.repo.url is None
        assert len(inv.entities) == 1

    def test_load_entity_types(self, tmp_path):
        """Loaded entities have correct types."""
        path = tmp_path / "dsm-entity-inventory.yml"
        path.write_text(VALID_INVENTORY_YAML, encoding="utf-8")

        inv = load_inventory(path)
        types = [e.type for e in inv.entities]
        assert types == ["section", "protocol", "backlog-item"]

    def test_load_entity_stable_flags(self, tmp_path):
        """Loaded entities have correct stable flags."""
        path = tmp_path / "dsm-entity-inventory.yml"
        path.write_text(VALID_INVENTORY_YAML, encoding="utf-8")

        inv = load_inventory(path)
        stable_flags = [e.stable for e in inv.entities]
        assert stable_flags == [True, True, False]

    def test_load_nonexistent_file_raises(self, tmp_path):
        """Loading a nonexistent file raises InventoryError."""
        path = tmp_path / "nonexistent.yml"
        with pytest.raises(InventoryError, match="not found"):
            load_inventory(path)

    def test_load_invalid_yaml_raises(self, tmp_path):
        """Loading invalid YAML raises InventoryError."""
        path = tmp_path / "bad.yml"
        path.write_text("{{invalid yaml", encoding="utf-8")
        with pytest.raises(InventoryError, match="parse"):
            load_inventory(path)

    def test_load_missing_version_raises(self, tmp_path):
        """Loading YAML without version field raises InventoryError."""
        path = tmp_path / "no-version.yml"
        path.write_text(
            "repo:\n  name: test\n  type: dsm-hub\nentities: []\n",
            encoding="utf-8",
        )
        with pytest.raises(InventoryError, match="validation"):
            load_inventory(path)

    def test_load_missing_repo_raises(self, tmp_path):
        """Loading YAML without repo field raises InventoryError."""
        path = tmp_path / "no-repo.yml"
        path.write_text(
            'version: "1.0"\nentities: []\n',
            encoding="utf-8",
        )
        with pytest.raises(InventoryError, match="validation"):
            load_inventory(path)

    def test_load_invalid_entity_raises(self, tmp_path):
        """Loading YAML with invalid entity raises InventoryError."""
        path = tmp_path / "bad-entity.yml"
        path.write_text(
            'version: "1.0"\n'
            "repo:\n  name: test\n  type: dsm-hub\n"
            "entities:\n  - id: test\n    type: invalid\n"
            "    path: t.md\n    heading: T\n",
            encoding="utf-8",
        )
        with pytest.raises(InventoryError, match="validation"):
            load_inventory(path)

    def test_load_accepts_path_object_and_string(self, tmp_path):
        """load_inventory accepts both Path and str."""
        path = tmp_path / "dsm-entity-inventory.yml"
        path.write_text(MINIMAL_INVENTORY_YAML, encoding="utf-8")

        inv_path = load_inventory(path)
        inv_str = load_inventory(str(path))
        assert inv_path.repo.name == inv_str.repo.name


# --- discover_inventory tests ---


class TestDiscoverInventory:
    """Tests for discover_inventory function."""

    def test_discover_finds_inventory_at_root(self, tmp_path):
        """discover_inventory finds dsm-entity-inventory.yml at repo root."""
        inv_file = tmp_path / "dsm-entity-inventory.yml"
        inv_file.write_text(MINIMAL_INVENTORY_YAML, encoding="utf-8")

        result = discover_inventory(tmp_path)
        assert result is not None
        assert result.name == "dsm-entity-inventory.yml"

    def test_discover_returns_none_when_absent(self, tmp_path):
        """discover_inventory returns None when no inventory exists."""
        result = discover_inventory(tmp_path)
        assert result is None

    def test_discover_ignores_subdirectories(self, tmp_path):
        """discover_inventory only checks repo root, not subdirs."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "dsm-entity-inventory.yml").write_text(
            MINIMAL_INVENTORY_YAML, encoding="utf-8",
        )

        result = discover_inventory(tmp_path)
        assert result is None

    def test_discover_accepts_string_path(self, tmp_path):
        """discover_inventory accepts str path."""
        (tmp_path / "dsm-entity-inventory.yml").write_text(
            MINIMAL_INVENTORY_YAML, encoding="utf-8",
        )

        result = discover_inventory(str(tmp_path))
        assert result is not None


# --- export_inventory tests ---


def make_doc(
    file: str, sections: list[tuple[str | None, str, int, int]]
) -> ParsedDocument:
    """Create a ParsedDocument from (number, title, line, level) tuples."""
    return ParsedDocument(
        file=file,
        sections=[
            Section(number=n, title=t, line=l, level=lv) for n, t, l, lv in sections
        ],
    )


class TestExportInventory:
    """Tests for export_inventory function."""

    def test_export_returns_entity_inventory(self):
        """export_inventory returns an EntityInventory."""
        doc = make_doc("test.md", [("1", "Intro", 1, 1)])
        result = export_inventory([doc], repo_name="my-repo")
        assert isinstance(result, EntityInventory)

    def test_export_repo_metadata(self):
        """Exported inventory has correct repo metadata."""
        doc = make_doc("test.md", [("1", "Intro", 1, 1)])
        result = export_inventory([doc], repo_name="my-repo")
        assert result.repo.name == "my-repo"
        assert result.repo.type == "dsm-spoke"
        assert result.version == "1.0"

    def test_export_custom_repo_type(self):
        """Exported inventory respects custom repo type."""
        doc = make_doc("test.md", [("1", "Intro", 1, 1)])
        result = export_inventory([doc], repo_name="hub", repo_type="dsm-hub")
        assert result.repo.type == "dsm-hub"

    def test_export_sections_become_entities(self):
        """Numbered sections become entities."""
        doc = make_doc("guide.md", [
            ("1", "Introduction", 1, 1),
            ("1.1", "Overview", 5, 2),
            ("2", "Usage", 20, 1),
        ])
        result = export_inventory([doc], repo_name="test")
        assert len(result.entities) == 3

    def test_export_unnumbered_sections_excluded(self):
        """Sections without numbers are excluded."""
        doc = make_doc("guide.md", [
            (None, "Unnumbered", 1, 1),
            ("1", "Numbered", 5, 1),
        ])
        result = export_inventory([doc], repo_name="test")
        assert len(result.entities) == 1
        assert result.entities[0].heading == "1 Numbered"

    def test_export_entity_fields(self):
        """Exported entity has correct fields."""
        doc = make_doc("guide.md", [("2.3.7", "Data Leakage Prevention", 10, 3)])
        result = export_inventory([doc], repo_name="test")
        entity = result.entities[0]
        assert entity.path == "guide.md"
        assert entity.heading == "2.3.7 Data Leakage Prevention"
        assert entity.level == 3
        assert entity.type == "section"
        assert entity.stable is True

    def test_export_entity_id_format(self):
        """Entity IDs follow the path/section/number pattern."""
        doc = make_doc("DSM_1.0.md", [("2.3.7", "Title", 10, 3)])
        result = export_inventory([doc], repo_name="test")
        assert result.entities[0].id == "DSM_1.0.md/section/2.3.7"

    def test_export_protocol_heuristic(self):
        """Headings matching protocol patterns get type 'protocol'."""
        doc = make_doc("guide.md", [
            ("1", "Sprint Boundary Checklist", 1, 1),
        ])
        result = export_inventory([doc], repo_name="test")
        assert result.entities[0].type == "protocol"

    def test_export_backlog_heuristic(self):
        """Headings matching BL-### pattern get type 'backlog-item'."""
        doc = make_doc("backlog.md", [
            ("1", "BL-156: Private-to-public mapping", 1, 1),
        ])
        result = export_inventory([doc], repo_name="test")
        assert result.entities[0].type == "backlog-item"

    def test_export_multi_document(self):
        """Export merges entities from multiple documents."""
        doc1 = make_doc("a.md", [("1", "Intro", 1, 1)])
        doc2 = make_doc("b.md", [("2", "Body", 1, 1)])
        result = export_inventory([doc1, doc2], repo_name="test")
        assert len(result.entities) == 2
        paths = [e.path for e in result.entities]
        assert "a.md" in paths
        assert "b.md" in paths

    def test_export_empty_documents(self):
        """Export with no documents produces empty entities list."""
        result = export_inventory([], repo_name="test")
        assert result.entities == []

    def test_export_to_yaml_file(self, tmp_path):
        """export_inventory with output_path writes valid YAML."""
        doc = make_doc("test.md", [("1", "Intro", 1, 1)])
        output = tmp_path / "dsm-entity-inventory.yml"
        export_inventory([doc], repo_name="test", output_path=output)

        assert output.exists()
        # Round-trip: load it back
        loaded = load_inventory(output)
        assert loaded.repo.name == "test"
        assert len(loaded.entities) == 1

    def test_export_to_yaml_string_path(self, tmp_path):
        """export_inventory accepts string output path."""
        doc = make_doc("test.md", [("1", "Intro", 1, 1)])
        output = tmp_path / "out.yml"
        export_inventory([doc], repo_name="test", output_path=str(output))
        assert output.exists()

    def test_export_unique_entity_ids(self):
        """Same section number in different files gets unique IDs."""
        doc1 = make_doc("a.md", [("1", "Intro", 1, 1)])
        doc2 = make_doc("b.md", [("1", "Intro", 1, 1)])
        result = export_inventory([doc1, doc2], repo_name="test")
        ids = [e.id for e in result.entities]
        assert len(ids) == len(set(ids))  # all unique