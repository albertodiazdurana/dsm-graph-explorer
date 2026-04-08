# DEC-008: Heading-Based Section Node IDs

**Date:** 2026-03-16
**Sprint:** 13
**Status:** ACCEPTED

## Context

EXP-007 revealed that GE's graph builder only created SECTION nodes for numbered
sections (`### 2.1 Title`), ignoring plain markdown headings (`## Title`). DSM_0.2
itself uses heading-based structure exclusively, producing 0 section nodes from a
2,625-line document.

## Decision

Heading-based sections use the ID format `{file_path}:h:{slug}` where slug is a
lowercase kebab-case version of the heading title. Numbered sections retain their
existing format `{file_path}:{number}`.

## Alternatives Considered

1. **Line-based ID** (`{file_path}:L{line}`): Unique but not readable or stable
   across edits. A heading moved one line changes its ID.

2. **Title-only ID** (`{file_path}:{title}`): Readable but titles can contain
   special characters that complicate graph queries.

3. **Heading-level prefix** (`{file_path}:h{level}:{slug}`): Encodes hierarchy
   in the ID, but level changes on restructuring would break IDs.

## Rationale

The `h:slug` format is readable, stable across minor edits (title stays the same),
and distinguishable from numbered IDs (the `h:` prefix). Slug generation strips
special characters and normalizes whitespace, producing clean IDs for graph queries.
Duplicate titles within a file are theoretically possible but rare in practice.

## Consequences

- All markdown headings now produce SECTION nodes in the graph
- Graph density increases for heading-heavy documents
- Existing numbered-section behavior is unchanged
- Cross-reference resolution by title matching is a natural next step (deferred)
