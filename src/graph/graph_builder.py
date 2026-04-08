"""Graph builder for DSM reference networks.

Constructs a NetworkX DiGraph from parsed documents and cross-references.

Node types:
    FILE:    one per parsed document (ID = file path)
    SECTION: one per section (ID = file_path:number or file_path:h:slug)

Edge types:
    CONTAINS:   FILE -> SECTION
    REFERENCES: SECTION -> SECTION (resolved cross-references)
"""

import os
import re

import networkx as nx

from parser.cross_ref_extractor import CrossReference
from parser.markdown_parser import ParsedDocument, Section


def _slugify(title: str) -> str:
    """Convert a heading title to a URL-friendly slug.

    Examples:
        "Session Transcript Protocol" -> "session-transcript-protocol"
        "Gate 1: Concept Approval" -> "gate-1-concept-approval"
    """
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug


def _section_id(file_id: str, section: Section) -> str:
    """Generate a unique node ID for a section.

    Numbered sections: file_path:number (e.g., "dsm-docs/DSM.md:2.1")
    Heading sections:  file_path:h:slug (e.g., "dsm-docs/DSM.md:h:inclusive-language")
    """
    if section.number:
        return f"{file_id}:{section.number}"
    return f"{file_id}:h:{_slugify(section.title)}"


def _find_enclosing_section(
    sections: list[Section], line: int
) -> Section | None:
    """Find the section that encloses a given line number.

    Walks backward through sections to find the last one
    whose line is <= the target line. Returns None if the line
    precedes all sections.
    """
    for s in reversed(sections):
        if s.line <= line:
            return s
    return None


def build_reference_graph(
    documents: list[ParsedDocument],
    references: dict[str, list[CrossReference]],
    section_lookup: dict[str, Section],
) -> nx.DiGraph:
    """Build a reference network graph from parsed documents.

    Args:
        documents: Parsed markdown documents with sections.
        references: Cross-references keyed by source file path.
        section_lookup: Mapping of section numbers to Section objects
            (from build_section_lookup).

    Returns:
        A NetworkX DiGraph with FILE and SECTION nodes connected by
        CONTAINS and REFERENCES edges.
    """
    G = nx.DiGraph()

    # Add FILE and SECTION nodes
    for doc in documents:
        file_id = doc.file
        G.add_node(file_id, type="FILE", title=os.path.basename(doc.file))

        for section in doc.sections:
            sid = _section_id(file_id, section)
            G.add_node(
                sid,
                type="SECTION",
                title=section.title,
                number=section.number,
                file=file_id,
                line=section.line,
                level=section.level,
                context_excerpt=section.context_excerpt,
            )
            G.add_edge(file_id, sid, type="CONTAINS")

    # Add REFERENCES edges
    for source_file, refs in references.items():
        doc = next((d for d in documents if d.file == source_file), None)
        if not doc:
            continue

        all_sections = list(doc.sections)

        for ref in refs:
            enclosing = _find_enclosing_section(all_sections, ref.line)
            if not enclosing:
                continue

            source_id = _section_id(source_file, enclosing)

            # Resolve the reference target
            if ref.type == "section" and ref.target in section_lookup:
                target_section = section_lookup[ref.target]
                for d in documents:
                    if any(
                        s.number == target_section.number for s in d.sections
                    ):
                        target_id = f"{d.file}:{target_section.number}"
                        if G.has_node(source_id) and G.has_node(target_id):
                            G.add_edge(
                                source_id,
                                target_id,
                                type="REFERENCES",
                                line=ref.line,
                                ref_type=ref.type,
                            )
                        break

            elif ref.type == "heading":
                target_slug = _slugify(ref.target)
                for node_id, data in G.nodes(data=True):
                    if (
                        data.get("type") == "SECTION"
                        and data.get("number") is None
                        and _slugify(data.get("title", "")) == target_slug
                    ):
                        if G.has_node(source_id):
                            G.add_edge(
                                source_id,
                                node_id,
                                type="REFERENCES",
                                line=ref.line,
                                ref_type=ref.type,
                            )

    return G
