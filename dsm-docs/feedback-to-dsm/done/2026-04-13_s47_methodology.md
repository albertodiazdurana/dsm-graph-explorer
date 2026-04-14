# Session 47 Methodology Feedback

**Date:** 2026-04-13
**Project:** DSM Graph Explorer
**Session:** 47

---

## Entry 59: PGB Concept Gate Granularity Gap

**Section:** DSM_0.2 §17.1 (Pre-Generation Brief Protocol)
**Score:** 6/10 (protocol worked at BL level but failed at module level)
**Context:** Sprint 16 implementation of `--knowledge-summary` (BL-302 Phase 1)

### Observation

The four-gate PGB was applied correctly at the backlog item level: BL-302 received a concept brief (what/why/how), user approved, Sprint 16 was scoped. However, when implementing the core module (`knowledge_summary.py`), the agent skipped the concept gate for the module's internal design decisions and went directly from codebase exploration to TDD + code.

The result: a module was built with an unbounded hierarchy component that would produce ~4,700 lines for DSM Central (202 files, 4,501 sections), far exceeding the 150-200 line output target. The user caught this during review, but the concept gate should have caught it before any code was written.

### What was skipped

The concept gate for the module should have covered:
- **Condensation rules:** How does each component filter 4,703 nodes into its output budget?
- **Line budget allocation:** ~200 lines split across 4 components (how many lines each?)
- **Threshold decisions:** Why threshold=10 for hotspots? Why top-10 for hubs?
- **What gets cut:** The hierarchy can't list everything, what's the truncation strategy?

Instead, the agent presented function signatures (names + brief descriptions) and treated user approval of that list as concept gate approval. Function signatures describe *what exists*, not *how it decides*.

### Root cause

The PGB says "concept (explain) → implementation (diff review) → run" but does not specify **gate granularity**. For simple artifacts (bug fix, config change), one concept gate at the task level is sufficient. For complex artifacts with internal design decisions that affect behavior, the concept gate needs to cover those decisions, not just the artifact's existence.

The gap: the PGB doesn't distinguish between "concept of the artifact" and "concept of the artifact's internal logic." For BL-302, the artifact concept was well-defined (produce markdown summary from graph). The internal logic concept (how to compress, what rules, what thresholds) was never presented.

### Proposal #52: PGB Gate Granularity Guidance

Add a note to the PGB concept gate definition:

> For complex artifacts (modules with multiple internal design decisions, algorithms with configurable thresholds, output formats with size constraints), the concept gate covers the artifact's internal logic, not just its existence. Present: what decisions the artifact makes, what rules govern those decisions, and what gets excluded. Function signatures are implementation briefs, not concept briefs.

**Trigger heuristic:** If the artifact has parameters that affect what appears in the output (thresholds, top-N limits, depth limits, line budgets), those parameters and their rationale are concept-gate material.

---

## Entry 60: Vision Without Speculative Implementation

**Section:** DSM_6.0 §1.9 (Think Ahead)
**Score:** 7/10 (principle is implicit but not stated explicitly)
**Context:** Sprint 16 design discussion for BL-302

### Observation

During Sprint 16 design, the agent proposed a data/format separation to enable
future JSON and MCP output. The user identified this as speculative: Sprint 16
only needs markdown, no second format is planned. The tension: the Intrinsic-ToC
vision spans four layers and multiple phases. The plan SHOULD have vision. The
implementation SHOULD NOT.

### Proposal #53: Addition to §1.9 Think Ahead

> **Vision-directed, deliverable-scoped.** Plans should articulate the full
> vision (layers, future phases). Implementation should target only reachable,
> urgent deliverables. The vision justifies the direction; the deliverable
> justifies the code. If a design choice only pays off in a future phase with
> no concrete timeline, document it in a research doc, do not implement it.

**Target section:** §1.9 Think Ahead. Open to discussion on exact placement
when the BL is implemented.

---

## Entry 61: Sprint Boundary Checklist Has No Automatic Trigger

**Section:** DSM_0.2 (Session Wrap-Up protocol, sprint boundary gate)
**Score:** 5/10 (protocol exists but enforcement relies on agent memory)
**Context:** Sprint 16 Phase 1 completed in S47; agent suggested session wrap-up
without executing the Sprint Boundary Checklist

### Observation

CLAUDE.md defines a 7-item Sprint Boundary Checklist (checkpoint, feedback,
decisions, blog journal, README, epoch plan, hub/portfolio notification) that
should run when a sprint completes. S47 completed Sprint 16 Phase 1 and the
agent suggested "wrap up" as the next step, meaning session wrap-up via
`/dsm-wrap-up`. The user caught the gap: Sprint 16 is a SPRINT boundary, not
just a session boundary, and should trigger the 7-item checklist before any
session-level wrap-up.

The agent did some checklist items implicitly (feedback files, decision log,
Central notification) during the session, but never:
- Updated the epoch plan to mark Sprint 16 COMPLETE
- Created a Sprint 16 checkpoint
- Wrote a Sprint 16 blog journal entry
- Updated the repository README
- Notified the portfolio
- Ran through the checklist as a formal closure step

### Root Causes

1. **No automatic trigger.** The checklist is a "remember to do this" item in
   CLAUDE.md, not a skill that auto-runs when a sprint is marked complete.
   `/dsm-wrap-up` handles session-end tasks but does not detect sprint
   boundaries and does not trigger the 7-item checklist.

2. **Vocabulary collision.** "Wrap up" is used for both session-end and
   sprint-end. Without an explicit distinction, the agent defaults to the
   more frequent scope (session).

3. **No gate check in the wrap-up flow.** The agent's decision to suggest
   wrap-up did not include a "is this a sprint boundary?" check. The Session
   Wrap-Up protocol in CLAUDE.md does not cross-reference the Sprint
   Boundary Checklist as a precondition.

4. **Implicit completion vs explicit closure.** The agent said "Sprint 16
   Phase 1 is substantially complete" multiple times without executing the
   boundary transition. Verbal acknowledgment of completion is not the same
   as formal closure.

### Proposal #54: Sprint Boundary Gate in Wrap-Up Flow

Three complementary changes:

1. **Add to `/dsm-wrap-up` (scripts/commands/dsm-wrap-up.md):** A pre-step
   that detects sprint boundaries by comparing the epoch plan's active
   sprint status against session state. If the active sprint appears
   complete (all sprint deliverables checked off OR user marked complete),
   the wrap-up skill must execute the Sprint Boundary Checklist before
   session-level wrap-up tasks.

2. **Add to CLAUDE.md sprint boundary section:** An explicit gate statement:

   > **Sprint boundary gate (before any wrap-up):** If this session completed
   > a sprint (evidenced by the sprint's deliverables being done, status
   > line ready to change from IN PROGRESS to COMPLETE), run the Sprint
   > Boundary Checklist before suggesting session wrap-up. Do not conflate
   > session-end with sprint-end.

3. **Add a `/dsm-sprint-boundary` skill** (optional, user-invocable) that
   walks the 7-item checklist interactively, prompting for each item and
   confirming completion before proceeding.

### Expected Impact

Prevents sprints from being informally "substantially complete" without the
formal closure artifacts (checkpoint, README update, portfolio notification).
Closes the gap between agent's verbal acknowledgment of completion and the
checklist's procedural requirements.

---

## Entry 62: Sprint Checklist Verification Without Reconciliation

**Section:** DSM_0.2 (Session Wrap-Up / Sprint boundary gate / `/dsm-go` Step 3.6)
**Score:** 5/10 (verification runs but documentation does not)
**Context:** Sprint 15 marked COMPLETE in S46-S47 with verbal confirmation of
all 7 boundary items; epoch plan's own Sprint 15 checklist still shows 1/7
boxes checked

### Observation

Entry 61 addresses the gap where the sprint boundary checklist has no
automatic trigger. Entry 62 addresses a separate, related gap: even when
the checklist IS run (verified verbally or during `/dsm-go` Step 3.6), the
checkboxes in the epoch plan's sprint-specific section do not get
reconciled with actual completion state.

S47 evidence:
- `/dsm-go` Step 3.6 (sprint boundary gate) verified Sprint 15 complete:
  checkpoint consumed, feedback in `done/`, decisions updated, blog journal
  written, README updated, hub/portfolio notified. 7/7 confirmed.
- Epoch plan's Sprint 15 section (lines 335-342) shows:
  ```
  **Sprint boundary checklist:**
  - [ ] Checkpoint document
  - [ ] Feedback files updated
  - [ ] Decision log updated
  - [ ] Blog journal entry
  - [ ] README updated
  - [x] Epoch plan updated
  - [ ] Hub/portfolio notified
  ```
  Only "Epoch plan updated" is ticked. The other 6 are complete in reality
  but unmarked in the plan.

The agent verified and acknowledged completion in conversation but never
edited the plan to tick the boxes. Verification and documentation are
separate actions; only the first happens automatically.

### Root Cause

Verification happens during a read-pass (`/dsm-go` Step 3.6 or manual
review). Ticking boxes requires a write-pass (plan edit). There is no
protocol step that says "after verifying item X is complete, update the
corresponding checkbox in the epoch plan."

The same asymmetry appears in other protocols: `/dsm-go` reads MEMORY.md,
but updating MEMORY.md happens only at session end via `/dsm-wrap-up`.
This is acceptable for MEMORY (infrequent updates) but not for sprint
checklists (many items per sprint, each needing explicit marking).

### Proposal #55: Verification-Triggered Checkbox Reconciliation

Two complementary changes:

1. **Extend `/dsm-go` Step 3.6 (sprint boundary gate):** After verifying
   each item, reconcile the epoch plan's checkbox for that item. If the
   checkbox is `[ ]` but the item is verified complete, update to `[x]`.
   If the checkbox is `[x]` but verification fails, flag the discrepancy.

2. **Add sprint-close protocol step:** When marking a sprint COMPLETE in
   the epoch plan (changing `**Status:** IN PROGRESS` to `**Status:**
   COMPLETE`), the protocol must also update every checkbox in the
   sprint's boundary checklist to reflect actual state. No box should
   remain `[ ]` when the sprint is closed.

### Expected Impact

Closes the gap between verification (reading) and documentation (writing).
Makes the epoch plan a reliable source of truth for sprint state, not
just for sprint intent. Enables future automation (e.g., a `/dsm-align`
check that flags stale unchecked boxes in completed sprints).

---

## Entry 63: No Epoch Boundary Checklist (Third Boundary-Protocol Gap)

**Section:** DSM_0.2 / DSM_1.0 (epoch-scale lifecycle protocols)
**Score:** 5/10 (sprint boundaries are protocolized, epoch boundaries are not)
**Context:** S47 closing Sprint 16 raised the question of Epoch 4 closure;
no canonical Epoch Boundary Checklist exists

### Observation

Third in a series of boundary-protocol gaps surfaced in S47 (Entries 61,
62, now 63). Sprint 16 completed and the user asked whether there is an
epoch-level equivalent of the Sprint Boundary Checklist. Answer: no.

What exists:
- Sprint Boundary Checklist (CLAUDE.md, 7 items): runs at sprint close.
- `/dsm-finalize-project` skill: has a "Retrospective (medium+)" step
  that includes epoch retrospectives with a template. But this runs only
  at PROJECT finalization, not at each epoch boundary.

What's missing:
- A dedicated Epoch Boundary Checklist
- Automatic trigger when an epoch completes
- A `/dsm-epoch-boundary` skill

Consequence: epochs accumulate sprint-level closures but never receive
explicit closure of their own. Retrospectives happen only at project end
or ad hoc. The epoch-scale pattern extraction, metric summary, and
deferred-requirements organization S47 did for Epoch 4 has no canonical form.

### Proposed Epoch Boundary Checklist (draft, 9 items)

Based on S47 execution against Epoch 4:

1. Epoch retrospective written (use `/dsm-finalize-project` template)
2. All sprint boundary checklists verified complete
3. Blog materials compiled (extract journal.md → materials.md per epoch)
4. Epoch plan marked COMPLETE
5. Metrics summary captured (tests, features, decisions, experiments)
6. Deferred requirements organized for next epoch (themed)
7. Next epoch plan drafted (or project close decision)
8. Hub/portfolio notified of epoch completion (epoch-level, not sprint-level)
9. Decision log reviewed for epoch-scope decisions

### Proposal #56: Add Epoch Boundary Checklist to DSM

Three complementary changes:

1. **Add to CLAUDE.md alignment template:** Epoch Boundary Checklist parallel
   to Sprint Boundary Checklist, with the 9 items (or refined).

2. **Extract `/dsm-epoch-boundary` skill:** Separate the epoch-retrospective
   logic from `/dsm-finalize-project` into a standalone skill that runs at
   each epoch close, reusing the existing template. `/dsm-finalize-project`
   then focuses on project-level closure and calls the epoch skill for any
   unclosed epochs.

3. **Cross-reference with Entry 61/62:** When the sprint boundary gate
   detects that a sprint close also closes an epoch, trigger the epoch
   boundary flow in addition to the sprint boundary flow.

### Expected Impact

Parallels the sprint boundary treatment at epoch scale. Captures epoch-
level learning while fresh, not years later. Standardizes the "5 themes
of deferred requirements" pattern that S47 produced ad hoc.