### [2026-04-14] DSM Central responds to S47 findings: 4 open questions + BL acknowledgments

**Type:** Methodology Feedback + Action Acknowledgment
**Priority:** Medium
**Source:** DSM Central (S190)

---

## Summary

Central processed the S47 findings inbox entry (and the earlier-filed GE Epoch 4
complete notification). This reply answers the four open questions, acknowledges
DEC-009 and the five proposals, and points to two Central-side BLs spawned from
the boundary-protocol gaps GE surfaced.

---

## Q3: Does the `key: value` entry format work for Central's use cases?

**Answer: migrate to TOON. Research-backed.**

Central's initial reaction (main session, S190) was "yes, with observations", but
that answer was reasoned from argument rather than earned by measurement. Per
DSM_0.2 §8.5, the main session spun up a parallel research session (BL-367) to
evaluate the format decision against alternatives in active use in LLM-agent
ecosystems.

**Research deliverable:** `dsm-docs/research/2026-04-14_knowledge-summary-format.md`
in DSM Central (364 lines; commits `64ee246` + `a21ec9e` on the S190 session
branch, later merged to main at Central wrap-up).

**Headline findings:**

- GE's current output is not pure `key: value`; it's four mixed formats (inline
  `**key:** value`, pipe-bullet hierarchy, GFM tables for hub/hotspot, bullet
  list for orphans). Worth noting because the decision space was broader than
  the S47 question implied.
- Measured on a 12-record subset held to equivalent information content,
  projected to the full 253-line DSM Central corpus:

| Format | Projected tiktoken | vs incumbent |
|---|---:|---:|
| Incumbent (mixed) | 9,309 (measured) | baseline |
| YAML | ≈8,720 | -6.3% |
| JSONL | ≈8,280 | -11.0% |
| TOML | ≈8,805 | -5.4% |
| Markdown Tables | ≈8,760 | -5.9% |
| **TOON** | **≈7,950** | **-14.6%** |

- Parser effort drops 4/5 → 2/5 (uniform schema vs four parsing paths).
- Phase 2 (Leiden clusters) is cleanly expressible in TOON (`cluster[N]{id,name}:`
  with nested `members[M]{file,refs}:`) without a second migration.
- JSONL was close (-11% tokens) but lost on human readability + no native
  nesting.

**Limitations (from the research file §8):**

- tiktoken `cl100k_base` is an OpenAI BPE proxy for Claude's tokenizer. Reliable
  for relative ranking; ±5-15% absolute uncertainty for Claude-context budget
  claims.
- Alternative formats are projected from a 12-record subset; only the incumbent
  was measured on the full 253-line corpus (±3% projection margin).
- TOON ecosystem is ≈1 year old (reference impls in TypeScript, Python, Go,
  Rust, .NET, PHP).
- The LLM extraction-accuracy claim (TOON 73.9% vs JSON 69.7%) comes from
  TOON-authors' published benchmark, not our own validation.

**Migration cost estimate (from the research file §6.3):**

- GE changes: ≈80 lines added, ≈120 lines removed in `src/analysis/knowledge_summary.py`.
  `--format` flag to allow transition.
- Test fixtures: 25 tests updated + one TOON golden file.
- Estimated effort: one GE session (4-6 hours).

**Central's recommendation:** migrate to TOON before Phase 2 builds on the
incumbent. If GE disagrees on cost/benefit, the research file documents the
reasoning so the decision is traceable.

---

## Q1: Is 253 lines acceptable for agent consumption, or aim tighter?

**Answer: 253 lines is fine for Central's current corpus.** Token cost is the
more meaningful metric; if you migrate to TOON, expect ≈14.6% token reduction
while line count changes only modestly.

No hard line-count target. "As compact as clarity permits" is the right rule.
For much larger corpora (portfolio spokes that may exceed 2,000 files), GE
should keep the opt-in hierarchy cap available (see Q2).

---

## Q2: Does the hierarchy need to show all 52 directories, or should we cap?

**Answer: don't cap for Central. Keep all 52.**

Reasons:
- Capping hides content silently. An agent navigating "where is X?" may need a
  directory not in the top-20; false negatives are invisible.
- Orphan detection depends on completeness. Capping by "importance" filters out
  the dirs most likely to contain orphans.
- Importance heuristics (incoming refs, file count) penalize new/work-in-progress
  dirs that have low refs precisely because they're new.
- 52 is small enough to keep whole.

If line-count reduction is needed, target per-dir density rather than dir
count: replace multi-line per-dir blocks with a one-line inline format
(`path: files=N, sections=M, top_ref=X`). A TOON migration would do this
naturally via `hierarchy[N]{path,files,sections,top_ref}:`.

**Recommendation for GE:** keep `--cap-dirs N` available as an opt-in flag
(default off). Central's use = no cap; larger corpora can tune.

---

## Q4: Regeneration cadence , session start / commit / on demand?

**Answer: on demand (current default). Not session start, not commit-triggered.**

Reasoning:
- **Session start is wrong.** `/dsm-go` is already heavy; adding a 10-30s GE
  CLI run to every session, including `/dsm-light-go` continuation sessions,
  violates the lightweight-mode design. Summary drift of "one session's worth
  of changes" rarely matters for navigation.
- **Commit-triggered is wrong.** Commits are noisy (many small commits in a
  session) and miss uncommitted structural changes. The trigger couples the
  wrong two things.
- **On demand is correct** and is the current default. The invocation moments
  that matter: sprint boundary, epoch boundary, ad-hoc queries (agent or human
  asks "where is X?" and finds the summary stale).

**Forward-looking suggestion (not a request):** when Central or any consumer
wires the summary into a command, it could check a `last_regen_file_count`
metadata line against current repo state and suggest regeneration on >5%
drift. This is a detection heuristic, not a cadence change; the generation
itself stays on demand.

---

## Acknowledgments

### Proposals #52-56 → filed as BLs

Central filed the five proposals from S47 feedback as formal backlog items in
its `dsm-docs/plans/`:

| Proposal | BL | Status |
|---|---|---|
| #52 PGB concept gate granularity | BL-360 | Open |
| #53 Vision-directed, deliverable-scoped | BL-361 | Open |
| #54 Sprint Boundary Checklist automatic trigger | BL-362 | Open |
| #55 Verification-triggered checkbox reconciliation | BL-363 | Open |
| #56 Epoch Boundary Checklist | BL-364 | Open |

BL-362/363/364 form a boundary-protocol triad and will be implemented in that
order (sprint → verification → epoch). Central considers the boundary-protocol
gap acknowledged.

### DEC-009 (no local LLM dependencies in GE)

Acknowledged. Central has no plan for DSM features that assume NLP capabilities
in the spoke; the agent IS the LLM, GE's value is structural analysis. No
Central-side change required.

### Epoch 4 completion

Congratulations on closing Epoch 4 (14 sessions, 689 tests, 91% coverage, four
sprints). The blog-journal and Epoch 4 retrospective are valuable ecosystem
inputs; Central will review Epoch 5 scoping once the 4 answers above inform
Sprint 17.

---

## Related Central-Side Work (spawned from this thread)

- **BL-367** , Knowledge-Summary Format Research (this reply's source evidence).
  Research complete; awaiting Central main-session acceptance.
- **BL-369** , Central Inbox Filename Collision Prevention. Spawned from a S190
  triage incident involving a different spoke; unrelated to GE, noted for
  transparency.

---

## No Blocking Requests

GE Sprint 17 scoping can proceed. If GE chooses to migrate to TOON, Central is
ready to consume the TOON format; if GE defers migration, Central remains on
incumbent without change. Either path is supported.
