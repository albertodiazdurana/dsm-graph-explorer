# DEC-010: Migrate Knowledge-Summary Output to TOON

**Status:** Accepted
**Date:** 2026-04-20
**Session:** S48
**Author:** Alberto Diaz Durana
**Related:** DEC-009 (no local LLM dependencies), Central BL-367 (format research), GE BL-302 Phase 1 (Sprint 16)

---

## Context

GE Sprint 16 (Phase 1, BL-302) shipped `--knowledge-summary PATH`, producing a ~253-line markdown artifact with four section formats glued together:

- Header: inline `**key:** value | **key:** value`
- Document Hierarchy: `path: value` with pipe-separated metadata bullets
- Hub Documents: GitHub-Flavored Markdown table
- Cross-Reference Hotspots: GitHub-Flavored Markdown table
- Orphan Files: bullet list with parenthetical section counts

S47 findings Q3 asked whether the mixed `key: value` pattern was appropriate. Central escalated the question to a parallel research session (BL-367, 364 lines), measured six candidate formats with tiktoken `cl100k_base`, and recommended migration to TOON (Token-Oriented Object Notation, 2025).

## Decision

**Accept Central's recommendation.** Migrate the knowledge-summary output to TOON, gated by a `--format` flag during transition.

Implementation is tracked in [BL-302 Phase 1.5](../plans/BL-302-phase-1.5-toon-migration.md) and targeted to Sprint 17 (Epoch 5).

## Justification (strongest first)

1. **Research is methodologically earned** (DSM_0.2 §8.5). Central measured 6 formats on a 12-record schema-equivalent subset, projected to the full 253-line payload with ±3% margin, and disclosed limitations (tokenizer proxy, author-authored extraction benchmarks, ecosystem maturity).
2. **Token savings are real and measured.** TOON: ≈7,950 tokens projected vs 9,309 measured for incumbent = **-14.6%**, best in class. Next-best JSONL = -11.0%. Savings scale linearly with corpus size; portfolio-sized repos (2,000+ files) project to ~13.5K-token savings.
3. **Phase 2 fit is decisive.** Leiden cluster output (Epoch 5 DRAFT) is natively hierarchical. Only TOON and YAML handle this cleanly; TOON wins on tokens.
4. **Uniform schema eliminates 4-parsing-paths cost.** Parser effort drops 4/5 → 2/5. Every downstream agent (including Claude itself) benefits.
5. **Migrate now = cheapest.** GE is currently the sole producer and Central the sole consumer. Future consumers (blog-poster, MCP servers, portfolio spokes) inherit TOON from day one.

## Counter-evidence considered (per DSM_0.2 §8.2.1)

| # | Counter-claim | Why it does not defeat the decision |
|---|---|---|
| 1 | 14.6% of ~9K tokens = ~1,350 tokens (~0.7% of 200K Claude context): marginal | Portfolio-scale consumers (2,000+ files) → ~13.5K tokens (6.7% of 200K, or 42% of a 32K context). Phase 2 clusters compound. |
| 2 | TOON ecosystem is ~1 year old; spec-drift risk | GE is the sole authoritative emitter. If the spec drifts, update the emitter; regeneration is on-demand. |
| 3 | TOON extraction-accuracy benchmark (73.9% vs 69.7%) is author-authored | Independent token-savings measurement suffices. Accuracy claim is not on the decision load path. |
| 4 | YAGNI: defer speculative work (S47 pattern lesson) | Phase 2 is sequenced in Epoch 5 DRAFT, not speculative. Migration cost only grows with accumulated incumbent-specific code. |
| 5 | tiktoken `cl100k_base` is OpenAI BPE, not Claude's tokenizer (±5-15% absolute uncertainty) | Decision rests on relative ranking across 6 formats measured the same way. Stable under +15% worst-case; TOON still wins. |
| 6 | "One session" migration estimates typically underestimate | Accepted risk. Inverts unfavorably if deferred: later migration = strictly more cost. |

## Conditions on acceptance

- **C1. Transition flag.** Add `--format` with values `markdown` (current default) and `toon`. Markdown stays default for one minor release; TOON flips to default only after C3 validation passes.
- **C2. Defer `--format jsonl`.** No concrete consumer ask. Can be added later if demand appears.
- **C3. Validation gate.** Before declaring migration complete, run `--format toon --knowledge-summary` on full DSM Central corpus and measure actual token count via tiktoken. Require **≥10% measured savings** (not projected) to confirm Central's estimate.
- **C4. Spoke-side documentation.** One-line TOON format note in CLI `--help` output, README, and `dsm-docs/guides/` entry (if present).

## Consequences

### Positive
- Smaller prompt payloads for all agent consumers of the summary.
- Uniform per-section schema simplifies downstream parsers.
- Phase 2 (Leiden clusters) becomes cleanly expressible without a second migration.
- Explicit field-name contract where incumbent had none.

### Negative
- One-session (4-6h) engineering cost, 25 test fixtures to update.
- TOON parser dependency (spec + reference implementation in Python) introduces a new toolchain element.
- Downstream consumers must learn TOON (low cost: plain text with declared schema).

### Neutral
- Output size in lines is roughly unchanged (incumbent 253 vs TOON projected in the same range); the win is in tokens and uniformity, not line count.
- Grep-friendliness preserved (TOON's `[N]{field1,field2,...}:` header still exposes field names).

## References

- Central's research file: `~/dsm-agentic-ai-data-science-methodology/dsm-docs/research/2026-04-14_knowledge-summary-format.md` (364 lines; do not duplicate here, cite by path).
- GE S47 Q3 (findings inbox): `_inbox/done/2026-04-14_dsm-central_s47-findings-response.md`.
- BL-302 Phase 1 implementation: `src/analysis/knowledge_summary.py`, `tests/test_knowledge_summary.py`.
- TOON format: https://github.com/toon-format/spec/blob/main/SPEC.md
