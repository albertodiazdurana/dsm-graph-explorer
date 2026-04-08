# Session 46 Methodology Feedback

**Date:** 2026-04-08
**Session:** 46
**Project:** dsm-graph-explorer

---

## Entry 58: Session Transcript Protocol self-check has a pure-reasoning-turn hole

**Context:** DSM_0.2 Session Transcript Protocol requires thinking to be appended to `.claude/session-transcript.md` as the first tool call of every turn, with an output summary appended as the last tool call. A turn-boundary self-check rule states (paraphrased from the project CLAUDE.md reinforcement block):

> "If your first tool call this turn was not a transcript append **and the turn requires any tool calls**, the protocol was violated."

**Incident:** In Session 46, while evaluating a Sprint 16 decision gate, the agent produced a ~60-line analysis (five-question evaluation, Option A vs Option B comparison, recommendation, proposed sprint shape) as a pure-text turn with **zero tool calls**. No thinking was appended to the transcript. The user noticed ("we are not writing in the session-transcript now. Why?") and the agent recovered with a `[RETROACTIVE]` entry.

**Root cause:** The self-check rule has an `AND` clause: "first tool call was not a transcript append **AND** the turn requires any tool calls." A pure-reasoning turn (decision analysis, recommendation, conceptual Q&A, trade-off discussion) has zero required tool calls, so the second conjunct is false, and the self-check never fires. The protocol violation is invisible to the agent: from the agent's perspective, there is nothing to "recover" because no rule was triggered.

**Why this matters:** Pure-reasoning turns are disproportionately high-value thinking to capture. They contain:
- Decision rationale (why Option A, not B)
- Considered-and-rejected alternatives
- Risk assessments and hedges
- Narrative framing that shapes downstream execution

This is exactly the content process narration is designed to preserve. Losing it means the transcript captures the *mechanical* reasoning (what tools to call, what files to read) but not the *judgment* reasoning. Reasoning-efficiency analysis (the stated primary consumer of transcripts) gets the shell without the substance.

**Observed failure mode:** The agent, having no self-check trigger, treats chat output as sufficient documentation. The analysis lives only in the conversation stream and is lost on conversation compaction, or on any future session reading the archived transcript.

**Proposed methodology change:** Remove the `AND the turn requires any tool calls` conjunct from the self-check rule. Every turn appends thinking, full stop. A pure-reasoning turn still requires one tool call (the transcript append), which is consistent with the "first tool call of every turn is a transcript append" framing already in the protocol. The `AND` clause appears to have been added to avoid requiring transcript entries for trivial acknowledgments ("OK, proceeding"), but that optimization leaks: it also exempts the turns where thinking matters most.

**Alternative framing:** If the concern is that one-word acknowledgments don't warrant a transcript entry, the exemption should be on *content triviality* ("no new reasoning this turn"), not on *tool-call count*. A turn that produces a multi-paragraph decision analysis is never content-trivial, regardless of whether it touches files.

**Implication for DSM_0.2:** The Session Transcript Protocol section should:
1. State the rule positively: "Every turn begins with a transcript append. Every turn."
2. Remove or rewrite the self-check `AND` clause.
3. Add an explicit example of the pure-reasoning-turn failure mode so future agents recognize it.
