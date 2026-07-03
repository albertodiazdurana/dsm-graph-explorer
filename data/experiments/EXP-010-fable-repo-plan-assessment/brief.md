# Brief for Fable 5 — Independent Assessment (EXP-010)

You are **Fable 5**, brought in as an **independent, adversarial reviewer** of the
DSM Graph Explorer repository and its current plan. Your assessment is not
decorative: another model (Opus 4.8) will **adjudicate every finding you make
against the actual code and tests**, so precise, verifiable, actionable findings
are what matter. Generic praise or unfalsifiable observations are worthless here.

**Repo root:** `/home/berto/dsm-graph-explorer` (all repo-relative paths below are
from here). One path is cross-repo and absolute.

---

## 0. How to work (token economy)

You are the expensive, analytical resource. **Delegate token-cheap gathering to
lighter models** (spawn cheaper sub-agents to read and summarize the Tier 2
context files below, or to collect mechanical facts like line counts, test names,
and where a symbol is defined). **Reserve your own reasoning for the critical and
analytical work**: judging correctness, soundness, and strategic alignment. Do not
spend your own budget reading large context files you can have a cheaper model
summarize first.

**Constraints:**
- **Read-only** on all source, tests, and docs. Do **not** modify any code or test.
- Your **only write target** is `data/experiments/EXP-010-fable-repo-plan-assessment/results.md`.
  Write your findings there, in the format specified in Section 5.
- Stance: **adversarial** — actively hunt for gaps, risks, and defects. Confirmation
  is cheap; independent skepticism is the value you add.

---

## 1. Project North Star (the highest-level objective)

Graph Explorer (GE) began as an integrity validator for DSM / Take-AI-Bite
documentation (parse markdown, extract cross-references, flag broken links and
version mismatches). Since Sprint 16 it has grown toward a larger north star:
**make a repository self-describing to LLM agents, a "README for LLMs."** GE
computes an **Intrinsic-ToC**, a repository's knowledge graph materialized into a
structured, machine-parseable, human-readable file that an agent reads for
orientation and uses as the entry point for deeper navigation. Defining stance:
**the agent IS the query engine**, no MCP, no API, no local LLM (DEC-009). GE is a
"knowledge cartographer": it computes navigation aids (hubs, hotspots, orphans,
hierarchy, and eventually cross-repo avatars and code/concept ontologies) so any
consuming agent can traverse a codebase by reasoning over structure rather than
embedding-search. The **TOON migration (Sprint 17)** serves this by cutting the
token cost of the Intrinsic-ToC, making the "README for LLMs" cheaper for the
consuming agent to read.

---

## 2. Context: where the work stands

The `--knowledge-summary` command produces the Intrinsic-ToC. Sprint 17 (BL-302
Phase 1.5, decision DEC-010) is migrating its output format from mixed markdown to
**TOON** (a compact tabular notation) to reduce token cost. Progress so far:
P0 (schema) + P1a (emitter helpers) + P1b (TOON emit path + `--format {markdown,toon}`
CLI routing) are done; the markdown output is byte-for-byte unchanged; suite is
701 passed / 1 skipped / 91% coverage.

**Remaining and imminent:** P2 will write `tests/fixtures/knowledge-summary.toon`
as a **golden fixture**, which *freezes* whatever the emitter currently produces.
This is why your code review matters **now**: a defect found after P2 is enshrined
in the golden file. P3 is the DEC-010 **C3 validation gate** — require **≥10%**
measured token savings (tiktoken `cl100k_base`) versus the ~9,309-token markdown
baseline before flipping the default to TOON.

---

## 3. Read set (tiered)

### Tier 1 — read directly and deeply (this is your core analytical material)
- `src/analysis/knowledge_summary.py` — the TOON emitter (`_generate_toon_summary`),
  the TOON schema/constants, and the 4 pure row helpers (`_hierarchy_rows`,
  `_hub_rows`, `_hotspot_rows`, `_orphan_rows`).
- `src/cli.py` — the `--format` routing and how `generate_knowledge_summary` is called.
- `tests/test_knowledge_summary.py` — current test coverage (what P2 will parameterize).
- `dsm-docs/decisions/DEC-010-toon-migration-format.md` — the decision + the C3 gate.
- `dsm-docs/plans/epoch-5-sprint-17-plan.md` and
  `dsm-docs/plans/BL-302-phase-1.5-toon-migration.md` — sprint/backlog scope.
- `dsm-docs/checkpoints/done/2026-07-03_s51_checkpoint.md` — current state + settled
  design points (note the deliberate design choices: TOON `file` columns carry the
  node-id path not the display title; the hotspots overflow note is dropped in TOON).

### Tier 2 — delegate to cheaper models to gather/summarize for you
- `dsm-docs/plans/epoch-5-plan.md` — the roadmap (S17 → S18 Leiden → S19 hop
  distance/EXP-001 → S20 ecosystem/avatar).
- `dsm-docs/decisions/DEC-009-no-local-llm-dependencies.md` — the architectural constraint.
- `dsm-docs/research/2026-04-13_intrinsic-toc-vision.md` — the full vision (4 layers + 4.5).
- `/home/berto/dsm-agentic-ai-data-science-methodology/dsm-docs/plans/done/BACKLOG-367_knowledge-summary-format-research.md`
  — **cross-repo, read-only.** The original token-reduction research (~14.6% ±3%)
  that the ≥10% C3 threshold rests on. Use it to judge whether that threshold is
  well-founded.
- `MEMORY.md` (project root), `README.md`, `pyproject.toml` — orientation. Note the
  README still frames GE as an integrity validator and may be stale.

---

## 4. Your three review axes and questions

### Axis A — Code correctness (before the P2 golden-fixture freeze)
- Does `_generate_toon_summary` produce valid, self-consistent TOON? Are the
  cardinality headers (e.g. `[0]` for empty sections), column schemas, and
  separators correct and internally consistent?
- Are the 4 row helpers a faithful single source of truth for both the markdown
  and TOON paths (the claim is markdown output is byte-identical after refactor)?
- Edge cases: empty graph, single-node graph, very large graph (bounded-output
  budget), unusual paths/titles, the dropped hotspots overflow note, path-vs-title
  column choices. Any correctness or data-loss bug that would be **frozen** by P2?
- Is anything about to be enshrined in the golden fixture that *should* change first?

### Axis B — Plan / decision soundness
- Is the **≥10% C3 threshold** well-founded against the BL-367 ~14.6% ±3% measurement?
  Is measuring with tiktoken `cl100k_base` on the Central corpus a valid proxy, and
  is the 9,309-token baseline the right comparison? What could make the gate pass or
  fail spuriously?
- Is Sprint 17 correctly scoped (P2 test migration, P3 gate, docs)? Anything missing,
  mis-ordered, or over/under-specified?

### Axis C — Strategic alignment (the north star)
- Is the current work (TOON migration, and the P0–P3 discovery so far) genuinely
  serving GE's highest-level objective, or is any of it locally sound but
  strategically off-track? Weigh the **README-vs-vision framing tension** explicitly
  (validator identity vs. knowledge-cartographer / "README for LLMs" identity).
- Given the north star, what **adjustments or additions to the Epoch 5 roadmap**
  (S17 TOON → S18 Leiden clustering → S19 hop distance/EXP-001 → S20 ecosystem/avatar)
  are worth considering: reordering, missing steps, over-investment, or a
  higher-leverage path?

---

## 5. Output format (write into `results.md`)

Write your assessment into
`data/experiments/EXP-010-fable-repo-plan-assessment/results.md`, using the template
already in that file. For **every finding**, provide:

- **ID** — F1, F2, …
- **Axis** — A (code) / B (plan) / C (alignment)
- **Severity** — high / medium / low
- **Location** — `file:line` for code, or doc + section for plan/alignment
- **Claim** — one sentence: what is wrong, risky, or misaligned
- **Evidence / reasoning** — why, grounded in what you read (cite specifics)
- **Recommendation** — the concrete change or decision you propose
- **Confidence** — high / medium / low (be honest; low-confidence findings are fine
  if flagged as such)

Then add, per axis, a short **narrative summary** answering the questions in
Section 4, and a final **top-3 priorities** list (the three things you would do
next if this were your project). Note anything you could NOT verify and why.

Remember: Opus will adjudicate each finding against the code. Make it easy to
confirm you right (or wrong) — cite `file:line` and quote the relevant snippet.
