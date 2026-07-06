# EXP-011 Results — Agent-Navigation A/B for the Intrinsic-ToC

**Corpus:** GE `dsm-docs/` (116 files, 1650 sections, 67 cross-refs)
**Run harness:** dynamic Workflow, fresh isolated `general-purpose` subagents, one per (task × arm),
blind to arm, forbidden from running the project's own `dsm-validate`/`--knowledge-summary` tooling.
**Measurement:** navigation `tool_calls` counted from each agent's transcript
(`tool_use` lines − 1 StructuredOutput − 1 arm-input load read for A1/A2). Self-reported counts
matched transcript counts exactly in the pilot.

---

## Pilot (2 tasks × 3 arms, run 2026-07-06, workflow `wf_74a16d93-706`)

| Task | Arm | Answer given | vs key | Nav tool_calls |
|------|-----|--------------|--------|----------------|
| **T1** most-referenced file *(key: `blog/epoch-1/materials.md`, 52)* | A0 none | `.claude/CLAUDE.md`, 72 | ✗ wrong file & metric | 6 |
| T1 | A1 markdown | `materials.md`, 52 | ✓ | 0 |
| T1 | A2 TOON | `materials.md`, 52 | ✓ | 0 |
| **T3** orphan-file count *(key: ≈112)* | A0 none | 97 | ✗ (own link-parse; diverges from graph count) | 2 |
| T3 | A1 markdown | **112** | ✓ | 0 |
| T3 | A2 TOON | **15** | ✗ undercount by ~97 | 0 |

*Note on T3/A1:* the agent computed the correct answer (112 = 15 shown + "97 more") but its
StructuredOutput call omitted two required fields and hit the retry cap; the answer was recovered
verbatim from its transcript (`agent-a923f21e…jsonl`). Schema-formatting failure, not a navigation
failure. The full run relaxes the schema to require only `answer`.

### Pilot findings

1. **Harness + measurement validated.** Fresh isolated agents behaved as designed; navigation
   tool-calls are recoverable from transcripts and matched self-report exactly. The 3 ToC arms that
   answered from the summary made **0 navigation calls** (1 arm-load read, excluded).

2. **H1 (ToC helps navigation) — supported on T1.** The no-ToC control spent **6 tool calls and
   still returned the wrong answer** (`.claude/CLAUDE.md`/72 — it measured basename mentions across
   the whole repo, a different metric than dsm-docs incoming cross-references). Both ToC arms
   answered correctly with **0** tool calls. The ToC supplies an authoritative metric the agent
   cannot cheaply or correctly reconstruct on its own.

3. **H2 (format matters) — strongly supported on T3 (headline).** markdown arm → **112**;
   TOON arm → **15**. The TOON schema drops the overflow total (EXP-010 finding **F4**:
   `orphans[15]{…}` with no `orphans_total`), so the consuming agent confidently **undercounts
   orphans by ~97**. Same corpus, same question, same zero navigation — the only difference is the
   ToC format, and TOON produces a materially wrong answer. This is a concrete instance of the
   format actively harming the consumer, not merely costing more tokens.

4. **Bonus (why an authoritative ToC has value).** The no-ToC arm's independent orphan computation
   (97) diverges from the ToC's graph-based count (112) because it used a looser link-detection
   method. The orphan count is genuinely method-dependent — which is precisely why a faithful,
   authoritative ToC is useful, and why TOON's truncation (15) is a regression rather than a
   rounding difference.

**Pilot verdict:** harness sound; go for the remaining 6 tasks. The early signal already leans
decisively toward *"the ToC helps, and markdown conveys it faithfully while the current TOON schema
corrupts at least one structural answer."*

---

## Full run (6 remaining tasks × 3 arms, workflow `wf_a383617e-e17`, 18/18 agents, 0 errors)

Tool-call counts are self-reported (validated equal to transcript counts in the pilot).

| Task | Arm | Answer | vs key | Tool calls |
|------|-----|--------|--------|-----------|
| **T2** hotspot *(key: `blog/epoch-1/materials.md` §3 "Growth Through Feedback", 22)* | A0 | §3, **24** refs, in `_inbox/done/…tfidf…md` (whole-repo); noted dsm-docs-scoped = materials.md §3 22 | ✗ primary (wrong file & count) | **13** |
| T2 | A1 md | materials.md §3 "Growth Through Feedback", 22 | ✓ | 0 |
| T2 | A2 toon | materials.md §3 "Growth Through Feedback", 22 | ✓ | 0 |
| **T4** largest dir *(task flawed — unscoped, see note)* | A0 | `_inbox/done/` 28 (repo-wide) | ✓ literal | 1 |
| T4 | A1 md | `_inbox/done/` 28; dsm-docs-scoped `checkpoints/done/` 19 | ✓ | 1 |
| T4 | A2 toon | `_inbox/done/` 28; dsm-docs-scoped `checkpoints/done/` 19 | ✓ | 1 |
| **T5** intrinsic-toc file+sections *(key: file ✓, 32 sections)* | A0 | file ✓, but **10** sections (own heading count) | ✗ (count wrong) | 1 |
| T5 | A1 md | file ✓, **32** sections | ✓ | 0 |
| T5 | A2 toon | file ✓, **32** sections | ✓ | 0 |
| **T6** decisions/ count *(key: 13)* | A0 | 13 (11 DEC + README + align-report) | ✓ | 1 |
| T6 | A1 md | 13 | ✓ | 1 |
| T6 | A2 toon | 13 | ✓ | 1 |
| **T7** TOON emitter src *(control; key: `knowledge_summary.py`, `_generate_toon_summary`)* | A0 | ✓ | ✓ | 4 |
| T7 | A1 md | ✓ | ✓ | 2 |
| T7 | A2 toon | ✓ | ✓ | 2 |
| **T8** C3 threshold+DEC *(control; key: ≥10%, DEC-010)* | A0 | ✓ ≥10%, DEC-010 | ✓ | 2 |
| T8 | A1 md | ✓ | ✓ | 1 |
| T8 | A2 toon | ✓ | ✓ | 1 |

**Task-design note (T4):** the question was not scoped to `dsm-docs/`, so all arms answered
repo-wide (`_inbox/done/`, 28) — outside the ToC's coverage — and each spent 1 tool call. T4 does
not discriminate the arms; kept for honesty. The intended dsm-docs-scoped answer
(`checkpoints/done/`, 19) is a secondary note in the ToC arms. A follow-up run should scope the
question.

---

## Per-arm rollup (all 8 tasks: pilot T1/T3 + batch T2/T4/T5/T6/T7/T8)

| Arm | Success | Total tool calls | Mean tool calls / task |
|-----|---------|------------------|------------------------|
| **A0 (no ToC)** | **4 / 8** (+1 partial) | 30 | 3.75 |
| **A1 (markdown ToC)** | **8 / 8** | 5 | 0.625 |
| **A2 (TOON ToC)** | **7 / 8** (only miss: T3 orphans) | 5 | 0.625 |

### Findings (full experiment)

1. **H1 (ToC helps navigation) — strongly supported.** ToC arms used **~6× fewer tool calls**
   (mean 0.63 vs 3.75) *and* were more accurate (8/8 and 7/8 vs 4/8). Far beyond the pre-registered
   ≥25% tool-call-reduction gate. The advantage is largest on **graph-derived** questions the agent
   cannot cheaply or correctly reconstruct — hub (T1), hotspot (T2), orphans (T3), exact section
   count (T5): on all four, ToC arms were correct at **0 tool calls** while the no-ToC arm was
   expensive *and* frequently wrong (T1 wrong at 6 calls; T2 wrong at 13 calls; T5 wrong count at 1
   call). On plain filesystem questions (T4, T6) and out-of-scope controls (T7, T8) the ToC gave
   little or no edge, as expected.

2. **H2 (format matters) — markdown strictly dominates the current TOON.** Across all 8 tasks, A1
   (markdown) and A2 (TOON) gave **identical answers and identical tool-call counts on 7 of 8**. The
   sole difference is **T3**: markdown → 112 (correct), TOON → 15 (wrong, F4 orphan-total loss). So
   the current TOON schema is **equal-or-worse on navigation AND more expensive on tokens** (F1,
   +1.74–7.58%). There is no task where TOON beat markdown.

3. **The no-ToC arm doesn't just cost more — it silently answers wrong.** T1 (`.claude/CLAUDE.md`
   instead of `materials.md`), T2 (24 refs on the wrong file), T5 (10 sections instead of 32): each
   is a confident, plausible, *wrong* answer produced by reconstructing a metric that differs from
   the graph's. This is the concrete cost the Intrinsic-ToC removes.

4. **Agents don't always exploit the ToC (T6).** Both ToC arms had "13 files" in the summary but
   still ran `ls` to confirm the count — a minor trust/verification behavior worth noting for how
   ToCs are consumed.

**Caveats:** n=8, directional not statistical. T4 was an unscoped (flawed) task. The experiment
tested the *current* (defective) TOON emitter; a redesigned TOON could close T3 and the token gap,
but nothing here shows TOON would ever *out-navigate* markdown — a fixed TOON's best case is a tie
while still needing to win on tokens (F1 makes that unlikely).

---

## Decision (pre-registered rule applied)

Observed: **A1/A2 ≪ A0** (ToC helps decisively) and **A2 ≤ A1** (TOON never beats markdown; loses
on T3). This is **Outcome 2** of the pre-registered rule → **markdown wins**.

**Recommendation (pending user confirmation of the S53 fork):**
- **The Intrinsic-ToC is validated — keep it.** Abandoning the ToC (Outcome 1) is off the table.
- **Keep the ToC in markdown; NO-GO on the TOON migration.** The current TOON is strictly
  dominated. Fork (a) fix-and-retry is not worth a sprint: its ceiling is a navigation *tie* with
  markdown while still owing a token win it is unlikely to achieve (F1).
- **Resolve DEC-010** toward abandonment/deprioritization of the TOON format, pending user sign-off.

**Resolution (author-confirmed, 2026-07-06):** NO-GO on TOON; keep the ToC in markdown. Formalized
in DEC-010 Amendment 2 and BL-302 Resolution. Sprint 17 P2/P4 cancelled.

---

## Appendix: Process metrics & caveats (write-up / blog source material)

Captured durably here because these figures otherwise live only in ephemeral workflow run
notifications. This appendix + EXP-011.md is intended to be self-sufficient for drafting a post
in a later session without re-running anything.

### Run / orchestration metrics

- **Orchestration:** dynamic multi-agent Workflows (deterministic fan-out), main-loop model Opus 4.8,
  subagents of type `general-purpose` (tools: Read/Grep/Glob/Bash + forced StructuredOutput).
  Concurrency cap ≈ min(16, cores−2); excess agents queued.
- **Two runs:**

| Run | Workflow ID | Agents | Errors | Subagent tokens | Tool-uses | Wall-clock |
|-----|-------------|--------|--------|-----------------|-----------|------------|
| Pilot (T1, T3) | `wf_74a16d93-706` | 6 | 1 schema-retry (answer recovered) | 159,031 | 22 | ~5.3 min (319,622 ms) |
| Batch (T2,T4,T5,T6,T7,T8) | `wf_a383617e-e17` | 18 | 0 | 485,069 | 65 | ~4.2 min (251,524 ms) |
| **Combined** | — | **24** | 1 (recovered) | **644,100** | **87** | ~9.5 min (two windows) |

- **Design of the fan-out:** one fresh, isolated subagent per (task × arm); arms **blind** (agent not
  told which arm; the only difference is presence/absence of the arm-input ToC file reference);
  structured-output schema forced a machine-checkable return.
- **Measurement method:** navigation `tool_calls` counted from each agent's transcript
  (`agent-<id>.jsonl`): `tool_use` lines − 1 (StructuredOutput) − 1 (the single arm-input load read,
  A1/A2 only). In the pilot, transcript counts matched agents' self-reports exactly, validating the
  method for the batch.

### Static ToC token cost (tiktoken `cl100k_base`) — the F1 reproduction

| Corpus | markdown | TOON | Δ |
|--------|----------|------|---|
| GE `dsm-docs/` (relative paths) | 2,903 | 3,123 | **+7.58%** (TOON worse; 8,485 vs 8,154 chars) |
| DSM Central (relative, same-day paired; from EXP-010) | 6,952 | 7,073 | **+1.74%** (TOON worse) |

Gate required −10%. Fewer characters, more tokens — BPE penalizes comma-adjacent long paths.

### Precursor experiment (the other multi-agent story) — EXP-010

EXP-011 exists because **EXP-010** (2026-07-03) surfaced finding F8. EXP-010 was itself a multi-agent
capability probe: **Fable-5 orchestrator + 9 Haiku gatherers (10 agents), adjudicated by Opus 4.8**;
~270–300K tokens, ~65–70% delegated to the cheaper Haiku model; 14/14 findings CONFIRMED, with the
load-bearing token measurement (F1) independently reproduced by Opus to the token. Full record:
`data/experiments/EXP-010-fable-repo-plan-assessment/` (EXP-010.md §5 adjudication, results.md F1–F14).

### Caveats (state these plainly in any write-up)

1. **n = 8, one run per (task × arm) cell** — directional, not statistical; no variance or
   significance testing.
2. **`tokens_to_answer` was not reliably measured per arm** (weak per-subagent metering). Lean the
   quantitative claims on `tool_calls` + success rate + the static ToC token cost above; do not claim
   per-arm "tokens saved during navigation."
3. **T4 was a flawed (unscoped) task** — the question didn't restrict to `dsm-docs/`, so all arms
   answered repo-wide (`_inbox/done/`, 28) at 1 tool call and it did not discriminate the arms.
   Exclude it as evidence or disclose the flaw.
4. **The orphan "truth" is method-dependent:** graph REFERENCES-edge count → 112 (the ToC's
   authoritative figure); the no-ToC agent's own link-parse → 97; TOON's truncated schema → 15.
   "TOON answered wrong" means wrong **relative to the ToC's own authoritative count**, and the point
   is the ~97-file undercount magnitude, not a single canonical number.
5. **Contamination controls:** fresh isolated subagents; questions target the repo's *current state*
   (rankings/counts) not general knowledge; agents were **forbidden from running the project's own
   `dsm-validate` / `--knowledge-summary` / `--graph-stats`** (otherwise an arm could regenerate the
   ToC in one call and confound the comparison).
6. **Harness robustness note:** the pilot's T3-A1 agent computed the correct answer (112) but hit the
   StructuredOutput retry cap by omitting required fields; recovered verbatim from its transcript. The
   batch relaxed the schema to require only `answer`.

### Source-pointer index (nothing important should be lost)

- **Hypotheses, design, environment, decision:** `EXP-011.md` §1–4, §6.
- **Per-task data + per-arm rollup + findings:** this file (`results.md`) — Pilot, Full run, Per-arm
  rollup sections.
- **Frozen arm inputs (reproducible):** `arm-inputs/toc-markdown.md`, `arm-inputs/toc-toon.toon`.
- **Workflow scripts (re-runnable):**
  `~/.claude/projects/-home-berto-dsm-graph-explorer/<session>/workflows/scripts/exp011-nav-{pilot,batch}-*.js`.
- **Precursor:** `data/experiments/EXP-010-fable-repo-plan-assessment/`.
- **Decision records:** `dsm-docs/decisions/DEC-010-toon-migration-format.md` (Amendment 2),
  `dsm-docs/plans/BL-302-phase-1.5-toon-migration.md` (Resolution).
- **Vision context ("README for LLMs" north star):** `dsm-docs/research/2026-04-13_intrinsic-toc-vision.md`.
- **Blog scaffold status:** `dsm-docs/blog/epoch-5/` does **not** exist yet — create it as the first
  step of the blog process (per-epoch materials.md + journal.md).
