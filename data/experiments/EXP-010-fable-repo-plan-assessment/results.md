# EXP-010 Results — Fable 5 Independent Assessment

> **Fable: write your assessment into this file.** Fill every `_(...)_` placeholder.
> Keep the section structure. Opus will adjudicate each finding against the actual
> code/tests in `EXP-010.md` §5, so cite `file:line` and quote snippets.

**Model:** Fable 5 (`claude-fable-5`)
**Run date:** 2026-07-03
**Files actually read (Tier 1 direct / Tier 2 delegated):**
- *Tier 1, read directly by Fable:* `src/analysis/knowledge_summary.py` (all 507 lines), `src/cli.py` (targeted: option block 415–465, knowledge-summary call site 1080–1160, plus full grep of `format`/`knowledge_summary`), `tests/test_knowledge_summary.py` (all 335 lines), `dsm-docs/decisions/DEC-010-toon-migration-format.md`, `dsm-docs/plans/epoch-5-sprint-17-plan.md`, `dsm-docs/plans/BL-302-phase-1.5-toon-migration.md`, `dsm-docs/checkpoints/done/2026-07-03_s51_checkpoint.md`, and the official TOON spec (`toon-format/spec` SPEC.md, §7/§9/§11/§12 read directly).
- *Tier 2, delegated to Haiku sub-agents:* `dsm-docs/plans/epoch-5-plan.md`, `DEC-009`, `dsm-docs/research/2026-04-13_intrinsic-toc-vision.md`, cross-repo `BACKLOG-367_knowledge-summary-format-research.md`, `README.md` + `pyproject.toml` + MEMORY check, test-suite run, mechanical greps, CLI reproduction runs.
- *Empirical runs (verified by Fable directly):* pre-refactor emitter extracted from git (`7b9c7c8`), old-vs-new markdown diff on the real graph and a synthetic graph; `--format toon`/`markdown` generated on the GE `dsm-docs/` corpus and on the **full DSM Central corpus** (both absolute- and relative-path invocations); tiktoken `cl100k_base` counts re-measured by me, not just by the sub-agent.

**Anything you could NOT access:** none. (Note: `MEMORY.md` named in the brief's Tier 2 list does not exist in the repo root; project state lives in checkpoints/plans/decisions. Everything else, including the cross-repo BL-367 file and the TOON spec, was accessible.)

### Process report (how the work was done)
- **Agents / sub-agents used:** 10 total — myself (Fable 5, orchestrator + all analysis) plus **9 Haiku sub-agents**: 8 parallel gatherers launched as one workflow (5 doc summarizers/fact collectors, 1 test-suite runner, 1 CLI-reproduction runner, 1 orientation reader) and 1 standalone TOON-spec fetcher.
- **Workflow:** (1) Read the brief and results template; sized Tier 1 (~2,400 lines). (2) Launched the 8-agent Haiku workflow in the background (Tier 2 summaries, test names/symbol maps, full pytest run, CLI runs producing both formats + token counts) and, in parallel, read all Tier 1 files myself. (3) Spawned a Haiku agent to fetch the official TOON spec; then read the spec's quoting/empty-array/delimiter sections **myself** because they were load-bearing for findings. (4) Ran my own verification battery: extracted the pre-Sprint-17 emitter from git and diffed old-vs-new markdown on the real exported graph and a synthetic adversarial graph; probed the TOON emitter with nasty inputs (quotes, newlines, colons, numeric-like strings, >15 orphans); ran the actual C3 measurement on the DSM Central corpus in both formats and both invocation styles, re-counting tokens with tiktoken myself. (5) Wrote this report. Division of labor: Haiku did token-cheap reading/summarizing/mechanical runs; every finding below rests on code, spec text, or command output I verified directly.
- **Token usage (estimates flagged as such):** Delegated (metered by the harness): **~189K tokens** (171,004 for the 8-agent workflow + 18,344 for the spec fetcher), all on Haiku. My own: not directly metered; best estimate **~45–55K tokens of unique analytical input** (Tier 1 files, spec sections, probe/measurement outputs, sub-agent summaries) and **~30–40K output tokens** (analysis, probe scripts, this report), with multi-turn cache re-reads on top of that (cached, cheap). Approximate total across the system: **~270–300K tokens**, roughly 65–70% of it delegated cheap gathering.

---

## 1. Findings index

| ID | Axis | Severity | Confidence | One-line claim |
|----|------|----------|------------|----------------|
| F1 | A/B | high | high | The implemented TOON schema produces MORE tokens than markdown on every real corpus measured — the DEC-010 C3 gate (≥10% savings) fails today, by ~12–33 points. |
| F2 | A | high | high | The emitter violates TOON-spec MUST rules (CSV quote-doubling instead of `\"`, literal newlines that break row cardinality, unquoted colons/numeric-like strings), and a unit test enshrines one violation. |
| F3 | B | high | high | The C3 gate protocol is invalid as written: it compares today's TOON against a stale, invocation-dependent 9,309-token baseline, which can produce a spurious PASS (−24%) when the true same-conditions delta is +1.7%. |
| F4 | A | medium | high | TOON silently discards overflow totals: on GE's own corpus the repo has 110 orphans but TOON reports `orphans[15]` with no "more" indicator (markdown says "... and 95 more"). |
| F5 | B | medium | high | P2 (golden-fixture freeze) is sequenced before P3 (validation gate) despite no dependency — the gate is runnable today and fails, so freezing now guarantees churn. |
| F6 | B | medium | high | The BL-367 −14.6%±3% projection was measured on a different schema than the one implemented; the "Low likelihood" rating on C3 failure was unfounded. |
| F7 | A/B | medium | high | Acceptance criterion "structurally valid TOON" has no verification mechanism: no reference-decoder round-trip is planned in P2, and per F2 the criterion is currently false. |
| F8 | C | medium | high | No experiment anywhere in Epoch 5 tests the north-star hypothesis (agents navigate better/cheaper with an Intrinsic-ToC); S17 optimizes a proxy metric it is currently pessimizing. |
| F9 | C | medium | high | Identity/dogfooding gap: README still frames GE as an "integrity validator" (v0.4.0, stale since 2026-03-17), and the repo does not ship its own Intrinsic-ToC at `.claude/knowledge-graph.md`. |
| F10 | A | low | high | Hub/hotspot top-N boundary ties are broken by graph insertion order (no secondary sort key) — non-canonical ordering about to be frozen in a golden fixture. |
| F11 | A | low | medium | Empty sections emit `name[0]{fields}:`, which is neither the spec's modern (`key: []`) nor legacy (`key[0]:`, fields-less) empty-array form. |
| F12 | A | low | high | `emit_table` with a non-comma delimiter omits the spec-required delimiter marker in the bracket/braces segments (`t[1]{a\tb}:` instead of `t[1\t]{a\tb}:`) — latent API bug. |
| F13 | C | low | medium | The TOON schema omits line-number pointers even though SECTION nodes carry a `line` attribute and the vision's Layer 2 requires "file and line pointers" — cheap to add before the freeze, costly after. |
| F14 | A | low | high | `generate_knowledge_summary(G, fmt="anything-else")` silently returns markdown instead of raising — the CLI is guarded by `click.Choice`, but the API contract is silent-fallthrough. |

**Verified-true claims (adversarial checks that came back clean):** the "markdown output byte-for-byte identical" refactor claim is TRUE — I diffed the pre-Sprint-17 emitter (git `7b9c7c8`) against the current one on the real exported graph and on a synthetic adversarial graph; both byte-identical. The suite result "701 passed / 1 skipped" reproduces (13.57s). The CLI `--format` flag is correctly guarded by `click.Choice(["markdown","toon"])` (`src/cli.py:439`). Empty-graph TOON output is well-formed per the emitter's own contract (all `[0]` headers).

---

## 2. Detailed findings

### F1 — Implemented TOON schema is token-NEGATIVE; the C3 gate fails today
- **Axis:** A (code/schema) + B (it breaks the plan's central premise)
- **Severity:** high
- **Location:** `src/analysis/knowledge_summary.py:436-462` (`_generate_toon_summary` schema assembly); DEC-010 C3 (`dsm-docs/decisions/DEC-010-toon-migration-format.md:52`); BL-302 P3 (`dsm-docs/plans/BL-302-phase-1.5-toon-migration.md:63-67`)
- **Claim:** On every real corpus measured, the implemented TOON output costs MORE tiktoken `cl100k_base` tokens than the markdown it replaces, so the ≥10%-savings gate fails — before the golden fixture freezes this schema.
- **Evidence / reasoning:** I generated both formats with the shipped CLI and measured with tiktoken `cl100k_base` (same tokenizer as BL-367/DEC-010):
  - GE's own `dsm-docs/` (relative paths): markdown **2,903** tokens vs TOON **3,123** → TOON **+7.58%**.
  - **Full DSM Central corpus** (the C3 corpus), relative-path invocation, same-day paired baseline: markdown **6,952** vs TOON **7,073** → TOON **+1.74%** (gate needs **−10%**).
  - Central, absolute-path invocation: markdown 9,936 vs TOON 12,205 → TOON **+22.84%**.
  Per-block decomposition (Central, absolute run) names the mechanism: `directories`+`hierarchy` = 10,440 TOON tokens vs 8,486 for markdown's Document Hierarchy; `hub` 445 vs 311 (+43%); `orphans` 437 vs 195 (+124%); TOON wins only on `hotspots` (855 vs 917). Three drivers: (1) the split-hierarchy schema repeats `dir` in every `hierarchy` row and carries a `path` column that duplicates `dir` + `title` (e.g. real row: `dsm-docs/checkpoints/epoch-1/done,2026-02-03_sprint3-complete.md,17,dsm-docs/checkpoints/epoch-1/done/2026-02-03_sprint3-complete.md`); (2) the settled design point "TOON `file` columns carry the node-id path, not the display title" (S51 checkpoint, lines 44-46) swaps short titles for long paths in `hub`/`orphans` — a navigability-for-tokens trade that was never re-measured; (3) BPE mechanics — markdown's ` | `, `path: `, `- ` boilerplate tokenizes cheaply while comma-adjacent long paths do not; BL-367 itself recorded TOON's char→token ratio of 1.44 (worst of the set), foreshadowing that TOON's character savings don't convert to token savings.
- **Recommendation:** Halt P2. Redesign the hierarchy schema to remove redundancy — e.g. drop the `path` column (reconstructible as `dir + "/" + file`), emit basename in a `file` column, and reconsider the title-vs-path choice per table — then re-run the paired measurement until the gate passes honestly. If the redesign still can't reach −10%, DEC-010's own C3 wording says: halt the migration and revisit the research assumptions.
- **Confidence:** high — reproducible commands, run twice (sub-agent, then myself), two corpora, two invocation styles, all agreeing on direction.

### F2 — Emitter violates TOON-spec MUST rules; a test enshrines one violation
- **Axis:** A
- **Severity:** high
- **Location:** `src/analysis/knowledge_summary.py:56-66` (`_quote`), `:82` (row join); `tests/test_knowledge_summary.py:298-300` (`test_colon_does_not_trigger_quoting`), `:295-296` (newline kept literal)
- **Claim:** The emitter implements CSV quoting, not TOON quoting: it violates the spec's MUST-level escape and quoting rules, so the output is not "structurally valid TOON" (BL-302 acceptance criterion), and P2 would freeze the dialect into the golden fixture.
- **Evidence / reasoning:** TOON SPEC.md §7.1 (escape table): `"` **MUST emit `\"`**, LF **MUST emit `\n`**, `\` MUST emit `\\` — the emitter doubles quotes CSV-style (`_quote('say "hi"')` → `'"say ""hi"""'`, knowledge_summary.py:65 `s.replace('"', '""')`) and leaves newlines literal, so `emit_table('t',['a','b'],[('x\ny','z')])` emits a `t[1]` header followed by **two** physical row lines — a strict decoder errors on both the invalid `""` escape and the cardinality mismatch (§14 strict mode: "the number of rows MUST equal N"). SPEC.md §7.2: a string MUST be quoted if it "contains a colon", "is numeric-like", is empty, has leading/trailing whitespace, or "equals '-' or starts with '-'" — §11.1 narrows only the *delimiter* condition for row cells, not these. The shipped output violates this on essentially every hub row: real Central/GE output contains `1,dsm-docs/blog/epoch-1/materials.md,52,3: Growth Through Feedback` (unquoted colon in `top_section`, by construction `f"{number}: {title}"`, knowledge_summary.py:264) and hotspot `section` cells like `3` or `1.10` (numeric-like strings that a typed decoder coerces to numbers — `"1.10"` becomes `1.1`). `_top_section_for_file`'s `"-"` fallback (line 265) is also a MUST-quote value. The docstring (lines 18-19) documents the CSV behavior as intended, and `test_colon_does_not_trigger_quoting` asserts the spec-violating behavior — so P2's parameterized tests would lock it in.
- **Recommendation:** Before P2: rewrite `_quote` to spec §7.1/§7.2 (backslash escapes; quote on colon, numeric-like, empty, leading/trailing whitespace, leading `-`, brackets/braces, control chars), fix the colon test, and add a round-trip test with the reference TOON decoder (see F7). Alternatively, if the team deliberately wants a CSV-quoting dialect, record that as a decision (it contradicts DEC-010's spec reference and BL-302's acceptance criterion) and stop calling the output TOON.
- **Confidence:** high — spec text read directly and quoted; violations reproduced in real corpus output and unit probes.

### F3 — C3 gate protocol is invalid: stale, invocation-dependent baseline enables a spurious pass (or fail)
- **Axis:** B
- **Severity:** high
- **Location:** `dsm-docs/plans/BL-302-phase-1.5-toon-migration.md:63-67` ("Record measured savings vs the incumbent baseline (9,309 tokens)"); DEC-010 C3 (line 52); S51 checkpoint lines 37-39
- **Claim:** Measuring today's TOON against the frozen April number 9,309 — instead of a same-day, same-invocation markdown baseline — can flip the gate's outcome in either direction.
- **Evidence / reasoning:** Two independent drifts break the frozen baseline. (1) *Corpus drift:* BL-367 measured 811 files / 8,991 sections / 1,254 cross-refs; today Central scans at **1,097 files / 12,147 sections / 1,299 cross-refs**, and same-style markdown now measures 9,936 tokens (+6.7%). (2) *Invocation dependence:* node IDs inherit the CLI's input path form. Run with an absolute path, every row carries `/home/berto/dsm-agentic-ai-data-science-methodology/...` and markdown measures 9,936 tokens (consistent with the April 9,309 → that baseline was almost certainly an absolute-path run); run relative, markdown measures 6,952. No invocation protocol is recorded anywhere. Concrete failure mode: run TOON with relative paths (7,073 tokens) and compare against the recorded 9,309 baseline → **"−24% savings", gate passes** — while the true same-conditions delta is **+1.74%** (F1). The reverse (absolute TOON 12,205 vs 9,309 → +31%) produces a spurious mega-fail. The gate as written cannot distinguish format effect from corpus growth and path-prefix effects.
- **Recommendation:** Rewrite P3: regenerate **both** formats on the same corpus snapshot, same invocation (relative paths, recorded command line), same day; the gate compares those two numbers only. Record the protocol in BL-302 so the P4 default-flip re-measurement is comparable.
- **Confidence:** high — all four measurements above are mine, commands reproducible.

### F4 — TOON silently loses overflow totals (orphans undocumented)
- **Axis:** A
- **Severity:** medium
- **Location:** `src/analysis/knowledge_summary.py:441-443` (`_hotspot_total`, `_orphan_total` discarded); `:298,378` (totals computed); S51 checkpoint lines 47-49 (documents only the hotspots drop)
- **Claim:** The TOON output caps hotspots at 20 and orphans at 15 and discards the "how many more exist" counts that markdown reports, so the Intrinsic-ToC misrepresents the repository to its consuming agent; only the hotspots half of this is documented as deliberate.
- **Evidence / reasoning:** On GE's own corpus the markdown Orphan Files section ends `- ... and 95 more` (110 orphans total) while TOON emits `orphans[15]{file,sections}:` — an agent reading TOON concludes the repo has exactly 15 orphans when it has 110. Synthetic probe: 20 orphans → `orphans[15]`, total silently gone. The S51 checkpoint's settled design points call out the *hotspots* overflow note as deliberately dropped ("the flat schema has no field for it") but never mention orphans. Note the schema already solves this problem elsewhere: `directories` carries a `more` column. For a "repository self-description" artifact, under-reporting defects (orphans are exactly the integrity signal GE was born to surface) is a north-star violation, and P2 would freeze it.
- **Recommendation:** Add totals before the golden freeze — cheapest form: `hotspots_total:` and `orphans_total:` scalar lines in the `summary:` block (2 lines, ~10 tokens); zero schema disruption.
- **Confidence:** high — reproduced on real and synthetic corpora.

### F5 — P2 (golden freeze) is mis-ordered before P3 (validation gate)
- **Axis:** B
- **Severity:** medium
- **Location:** `dsm-docs/plans/BL-302-phase-1.5-toon-migration.md:58-67` (§Phases P2, P3); `dsm-docs/plans/epoch-5-sprint-17-plan.md:57-61` (phase table)
- **Claim:** P3 has no dependency on P2 — the emitter is complete and the measurement takes minutes — yet the plan freezes the golden fixture and parameterizes 25 tests over a schema whose validation gate has not run; BL-302's own risk mitigation ("If we fail, revisit schema design (P0)") implies P2 work would be redone.
- **Evidence / reasoning:** I ran P3's measurement today with the shipped CLI in under a minute (F1) and it fails. Had P2 been completed first, the golden `knowledge-summary.toon`, the TOON structural assertions, and the format parameterization of 25 tests would all churn in the schema redesign. The brief's own framing ("a defect found after P2 is enshrined") applies equally to the economics: gate-first costs nothing and de-risks the largest phase (the plan itself budgets "half the session" for P2, risk table line 105).
- **Recommendation:** Swap the order: run the (fixed, per F3) P3 measurement first; only freeze the golden after the gate passes on the final schema. Keep P2's structural-assertion work, but write it against the post-redesign schema.
- **Confidence:** high.

### F6 — The BL-367 projection was for a different schema; the "Low" C3-failure risk rating was unfounded
- **Axis:** B
- **Severity:** medium
- **Location:** `dsm-docs/plans/BL-302-phase-1.5-toon-migration.md:49` (P0 schema sketch), `:103` (risk table: "Likelihood: Low ... ±3% margin is well below the 10% threshold"); DEC-010 justification 2 (line 32); BL-367 (cross-repo, methodology section)
- **Claim:** The −14.6%±3% number came from a 12-record hand-transcoding of a *planned* schema (single `hierarchy[N]{path,files,sections,top_files}` table) scaled by per-record multipliers; the implemented schema (two tables: `directories[D]{path,files,sections,shown,more}` + per-file `hierarchy[F]{dir,title,sections,path}` rows, plus path-not-title `file` columns) was never measured, so the projection and its ±3% margin do not transfer.
- **Evidence / reasoning:** BL-302 P0 (line 49) specifies `hierarchy[N]{path,files,sections,top_files}:` — one row per directory. The implementation (module docstring, knowledge_summary.py:23-44) split this into two arrays because "a nested dir->files form is not flat-tabular", adding a per-file row with `dir` repeated and a fully-redundant `path` column. BL-367's methodology (per the cross-repo file): incumbent measured in full, alternatives transcoded from a 12-record subset "with per-record multipliers", margin ±3% "assuming within-corpus row-sparsity consistency". A schema with different tables, different columns, and different payload (paths vs titles) is outside that assumption — and F1's measurements show the sign flipped. The risk table's "Low likelihood" rating therefore rested on a measurement of an artifact that was never built. Secondary drift: the P0 sketch in BL-302 was never updated to the implemented schema (the only authoritative schema is the module docstring), and DEC-010's "25 test fixtures to update" / "TOON parser dependency" wording is likewise stale.
- **Recommendation:** Treat measured-schema ≠ implemented-schema as the root-cause lesson for the methodology feedback loop; update BL-302's P0 section to the real schema; require any future format decision to re-measure after implementation, not only at research time (which is exactly what a correctly-ordered C3 does).
- **Confidence:** high on the mismatch (documents disagree on their face); medium on how much of the sign-flip each driver explains (redundancy vs BPE effects — decomposition in F1 supports both).

### F7 — "Structurally valid TOON" has no verification mechanism (and is currently false)
- **Axis:** A/B
- **Severity:** medium
- **Location:** `dsm-docs/plans/BL-302-phase-1.5-toon-migration.md:77` (acceptance criterion), `:95` (dependencies: "TOON Python reference implementation ... if feasible"), `dsm-docs/plans/epoch-5-sprint-17-plan.md:74` (Open Design Question 1, formally unresolved); P2 scope (BL-302:58-61)
- **Claim:** The sprint resolved "emitter vs library" silently in favor of a hand-rolled emitter, and P2's planned assertions (header present, cardinality, field names, row count) are written by the same hand as the emitter — nothing independent ever checks the output against the spec, which is how F2's violations survived to P1b with 701 tests green.
- **Evidence / reasoning:** Open Design Question 1 says "Resolve at the implementation gate (BL-302 P0/P1)" — no decision record resolves it; `pyproject.toml` confirms no TOON dependency exists. The existing P1a tests (TestQuote/TestEmitTable, tests:280-325) assert the emitter's *own* CSV semantics, including the spec-violating colon behavior. There is also currently **no test at all for `_generate_toon_summary`/`generate_knowledge_summary(fmt="toon")`** — the assembler that P2's golden would freeze is untested as of P1b. The markdown side has the same self-referential weakness: the 25 legacy tests are substring checks (e.g. `tests:112` `assert "**./***" in result or "file" in result.lower()` — the first operand is a typo'd pattern that never matches, so the test passes via the vacuous `or` branch), which cannot enforce the byte-identity claim either (I verified it via git instead).
- **Recommendation:** In P2, pin the official TOON Python reference implementation as a **dev-only** dependency (DEC-009 forbids LLM/NLP models, not a parser; BL-302:95 already contemplated it) and add one round-trip test: decode the golden fixture in strict mode, assert section names, row counts, and that path/title/number values survive as strings. Add a markdown golden fixture at the same time.
- **Confidence:** high.

### F8 — The north-star hypothesis is untested and unscheduled; S17 optimizes a proxy it currently pessimizes
- **Axis:** C
- **Severity:** medium (strategically the most important C finding)
- **Location:** `dsm-docs/plans/epoch-5-plan.md` (roadmap S17→S20; success criteria); `dsm-docs/research/2026-04-13_intrinsic-toc-vision.md` (Sprint 16 scope: "Is format parseable for agent navigation?"); sprint-17 plan §Experiment Gate
- **Claim:** Nothing in Epoch 5 measures whether an agent actually orients or navigates better/cheaper with the Intrinsic-ToC than without it — the one claim the entire "README for LLMs" north star stands on — while two sprints (S17 format, S18 Leiden) invest in making the artifact cheaper and richer.
- **Evidence / reasoning:** The roadmap's experiments are: C3 token measurement (S17 — a cost proxy, currently failing per F1), EXP-001 hop-distance/reachability (S19 — validates *parser* output against a reference graph, not agent behavior), and S20 ecosystem materialization. The vision doc itself framed Sprint 16 as testing "can graph topology produce useful orientation? ... Is format parseable for agent navigation?" — no experiment has answered those questions; S17's Experiment Gate explicitly skips ("performance-only sprint"). Meanwhile the token argument is second-order: DEC-010's own counter-claim #1 concedes ~1,350 tokens saved is ~0.7% of a 200K context; a single unnecessary file-read by a disoriented agent costs more than the entire format migration saves — and per F1 the migration currently saves less than zero. If TOON turns out to *also* be marginally harder for agents to reason over than markdown (unvalidated; BL-367's accuracy numbers are the TOON authors' own, as DEC-010 counter-claim #3 concedes), Sprint 17 is net-negative on both axes. This is a locally-sound-but-strategically-unanchored pattern: real measurements, wrong metric.
- **Recommendation:** Add a small agent-navigation experiment (EXP-011-style) to Epoch 5 **before or alongside S18**: same repo, same N navigation tasks ("where is X decided?", "which file defines Y?"), three arms (no ToC / markdown ToC / TOON ToC), measure task success, tool calls, and tokens-to-answer. It directly validates Layers 1-2, tells you whether TOON's format even matters to the consumer, and de-risks S18 (if flat topology doesn't help agents, clusters built on it won't either).
- **Confidence:** high that the gap exists (no such experiment is planned anywhere I or the sub-agents read); medium on how much it would change decisions — that's the point of running it.

### F9 — Identity and dogfooding gap: the "README for LLMs" project has a stale human README and no ToC of its own
- **Axis:** C
- **Severity:** medium
- **Location:** `README.md` (opening framing; v0.4.0, updated 2026-03-17, "Epoch 4 in progress (Sprint 16 complete)"); DEC-010 C4; vision doc Layer 1 (".claude/knowledge-graph.md"); sprint-17 plan Sprint Boundary Checklist ("Repository README updated")
- **Claim:** The README still opens "Repository integrity validator and graph database explorer...", mentions the Intrinsic-ToC only once in a Future section, and the repo does not ship its own knowledge summary at the vision's named location `.claude/knowledge-graph.md` (verified absent) — the knowledge-cartographer identity exists only in dsm-docs.
- **Evidence / reasoning:** The brief flags the README-vs-vision tension; it's real and compounding: three sprints of north-star work (S16-S17 + the S49-S50 Layer 4.5/DEC-011 research) are invisible to a newcomer — or to an *agent* — reading the repo top-level. The sprint boundary checklist has required "Repository README updated (status, results, structure)" every sprint, and it hasn't happened since 2026-03-17, so the process control exists but isn't executing (light-session chains defer it, per the S51 checkpoint's own deferred-items warning). Dogfooding matters doubly here: GE's own committed Intrinsic-ToC would be both the best demo and a standing regression corpus for exactly the kind of defect F1/F4 surfaced.
- **Recommendation:** Elevate DEC-010 C4 from "one-line TOON note" to a README re-framing (validator → knowledge cartographer, with the validator as the founding capability), and commit GE's own generated `.claude/knowledge-graph.md` as part of Sprint 17's docs deliverable.
- **Confidence:** high on facts; medium on priority relative to code work.

### F10 — Top-N boundary ties depend on graph insertion order
- **Axis:** A
- **Severity:** low
- **Location:** `src/analysis/knowledge_summary.py:209-210` (`_hub_rows`: `sorted(..., key=lambda x: x[1], reverse=True)` then `ranked[:n]`), `:297-299` (`_hotspot_rows` same pattern)
- **Claim:** Hubs and hotspots sort only on the count; Python's stable sort breaks ties by dict/node insertion order, so which item makes the top-10/top-20 boundary — and row order among ties — is not a function of the graph's content.
- **Evidence / reasoning:** Node order in networkx follows insertion order from graph construction, which depends on file-walk order in the builder. A golden fixture freezes one such ordering; any later change to parse order, or an OS-level directory-order difference, reorders tied rows and flips boundary inclusion, producing spurious golden diffs (or worse, masking real ones). Same applies to the markdown path, but the golden-freeze makes it acute now.
- **Recommendation:** Add a deterministic secondary key before P2: `key=lambda x: (-count, path)` for hubs and `(-refs, file, section)` for hotspots.
- **Confidence:** high on the mechanism (code is explicit); low on near-term probability of it biting.

### F11 — Empty-section headers use a form the spec doesn't define
- **Axis:** A
- **Severity:** low
- **Location:** `src/analysis/knowledge_summary.py:74-77` (`emit_table` empty case); `tests/test_knowledge_summary.py:314-316`; S51 checkpoint lines 22-23 ("Empty sections emit `[0]` zero-cardinality headers")
- **Claim:** Empty arrays emit `hub[0]{rank,file,incoming_refs,top_section}:`; spec §9.1 says encoders SHOULD emit `key: []` and MAY emit legacy `key[0]:` — the fields-block-plus-zero form is neither of the enumerated forms decoders MUST accept.
- **Evidence / reasoning:** SPEC.md line 419: "Empty arrays (object field position): encoders SHOULD emit `key: []`. Encoders MAY emit the legacy header form `key[0<delim?>]:`"; line 426 enumerates what decoders MUST accept — `key: []`, `[]`, `key[0<delim?>]:`, `[0<delim?>]:`. A zero-row tabular header with a fields segment is arguably grammar-reachable via §9.3, so a lenient decoder may take it; but the "schema contract" argument (keeping field names visible when empty) is a deliberate dialect choice that should be recorded, or the canonical `key: []` adopted, before the golden freezes it.
- **Confidence:** medium — the spec text is clear on canonical forms, but whether `[0]{fields}` strictly errors is decoder-dependent; I did not run a reference decoder against it (see Limits).

### F12 — `emit_table`'s non-comma delimiter path emits an undeclared delimiter
- **Axis:** A
- **Severity:** low
- **Location:** `src/analysis/knowledge_summary.py:77` (`header = f"{name}[{len(rows)}]{{{delim.join(fields)}}}:"`); `tests/test_knowledge_summary.py:302-304` (tab quoting tested, header form not)
- **Claim:** For `delim="\t"` the header comes out `t[1]{a\tb}:` but spec §11 requires the delimiter symbol inside the bracket segment (`t[1<TAB>]{a<TAB>b}:`); absent it, a decoder assumes comma and mis-splits every row.
- **Evidence / reasoning:** Probe output: `emit_table('t',['a','b'],[('1','2')], delim='\t')` → `'t[1]{a\tb}:\n  1\t2'`. SPEC.md §11: "Tab: header includes HTAB inside brackets and braces (e.g., `[N<TAB>]`, `{a<TAB>b}`)... Comma (default): header omits the delimiter symbol." Production only uses comma today, so this is latent — but the parameter is public API and partially tested, i.e., it looks supported.
- **Recommendation:** Either emit the delimiter marker in the bracket/braces segments or drop the `delim` parameter until needed (YAGNI cuts both ways).
- **Confidence:** high.

### F13 — Schema omits line pointers the vision says Layer 2 needs
- **Axis:** C (schema/strategy seam)
- **Severity:** low
- **Location:** TOON schema (knowledge_summary.py:26-47) — no `line` column anywhere; SECTION nodes carry `line` (see `tests/test_knowledge_summary.py:40-61`, graph builder attaches it); vision doc Layer 2 ("file and line pointers for every item")
- **Claim:** The golden fixture is about to freeze a schema with no line numbers, though the data is already on every SECTION node and the vision names "linkable for drill-down (file and line pointers)" as a defining Layer-1/2 property.
- **Evidence / reasoning:** Adding `line` to `hotspots` (and optionally a `line` for the `top_section` in `hub`) costs a few tokens per row now; adding it after P2/P4 is a schema migration with a golden-fixture change and consumer notice. Given F1 already forces a schema revision, this is the moment to decide it deliberately (even a documented "no, deferred" beats freezing by omission).
- **Confidence:** medium — it's a judgment call on scope, flagged because the freeze makes it time-sensitive.

### F14 — Silent format fallthrough in the API
- **Axis:** A
- **Severity:** low
- **Location:** `src/analysis/knowledge_summary.py:480-481` (`if fmt == "toon": return _generate_toon_summary(G)` — anything else falls through to markdown)
- **Claim:** `generate_knowledge_summary(G, fmt="json")` (or a typo like `"TOON"`) silently returns markdown instead of raising, so a future non-CLI caller (Central-side scripts, P3 measurement harness) can measure/consume the wrong format without noticing.
- **Evidence / reasoning:** The CLI is protected by `click.Choice(["markdown","toon"])` (`src/cli.py:439`), but the module-level API — the thing BL-302 positions as the reusable artifact — has no guard. A one-line `raise ValueError(f"unknown format: {fmt!r}")` for unrecognized values closes it.
- **Confidence:** high.

---

## 3. Per-axis narrative

### Axis A — Code correctness (pre-P2 golden freeze)

**Is the emitter P2-ready? No — do not freeze the golden fixture yet.** The refactor plumbing is genuinely solid: I verified the headline "markdown byte-for-byte identical" claim adversarially — extracted the pre-Sprint-17 emitter from git (`7b9c7c8`), ran old and new on the same real exported graph and on a synthetic adversarial graph, and both were byte-identical — and the 4 row helpers are a faithful single source for both paths (the markdown generators consume them exactly; hub/orphan carry `title` alongside path so each path picks its column). The suite reproduces at 701 passed / 1 skipped. Cardinality headers always match emitted row counts, blank-line block separation is tolerated by spec §12, key names are spec-legal, and the empty graph degrades cleanly.

But what the golden would freeze is wrong in three independent ways: the output is not spec-TOON (F2 — CSV escapes, unquoted colons/numeric-like strings, literal newlines; one unit test asserts the violation), it silently misreports the repository (F4 — 15 orphans shown where 110 exist, no total), and the schema itself is the direct cause of the failed token gate (F1 — triple path redundancy in `directories`/`hierarchy`, paths-for-titles in `hub`/`orphans`). Smaller pre-freeze items: non-deterministic tie-breaks (F10), the non-canonical `[0]{fields}` empty form (F11), the tab-delimiter header bug (F12), and the silent `fmt` fallthrough (F14). Note also that as of P1b there is **no test at all** covering `_generate_toon_summary` — the assembler the golden would canonize is untested. Every one of these is cheap to fix now and expensive after P2/P4.

### Axis B — Plan / decision soundness

**The ≥10% threshold was internally coherent but is now empirically dead.** Against BL-367's −14.6%±3%, a ≥10% gate left ~1.6 points of margin — defensible *for the schema BL-367 measured*. The implemented schema is a different artifact (F6), and when I ran the actual C3 measurement today, the fairest configuration (relative paths, same-day paired baseline, full Central corpus) gives TOON **+1.74% more** tokens; every other configuration is worse. The gate fails, full stop — and the plan's "Low likelihood" risk rating for exactly this outcome was never grounded in a measurement of the real schema.

The tiktoken `cl100k_base` proxy is acceptable *for the relative TOON-vs-markdown comparison* (same tokenizer both sides; DEC-010 counter-claim #5 reasons correctly about ranking stability), though the absolute "≥10%" reading inherits ±5-15% tokenizer uncertainty for the actual Claude consumer. The **9,309-token baseline is not valid** (F3): the corpus has grown 811→1,097 files (+6.7% markdown tokens) and the number is invocation-dependent (absolute-path runs inflate everything ~40%; the recorded baseline is consistent with an absolute-path run). Comparing cross-invocation can manufacture a −24% "pass" out of a true +1.7% loss. P3 must be same-day, same-invocation, paired.

Sprint 17 scope is otherwise right-sized (flag, emitter, tests, gate, docs; jsonl and default-flip correctly deferred), with two structural flaws: P2 before P3 is backwards (F5 — the gate costs minutes and fails today; the golden would have frozen a schema that has to change), and no phase independently verifies "structurally valid TOON" (F7 — hand-rolled emitter, self-referential tests, open design question #1 resolved silently). The C3-gate discipline itself deserves credit — a decision with a falsifiable kill-switch is good methodology — it just needs to run earlier, against an honest baseline, on the schema as built.

### Axis C — Strategic alignment (north star)

**Directionally aligned, but optimizing an unvalidated proxy — and currently pessimizing even that.** Reducing the Intrinsic-ToC's token cost genuinely serves the "README for LLMs" north star, and the TOON bet was made with real measurements and recorded counter-evidence. But the chain has an unexamined link: no experiment anywhere in Epoch 5 tests whether an agent navigates better or cheaper with the Intrinsic-ToC at all, in either format (F8). The vision document itself posed the question ("Is format parseable for agent navigation?") at Sprint 16 and it remains unanswered while S17 spends 1-1.5 sessions on format mechanics that today yield negative token savings (F1) and strictly less information (F4). The dropped overflow totals are the sharpest strategic irony: a self-describing-repository artifact that under-reports the repo's own orphan problem 15-vs-110 fails at self-description, in exactly the dimension (integrity signals) that is GE's founding competence.

The README-vs-vision tension is real but is the symptom, not the disease (F9): the identity migration (validator → knowledge cartographer) has happened in dsm-docs and nowhere user-facing, and the repo doesn't dogfood its own ToC at the vision's named location. **Roadmap adjustments:** (1) insert a cheap agent-navigation A/B experiment before S18 — it validates Layers 1-2, arbitrates markdown-vs-TOON on the metric that matters (agent task performance, not just tokens), and de-risks Leiden; (2) gate S18's cluster *output format* on a C3-style measurement of the *implemented* cluster schema, applying F6's lesson; (3) fold the README re-framing and a committed `.claude/knowledge-graph.md` into S17's C4 docs work; (4) S19/S20 ordering is fine — EXP-001 hop-distance is parser validation, orthogonal to the above; keep it.

---

## 4. Top-3 priorities

1. **Run the honest C3 gate now and let it fail loudly, before P2** — same-day paired baseline, relative paths, full Central corpus (my measurement: TOON +1.74%, needs −10%) — because DEC-010's own condition says halt-and-revisit, and every hour of P2/docs work before that reckoning is spent enshrining a schema that cannot ship.
2. **Redesign the schema and fix the emitter in one pass, then freeze the golden**: de-duplicate `hierarchy`/`directories` (drop the redundant `path` column; reconsider path-vs-title per table), add `hotspots_total`/`orphans_total` to the summary block, make `_quote` spec-conformant (backslash escapes; quote colons/numeric-like/edge values), add deterministic tie-breaks — then write P2's golden plus a strict-mode round-trip against the pinned reference TOON decoder.
3. **Add an agent-navigation experiment to Epoch 5 ahead of S18** (no-ToC vs markdown-ToC vs TOON-ToC on fixed navigation tasks; measure success, tool calls, tokens) — the north star claims agents orient better with an Intrinsic-ToC, nothing has ever tested it, and both the TOON bet and the Leiden bet are downstream of the answer.

---

## 5. Confidence and limits

**Most sure (invite adjudication here first — it's all reproducible):** the token measurements (F1/F3) — exact commands are quoted in the findings and re-runnable in minutes; the markdown byte-identity verification (git `7b9c7c8` vs HEAD, identical on two graphs); the emitter-vs-spec divergences (F2/F11/F12) — spec sections read directly and quoted, violations reproduced both in unit probes and in real corpus output; the orphan-truncation data loss (F4, 15-vs-110 on GE's own corpus).

**Least sure / not verified:**
- I did **not** run a reference TOON decoder against the output (none is installed; adding one was outside read-only scope). My strict-mode failure claims in F2/F11 derive from spec text, not an executed parser — a lenient decoder may accept more than the spec promises. This is the single best place for Opus to probe.
- The 91% coverage figure: I re-ran the suite (701/1 confirmed) but not the coverage measurement.
- BL-367's internals reached me via a Haiku summary; I cross-checked its key numbers (444→379 tokens, −14.6%, ±3%, 9,309, char-ratio 1.44) against DEC-010's independent citations and they agree, but I did not personally read the 364-line file.
- The claim that the April 9,309 baseline was an absolute-path run is an inference from consistency (my absolute run: 9,936 at +35% file growth; my relative run: 6,952), not from a recorded protocol — which is itself the F3 problem.
- Axis C recommendations (F8/F9/F13) are judgment calls on priority; the underlying facts (no such experiment planned; README stale; no line columns; no committed ToC) are verified.
- GraphML round-trip caveat on the byte-identity check: both emitter versions consumed the same loaded graph, so refactor-equivalence holds regardless, but attribute coercion in GraphML means this isn't a byte-level check of the *CLI pipeline* end-to-end (the CLI-generated markdown was, however, produced by the same shared helpers).
