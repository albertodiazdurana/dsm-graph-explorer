# Sprint 17: BL-302 Phase 1.5 (TOON Migration)

**Duration:** 1-1.5 sessions (4-9 hours; BL-302 estimate with +50% validation buffer)
**Goal:** Migrate `--knowledge-summary` output to TOON behind a `--format` flag, validated by ≥10% measured token savings on the DSM Central corpus.
**Prerequisites:** Epoch 4 complete; [DEC-010](../decisions/DEC-010-toon-migration-format.md) accepted; BL-302 Phase 1 shipped (Sprint 16).

**Work item (all phase detail lives here, this plan is the sprint-level wrapper):**
[BL-302 Phase 1.5 — TOON Migration](BL-302-phase-1.5-toon-migration.md). See also
[epoch-5-plan.md](epoch-5-plan.md) §Sprint 17.

---

## Research Assessment

Scope is fully specified. Format research is done (Central BL-367, 6 formats measured
with tiktoken `cl100k_base`) and the decision is recorded ([DEC-010](../decisions/DEC-010-toon-migration-format.md)).
No unresolved unknowns that would make task estimates speculative. No Phase 0.5 deep-dive
needed before deliverables.

## Experiment Gate

**Performance-only sprint** (no new user-facing capability). This is a format refactor of
an existing capability (`--knowledge-summary`, shipped Sprint 16); the only new surface is a
`--format` flag. Experiment skip justified. The DEC-010 **C3 token measurement** (P3 below) is
the sprint's validation step, not a capability experiment.

## Branch Strategy

Level 3 branch `sprint-17/toon-migration` off the session branch (`session-51`). Merges back to
the session branch when all MUST deliverables are checked off. See DSM_0.2 Three-Level Branching.

---

## Deliverables

### MUST (sprint fails without these)
- [ ] `--format {markdown,toon}` flag on `--knowledge-summary`; `markdown` stays default (BL-302 P0-P1, DEC-010 C1).
- [ ] TOON emitter in `src/analysis/knowledge_summary.py` — shared `emit_table` helper across all 4 sections + `summary:` header (BL-302 P1).
- [ ] Test migration: 25 tests in `tests/test_knowledge_summary.py` adapted; `tests/fixtures/knowledge-summary.toon` golden file (BL-302 P2).
- [ ] C3 validation gate: run on DSM Central corpus, measure with tiktoken `cl100k_base`, ≥10% savings vs 9,309-token baseline (BL-302 P3, DEC-010 C3).
- [ ] Docs: CLI `--help`, README, `dsm-docs/guides/` (if a CLI guide exists) note the TOON format (DEC-010 C4).

### SHOULD (expected, defer if blocked)
- [ ] Coverage ≥ 91% (current baseline; no regression).

### COULD (stretch)
- _(none — `--format jsonl` (DEC-010 C2) and the default flip (BL-302 P4) are explicitly deferred out of this sprint.)_

---

## Phases

All phase detail (sub-tasks, schema specs, escape-handling notes) lives in
[BL-302 §Phases](BL-302-phase-1.5-toon-migration.md#phases). Summary map:

| Phase | Focus | Execution mode | Success criterion |
|---|---|---|---|
| P0: Schema design | Specify TOON schema per section + delimiter choice | document | Schema recorded in module docstring/comment |
| P1: Emitter | `emit_table` helper + 4 section generators routed by `--format` | code | TOON output structurally valid; markdown path intact |
| P2: Test migration | Parameterize tests over formats; add `.toon` golden file | code | 25 tests pass; TOON structural assertions pass |
| P3: Validation gate | Run on Central corpus, tiktoken measurement | script | ≥10% measured savings vs 9,309 baseline (else halt) |

---

## Phase Boundary Checklist (intra-sprint)
- [ ] Update methodology.md with phase observations and scores
- [ ] Create checkpoint if significant milestone reached
- [ ] Log decisions made during phase (dsm-docs/decisions/)
- [ ] Update blog materials if insights worth sharing

---

## Open Design Questions
1. **Emitter vs library:** hand-write the TOON emitter (GE is producer-only, no parser needed; avoids a young-ecosystem dependency per DEC-010 counter-claim #2) or pin a TOON reference implementation in `pyproject.toml`? Resolve at the implementation gate (BL-302 P0/P1).
2. **Delimiter choice:** comma vs tab vs pipe, evaluated against payload characteristics (paths, titles may contain commas → escape handling) (BL-302 P0).

---

## How to Resume
1. Read this sprint plan.
2. Read the most recent checkpoint in `dsm-docs/checkpoints/`.
3. Read [BL-302 Phase 1.5](BL-302-phase-1.5-toon-migration.md) for phase detail and acceptance criteria.
4. Read `src/analysis/knowledge_summary.py` (current markdown emitter, 286 lines) and `tests/test_knowledge_summary.py`.

---

## Sprint Boundary Checklist
- [ ] Checkpoint document created (dsm-docs/checkpoints/)
- [ ] Feedback files updated (backlogs, methodology)
- [ ] Decision log updated with sprint decisions
- [ ] Tests passing (DSM 4.0 projects)
- [ ] dsm-docs/guides/smoke-tests.md current (or N/A if no smoke tests recorded this sprint)
- [ ] Blog journal entry written
- [ ] Blog publication tracker updated (`dsm-docs/blog/README.md`)
- [ ] Repository README updated (status, results, structure)
- [ ] Next steps summary (3-5 sentences: next sprint goal, key deliverables, relevant plan reference)
