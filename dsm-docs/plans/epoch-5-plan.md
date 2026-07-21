# DSM Graph Explorer - Epoch 5 Plan

**Project Type:** Software Engineering (DSM 4.0 Track)
**Start Date:** 2026-06-25 (Sprint 17 kickoff; scoped 2026-04-20)
**Status:** IN PROGRESS (Sprint 17 closed, Sprint 18 planned)
**Prerequisite:** Epoch 4 Complete ([epoch-4-plan.md](done/epoch-4-plan.md)), see [epoch-4-retrospective.md](../checkpoints/epoch-4/epoch-4-retrospective.md)
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
  from Phase 2 cluster work.
- **Outcome (S53):** TOON not adopted, markdown retained. The dedicated-sprint
  structure worked as intended, the isolated C3 gate rejected the migration before
  Phase 2 was built on it.

### Sprint 18: BL-302 Phase 2 (Leiden Clustering)

- Graph scope exclusion prerequisite: `DEFAULT_EXCLUDES` so clustering runs on project
  content, not dependencies. Added S55 after `--knowledge-summary` was observed emitting
  16 of 57 directories from `.venv/` and `.pytest_cache/`
- Concept clusters from co-reference patterns (structural only, per DEC-009)
- Leiden algorithm via `networkx.community` or `leidenalg`
- Integrate into `--knowledge-summary` **markdown** output, using the nesting the existing
  `generate_hierarchy` emitter already produces
- EXP-012 cluster-quality gate, run before any fixture freeze
- Research: code-review-graph for implementation patterns
- Scope detail: [BL-302 Phase 2](BL-302-phase-2-leiden-clustering.md)
- Sprint plan: [epoch-5-sprint-18-plan.md](epoch-5-sprint-18-plan.md)
- Effort: 1.5-2 sessions (6-12 hours)

> **Corrected S55 (2026-07-21):** this entry previously read "TOON-native cluster nesting,
> enabled by Sprint 17". Sprint 17 closed without adopting TOON, and the underlying claim
> that the incumbent markdown cannot express nesting was refuted by measurement. Phase 2
> has no format prerequisite. See
> [BL-302 Phase 1.5 §Post-Closure Correction](BL-302-phase-1.5-toon-migration.md).

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

- [x] BL-302 Phase 1.5 **resolved** (Sprint 17). Superseded S55: the original
      criterion required the DEC-010 C3 gate to PASS (≥10% token savings). It was
      run in S52 and FAILED (+1.74% Central / +7.58% GE), TOON was not adopted,
      and the phase closed with markdown retained. The criterion is satisfied by
      the phase reaching a recorded resolution, not by the gate passing, a gate
      that correctly rejects its candidate is a successful gate. See
      [DEC-010](../decisions/DEC-010-toon-migration-format.md) Amendment 2.
- [ ] BL-302 Phase 2 delivered (concept clusters in knowledge summary,
      markdown output, structural only per DEC-009)
- [ ] EXP-001 reference graph validation complete (pass/fail against 286 edges)
- [ ] Cross-repo reference support in `--knowledge-summary`
- [ ] 3 new experiments (validation gates for each significant feature)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| ~~TOON ecosystem instability~~ | - | - | **Retired S55:** TOON not adopted (Sprint 17), no TOON dependency remains |
| ~~DEC-010 C3 validation gate fails~~ | - | - | **Materialized S52.** The gate failed (+1.74% Central / +7.58% GE vs required -10%) and the migration was abandoned. Rated Low likelihood / Medium impact; the likelihood estimate was wrong |
| Leiden clustering quality on sparse graphs | Medium | Medium | Start with EXP to validate; fall back to simpler approaches if quality is poor |
| FalkorDBLite maintainer silence continues | High | Low | Merge/don't-merge not under our control; publish blog regardless |

---

## Notes

- Scoped as of 2026-04-20 (Session 48). Sprint 17 plan file to be created
  at Sprint 17 kickoff with DSM_2.0.C §1 Template 8 sections (BL-378);
  not created at epoch-scoping time to avoid pre-kickoff drift.
- Sprint 17 restructured per DEC-010: TOON migration sequenced before Leiden
  clusters so Phase 2 builds on the new format. **Superseded S55:** TOON was not
  adopted and the premise that Phase 2 needed it was refuted by measurement.
  Sprint 18 depends on no format work. See
  [BL-302 Phase 1.5 §Post-Closure Correction](BL-302-phase-1.5-toon-migration.md).
- Sprint ordering may still shift based on ecosystem priorities surfaced by
  DSM Central or portfolio (see [DSM Central responses above](#centrals-responses-2026-04-14-s47-inbox-response)).
- Epoch 5 is expected to be 4 sprints; overflow (Sprint 21) only if scope expands.
