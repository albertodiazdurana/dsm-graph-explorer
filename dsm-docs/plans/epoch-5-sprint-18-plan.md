# Sprint 18: BL-302 Phase 2 (Leiden Clustering)

**Duration:** 1.5-2 sessions (6-12 hours; four phases, P1 small and well-bounded, P2 carrying the sprint's real uncertainty)
**Goal:** Emit structural concept clusters in `--knowledge-summary` markdown, computed by Leiden community detection over a reference graph scoped to project content, validated by a cluster-quality gate run before any fixture freeze.
**Prerequisites:** Sprint 17 closed ([BL-302 Phase 1.5](BL-302-phase-1.5-toon-migration.md), CLOSED, markdown retained per [DEC-010](../decisions/DEC-010-toon-migration-format.md) Amendment 2); BL-302 Phase 1 shipped (Sprint 16).

**Work item (all phase detail lives here, this plan is the sprint-level wrapper):**
[BL-302 Phase 2 — Leiden Clustering](BL-302-phase-2-leiden-clustering.md). See also
[epoch-5-plan.md](epoch-5-plan.md) §Sprint 18.

---

## Research Assessment

Scope is specified and the inherited premise has been corrected. The epoch-5 plan scoped
this sprint as depending on TOON-native nesting; that dependency was refuted in S55 by
running both emitters (see [BL-302 Phase 2 §Correction](BL-302-phase-2-leiden-clustering.md)).
Markdown already nests, so no format work precedes clustering.

One genuine unknown remains, flat partition vs multi-resolution hierarchy (Open Design
Question 1). It does not make task estimates speculative, it changes the shape of P3's
output, so it is resolved in-sprint against real clusters rather than by a Phase 0.5
deep-dive.

## Experiment Gate

**Experiment REQUIRED.** This differs from Sprint 17, and the difference is deliberate
rather than inherited. Sprint 17 was a performance-only format refactor of an existing
capability, so its experiment skip was justified. Sprint 18 adds **new user-facing
capability**: a cluster section that did not previously exist. Per DSM 4.0 Section 4,
tests establish correctness while capability experiments establish whether the capability
is real, and "does Leiden over this graph produce clusters that correspond to recognizable
project areas?" is a capability question that no unit test answers.

P4 is that experiment: **EXP-012 (cluster quality)**, next in sequence after EXP-011.
Run it early, before any golden-fixture freeze. Sprint 17 sequenced its C3 gate after a
freeze, and when the gate was finally run it failed, having nearly enshrined a schema that
could not ship. That ordering is not repeated here.

## Branch Strategy

Level 3 branch `sprint-18/leiden-clustering` off the session branch (`session-55`).
Merges back to the session branch when all MUST deliverables are checked off.
See DSM_0.2 Three-Level Branching.

---

## Deliverables

### MUST (sprint fails without these)
- [ ] `DEFAULT_EXCLUDES` merged with `config.exclude`, so `--knowledge-summary` emits zero `.venv/`, `site-packages/`, or `.pytest_cache/` directories (BL-302 P2 §P1).
- [ ] Explicit opt-out for callers that want dependency content included (BL-302 P2 §P1).
- [ ] Leiden community detection over the cleaned reference graph, seeded for reproducible output (BL-302 P2 §P2).
- [ ] Cluster section emitted in `--knowledge-summary` markdown, bounded with the existing `... and N more` truncation convention (BL-302 P2 §P3).
- [ ] EXP-012 cluster-quality gate run and recorded **before** any fixture freeze (BL-302 P2 §P4).
- [ ] Tests alongside each phase; existing suite stays green (701 passed / 1 skipped baseline).
- [ ] Docs: CLI `--help` and README note the cluster section and the default exclusions.

### SHOULD (expected, defer if blocked)
- [ ] Coverage ≥ 91% (current baseline; no regression).
- [ ] `dsm-docs/guides/config-reference.md` documents `DEFAULT_EXCLUDES` and the opt-out.

### COULD (stretch)
- [ ] Multi-resolution cluster hierarchy, only if Open Design Question 1 resolves toward hierarchy and P2/P3 land early.

---

## Phases

All phase detail (sub-tasks, design notes, acceptance criteria) lives in
[BL-302 Phase 2 §Phases](BL-302-phase-2-leiden-clustering.md#phases). Summary map:

| Phase | Focus | Execution mode | Success criterion |
|---|---|---|---|
| P1: Graph scope exclusion | `DEFAULT_EXCLUDES` constant merged with `config.exclude` + opt-out | code | Zero `.venv`/`site-packages`/`.pytest_cache` dirs in output; excluded count reported |
| P2: Leiden clustering | Community detection over the cleaned graph, seeded | code | Clusters computed reproducibly across runs at a fixed seed |
| P3: Cluster emission | Bounded markdown cluster section | code | Output nests like `generate_hierarchy`; bounded regardless of repo size |
| P4: Validation gate | EXP-012 cluster quality on a known-structure repo | experiment | Clusters map to recognizable project areas (else halt before freeze) |

---

## Phase Boundary Checklist (intra-sprint)
- [ ] Update methodology.md with phase observations and scores
- [ ] Create checkpoint if significant milestone reached
- [ ] Log decisions made during phase (dsm-docs/decisions/)
- [ ] Update blog materials if insights worth sharing

---

## Open Design Questions
1. **Flat partition vs multi-resolution hierarchy:** a flat partition is sufficient for a table of contents and is materially cheaper; the hierarchy is what "nesting" originally referred to in the retired TOON framing. Resolve at P2 against real output, not in advance (BL-302 P2 §P2).
2. **Library choice:** `leidenalg` (true Leiden, extra dependency) vs `networkx.community` (already present, Louvain-family). Weigh against DEC-009's no-new-required-dependencies posture; graph libraries stay optional extras either way (BL-302 P2 §P2).
3. **Exclusion of `.claude/`:** agent session transcripts (27 files here) are not project knowledge, but `.claude/CLAUDE.md` arguably is. Decide whether `DEFAULT_EXCLUDES` takes `.claude/transcripts/` specifically or `.claude/` wholesale (BL-302 P2 §P1).

---

## How to Resume
1. Read this sprint plan.
2. Read the most recent checkpoint in `dsm-docs/checkpoints/`.
3. Read [BL-302 Phase 2](BL-302-phase-2-leiden-clustering.md) for phase detail and acceptance criteria, especially §Correction to the inherited premise.
4. Read `src/analysis/knowledge_summary.py` (current emitters, 507 lines), `src/cli.py:56` (`_resolve_paths`) and `src/cli.py:842` (`filter_files` call), and `tests/test_knowledge_summary.py`.

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
