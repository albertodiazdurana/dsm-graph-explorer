# DSM Graph Explorer - Epoch 5 Plan (DRAFT)

**Project Type:** Software Engineering (DSM 4.0 Track)
**Start Date:** TBD (awaiting DSM Central responses to Epoch 4 findings)
**Status:** DRAFT / PLANNING
**Prerequisite:** Epoch 4 Complete ([epoch-4-plan.md](epoch-4-plan.md)), see [epoch-4-retrospective.md](../checkpoints/epoch-4/epoch-4-retrospective.md)
**Project Lead:** Alberto Diaz Durana (with AI assistance)

---

## Inputs from Epoch 4

### Deferred Requirements (5 themes, from epoch-4-plan.md §Deferred)

- **Theme A:** Intrinsic-ToC evolution (BL-302 Phase 2-3, metadata, lint, parseable format)
- **Theme B:** Ecosystem graph / Avatar (Layers 3-4 of vision, code ontologies, MCP)
- **Theme C:** Graph infrastructure (hop distance, EXP-001 validation, visualization)
- **Theme D:** Open source contribution pipeline (FalkorDB PR, blog)
- **Theme E:** Parser extensions (section renames, TF-IDF pre-filter)

### Open Questions for DSM Central (from S47 findings notification)

1. Is 253 lines acceptable for agent consumption?
2. Should the hierarchy cap directories?
3. Does the `key: value` entry format work?
4. What's the regeneration cadence?

**Epoch 5 scoping is blocked on these answers.** Partial progress is
possible on Themes C (graph infrastructure) and D (open source) which
do not depend on Central's answers.

### Conceptual Anchors

- **Intrinsic-ToC vision** (`dsm-docs/research/2026-04-13_intrinsic-toc-vision.md`)
  guides all graph-summary work.
- **DEC-009** (no local LLM) defines the constraint envelope.

---

## Tentative Scope (subject to Central's responses)

### Sprint 17: BL-302 Phase 2 (Leiden Clustering)

- Concept clusters from co-reference patterns
- Leiden algorithm via `networkx.community` or `leidenalg`
- Integrate into `--knowledge-summary` output
- Research: code-review-graph for implementation patterns

### Sprint 18: Hop Distance + EXP-001 Validation

- Hop distance from entry point in `--graph-stats`
- Validate GE parser output against EXP-001's 286-edge reference graph
- Two-tier threshold model (core ≤3 hops, modules ≤1 hop)

### Sprint 19: Ecosystem Graph Foundations (Avatar Layer 3)

- Cross-repo references materialized in Intrinsic-ToC entries
- Ecosystem-level graph connecting spoke ToCs
- Persistence strategy decision (FalkorDB vs linked markdown)

### Sprint 20: TBD

Options:
- BL-302 Phase 3 (project-type navigation)
- Code ontology parsing (Layer 4 entry)
- Web visualization (pyvis)
- Epoch 5 close-out if scope is satisfied

---

## Success Criteria (draft)

- [ ] BL-302 Phase 2 delivered (concept clusters in knowledge summary)
- [ ] EXP-001 reference graph validation complete (pass/fail against 286 edges)
- [ ] Cross-repo reference support in `--knowledge-summary`
- [ ] DSM Central's 4 open questions answered and reflected in the design
- [ ] 3 new experiments (validation gates for each significant feature)

---

## Risk Assessment (draft)

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Central non-response to S47 findings | Medium | High | Start with unblocked themes (C, D); revisit blocking themes when responses arrive |
| Leiden clustering quality on sparse graphs | Medium | Medium | Start with EXP to validate; fall back to simpler approaches if quality is poor |
| FalkorDBLite maintainer silence continues | High | Low | Merge/don't-merge not under our control; publish blog regardless |

---

## Notes

- This plan is a DRAFT. Formalize at Epoch 5 start (after Central responses).
- Sprint ordering may change based on ecosystem priorities surfaced by
  DSM Central or portfolio.
- Epoch 5 may be shorter than Epoch 4 if scope is tightly defined by
  Central's responses (e.g., if only Phase 2 is prioritized, Epoch 5
  could be 2-3 sprints instead of 4).
