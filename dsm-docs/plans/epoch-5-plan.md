# DSM Graph Explorer - Epoch 5 Plan

**Project Type:** Software Engineering (DSM 4.0 Track)
**Start Date:** TBD (scoped 2026-04-20, Sprint 17 kickoff pending)
**Status:** PLANNING (SCOPED)
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

### Central's Responses (2026-04-14, S47 inbox response)

All four S47 open questions answered (see
`_inbox/done/2026-04-14_dsm-central_s47-findings-response.md`):

1. **Q1 (253-line size):** Acceptable as-is; no hard line-count cap. If
   reduction is needed later, target per-dir density rather than dir count.
2. **Q2 (hierarchy cap):** Don't cap for Central; keep `--cap-dirs N` as
   opt-in for larger corpora (portfolio spokes >2,000 files).
3. **Q3 (entry format):** **Migrate to TOON** (research-backed, ~14.6%
   measured token reduction). Tracked in
   [DEC-010](../decisions/DEC-010-toon-migration-format.md) +
   [BL-302 Phase 1.5](BL-302-phase-1.5-toon-migration.md).
4. **Q4 (regeneration cadence):** On-demand (current default) stays.
   Not session-start, not commit-triggered.

### Conceptual Anchors

- **Intrinsic-ToC vision** (`dsm-docs/research/2026-04-13_intrinsic-toc-vision.md`)
  guides all graph-summary work.
- **DEC-009** (no local LLM) defines the constraint envelope.

---

## Scope

### Sprint 17: BL-302 Phase 1.5 (TOON Migration)

- `--format {markdown,toon}` flag on `--knowledge-summary`
- TOON emitter replaces four-format markdown path (shared `emit_table` helper)
- 25-test migration + TOON golden file
- DEC-010 C3 validation gate: measured ≥10% token savings on DSM Central corpus
- Documentation updates (CLI help, README, guides)
- Scope detail: [BL-302 Phase 1.5](BL-302-phase-1.5-toon-migration.md)
- Effort: 1-1.5 sessions (4-9 hours)
- Rationale for dedicated sprint: isolates the format migration + validation gate
  from Phase 2 cluster work, so Leiden builds on TOON rather than on incumbent.

### Sprint 18: BL-302 Phase 2 (Leiden Clustering)

- Concept clusters from co-reference patterns
- Leiden algorithm via `networkx.community` or `leidenalg`
- Integrate into `--knowledge-summary` output (TOON-native cluster nesting,
  enabled by Sprint 17)
- Research: code-review-graph for implementation patterns

### Sprint 19: Hop Distance + EXP-001 Validation

- Hop distance from entry point in `--graph-stats`
- Validate GE parser output against EXP-001's 286-edge reference graph
- Two-tier threshold model (core ≤3 hops, modules ≤1 hop)

### Sprint 20: Ecosystem Graph Foundations (Avatar Layer 3)

- Cross-repo references materialized in Intrinsic-ToC entries
- Ecosystem-level graph connecting spoke ToCs
- Persistence strategy decision (FalkorDB vs linked markdown)

### Overflow (Sprint 21 if Epoch 5 extends)

Options:
- BL-302 Phase 3 (project-type navigation)
- Code ontology parsing (Layer 4 entry)
- Web visualization (pyvis)
- Epoch 5 close-out if scope is satisfied

---

## Success Criteria

- [ ] BL-302 Phase 1.5 (TOON migration) delivered; DEC-010 C3 validation
      gate passed (≥10% measured token savings on DSM Central corpus)
- [ ] BL-302 Phase 2 delivered (concept clusters in knowledge summary,
      TOON-native nesting)
- [ ] EXP-001 reference graph validation complete (pass/fail against 286 edges)
- [ ] Cross-repo reference support in `--knowledge-summary`
- [ ] 3 new experiments (validation gates for each significant feature)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| TOON ecosystem instability (spec drift, parser bugs) | Low | Low | Pin parser version; GE is the sole producer, regenerate on demand if spec changes (DEC-010 §Counter-evidence #2) |
| DEC-010 C3 validation gate fails (<10% measured savings) | Low | Medium | Revisit schema design (BL-302 Phase 1.5 P0); research's ±3% margin is well below the 10% threshold |
| Leiden clustering quality on sparse graphs | Medium | Medium | Start with EXP to validate; fall back to simpler approaches if quality is poor |
| FalkorDBLite maintainer silence continues | High | Low | Merge/don't-merge not under our control; publish blog regardless |

---

## Notes

- Scoped as of 2026-04-20 (Session 48). Sprint 17 plan file to be created
  at Sprint 17 kickoff with DSM_2.0.C §1 Template 8 sections (BL-378);
  not created at epoch-scoping time to avoid pre-kickoff drift.
- Sprint 17 restructured per DEC-010: TOON migration sequenced before
  Leiden clusters so Phase 2 builds on the new format.
- Sprint ordering may still shift based on ecosystem priorities surfaced by
  DSM Central or portfolio (see [DSM Central responses above](#centrals-responses-2026-04-14-s47-inbox-response)).
- Epoch 5 is expected to be 4 sprints; overflow (Sprint 21) only if scope expands.
