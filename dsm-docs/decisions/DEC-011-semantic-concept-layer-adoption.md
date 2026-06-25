# DEC-011: Adopt the Semantic Concept Layer (Layer 4.5)

**Status:** Accepted
**Date:** 2026-06-25
**Session:** S50
**Author:** Alberto Diaz Durana
**Related:** DEC-009 (no local LLM dependencies), BL-GE-001 (Semantic Concept Layer registration), research `2026-04-23_semantic-concept-layer.md`, Intrinsic-ToC Vision §4.5

---

## Context

The Intrinsic-ToC graph today has three node types, files, sections, and terms, connected by containment and cross-reference edges. BL-GE-001 (S49) registered a proposed fourth type, the **semantic concept**, an abstract object that recurs across files, sections, and repos but is not itself any one of them (examples: `DEC-009`, `Intrinsic-ToC`, `session baseline`).

The S49 research file explored the design space and identified two headline products:

1. **Discoverability**, answer "where is concept X defined, and everywhere it is used?" without grepping a string.
2. **Drift / contradiction detection**, surface when a concept's value disagrees across sites (the `dsm-version` example: `CHANGELOG.md` authoritative vs stale `.claude/last-align.txt` / `MEMORY.md`).

The research concluded with seven open questions (§9) and recommended a minimal-experiment-first path. This DEC resolves the adopt question and sets the scope of commitment.

## Decision

**Adopt the Semantic Concept Layer for Epoch 6**, using the structural / author-declared model (DEC-009-aligned), beginning with a minimal `dsm-version` drift-detection slice.

This is an **Option-A scope decision**: the DEC commits firmly to adoption, the DEC-009 boundary, and the first experiment. The remaining architectural choices from research §9 are recorded below as **non-binding leanings**, to be ratified in the Epoch 6 plan once the minimal slice has validated the model. The intent is to avoid fixing schema details before the experiment teaches us, the same over-commitment failure mode DEC-009 corrected.

### Architectural leanings (non-binding, §9)

| # | Question | Leaning (to be ratified post-slice) |
|---|----------|-------------------------------------|
| 1 | Concept identity | Declared-ID spine + canonical name + declared alias set; `used-in` edges attach via any alias |
| 2 | Declaration mechanism | Heading convention (`### Concept: X` reuses existing section parsing); revisit after the slice |
| 3 | Relationship to Layer 4 | Separate node type in a shared store (keeps purely methodological concepts first-class) |
| 4 | Storage | FalkorDB node label, or a manifest compiled into both graph and per-repo ToC blocks; final pick deferred |
| 5 | Edge set | Start with the three (`defined-in`, `used-in`, `depends-on`); evaluate `supersedes` / `contradicts` for drift later |
| 6 | Drift tolerance | Drift = "use-site value ≠ current authoritative value"; staleness tolerance set empirically by the experiment |
| 7 | First experiment | **`dsm-version` drift detection across this repo**, the one firm commitment (see C2) |

## Justification (strongest first)

1. **Drift detection has proven, immediate value.** This very session had to detect `dsm-version` drift by hand (last-align `v1.14.0` vs CHANGELOG `1.17.0`) before running `/dsm-align`. A concept node with `defined-in` / `used-in` edges and per-site values turns that manual check into a query. The need is demonstrated, not hypothetical.
2. **The research is methodologically earned** (DSM_0.2 §8.5). S49 completed a full design-space exploration, concept identity, declaration syntax, edge semantics, storage, Layer-4 relationship, drift mechanics, before this decision, with tentative positions and trade-offs on record.
3. **Stays inside DEC-009 by construction.** The automatic pipeline is purely structural (author-declared concepts, declared aliases, pattern-extracted values). Any inference (candidate concepts, candidate `depends-on` edges) is surfaced as a review-gated suggestion, never written automatically. The "agent IS the query engine" stance is preserved.
4. **Minimal-slice-first bounds the commitment.** Adopting the model now costs nothing to build yet; the `dsm-version` slice is the smallest end-to-end proof and gates broader investment. Deciding adopt unblocks Epoch 6 planning without locking schema choices prematurely.

## Counter-evidence considered (per DSM_0.2 §8.2.1)

| # | Counter-claim | Why it does not defeat the decision |
|---|---------------|-------------------------------------|
| 1 | This duplicates grep, the consuming agent can already find concepts by searching | grep matches strings, not identity. It cannot unify aliases ("Intrinsic-ToC" = "knowledge summary"), and it cannot compare a value across use-sites against an authoritative definition. Drift detection is a value-comparison query, not a text search. |
| 2 | YAGNI, defer until Epoch 6 anyway (S47 speculative-work lesson) | This DEC *is* the Epoch 6 gate; the research path was research → DEC → plan. Deciding adopt now records the commitment and unblocks planning. No code is built under this DEC, so there is no speculative build cost. |
| 3 | Concept identity is unsolved (synonyms, renames break identity) | Exactly why the declared-ID is the spine and undeclared-concept extraction stays review-gated. The minimal slice uses one unambiguous declared concept (`dsm-version`), so identity ambiguity is not on the critical path of the first experiment. |
| 4 | A fourth node type adds graph complexity for uncertain payoff | The payoff (drift detection) is concrete and recurring across the ecosystem; the complexity is gated behind C2/C4 so it only lands after the slice proves value. |

## Conditions on acceptance

- **C1. DEC-009 boundary holds.** The automatic extraction pipeline is purely structural. Any model inference is a review-gated suggestion surfaced for human accept/reject, never written to the graph automatically.
- **C2. Minimal slice first.** `dsm-version` drift detection (author-declared concept + use-site value comparison) ships and validates the model before any broader schema build.
- **C3. Leanings are non-binding.** The architectural positions in the leanings table are inputs to the Epoch 6 plan, not commitments. The plan ratifies or revises them after the slice.
- **C4. No production graph writes pre-review.** No new concept node type is written to the production knowledge graph until the minimal slice is reviewed and accepted.

## Consequences

### Positive
- Drift / contradiction detection becomes a graph query instead of a manual cross-file check.
- Discoverability: navigate from an idea to all its materializations across a repo or the ecosystem.
- Concepts become first-class, so a purely methodological concept (e.g., "Sprint Boundary Checklist") exists in the graph even with no code or single-file home.
- The minimal-slice gate means the model is validated cheaply before broader investment.

### Negative
- A fourth node type increases graph schema and rebuild complexity.
- Author-declared concepts impose declaration friction (a heading convention or manifest entry per concept).
- Alias / synonym identity remains a hard problem deferred past the first slice.

### Neutral
- Targets Epoch 6, not Epoch 5; does not touch the current knowledge-summary (BL-302) or TOON-migration (Sprint 17) work.
- Several schema decisions are intentionally left open (the leanings), so this DEC narrows the question rather than closing all of it.

## References

- Research file: `dsm-docs/research/2026-04-23_semantic-concept-layer.md` (design-space exploration; §9 open questions, §10 minimal-experiment recommendation).
- BL-GE-001: `dsm-docs/plans/BL-GE-001_semantic-concept-layer.md` (registration BL; acceptance criterion "DEC drafted once research concludes").
- DEC-009: `dsm-docs/decisions/DEC-009-no-local-llm-dependencies.md` (extraction-policy constraint).
- Intrinsic-ToC Vision: `dsm-docs/research/2026-04-13_intrinsic-toc-vision.md` §4.5 (Layer 4.5 architectural position).
