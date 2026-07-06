**Date Completed:** 2026-07-06
**Outcome Reference:** Consumed at session 53 start

# Handoff: TOON Migration Redesign Decision (Session 53)

**Created:** 2026-07-03 (Session 52)
**Branch:** sprint-17/toon-migration
**Blocks:** Sprint 17 completion (BL-302 Phase 1.5)
**Decision owner:** Alberto Diaz Durana

---

## Why this exists

Sprint 17's TOON migration was **halted** after capability experiment EXP-010
(Fable 5 independent assessment, Opus adjudication) ran the DEC-010 C3 validation
gate early and it **failed**: the implemented TOON schema is token-POSITIVE
(+1.74% on DSM Central, +7.58% on GE), not the −10% the gate requires. The full
finding set (14 findings, all adjudicated CONFIRMED) is in
`data/experiments/EXP-010-fable-repo-plan-assessment/`.

P1b (emitter + `--format` routing) is committed and the markdown path is
byte-identical to before, so nothing is broken. What is blocked is P2 (golden
freeze) and the default-flip, because the schema they would enshrine cannot pass
the gate.

## The decision to make (three forks)

- **(a) Fix-and-retry TOON.** Do the schema/emitter redesign (fix list below),
  re-run the honest paired gate, ship only if it clears −10%.
- **(b) Reopen DEC-010.** The token-negative result plus F8 (no experiment tests
  whether an agent navigates better/cheaper with the Intrinsic-ToC in *any*
  format) suggest the token metric may be the wrong gate. Reconsider whether TOON
  is worth it at all.
- **(c) Both, sequenced.** Run a cheap agent-navigation experiment first
  (no-ToC vs markdown-ToC vs TOON-ToC on fixed navigation tasks, measure task
  success / tool calls / tokens-to-answer), then decide (a) vs abandon.

Recommendation from EXP-010's top-3: lean toward **(c)** — it answers the
prerequisite question (does the format even matter to the consumer?) before
spending another sprint on format mechanics.

## Fix list (required before ANY TOON retry, from EXP-010 F1-F14)

1. **Schema de-duplication (F1, root cause):** drop the redundant `path` column in
   `hierarchy`/`directories` (reconstruct as dir+basename), reconsider title-vs-path
   per table. This is what makes TOON token-positive.
2. **Spec-conformant `_quote` (F2):** backslash escapes not CSV doubling, quote
   colons / numeric-like / empty / leading-`-` / whitespace-edge values. Fix
   `test_colon_does_not_trigger_quoting` (currently asserts the violation).
3. **Overflow totals (F4):** add `hotspots_total` / `orphans_total` to the
   `summary:` block (TOON currently drops them; 15-vs-110 orphan misreport).
4. **Deterministic tie-breaks (F10):** secondary sort key in `_hub_rows`/`_hotspot_rows`.
5. **Gate protocol (F3):** same corpus snapshot, same invocation (relative paths,
   recorded command), same day, paired. Retire the stale 9,309 baseline.
6. **Reference-decoder round-trip (F7):** pin the TOON reference impl dev-only
   (DEC-009 forbids LLM/NLP models, not a parser); strict-mode decode the golden.
7. **API guard (F14):** `raise ValueError` on unknown `fmt` instead of silent
   markdown fallthrough.

Lower priority / judgment: empty-array canonical form (F11), tab-delimiter header
marker (F12), line-number columns (F13), README re-frame + dogfood own ToC (F9).

## Also update when the decision lands

- BL-302 P0 schema sketch is stale (never updated to the two-table implementation) — F6.
- DEC-010 currently marked "implementation HALTED"; the S53 decision resolves it.

## Pointers

- Experiment: `data/experiments/EXP-010-fable-repo-plan-assessment/EXP-010.md` (§5 adjudication), `results.md` (findings)
- Plan: `dsm-docs/plans/BL-302-phase-1.5-toon-migration.md` ("Sprint 17 Course Correction")
- Decision: `dsm-docs/decisions/DEC-010-toon-migration-format.md` (Amendment)
- Emitter: `src/analysis/knowledge_summary.py`
