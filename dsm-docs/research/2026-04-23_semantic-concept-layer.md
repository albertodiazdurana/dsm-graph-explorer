# Semantic Concept Layer (Layer 4.5): Design-Space Research

**Date:** 2026-04-23
**Session:** 49
**Author:** Alberto Diaz Durana (with AI assistance)
**Status:** Active research
**Purpose:** Explore the design space for the Semantic Concept Layer (Layer 4.5) ahead of a decision
**Target Outcome:** A DEC deciding whether and how to adopt concept nodes in the knowledge graph
**Related:** [BL-GE-001](../plans/BL-GE-001_semantic-concept-layer.md), [Intrinsic-ToC Vision §4.5](2026-04-13_intrinsic-toc-vision.md), [DEC-009](../decisions/DEC-009-no-local-llm-dependencies.md)

---

## 1. Purpose and Scope

This file explores the design space for the Semantic Concept Layer registered in BL-GE-001. It is **input to a future DEC**, not an actionable plan: it surfaces the questions, options, and trade-offs, but commits to nothing. The path is research (this file) → DEC → Epoch 6 plan update if adopted.

**In scope:** what a concept node is, how concepts are identified and declared, edge semantics, storage, relationship to Layer 4, drift-detection mechanics, and the DEC-009 boundary.

**Out of scope:** implementation, schema finalization, CLI surface, and any commitment to build. Those follow a DEC.

## 2. The Concept Node

A **concept** is an abstract object, an idea that recurs across files, sections, and repos but is not itself any one of them. Examples from this ecosystem: `DEC-009`, `Intrinsic-ToC`, `session baseline`, `Sprint Boundary Checklist`.

The hard problem is **identity**: what makes two mentions "the same concept"?

| Identity option | Pro | Con |
|---|---|---|
| Declared ID (e.g., `DEC-009`) | Unambiguous, stable, author-controlled | Requires every concept to be explicitly declared; informal concepts have no ID |
| Canonical name (string) | Natural, no extra ceremony | Naming collisions; rename breaks identity |
| Slug (normalized name) | Tolerant of casing/spacing variants | Still breaks on synonyms ("knowledge summary" vs "Intrinsic-ToC") |

**Aliases** are the crux: "Intrinsic-ToC", "knowledge summary", and "the ToC" may all denote one concept. A workable model is a concept node with one canonical ID plus a declared alias set, so `used-in` edges can attach via any alias.

**Tentative position:** declared ID is the spine (DEC-009-aligned, structural); canonical name + alias set are attributes of the node. Extraction of *undeclared* concepts is a separate, review-gated path (§8).

## 3. Edge Semantics

Three proposed edge types, needing precise definitions to be machine-derivable:

- **`defined-in`** (concept → file/section): the *authoritative* definition. Exactly one per concept in the simple case; multiple only when a concept is legitimately co-defined. Distinguishing "definition" from "mention" is the key parsing challenge, likely needs an explicit author marker (a definition anchor), not inference.
- **`used-in`** (concept → file/section): any reference that is not the definition. Cardinality: many. Derivable structurally if concepts carry declared IDs/aliases to match against.
- **`depends-on`** (concept → concept): a conceptual build-on relationship (DEC-010 depends-on DEC-009). Author-declared; not inferable structurally without a declaration.

Open: is `depends-on` directional only, or do we also want `contradicts` / `supersedes` edges (a DEC superseding another)? Drift detection (§7) may want `supersedes`.

## 4. Declaration Syntax

Author-declared is the default (§8), so the friction of declaring matters. Candidate mechanisms:

| Mechanism | Example | Friction | Parse cost |
|---|---|---|---|
| Inline marker | `{{concept:dsm-version}}` at definition site | Medium (edits prose) | Low |
| Frontmatter block | `concepts: [{id, defines, aliases}]` per file | Low-medium (one block/file) | Low |
| Concept manifest | central `concepts.yaml` listing all concepts + anchors | Low per-concept, high central upkeep | Lowest |
| Heading convention | a `### Concept: X` section IS the definition | Very low (reuses existing structure) | Medium (heading scan) |

**Trade-off:** inline markers co-locate declaration with content (least drift between code and concept) but pollute prose; a manifest centralizes but can drift from the files it points at. A heading convention is attractive because it reuses the structure the graph already parses (sections are already nodes).

## 5. Relationship to Layer 4 (Code Ontologies)

Two framings:

1. **Separate layers, shared store.** Layer 4 (code AST nodes) and Layer 4.5 (concept nodes) are distinct node types in one ontology graph. A code symbol can carry a `defines` edge to a concept (e.g., a `KnowledgeSummary` class defines the `Intrinsic-ToC` concept). This is the richer model.
2. **4.5 as a projection of 4.** Concepts are a view over code+doc structure, not their own store. Simpler, but loses author-declared concepts that have no code/doc anchor.

**Tentative position:** separate node type, shared store (framing 1). It keeps concepts first-class (so a purely methodological concept like "Sprint Boundary Checklist" exists even with no code), while allowing code/doc nodes to link into the concept graph. The DEC should decide.

## 6. Storage Options

| Option | Pro | Con |
|---|---|---|
| Same FalkorDB graph (new node label) | One store, edges across types are free | Couples concept lifecycle to graph rebuilds |
| Separate concept manifest (YAML/JSON) | Human-editable, version-controlled, diff-able | Cross-store joins are manual; risk of drift from graph |
| Linked Intrinsic-ToCs (per-repo concept blocks) | Fits the ecosystem/avatar model; cross-repo by construction | No central query; assembly cost at read time |

The choice interacts with §5: framing 1 (shared store) pushes toward the FalkorDB option; the avatar/ecosystem vision (Layer 3) pushes toward linked per-repo concept blocks. These are not exclusive, the manifest could be the authored source that compiles into both the graph and the per-repo ToC blocks.

## 7. Drift / Contradiction Detection Mechanics

This is the second headline product and the one with the clearest immediate value.

**Worked example, `dsm-version`:** the concept `dsm-version` has `defined-in` → `CHANGELOG.md` (authoritative) and `used-in` → `.claude/last-align.txt`, `MEMORY.md`, per-spoke alignment markers. Each use-site carries an observed value. A drift check compares observed values against the authoritative definition:

- `CHANGELOG.md` = `1.14.0` (authoritative)
- `.claude/last-align.txt` = `v1.6.0` (stale → **drift flagged**)
- `MEMORY.md` = `v1.6.0` (stale → **drift flagged**)

This is exactly the condition this very session had to detect by hand. A concept node makes it a query.

**What counts as drift vs intentional change?** A version bump is intentional at the authoritative site and *expected* to propagate; drift is when use-sites lag the definition. So drift = "use-site value ≠ current authoritative value" with a staleness tolerance. A `supersedes` edge (§3) could distinguish "intentionally replaced" from "accidentally inconsistent".

**Mechanism:** structural comparison of declared values at definition vs use sites. No inference required if values are declared/extractable by pattern, fully DEC-009-compatible.

## 8. DEC-009 Boundary

[DEC-009](../decisions/DEC-009-no-local-llm-dependencies.md): no local LLM dependencies; GE does structural analysis, the consuming agent is the LLM.

The Semantic Concept Layer stays inside this boundary by construction:

- **Default path is structural:** author-declared concepts, declared aliases, pattern-extracted values. No model inference anywhere in the automatic pipeline.
- **Inference is review-gated only:** if a future tool proposes candidate concepts or candidate `depends-on` edges (by any method, including an external LLM the *user* runs), those are surfaced as suggestions for a human to accept/reject. Nothing inferred is written automatically.

This preserves the "agent IS the query engine" stance: GE materializes structural concept facts; any LLM reasoning over them happens in the consuming agent, not in GE.

## 9. Open Questions for the DEC

1. Concept identity model: declared-ID spine + alias set, or something lighter?
2. Declaration mechanism: inline marker, frontmatter, manifest, or heading convention (§4)?
3. Layer 4 relationship: separate node type in a shared store, or projection (§5)?
4. Storage: FalkorDB label, manifest, linked ToC blocks, or compiled-from-manifest (§6)?
5. Edge set: just the three, or add `supersedes` / `contradicts` for drift (§3, §7)?
6. Drift staleness tolerance: how stale is "drift" vs "in-flight propagation" (§7)?
7. Scope of first experiment: drift detection on `dsm-version` across this repo, as the minimal proof?

## 10. Next Actions

- Draft a DEC resolving the §9 questions (downstream of this research).
- If adopted, note Semantic Concept Layer scoping for Epoch 6 (not Epoch 5).
- Candidate minimal experiment: implement `dsm-version` drift detection (§7) as the smallest end-to-end slice, author-declared concept + use-site value comparison, to validate the model before broader investment.
