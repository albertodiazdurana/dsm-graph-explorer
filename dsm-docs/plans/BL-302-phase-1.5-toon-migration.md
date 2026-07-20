# BL-302 Phase 1.5: TOON Migration for Knowledge-Summary Output

**Status:** CLOSED — TOON **not adopted** (S53, 2026-07-06, per EXP-011). The Intrinsic-ToC is validated and kept in **markdown**. See "Resolution" below.
**Priority:** High
**Date Created:** 2026-04-20
**Origin:** DEC-010 (this project) + DSM Central BL-367 (format research) + GE S47 Q3
**Author:** Alberto Diaz Durana
**Target:** Sprint 17 (Epoch 5)
**Related:** [DEC-010](../decisions/DEC-010-toon-migration-format.md), BL-302 Phase 1 (Sprint 16, shipped), Phase 2 (Leiden clusters, Epoch 5)

---

## Sprint 17 Course Correction (2026-07-03, Session 52)

**P2 HALTED. The DEC-010 C3 validation gate was run early (per EXP-010) and FAILED.**

Independent capability experiment EXP-010 (Fable 5 assessment, Opus adjudication)
measured the implemented TOON schema with tiktoken `cl100k_base`:
- GE `dsm-docs/` corpus (relative paths): markdown 2,903 vs TOON 3,123 tokens, TOON **+7.58%**.
- Full DSM Central corpus (relative, same-day paired): markdown 6,952 vs TOON 7,073, TOON **+1.74%**.
- The gate requires **−10%** savings. The implemented schema is token-POSITIVE on every corpus measured.

**Root cause:** the implemented schema differs from the one BL-367 projected −14.6% for.
Two flat tables (`directories` + per-file `hierarchy`) repeat the directory in every
row and carry a `path` column that duplicates dir+basename, and `hub`/`orphans` carry
long node-id paths instead of short titles. TOON emits fewer characters but MORE tokens
(BPE: comma-adjacent long paths tokenize poorly).

**Required before any TOON retry (enumerated, not yet decided):**
1. Redesign the `hierarchy`/`directories` schema to remove path redundancy (drop `path`, reconstruct from dir+basename, reconsider title-vs-path per table).
2. Make `_quote` spec-conformant (backslash escapes, quote colons/numeric-like/empty/edge values). The current emitter is CSV-dialect, not spec-TOON, and two unit tests enshrine the violation.
3. Add orphan/hotspot overflow totals (TOON silently drops them, markdown reports "... and N more").
4. Add deterministic tie-breaks to the hub/hotspot sorts before any golden freeze.
5. Fix the P3 gate protocol: same corpus snapshot, same invocation (relative paths, recorded command), same day, paired. The frozen 9,309-token baseline is stale (corpus grew) and invocation-dependent.
6. Add a strict-mode reference-decoder round-trip test (pin the TOON reference implementation as a dev-only dependency).

**Direction deferred to Session 53**, three forks: (a) fix-and-retry TOON, (b) reopen
DEC-010 (the token metric may be the wrong gate, no experiment tests whether agents
navigate better with the Intrinsic-ToC at all), (c) run an agent-navigation experiment
first, then decide.

**Evidence:** `data/experiments/EXP-010-fable-repo-plan-assessment/` (EXP-010.md §5
adjudication table, results.md findings F1-F14).

### Resolution (2026-07-06, Session 53): fork (c) → TOON not adopted

Session 53 ran fork (c): **EXP-011** agent-navigation A/B
(`data/experiments/EXP-011-agent-navigation-toc/`), 24 fresh isolated subagents, 8
navigation tasks, three arms (no-ToC / markdown-ToC / TOON-ToC).

- **The Intrinsic-ToC helps navigation (H1):** ToC arms ~6× fewer tool calls
  (0.63 vs 3.75 mean) and higher accuracy (markdown 8/8, TOON 7/8 vs no-ToC 4/8).
  First direct evidence the ToC serves the north star (answers EXP-010 F8).
- **markdown strictly dominates the current TOON (H2):** identical answers/tool-calls
  on 7/8 tasks; TOON's only difference is answering the orphan-count task **wrong**
  (15 vs 112, the F4 loss) — while also costing more tokens (F1). No task favored TOON.

**Decision (confirmed by author): keep the ToC in markdown; do NOT adopt TOON.** The
6-item fix list above is **not pursued** — a fixed TOON's ceiling is a navigation tie
with markdown while still owing a token win it likely can't achieve. P2 (golden freeze)
and P4 (default flip) are **cancelled**. DEC-010 Amendment 2 records the same. The
`--format` flag / TOON emitter may stay as dev surface; markdown remains the default and
sole supported format.

---

## Post-Closure Correction (2026-07-21, Session 55): nesting premise refuted

**Status is unchanged, this BL stays CLOSED.** The correction below refutes one
*justification* inside a decision that was already abandoned on other grounds. It changes
nothing about Phase 1.5's outcome. It is recorded because the claim was load-bearing for
**Phase 2's** scope, where it survived Phase 1.5's closure and would have misdirected the
next sprint.

The third bullet under §Motivation reads:

> Phase 2 (Leiden clusters) requires native nesting; TOON handles this, incumbent does not.

**Both halves are false.** Both emitters were run against this repository in S55
(227 files, 2,585 sections, 133 cross-references):

- The markdown path (`generate_hierarchy`, `src/analysis/knowledge_summary.py:161-181`)
  already emits two-level nesting: a bold directory header, then indented per-file
  bullets, then an `... and N more` truncation line.
- The TOON path (`_generate_toon_summary`) **flattens** the same data into
  `directories[56]{path,files,sections,shown,more}` plus a second table repeating the
  path column.

So the incumbent does express nesting, and the implemented TOON expresses less of it.
Measured alongside: markdown 230 lines / 17,734 bytes, TOON 206 lines / 18,032 bytes,
fewer lines but more bytes, the same character-vs-token divergence that failed the
DEC-010 C3 gate in S52.

**Why it went unchallenged:** the claim was written as forward justification for a
migration, at a point when no TOON emitter existed to check it against. By the time one
did (S51 P1b), the claim had already done its work and nobody re-read it. It is the same
shape as the C3 gate deferral, a cheap falsifiable check postponed past the point where
its answer would have changed the plan.

The original bullet is left in place rather than rewritten, so the record of what was
believed at the time survives. Consequence is carried forward in
[BL-302 Phase 2](BL-302-phase-2-leiden-clustering.md) §Correction to the inherited
premise, and [epoch-5-plan.md](epoch-5-plan.md) §Sprint 18 is corrected to drop the TOON
dependency.

---

## Context

BL-302 Phase 1 (Sprint 16) shipped `--knowledge-summary` with a mixed markdown format (inline bold key:value, pipe bullets, GFM tables). DEC-010 accepts Central's BL-367 research recommendation to migrate that output to TOON. This BL tracks the migration itself as a prep step before Phase 2 (Leiden cluster output) so Phase 2 is not built on the incumbent format.

"Phase 1.5" naming signals the sequencing: between Phase 1 (shipped) and Phase 2 (future). It is not a separate feature, it is a format refactor of the existing feature.

## Motivation

- Measured **-14.6% token reduction** vs incumbent (tiktoken `cl100k_base`, ±3% projection margin).
- Parser effort drops 4/5 → 2/5 (four format paths collapse to one uniform schema).
- Phase 2 (Leiden clusters) requires native nesting; TOON handles this, incumbent does not.
  **[REFUTED S55, see §Post-Closure Correction above. Left in place as the historical record.]**
- Producer/consumer single-pair state (GE → Central) makes now the cheapest migration window.

Full justification and counter-evidence in [DEC-010](../decisions/DEC-010-toon-migration-format.md).

## Scope

### In scope
- `--format {markdown,toon}` flag on the `--knowledge-summary` CLI path. Default: `markdown` during transition.
- TOON emitter in `src/analysis/knowledge_summary.py` (replaces or parallels existing markdown emitter).
- Shared `emit_table(name, fields, rows)` helper across all four sections (hierarchy, hub, hotspots, orphans).
- TOON header emitter for the top-level `summary:` block.
- Test migration: 25 existing tests in `tests/test_knowledge_summary.py` adapted or split across format variants.
- Golden file: `tests/fixtures/knowledge-summary.toon`.
- Validation run on DSM Central corpus with tiktoken measurement.
- Documentation updates: CLI `--help` text, README entry, `dsm-docs/guides/` if a CLI guide exists.

### Out of scope
- `--format jsonl` (YAGNI: no concrete consumer ask yet; DEC-010 C2).
- Flipping the default to TOON (separate change after validation passes; see Phase P4).
- TOON support for any other GE CLI output (only `--knowledge-summary`).
- Phase 2 Leiden cluster output (tracked separately).

## Phases

### P0: Schema design
- Specify TOON schema for each section: `summary:`, `hierarchy[N]{path,files,sections,top_files}:`, `hub[N]{rank,file,incoming_refs,top_section}:`, `hotspots[N]{refs,file,section,title}:`, `orphans[N]{file,sections}:`.
- Confirm delimiter choice (comma vs tab vs pipe) against payload characteristics.
- Record schema in docstring or separate schema comment in the module.

### P1: Emitter implementation
- Add `emit_table(name, fields, rows)` helper.
- Rewrite each of the 4 section generators to support TOON output, routed by `--format`.
- Keep markdown emitters intact (behind same flag, default).

### P2: Test migration
- Parameterize existing tests over both formats where appropriate.
- Add TOON-specific structural assertions (header line present, cardinality declared, field names correct, row count matches).
- Add the `tests/fixtures/knowledge-summary.toon` golden file.

### P3: Validation gate (DEC-010 C3)
- Run `--format toon --knowledge-summary` on the full DSM Central corpus.
- Measure token count with tiktoken `cl100k_base`.
- Record measured savings vs the incumbent baseline (9,309 tokens).
- **Accept criterion:** ≥10% measured savings. If below, halt the migration and revisit the research assumptions.

### P4: Default flip (separate release)
- After P3 passes and at least one external consumer validates: change default to `toon`.
- Keep `--format markdown` available for at least one further minor release for rollback.
- Not part of this BL's completion criteria; tracked as a follow-up.

## Acceptance Criteria

- [ ] `--format {markdown,toon}` flag implemented; `markdown` remains the default on BL completion.
- [ ] TOON output produces structurally valid TOON for all four sections and the summary header.
- [ ] All 25 existing tests pass; new TOON-format assertions pass.
- [ ] Coverage ≥ 91% (current baseline; no regression).
- [ ] Validation run on DSM Central corpus shows ≥10% measured token savings vs the 9,309-token baseline (DEC-010 C3).
- [ ] CLI `--help`, README, and guides updated with a one-line TOON note (DEC-010 C4).
- [ ] `tests/fixtures/knowledge-summary.toon` golden file committed.

## Effort Estimate

Central's BL-367 estimate: 1 GE session (4-6 hours).

GE-adjusted estimate: **1-1.5 sessions** (4-9 hours). The +50% buffer covers:
- P3 validation gate (Central's estimate did not include a measurement step).
- TOON emitter edge cases not surfaced in the 12-record subset (e.g., values containing commas or quotes that require TOON escape handling).
- C4 documentation updates.

## Dependencies

- TOON Python reference implementation (stdlib-only if feasible; otherwise a pinned dependency added to `pyproject.toml`).
- `tiktoken` for the P3 validation measurement (already used by Central in BL-367; add to dev-deps if not present).
- No blocking dependencies on Central-side work.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Measured savings fall short of 10% (C3 gate fails) | Low | Research's ±3% projection margin is well below the 10% threshold. If we fail, revisit schema design (P0) before migrating further. |
| TOON parser library instability | Low-Medium | Pin version. GE is producer only; we control the emit side. |
| Test migration blows the session budget | Medium | P2 is the largest phase (25 tests + golden file). Budget half the session for it. |
| Downstream consumer breakage at default flip | N/A for this BL | Flip is P4, out of this BL's scope. |

## References

- [DEC-010](../decisions/DEC-010-toon-migration-format.md): decision and counter-evidence.
- Central research file: `~/dsm-agentic-ai-data-science-methodology/dsm-docs/research/2026-04-14_knowledge-summary-format.md`.
- Current implementation: `src/analysis/knowledge_summary.py` (286 lines).
- Current tests: `tests/test_knowledge_summary.py` (25 tests, 5 classes, 270 lines).
- TOON spec: https://github.com/toon-format/spec/blob/main/SPEC.md
