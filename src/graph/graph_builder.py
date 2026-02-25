"""Graph builder for DSM reference networks.

Constructs a NetworkX DiGraph from parsed documents and cross-references.

Node types:
    FILE:    one per parsed document (ID = file path)
    SECTION: one per numbered section (ID = file_path:section_number)

Edge types:
    CONTAINS:   FILE -> SECTION
    REFERENCES: SECTION -> SECTION (resolved cross-references)
"""

import os

import networkx as nx

from parser.cross_ref_extractor import CrossReference
from parser.markdown_parser import ParsedDocument, Section


def _find_enclosing_section(
    numbered_sections: list[Section], line: int
) -> Section | None:
    """Find the section that encloses a given line number.

    Walks backward through numbered sections to find the last one
    whose line is <= the target line. Returns None if the line
    precedes all sections.
    """
    for s in reversed(numbered_sections):
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
            if section.number:
                section_id = f"{file_id}:{section.number}"
                G.add_node(
                    section_id,
                    type="SECTION",
                    title=section.title,
                    number=section.number,
                    file=file_id,
                    line=section.line,
                    level=section.level,
                    context_excerpt=section.context_excerpt,
                )
                G.add_edge(file_id, section_id, type="CONTAINS")

    # Add REFERENCES edges
    for source_file, refs in references.items():
        doc = next((d for d in documents if d.file == source_file), None)
        if not doc:
            continue

        numbered_sections = [s for s in doc.sections if s.number]

        for ref in refs:
            enclosing = _find_enclosing_section(numbered_sections, ref.line)
            if not enclosing:
                continue

            source_id = f"{source_file}:{enclosing.number}"

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

    return G
