"""Entity inventory parser and exporter for DSM repositories.

Loads and validates dsm-entity-inventory.yml files that describe
referenceable entities (sections, protocols, backlog items) in a repository.
Used for cross-repo reference resolution.

Also provides export_inventory() to generate an inventory from parsed documents.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

if TYPE_CHECKING:
    from parser.markdown_parser import ParsedDocument

INVENTORY_FILENAME = "dsm-entity-inventory.yml"

EntityType = Literal["section", "protocol", "backlog-item"]
RepoType = Literal["dsm-hub", "dsm-spoke", "external"]


class InventoryError(Exception):
    """Raised when an inventory file cannot be loaded or validated."""


class Entity(BaseModel):
    """A single referenceable entity in a repository."""

    id: str = Field(description="Stable identifier, e.g. DSM_1.0/section/2.3.7")
    type: EntityType = Field(description="Entity type")
    path: str = Field(description="File path relative to repo root")
    heading: str = Field(description="Section or item heading text")
    level: int | None = Field(default=None, description="Heading level (1-6)")
    stable: bool = Field(default=True, description="Whether the entity is stable")

    @field_validator("id")
    @classmethod
    def id_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("id cannot be empty")
        return v

    @field_validator("path")
    @classmethod
    def path_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("path cannot be empty")
        return v

    @field_validator("heading")
    @classmethod
    def heading_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("heading cannot be empty")
        return v

    @field_validator("level")
    @classmethod
    def level_positive(cls, v: int | None) -> int | None:
        if v is not None and v < 1:
            raise ValueError("level must be >= 1")
        return v


class RepoInfo(BaseModel):
    """Repository metadata."""

    name: str = Field(description="Repository name")
    type: RepoType = Field(description="Repository type")
    url: str | None = Field(default=None, description="Repository URL")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name cannot be empty")
        return v


class EntityInventory(BaseModel):
    """Complete entity inventory for a repository."""

    version: str = Field(description="Inventory format version")
    repo: RepoInfo = Field(description="Repository metadata")
    entities: list[Entity] = Field(
        default_factory=list, description="List of entities"
    )

    @model_validator(mode="after")
    def check_unique_ids(self) -> "EntityInventory":
        seen: set[str] = set()
        for entity in self.entities:
            if entity.id in seen:
                raise ValueError(
                    f"Duplicate entity id: {entity.id}"
                )
            seen.add(entity.id)
        return self

    def get_entity(self, entity_id: str) -> Entity | None:
        """Look up an entity by ID. Returns None if not found."""
        for entity in self.entities:
            if entity.id == entity_id:
                return entity
        return None


def load_inventory(path: str | Path) -> EntityInventory:
    """Load and validate an entity inventory from a YAML file.

    Args:
        path: Path to the inventory YAML file.

    Returns:
        Validated EntityInventory instance.

    Raises:
        InventoryError: If the file is missing, unparseable, or invalid.
    """
    path = Path(path)
    if not path.exists():
        raise InventoryError(f"Inventory file not found: {path}")

    try:
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        raise InventoryError(f"Failed to parse inventory YAML: {e}") from e

    if not isinstance(data, dict):
        raise InventoryError(
            f"Inventory file must contain a YAML mapping, got {type(data).__name__}"
        )

    try:
        return EntityInventory(**data)
    except Exception as e:
        raise InventoryError(f"Inventory validation error: {e}") from e


def discover_inventory(repo_path: str | Path) -> Path | None:
    """Check if a repository has an entity inventory file at its root.

    Args:
        repo_path: Path to the repository root.

    Returns:
        Path to the inventory file if found, None otherwise.
    """
    path = Path(repo_path) / INVENTORY_FILENAME
    if path.is_file():
        return path
    return None


# Heuristic patterns for entity type classification
_PROTOCOL_PATTERNS = [
    re.compile(r"(?i)checklist"),
    re.compile(r"(?i)protocol"),
    re.compile(r"(?i)template"),
    re.compile(r"(?i)workflow"),
    re.compile(r"(?i)procedure"),
]
_BACKLOG_PATTERN = re.compile(r"BL-\d+")


def _classify_entity_type(title: str) -> EntityType:
    """Classify an entity type based on heading title heuristics."""
    if _BACKLOG_PATTERN.search(title):
        return "backlog-item"
    for pattern in _PROTOCOL_PATTERNS:
        if pattern.search(title):
            return "protocol"
    return "section"


def export_inventory(
    documents: list[ParsedDocument],
    repo_name: str,
    repo_type: RepoType = "dsm-spoke",
    output_path: str | Path | None = None,
) -> EntityInventory:
    """Generate an entity inventory from parsed documents.

    Scans all numbered sections and classifies them by type using
    heuristics (protocol, backlog-item, or section).

    Args:
        documents: Parsed markdown documents.
        repo_name: Name for the repository in the inventory.
        repo_type: Repository type (dsm-hub, dsm-spoke, external).
        output_path: Optional path to write the YAML file.

    Returns:
        The generated EntityInventory.
    """
    entities: list[Entity] = []

    for doc in documents:
        for section in doc.sections:
            if section.number is None:
                continue

            heading = f"{section.number} {section.title}"
            entity_type = _classify_entity_type(section.title)
            entity_id = f"{doc.file}/section/{section.number}"

            entities.append(Entity(
                id=entity_id,
                type=entity_type,
                path=doc.file,
                heading=heading,
                level=section.level,
                stable=True,
            ))

    inventory = EntityInventory(
        version="1.0",
        repo=RepoInfo(name=repo_name, type=repo_type),
        entities=entities,
    )

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = inventory.model_dump(exclude_none=True)
        output_path.write_text(
            yaml.dump(data, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )

    return inventory