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

---

### Phase 2: Core Modules

**Date:** _TBD_

_Observations from Phase 2_

---

### Phase 3: Integration & Evaluation

**Date:** _TBD_

_Observations from Phase 3_

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

**Last Updated:** 2026-02-01
**Total Observations:** 3
