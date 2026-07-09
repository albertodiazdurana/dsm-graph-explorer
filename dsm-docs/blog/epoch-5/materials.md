# Epoch 5 Blog Materials

## Article: "How a Fleet of Agents Red-Carded My Own Decision" (multi-agent as decision instrument, TOON red-carded)

**Angle:** methodology-as-instrument, framed around the 2026 FIFA World Cup "red card".
**Audience:** technically literate agentic-AI / DSM practitioners.
**Length:** ~1,500-2,000 words.
**Draft file:** `2026-07-06-multi-agent-red-card.md`.

### The arc in one paragraph

Sprint 17 committed to migrating the Intrinsic-ToC ("README for LLMs") from Markdown
to TOON to save ~10% of the tokens every consuming agent pays (DEC-010). A multi-agent
adversarial assessment (EXP-010) found the migration actually *increased* tokens (F1)
and surfaced the deeper blind spot (F8): no experiment anywhere had tested whether the
ToC helps an agent navigate at all, in any format. A second, pre-registered multi-agent
A/B (EXP-011) then validated the ToC and reversed the TOON bet. Both experiments were
themselves multi-agent orchestrations, used as a decision instrument to make and then
unmake an engineering call.

### Key figures (verified, from experiment records)

- **EXP-010** (2026-07-03): Fable-5 orchestrator + 9 Haiku gatherers, adjudicated by
  Opus 4.8. ~270-300K tokens, ~65-70% delegated to the cheaper model. 14/14 findings
  CONFIRMED; the load-bearing token measurement reproduced by Opus to the token.
- **F1:** implemented TOON costs MORE tokens than markdown on every real corpus:
  GE `dsm-docs/` +7.58% (2,903 md vs 3,123 TOON), DSM Central +1.74%. Gate needed -10%.
  Cause: BPE penalizes comma-adjacent long paths; fewer characters, more tokens.
- **F8:** the north-star hypothesis (agents navigate better/cheaper with the ToC) was
  never tested; Sprint 17 optimized a proxy (tokens) it was currently pessimizing.
- **EXP-011** (2026-07-06): 24 fresh isolated `general-purpose` subagents across two
  Workflows (6-run pilot + 18-run batch), 8 navigation tasks x 3 arms, arms blind.
  644,100 subagent tokens, 87 tool-uses, ~9.5 min wall-clock, 1 recovered error.
- **Per-arm rollup:** A0 no-ToC 4/8 success, mean 3.75 tool calls; A1 markdown 8/8,
  0.625; A2 TOON 7/8, 0.625. ToC arms ~6x fewer tool calls AND more accurate.
- **The red card (T3, orphan count):** markdown -> 112 (correct), TOON -> 15 (wrong,
  ~97 undercount via F4 dropped overflow total). Predicted before the run, occurred exactly.

### Metaphor map (frame, used sparingly)

| Football | Post |
|---|---|
| Red card / sent off | TOON not adopted (DEC-010 Amendment 2) |
| Pre-match scouting report | EXP-010 adversarial assessment |
| On the pitch | EXP-011 A/B navigation experiment |
| VAR / video replay | tool-calls counted from agent transcripts, not self-report |
| Pre-registered team sheet | success criteria + answer key fixed before kickoff |
| Injury time | the honest caveats section |

### Root-cause framing (the spine of the post)

Two nested errors, and the deeper one is about the metric:

1. **Execution failure (surface):** TOON was selected to reduce context consumption
   and it did the opposite, it added tokens (F1). It failed its own chosen test.
2. **Framing failure (root):** "reduce context consumption" was a **proxy metric**.
   The real objective is agent **navigation performance**, does the agent orient
   faster, cheaper, and correctly. TOON was picked to optimize the proxy; measured on
   the real objective it *punished* performance (the orphan-count red card). The
   original error was not picking TOON, it was picking the metric formats were judged by.

The fleet's real contribution: it caught a bad **success metric**, not just a bad format.
Section 2 names the proxy-metric selection openly; Section 5 lands this as the root lesson.

### Three transferable lessons (the payload)

1. Pre-register success criteria AND the ground-truth answer key before running, so the
   decision falls out mechanically.
2. Verify agent output against transcripts, do not trust self-report (pilot validated
   transcript counts == self-report, so the batch could rely on it).
3. Test the north-star claim, not a cheap correlated proxy (tokens); a single wrong
   navigation costs more than the whole migration saved.

### Honesty constraints (state plainly)

- n=8, one run per cell: directional, not statistical.
- T4 was a flawed unscoped task (answered repo-wide); excluded as discriminating evidence.
- `tokens_to_answer` weakly metered per arm; quantitative claims lean on tool_calls +
  success rate + the static ToC token cost.

### Source pointers

- `data/experiments/EXP-011-agent-navigation-toc/` (EXP-011.md, results.md incl. process appendix, tasks.md, arm-inputs/)
- `data/experiments/EXP-010-fable-repo-plan-assessment/` (EXP-010.md, results.md F1-F14, brief.md)
- `dsm-docs/decisions/DEC-010-toon-migration-format.md` (Amendment 2)
- `dsm-docs/plans/BL-302-phase-1.5-toon-migration.md` (Resolution)
- `dsm-docs/research/2026-04-13_intrinsic-toc-vision.md` (north-star context)
