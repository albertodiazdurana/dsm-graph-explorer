# BL-302 Phase 1.5: TOON Migration for Knowledge-Summary Output

**Status:** Open
**Priority:** High
**Date Created:** 2026-04-20
**Origin:** DEC-010 (this project) + DSM Central BL-367 (format research) + GE S47 Q3
**Author:** Alberto Diaz Durana
**Target:** Sprint 17 (Epoch 5)
**Related:** [DEC-010](../decisions/DEC-010-toon-migration-format.md), BL-302 Phase 1 (Sprint 16, shipped), Phase 2 (Leiden clusters, Epoch 5)

---

## Context

BL-302 Phase 1 (Sprint 16) shipped `--knowledge-summary` with a mixed markdown format (inline bold key:value, pipe bullets, GFM tables). DEC-010 accepts Central's BL-367 research recommendation to migrate that output to TOON. This BL tracks the migration itself as a prep step before Phase 2 (Leiden cluster output) so Phase 2 is not built on the incumbent format.

"Phase 1.5" naming signals the sequencing: between Phase 1 (shipped) and Phase 2 (future). It is not a separate feature, it is a format refactor of the existing feature.

## Motivation

- Measured **-14.6% token reduction** vs incumbent (tiktoken `cl100k_base`, ±3% projection margin).
- Parser effort drops 4/5 → 2/5 (four format paths collapse to one uniform schema).
- Phase 2 (Leiden clusters) requires native nesting; TOON handles this, incumbent does not.
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
