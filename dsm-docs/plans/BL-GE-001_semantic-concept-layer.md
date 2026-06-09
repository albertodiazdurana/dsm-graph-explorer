# BL-GE-001: Semantic Concept Layer (Layer 4.5)

**Status:** Proposed
**Priority:** Medium
**Date Created:** 2026-04-23
**Origin:** GE S49 (user proposal, 2026-04-23)
**Author:** Alberto Diaz Durana
**Target:** Research-gated → DEC → Epoch 6 plan (not in Epoch 5 sprint scope)
**Related:** [Intrinsic-ToC Vision §4.5](../research/2026-04-13_intrinsic-toc-vision.md), [DEC-009](../decisions/DEC-009-no-local-llm-dependencies.md), future research file (`2026-04-23_semantic-concept-layer.md`), future DEC

---

## Context

The Intrinsic-ToC vision (Layers 1-4) maps a repository's **structural** graph: files, sections, headings, cross-references, and (future) code ASTs. The graph today has three node types, files, sections, and terms, connected by cross-reference and containment edges.

This BL registers a proposed **fourth node type: semantic concepts**, abstract objects that exist independent of where they are written. A concept like "DEC-009" or "Intrinsic-ToC" or "session baseline" is not a file or a section; it is an idea that appears across many files, sections, and repos. The Semantic Concept Layer makes those ideas first-class graph nodes.

It is registered as **Layer 4.5**, a sister to Layer 4 (Code Ontologies). Layer 4 extracts structure from code; Layer 4.5 extracts structure from *meaning*. Both sit above the document-structure layers (1-3).

This is a registration BL: it gates a research file and a downstream DEC, not an implementation sprint. No code is written under this BL directly.

## Motivation

Two headline products justify the layer:

### (a) Discoverability

Answer "where is concept X defined, and everywhere it is used?" across a repo or the whole ecosystem, without grepping for a string. A concept node links to every file/section that defines or references it, so an agent can navigate from an idea to all its materializations directly.

### (b) Drift and contradiction detection

Surface when a concept is defined inconsistently, or when its meaning has drifted over time. Worked example, **`dsm-version`**: the DSM version string appears in `CHANGELOG.md`, `.claude/last-align.txt`, `MEMORY.md`, and per-spoke alignment markers. When these disagree (last-align says `v1.6.0` while CHANGELOG says `v1.14.0`), that is concept drift. A Semantic Concept Layer would represent `dsm-version` as one node with multiple `defined-in` edges and flag the value mismatch automatically, instead of relying on a human to notice.

## Architectural Position

- **Layer 4.5**, between Layer 4 (Code Ontologies) and the document layers. Sister to Layer 4: both are "above structure" ontology layers, one for code, one for concepts.
- Adds a **concept** node type to the existing three (files, sections, terms).
- Proposed edge types:
  - `defined-in` — concept → the file/section that authoritatively defines it
  - `used-in` — concept → files/sections that reference it
  - `depends-on` — concept → other concepts it builds on (e.g., DEC-010 `depends-on` DEC-009)

## Extraction Policy (DEC-009 alignment)

[DEC-009](../decisions/DEC-009-no-local-llm-dependencies.md) forbids local LLM dependencies; GE's value is structural analysis, the consuming agent is the LLM. The Semantic Concept Layer respects this:

- **Author-declared concepts are the default and primary mechanism.** Concepts are registered explicitly (e.g., a lightweight declaration syntax in markdown, or a concept manifest), parsed structurally. No model inference, fully DEC-009-compliant.
- **Extracted concepts are allowed only as author-review-gated suggestions, never automatic.** If a future tool proposes candidate concepts (via any inference method), they are surfaced as suggestions for a human to accept or reject, never written into the graph automatically. This keeps the automatic path purely structural.

## Deliverables

1. **Vision amendment** (Step B): a Layer 4.5 section added to `2026-04-13_intrinsic-toc-vision.md` §4.
2. **Research file** (Step C): `dsm-docs/research/2026-04-23_semantic-concept-layer.md`, exploring the design space (concept identity, declaration syntax, edge semantics, storage, relationship to Layer 4, drift-detection mechanics).
3. **Downstream** (not in this BL): a DEC after the research concludes, then an Epoch 6 plan update if adopted.

## Dependencies

- **DEC-009** (constraint): bounds the extraction policy to structural / author-declared.
- **Layer 4 (Code Ontologies)**: sister layer; shares the "ontology above structure" framing and may share storage.
- **BL-302** (graph infrastructure): the concept layer extends the same graph the knowledge-summary work builds on.

## Open Questions

1. **Concept identity:** what uniquely identifies a concept, a declared ID, a canonical name, a slug? How are aliases handled (e.g., "Intrinsic-ToC" vs "knowledge summary")?
2. **Relationship to Layer 4:** is Layer 4.5 truly separate, or a projection of the same ontology store with a different node type? Does code-derived structure feed concept nodes?
3. **Declaration syntax:** how does an author declare a concept and its `defined-in` anchor with minimal friction?
4. **Storage:** does the concept layer live in the same FalkorDB graph, a separate concept manifest, or linked Intrinsic-ToCs?
5. **Drift mechanics:** what exactly constitutes "drift" for a concept, and how is a contradiction distinguished from an intentional version bump?

## References

- [Intrinsic-ToC Vision](../research/2026-04-13_intrinsic-toc-vision.md) §4 (Architecture Layers), to be amended with §4.5.
- [DEC-009](../decisions/DEC-009-no-local-llm-dependencies.md): no local LLM dependencies (extraction-policy constraint).

## Acceptance Criteria

- [ ] Layer 4.5 section added to the Intrinsic-ToC vision file (Step B).
- [ ] Research file `2026-04-23_semantic-concept-layer.md` created with the design-space exploration (Step C).
- [ ] `plans/README.md` documents the `BL-GE-{NNN}` naming convention (Step D).
- [ ] A DEC is drafted once research concludes (downstream, separate work item).
