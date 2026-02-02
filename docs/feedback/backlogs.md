# DSM Feedback: Backlogs

**Project:** DSM Graph Explorer
**Purpose:** Track observations about DSM gaps, improvements, and backlog items discovered during this project.

**Reference:** Section 6.4.5 (Project Feedback Deliverables) — File 1 of 3

---

## Instructions

As you work through the project, note:
- **Gaps** in DSM guidance (missing sections, unclear instructions)
- **Improvement opportunities** (templates, checklists, examples)
- **Action items** for DSM enhancement (potential backlog items)

Be specific: reference section numbers, describe the gap, propose solutions.

---

## Observations

### Phase 0: Environment Setup

**Date:** 2026-01-31

**Observation:**
_Add observations as they arise during implementation_

**Example format:**
- **Gap:** Section X.Y.Z doesn't cover [specific scenario]
- **Impact:** [How this affected the project]
- **Proposed solution:** [Suggestion for DSM improvement]
- **Priority:** High/Medium/Low
- **Potential backlog:** BACKLOG-XXX: [Title]

---

### Phase 1: Data Pipeline

**Date:** 2026-02-01

- **Gap:** DSM 4.0 Section 3 (Development Protocol) and the handoff template don't include guidance on **explaining proposed artifacts to the user before generating them**. The TDD workflow says "write tests first" but doesn't address the collaboration pattern where the human needs to understand and approve what will be created before the AI generates it.
- **Impact:** AI agent generated test fixture + full test suite without the user understanding the rationale or structure. User had to reject and request explanation. This breaks the collaborative flow.
- **Proposed solution:** Add to DSM 4.0 Section 3 a step between planning and implementation: "**Pre-generation brief** — Before creating each artifact, provide a brief explanation of: (1) what the file is, (2) why it's needed, (3) what it contains at a high level. Get user acknowledgment before proceeding." This aligns with DSM's core philosophy of human-AI collaboration.
- **Priority:** High
- **Potential backlog:** BACKLOG-XXX: Add pre-generation brief step to DSM 4.0 Development Protocol

- **Gap:** DSM 4.0 Section 2 (Project Structure) and DSM 2.0 (Project Management Guidelines) structure work as large monolithic sprints with internal "phases". There is no guidance on **splitting projects into short, focused sprints** where each sprint produces its own feedback cycle and blog material.
- **Impact:** The original plan was a single sprint with 4 phases (36 hours). This delays feedback until the end and makes blog material stale. Restructuring into 4 short sprints (one per phase) means each sprint ends with: DSM feedback update, blog journal entry, and a checkpoint. This produces fresher material, faster iteration on methodology observations, and natural "chapters" for the blog narrative.
- **Proposed solution:** Add to DSM 4.0 Section 3 or DSM 2.0 a recommendation: "**Short sprint cadence** — Structure projects as a series of short sprints (each delivering a working increment) rather than one large sprint with internal phases. Each sprint boundary should produce: (1) DSM feedback update, (2) blog journal entry, (3) checkpoint document. This accelerates the feedback loop and generates richer blog material."
- **Priority:** High
- **Potential backlog:** BACKLOG-XXX: Add short sprint cadence guidance to DSM project management

- **Gap:** DSM 4.0 Section 3 (Development Protocol) does not include a **research/state-of-the-art review step** before implementation planning. The methodology goes from environment setup directly to development without validating the approach against published best practices.
- **Impact:** Without a research step, teams risk reinventing validated solutions or missing established patterns. In this project, a research review (coreference resolution literature, existing markdown link checkers, code static analysis patterns) confirmed our regex approach fills a real gap and follows the well-established parsing → resolution → validation pipeline. Without it, we would have proceeded on assumption rather than evidence.
- **Proposed solution:** Add to DSM 4.0 Section 3 a mandatory step between Phase 0 (Setup) and Phase 1 (Development): "**Phase 0.5: Research & Grounding** — Before implementation, conduct a brief state-of-the-art review: (1) identify related tools and approaches, (2) assess gaps your project fills, (3) validate your technical approach against published best practices, (4) document findings in `docs/research/`. This grounds the plan on validated approaches rather than assumptions."
- **Priority:** High
- **Potential backlog:** BACKLOG-XXX: Add research/grounding phase to DSM 4.0 Development Protocol

- **Gap:** DSM 4.0 Section 2 (Project Structure Patterns) specifies feedback files as loose files in the `docs/` directory (e.g., `docs/dsm-feedback-backlogs.md`), inconsistent with the subfolder pattern used for all other document types (`docs/handoffs/`, `docs/decisions/`, `docs/checkpoints/`, `docs/blog/`). The project structure template should use `docs/feedback/` as a subfolder.
- **Impact:** Feedback files were initially created at `docs/dsm-feedback-*.md` following the Phase 0 handoff instructions, then had to be manually moved to `docs/feedback/` mid-project. References in CLAUDE.md, README.md, and SPRINT_PLAN.md all needed updating. This is avoidable friction.
- **Proposed solution:** Update the DSM 4.0 Section 2 project structure template to use `docs/feedback/` as a subfolder (containing `backlogs.md`, `methodology.md`, `blog.md`) instead of loose `docs/dsm-feedback-*.md` files. This is consistent with the existing subfolder convention for other document types.
- **Priority:** Medium
- **Potential backlog:** BACKLOG-XXX: Standardize feedback file location in DSM 4.0 project structure template

- **Gap:** DSM Appendix E.12 (Validation Tracker) and Section 6.4.5 (Three-File Feedback System, specifically `methodology.md`) overlap significantly. Both score DSM sections on effectiveness and capture recommendations. The Validation Tracker uses 4-criterion scoring (clarity, applicability, completeness, efficiency) with individual dated entries, while `methodology.md` uses a single overall score per section with "what worked well" / "what needs improvement" columns. The naming ("validation" vs "feedback") doesn't clarify the distinction. The sql-query-agent project independently flagged this same confusion (Entry 3 in its validation tracker, scored 3.0 for clarity).
- **Impact:** Projects either maintain redundant documents (doubling overhead) or must decide which to use without clear guidance. Two concurrent dog-fooding projects arrived at the same pain point independently — strong signal this needs resolution.
- **Proposed solution:** Consolidate into the three-file feedback system. Either (a) enrich `methodology.md` with the 4-criterion scoring from E.12 if the extra granularity is desired, or (b) keep the simpler single-score format and deprecate the standalone Validation Tracker. The three-file system (backlogs, methodology, blog) already covers gaps, section effectiveness, and blog process — adding a 4th file duplicates rather than extends.
- **Priority:** Medium
- **Potential backlog:** BACKLOG-XXX: Consolidate Validation Tracker (E.12) with Three-File Feedback System (6.4.5)

---

### Sprint 3: CLI & Real-World Run

**Date:** 2026-02-02

- **Gap:** The pre-generation brief protocol (added to DSM as feedback from Sprint 1, now in Custom Instructions template v1.1) lacks guidance on **what constitutes approval**. The protocol says "explain before generating" but does not specify that the agent must receive an **explicit acknowledgment** before proceeding. In Sprint 3, the agent provided a pre-generation brief for the CLI module, the user said "ready" (signaling readiness to start the sprint, not approval of specific files), and the agent generated both test and implementation files without waiting for per-file approval. The user had to intervene: "Why did you do this? This should be documented as a user-agent collaboration error."
- **Impact:** The agent created 2 files (`tests/test_cli.py`, `src/cli.py`) without the user reviewing or approving the design. This breaks the collaborative flow and undermines the human's role as approver. It is the same class of error that prompted the pre-generation brief protocol in Sprint 1 — meaning the protocol's wording is insufficient to prevent recurrence.
- **Proposed solution:** Strengthen the pre-generation brief protocol to explicitly require: "(1) Agent explains what it will create, (2) **Agent waits for explicit user approval** (e.g., 'go ahead', 'approved', 'yes'), (3) Agent generates the artifact." The word "approval" or "acknowledgment" must appear in the protocol. A simple "ready" from the user in a different context (e.g., starting a sprint) should not be interpreted as blanket file-creation approval.
- **Priority:** High
- **Potential backlog:** BACKLOG-XXX: Strengthen pre-generation brief to require explicit approval before file creation

---

### Phase 4: Documentation

**Date:** _TBD_

_Observations from Phase 4_

---

## Summary of Backlog Items to Create

At project completion, list all potential backlog items discovered:

| Priority | Title | Section Affected | Description |
|----------|-------|------------------|-------------|
| _High/Med/Low_ | _Title_ | _Section X.Y_ | _Brief description_ |

---

**Last Updated:** 2026-02-02
**Total Observations:** 6
