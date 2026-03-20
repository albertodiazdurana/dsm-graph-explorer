# Session 41 Methodology Feedback

## Entry 55: /dsm-go skill missing session branch creation step

**Date:** 2026-03-20
**Session:** 41
**Score:** 3/10 (policy exists but is not enforced by the skill that should implement it)
**Category:** Protocol-Implementation Gap

**Observation:** DSM_0.2 core (Three-Level Branching Strategy, lines 765-843) declares that a Level 2 session branch must be created at every session start via `/dsm-go` or `/dsm-light-go`. The naming convention is `session-N/YYYY-MM-DD`. However, the `/dsm-go` skill definition (`~/.claude/commands/dsm-go.md`) contains no step that creates a branch. All 10 steps (MEMORY.md read, DSM_0.2 checks, handoff lifecycle, checkpoint check, sprint boundary gate, git status, session baseline, transcript, recent history, report) operate on whatever branch is current, which defaults to `master`/`main`.

**Evidence:**
- DSM_0.2 core line 776: "Created at every session start (`/dsm-go`, `/dsm-light-go`)"
- `/dsm-go` skill: Steps 1-10, no branch creation
- Step 5.8 references branch session numbers ("extracted from the branch name, e.g., `session-139/...`"), implying branches should exist, but no prior step creates them
- Session-Start Branch Resumption Protocol (lines 821-830) checks for open branches but is also absent from the skill

**Impact:** Every session since the branching strategy was added has been running directly on `master`, bypassing the isolation and reversibility that session branches are designed to provide. The Level 2 → Level 1 merge at wrap-up is also impossible since there is no separate branch to merge.

**Root cause:** The branching strategy was added to DSM_0.2 core as a declarative policy, but the `/dsm-go` skill definition was not updated with a corresponding procedural step. The policy and the implementation are in different files with no cross-validation.
