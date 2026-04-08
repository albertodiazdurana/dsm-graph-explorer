# DSM Feedback: Backlog Proposals

**Project:** DSM Graph Explorer
**DSM Version Used:** DSM 4.0 v1.0, DSM 1.0 v1.1
**Author:** Alberto Diaz Durana
**Date:** 2026-02-03

---

## High Priority

### Add pre-generation brief step to DSM 4.0 Development Protocol
- **DSM Section:** DSM 4.0 Section 3 (Development Protocol)
- **Problem:** The TDD workflow says "write tests first" but doesn't address the collaboration pattern where the human needs to understand and approve what will be created before the AI generates it.
- **Proposed Solution:** Add a step between planning and implementation: "**Pre-generation brief** — Before creating each artifact, provide a brief explanation of: (1) what the file is, (2) why it's needed, (3) what it contains at a high level. Get user acknowledgment before proceeding."
- **Evidence:** AI agent generated test fixture + full test suite without the user understanding the rationale or structure. User had to reject and request explanation. This breaks the collaborative flow.

### Strengthen pre-generation brief to require explicit approval (STOP protocol)
- **DSM Section:** DSM_Custom_Instructions_v1.1.md + DSM 4.0 Section 3
- **Problem:** The pre-generation brief protocol (added after Sprint 1 feedback) says "explain before generating" but does not specify that the agent must receive an **explicit acknowledgment** before proceeding. A simple "ready" from the user in a different context (e.g., starting a sprint) can be misinterpreted as blanket file-creation approval.
- **Proposed Solution:** Add a "STOP — Protocol Reminder" section to project CLAUDE.md files with explicit steps:
  ```
  BEFORE modifying ANY file:
  1. Explain the change (what file, what modification, why)
  2. Wait for explicit approval ("go ahead", "approved", "yes", "proceed")
  3. Only then execute

  This applies to ALL file modifications — including bug fixes, backlog items,
  and "obvious" changes. No exceptions.
  ```
  The word "STOP" and numbered steps make the protocol unambiguous. Include violation history to reinforce importance.
- **Evidence:** Three violations in dsm-graph-explorer: Sprint 1 (test generation), Sprint 3 (CLI generation), Post-Sprint 3 (trailing period fix). Same class of error repeated three times despite feedback after each occurrence. The protocol wording was insufficient — an explicit STOP reminder with numbered steps is needed.

### Add short sprint cadence guidance to DSM project management
- **DSM Section:** DSM 4.0 Section 3 + DSM 2.0 (Project Management Guidelines)
- **Problem:** DSM structures work as large monolithic sprints with internal "phases". There is no guidance on splitting projects into short, focused sprints where each sprint produces its own feedback cycle and blog material.
- **Proposed Solution:** Add recommendation: "**Short sprint cadence** — Structure projects as a series of short sprints (each delivering a working increment) rather than one large sprint with internal phases. Each sprint boundary should produce: (1) DSM feedback update, (2) blog journal entry, (3) checkpoint document."
- **Evidence:** The original plan was a single sprint with 4 phases. Restructuring into 4 short sprints produced fresher material, faster iteration on methodology observations, and natural "chapters" for the blog narrative.

### Add research/grounding phase to DSM 4.0 Development Protocol
- **DSM Section:** DSM 4.0 Section 3 (Development Protocol)
- **Problem:** The methodology goes from environment setup directly to development without validating the approach against published best practices.
- **Proposed Solution:** Add a mandatory step between Phase 0 (Setup) and Phase 1 (Development): "**Phase 0.5: Research & Grounding** — Before implementation, conduct a brief state-of-the-art review: (1) identify related tools and approaches, (2) assess gaps your project fills, (3) validate your technical approach against published best practices, (4) document findings in `dsm-docs/research/`."
- **Evidence:** A research review (coreference resolution literature, existing markdown link checkers, code static analysis patterns) confirmed our regex approach fills a real gap and follows the well-established parsing → resolution → validation pipeline. Without it, we would have proceeded on assumption rather than evidence.

### Create comprehensive dsm-docs/ folder structure reference document
- **DSM Section:** DSM 4.0 Section 2 (Project Structure Patterns)
- **Problem:** DSM 4.0 Section 2 lists folder names (`dsm-docs/handoffs/`, `dsm-docs/decisions/`, etc.) but does not adequately explain the **purpose** of each subfolder, what **files** belong in each, the **format** expected for each file type, or the **relationship** between folders. AI agents (and humans new to DSM) cannot understand the structure without external references.
- **Proposed Solution:** Create a "dsm-docs/ Folder Structure Reference" section in DSM 4.0 Section 2. For each subfolder, document:
  1. **Purpose** — What this folder is for (e.g., "feedback/ contains observations about DSM methodology effectiveness")
  2. **Files** — List of expected files with descriptions (e.g., "backlogs.md — proposed improvements to DSM")
  3. **Format** — Template or format specification for each file type
  4. **Timing** — When files are created/updated (e.g., "at sprint boundaries")
  5. **Relationship** — How this folder relates to others (e.g., "feedback/ is for DSM methodology feedback; backlog/ is for cross-project alignment reports")
  Include a link to a reference implementation project (e.g., sql-query-agent) as a concrete example.
- **Evidence:** During Sprint 3 closure, the AI agent required **6 explicit corrections** from the user:
  1. Tried to create backlog items in DSM repository instead of project's `dsm-docs/feedback-to-dsm/backlogs.md`
  2. Confused `dsm-docs/feedback-to-dsm/` vs `dsm-docs/blog/` for blog-related files
  3. Did not understand `dsm-docs/backlog/` (alignment) vs `dsm-docs/feedback-to-dsm/` (DSM feedback) distinction
  4. User had to provide `docs-folder-reference-sql-agent.md` as explicit reference
  5. User had to point to sql-agent files as format examples
  6. Multiple iterations needed to get file formats correct
  This level of confusion — requiring an external reference project — indicates the documentation is insufficient for self-contained understanding.

---

## Medium Priority

### Standardize feedback file location in DSM 4.0 project structure template
- **DSM Section:** DSM 4.0 Section 2 (Project Structure Patterns)
- **Problem:** DSM specifies feedback files as loose files in the `dsm-docs/` directory (e.g., `dsm-docs/dsm-feedback-backlogs.md`), inconsistent with the subfolder pattern used for all other document types (`dsm-docs/handoffs/`, `dsm-docs/decisions/`, `dsm-docs/checkpoints/`, `dsm-docs/blog/`).
- **Proposed Solution:** Update DSM 4.0 Section 2 project structure template to use `dsm-docs/feedback-to-dsm/` as a subfolder (containing `backlogs.md`, `methodology.md`) instead of loose `dsm-docs/dsm-feedback-*.md` files.
- **Evidence:** Feedback files were initially created at `dsm-docs/dsm-feedback-*.md` following the Phase 0 handoff instructions, then had to be manually moved to `dsm-docs/feedback-to-dsm/` mid-project. References in CLAUDE.md, README.md, and SPRINT_PLAN.md all needed updating.

### Consolidate Validation Tracker (E.12) with Three-File Feedback System (6.4.5)
- **DSM Section:** DSM Appendix E.12 + Section 6.4.5
- **Problem:** Validation Tracker (E.12) and methodology.md (6.4.5) overlap significantly. Both score DSM sections on effectiveness and capture recommendations. The naming ("validation" vs "feedback") doesn't clarify the distinction.
- **Proposed Solution:** Consolidate into the feedback system. Either (a) enrich `methodology.md` with the 4-criterion scoring from E.12 if desired, or (b) keep the simpler single-score format and deprecate the standalone Validation Tracker. Two files (backlogs, methodology) is sufficient.
- **Evidence:** Two concurrent dog-fooding projects (dsm-graph-explorer and sql-query-agent) independently flagged this same confusion. Strong signal this needs resolution.

### Add Sprint Boundary Checklist to Section 6.4
- **DSM Section:** Section 6.4 (Checkpoint and Feedback Protocol)
- **Problem:** No standard checklist exists for sprint boundaries. Projects may miss documentation steps.
- **Proposed Solution:** Add to Section 6.4 a Sprint Boundary Checklist: `[ ] Checkpoint document`, `[ ] Feedback files updated`, `[ ] Decision log entries`, `[ ] Blog entry drafted`, `[ ] README updated`, `[ ] Tests passing`.
- **Evidence:** Applied TRANSFER-4 from sql-query-agent alignment document at Sprint 3 completion. The checklist ensured all documentation was completed systematically.

### Formalize Cross-Project Alignment Report as standard DSM artifact
- **DSM Section:** New artifact type (proposed)
- **Problem:** Patterns refined in one project (e.g., feedback protocol, blog workflow) need a mechanism to transfer to other projects.
- **Proposed Solution:** Formalize "Cross-Project Alignment Report" as a standard DSM artifact. Template: Transfer Items (what pattern, source, status), Observations, Action Items. Location: `dsm-docs/backlog/dsm-alignment-*.md`.
- **Evidence:** Applied alignment document from sql-query-agent to dsm-graph-explorer successfully. Four transfer items (TRANSFER-1 to TRANSFER-4) all proved applicable.

### Add fixture validation against production data to TDD workflow
- **DSM Section:** DSM 4.0 Section 3 (Development Protocol) or Section 4.4 (Tests vs Capability Experiments)
- **Problem:** TDD creates synthetic test fixtures before implementation, but those fixtures encode assumptions about data format. If the assumptions are wrong, the entire test suite validates the wrong thing. The trailing period bug (448 false positives reduced to 6 after fix) happened because the fixture used `### 2.3.7 Title` when real DSM files use `### 2.3.7. Title`.
- **Proposed Solution:** Add to DSM 4.0: "Before writing tests against synthetic fixtures, verify the fixture format matches actual production data. Run at least one capability experiment on real data in Sprint 1 to validate assumptions. If the project parses or processes external data, inspect representative samples of that data before creating test fixtures."
- **Evidence:** Three assumption gaps in dsm-graph-explorer all stemmed from not checking real data early: (1) KNOWN_DSM_IDS incomplete, (2) DSM short forms missed, (3) trailing period format missed. All would have been caught by opening one real DSM file in Sprint 1.

### Add blog post metadata template to Section 2.5.6
- **DSM Section:** Section 2.5.6 (Blog/Communication Deliverable Process)
- **Problem:** The blog process specifies preparation, scoping, drafting, and publication steps but does not include a standard metadata format for blog posts themselves. Posts lack consistent fields for date, author, status, and platform.
- **Proposed Solution:** Add to Section 2.5.6 a blog post metadata template:
  ```markdown
  **Date:** YYYY-MM-DD
  **Author:** [Name]
  **Status:** Draft | Review | Published
  **Platform:** LinkedIn | Blog | GitHub | etc
  ```
  All blog posts should include this header for consistency and future reference.
- **Evidence:** Writing WSL migration blog post; initial draft used informal date format. Standardizing ensures posts are properly dated and trackable.

### Add Mermaid diagram recommendation to blog deliverable process
- **DSM Section:** Section 2.5.6-2.5.8 (Blog/Communication Deliverable Process)
- **Problem:** Blog posts benefit from visual diagrams (architecture, workflows, pipelines), but DSM does not recommend specific tools or workflows for creating them. Authors may spend time evaluating options or creating diagrams in inconsistent formats.
- **Proposed Solution:** Add to Section 2.5.6 a recommendation for diagram creation:
  ```markdown
  **Diagrams:** Use Mermaid syntax for architecture and flow diagrams.
  - Render at mermaid.live for PNG/SVG export
  - Store source in dsm-docs/blog/<epoch>/images/ as .mmd files
  - Vertical layouts (flowchart TB) work better for LinkedIn feed
  ```
  Mermaid is text-based (version-controllable), renders in GitHub markdown, and exports cleanly for social media.
- **Evidence:** Created architecture diagram for Epoch 1 blog post using Mermaid. The AI assistant generated the diagram code, user rendered at mermaid.live, exported PNG for LinkedIn. Workflow was efficient: text-based iteration, then single export step.

### Add date-prefix naming convention for blog files
- **DSM Section:** Section 2.5.6 (Blog/Communication Deliverable Process)
- **Problem:** Blog files named generically (`blog-draft.md`, `linkedin-post.md`) don't sort chronologically in file listings. As post count grows, finding posts by date requires opening each file.
- **Proposed Solution:** Add to Section 2.5.6: "Name blog post files with date prefix: `YYYY-MM-DD-title.md` (e.g., `2026-02-05-compiler-architecture.md`). Use the publication date. This matches static site generator conventions (Jekyll, Hugo) and enables chronological sorting in directory listings."
- **Evidence:** Renamed three blog files in dsm-graph-explorer from generic names to date-prefixed names. Immediately improved discoverability.

### Define file-by-file approval loop in Development Protocol
- **DSM Section:** DSM 4.0 Section 3 (Development Protocol) + Custom Instructions
- **Problem:** The Pre-Generation Brief Protocol says "explain before generating, wait for approval," but does not define the mechanical loop for multi-file tasks. Without step-by-step instructions, the agent defaults to batch generation (creating multiple files before stopping for review). Additionally, modal approval dialogs (e.g., AskUserQuestion in Claude Code) darken the background and block the IDE content the user needs to read, making review impractical.
- **Proposed Solution:** Add a numbered "File-by-File Approval Loop" to DSM 4.0 Section 3:
  ```
  FILE-BY-FILE APPROVAL LOOP (multi-file tasks):
  1. Display progress list with current item marked
  2. Show description of next file (what, why, key decisions) — STOP
  3. Wait for short Y/N approval from user — STOP
  4. If Y: create file, wait for user to review via diff — STOP
  5. Display progress list with completed item crossed out, next item marked
  6. Repeat from step 2
  ```
  Approvals must use plain text (not modal dialogs) so the user can read the explanation and the generated file simultaneously. The agent must not proceed to the next file until the current one is approved.
- **Evidence:** Three occurrences of the same problem across dsm-graph-explorer: Sprint 1 (batch test generation), Sprint 3 (batch CLI generation), Sprint 5 (batch docs generation). Each time the protocol was strengthened in CLAUDE.md, but the behavior recurred because the loop mechanics were not specified. See `methodology.md` Entry 19.

### Clarify journal.md vs materials.md roles in blog deliverable process
- **DSM Section:** Section 2.5.6 (Blog/Communication Deliverable Process)
- **Problem:** Section 2.5.6 specifies "Materials" and "Journal" as separate blog deliverables, but their roles overlap in practice. Three issues: (1) journal.md accumulates "Blog Material" subsections that duplicate what materials.md is for, (2) materials.md is per-epoch but blog posts are per-topic, so one materials.md per epoch is insufficient when multiple posts exist, (3) maintaining two overlapping files adds overhead without clear benefit.
- **Proposed Solution:** Two options:
  - **Option A (Separate):** Clarify that journal = session-scoped observations only (no draft content), and materials = one file per blog post (not per epoch), named `YYYY-MM-DD-title-materials.md`.
  - **Option B (Merge):** Replace both with a single `YYYY-MM-DD-title-materials.md` per blog post that includes both capture notes and draft structure. The journal becomes unnecessary as a standalone file; observations live inside the post's materials file.
  Either option should specify: (a) exactly what goes in each file, (b) when each file is created/updated, (c) how to handle multiple posts per epoch.
- **Evidence:** In dsm-graph-explorer Epoch 2, materials.md covers only the WSL migration post, while journal.md contains blog material for both WSL and Sprint 4. The journal's "Blog Material" sections are the actual preparation content; materials.md is a one-time pre-draft that wasn't maintained as the epoch progressed.

---

### Add convention linting mode to complement cross-reference validation
- **DSM Section:** DSM_0.2 (Custom Instructions, text conventions) + DSM_3 Section 3 (Document Standards)
- **Problem:** Graph Explorer validates structural cross-references (Section X.Y, Appendix B.2, Template N) but does not check surface-level document conventions: emoji/symbol usage, TOC presence, em-dash punctuation, CRLF line endings, mojibake encoding artifacts, and backlog metadata fields. These conventions are defined in DSM_0.2 and DSM_3 but can only be verified manually. A full manual audit (BACKLOG-076) found 34 emoji violations, 3 TOC violations, 4 em-dashes, and mojibake encoding in 6 files.
- **Proposed Solution:** Add a `--lint` mode (or separate `lint_conventions.py` script) that checks:
  1. **Emoji/symbol usage:** Flag checkmarks, cross marks, warning symbols, chart symbols (should use WARNING:/OK:/ERROR: text)
  2. **TOC presence:** Flag `## Table of Contents` or similar headings (DSM uses self-documenting hierarchical numbering)
  3. **Em-dash punctuation:** Flag `—` characters (should use commas or semicolons)
  4. **CRLF line endings:** Flag files with `\r\n` (should be `\n`)
  5. **Mojibake encoding:** Flag common double-encoded UTF-8 patterns (e.g., `âœ—`, `âœ"`, `âš`)
  6. **Backlog metadata:** Validate required fields (Status, Priority, Date Created, Origin, Author) in BACKLOG-### files
  Combined with existing cross-reference validation, this would provide a complete DSM compliance pipeline triggered at version bumps.
- **Evidence:** BACKLOG-076 self-compliance audit required two manual passes (conventions + cross-references) across 8 files. The cross-reference pass maps naturally to Graph Explorer's existing capability. The convention pass is a new capability that would eliminate the manual effort and prevent convention drift between audits.

### Add dsm-docs/guides/ subfolder for user-facing documentation
- **DSM Section:** DSM 4.0 Section 2 (Project Structure Patterns)
- **Problem:** All existing `dsm-docs/` subfolders serve project-management purposes: `checkpoints/`, `decisions/`, `handoffs/`, `feedback/`, `blog/`, `backlog/`, `plan/`. User-facing documentation (installation guides, configuration references, how-tos) has no prescribed location. Projects either place guides in an ad-hoc subfolder or mix them with PM artifacts, blurring the folder structure's intent.
- **Proposed Solution:** Add `dsm-docs/guides/` to the DSM 4.0 Section 2 project structure template as a standard subfolder for user-facing documentation. Contents would include installation guides, configuration references, API documentation, and how-to guides. This keeps the existing PM subfolders focused on their original purpose while giving user-facing content a clear home.
- **Evidence:** In dsm-graph-explorer Sprint 5, a remediation guide and a configuration reference needed a location. No existing subfolder fit, so `dsm-docs/guides/` was created ad-hoc. The separation immediately clarified the folder structure: PM artifacts in their respective subfolders, user-facing docs in `guides/`. See `methodology.md` Entry 20.

### Rename dsm-docs/feedback-to-dsm/ to dsm-docs/feedback-to-dsm-to-dsm/ for explicit directionality
- **DSM Section:** DSM 4.0 Section 2 (Project Structure Patterns)
- **Problem:** The folder name `dsm-docs/feedback-to-dsm/` does not convey that its contents are feedback *to DSM* (methodology observations and improvement proposals). The generic name is easily confused with `dsm-docs/backlog/` (cross-project alignment reports), especially since `feedback/` contains a file called `backlogs.md`, making the word "backlog" appear in both contexts with different meanings. A new contributor or AI agent cannot distinguish the two folders by name alone.
- **Proposed Solution:** Rename `dsm-docs/feedback-to-dsm/` to `dsm-docs/feedback-to-dsm-to-dsm/` in the DSM 4.0 Section 2 project structure template. The directional name makes the folder's purpose self-documenting: it contains observations and proposals flowing from the project back to the DSM methodology. No change to file contents or the three-file feedback system itself.
- **Evidence:** In dsm-graph-explorer, the AI agent confused `dsm-docs/feedback-to-dsm/` with `dsm-docs/backlog/` on multiple occasions (see also Entry 5 in methodology.md). The naming collision between the folder `dsm-docs/backlog/` and the file `dsm-docs/feedback-to-dsm/backlogs.md` compounds the ambiguity. See `methodology.md` Entry 21.

### Add next-steps summary to Sprint Boundary Checklist
- **DSM Section:** Section 6.4 (Checkpoint and Feedback Protocol) + DSM 2.0 Template 8
- **Problem:** The Sprint Boundary Checklist is entirely backward-looking: checkpoint, feedback, decisions, journal, README. It captures what was done but not what comes next. The next session starts without immediate orientation and must re-read the epoch plan to determine the upcoming sprint's goal and deliverables.
- **Proposed Solution:** Add a "Next steps summary" item to the Sprint Boundary Checklist: a brief paragraph (3-5 sentences) describing the next sprint's goal, key deliverables, and relevant plan reference. Example: "Sprint 6 implements semantic validation: TF-IDF keyword similarity and drift detection (EXP-003). Key deliverables: `src/validator/semantic_validator.py`, capability experiment results. See epoch-2-plan.md Phase 6." This item should be written into the checkpoint document and/or MEMORY.md so the next session can orient immediately.
- **Evidence:** Sprint 5 wrap-up in dsm-graph-explorer completed all checklist items (checkpoint, journal, feedback, README) but omitted any forward-looking summary. The next session had to re-read the epoch plan to understand what Sprint 6 involves. A single paragraph at wrap-up would have saved that orientation step. See `methodology.md` Entry 22.

### Add append-only rule to Session Transcript Protocol
- **DSM Section:** DSM_0.2 Session Transcript Protocol
- **Problem:** The protocol specifies "two appends per turn" but does not state that the transcript is append-only. An agent that misses an append naturally tries to backfill or edit past entries, corrupting the real-time log the user monitors.
- **Proposed Solution:** Add to the Session Transcript Protocol rules: "The transcript is append-only. Never modify or backfill past entries. Each entry reflects reasoning at the moment it was written. If a past entry was missed, note the gap in the next entry rather than editing history."
- **Evidence:** In dsm-graph-explorer Sprint 6, the agent created the transcript file with backfilled entries, then later attempted to edit a past block to add a missed output summary. The user rejected the edit. See `methodology.md` Entry 25.

### Document three-file feedback as atomic operation
- **DSM Section:** DSM_0.2 Session-End Inbox Push + DSM 4.0 Section 6
- **Problem:** The three-file feedback system (methodology.md + backlogs.md + DSM Central inbox) is documented across multiple sections but never stated as an indivisible operation. An agent can write to one destination while forgetting the others, creating incomplete records.
- **Proposed Solution:** Add to DSM_0.2: "Every feedback item must be written to all three destinations as a single operation: (1) `dsm-docs/feedback-to-dsm/methodology.md` numbered entry with scores, (2) `dsm-docs/feedback-to-dsm/backlogs.md` numbered proposal, (3) DSM Central `dsm-docs/inbox/{project}.md` inbox entry. Partial writes are incomplete."
- **Evidence:** In dsm-graph-explorer Sprint 6, the agent sent the "session transcript append-only" feedback only to DSM Central's inbox, skipping both local feedback files. The user caught the omission. See `methodology.md` Entry 26.

### Standardize spoke folder names and add scaffolding pre-check
- **DSM Section:** DSM spoke structure template (referenced by BACKLOG-083)
- **Problem:** The DSM spoke structure template prescribes `dsm-docs/plans/` (plural), but dsm-graph-explorer already used `dsm-docs/plan/` (singular) with actual epoch plans. The scaffolding task (BACKLOG-083) created `dsm-docs/plans/` with `.gitkeep` alongside the existing `dsm-docs/plan/`, leaving a dead duplicate folder. The singular/plural naming inconsistency prevents automated detection of the collision.
- **Proposed Solution:** (1) Standardize on a single canonical name for each spoke folder (either singular or plural, applied consistently across all templates). (2) Add a scaffolding pre-check step: before creating a template folder, search for existing folders with similar names (singular/plural variants, common abbreviations). If a match exists, adopt the existing folder rather than creating a duplicate.
- **Evidence:** In dsm-graph-explorer, `dsm-docs/plan/` was created in Epoch 1 with epoch-1-plan.md. Commit `87eff49` later scaffolded `dsm-docs/plans/` (plural) per BACKLOG-083. The duplicate went unnoticed until the user spotted it during Sprint 6. See `methodology.md` Entry 27.

### Add experiments/ to DSM 4.0 project structure template
- **DSM Section:** DSM 4.0 Section 2 (Project Structure Patterns)
- **Problem:** Capability experiments (EXP-xxx) are a first-class concept in DSM 4.0 Section 4.4, but the project structure template in Section 2 does not include an `experiments/` folder. Projects create this folder organically but it is not standardized.
- **Proposed Solution:** Add `experiments/` to the project structure template in DSM 4.0 Section 2, alongside `src/`, `tests/`, and `dsm-docs/`. Include a brief note: "Capability experiment scripts (EXP-xxx). See Section 4.4 for the distinction between tests and experiments."
- **Evidence:** In dsm-graph-explorer, `experiments/` was created to hold `exp003_tfidf_threshold.py` and `exp003b_real_data_validation.py`. The folder was created organically without template guidance. See `methodology.md` Entry 28.

### Add two-gate approval model to Pre-Generation Brief Protocol
- **DSM Section:** DSM_0.2 (Custom Instructions) + DSM 4.0 Section 3 (Development Protocol)
- **Problem:** The Pre-Generation Brief Protocol defines a single "approval" gate: explain what/why, wait for approval, then generate. In practice, the agent treats this single gate as blanket permission to both write and execute the artifact. The user never gets to review the actual implementation (code, configuration, documentation) before it is used. This conflation has caused five recurrences of the same class of violation across Sprints 1, 3, 5, post-5, and 7, each with a different surface cause but identical root: a single gate cannot distinguish concept approval from implementation approval.
- **Proposed Solution:** Replace the single-gate protocol with a three-gate model:
  ```
  GATE 1 — Concept Approval:
  1. Explain: what artifact, why needed, key design decisions
  2. STOP — wait for explicit "y" from user

  GATE 2 — Implementation Approval:
  3. Write the file (user sees diff in IDE)
  4. STOP — wait for explicit "y" from user

  GATE 3 — Run Approval (when applicable):
  5. Explain what will be executed (command, target, expected behavior)
  6. STOP — wait for explicit "y" from user
  7. Execute and report results
  ```
  Gates 1 and 2 are mandatory for every file. Gate 3 applies when the artifact needs to be run (tests, scripts, benchmarks, CI triggers). Gate 1 validates intent; Gate 2 validates implementation; Gate 3 validates execution scope. This applies to all artifacts: code, tests, configuration, documentation, experiment scripts.
- **Evidence:** In dsm-graph-explorer Session 16, the agent presented EXP-004's brief (Gate 1), received "y", then immediately wrote 270 lines and ran the script against an external repository without presenting the code for review (skipped Gate 2). The user caught the violation. This is the fifth recurrence; see `methodology.md` Entries 19, 23, 29 for the pattern history.

---

### Add behavioral activation step to lightweight session skills
- **DSM Section:** DSM_0.2 (Custom Instructions), Session Transcript Protocol
- **Problem:** `/dsm-light-go` and `/dsm-light-wrap-up` are missing the explicit behavioral activation for the Session Transcript Protocol that `/dsm-go` provides at step 7. `/dsm-light-go` has a passive note ("Session Transcript Protocol remains active") in the Notes section, but this does not trigger transcript logging in a fresh conversation thread. Result: Session 20 completed an entire Sprint 8 implementation (7 files, 47 tests) with zero transcript entries.
- **Proposed Solution:** Add a numbered step to `/dsm-light-go` (after the report step) with the same imperative language used in `/dsm-go`:
  ```
  Step 7 (or 7.5): **Behavioral activation (Session Transcript Protocol):**
  From this point forward, follow the Session Transcript Protocol (DSM_0.2):
  append thinking to `.claude/session-transcript.md` as the first tool call
  of every turn, before any other work. Append output summary as the last
  tool call after completing work. This behavior remains active for the
  remainder of this session.
  ```
  Remove or update the passive note in the Notes section to avoid duplication. Apply the same pattern to `/dsm-light-wrap-up` if its steps also need transcript logging during wrap-up work.
- **Evidence:** Session 20 (dsm-graph-explorer, 2026-03-03). Boundary marker appended at lines 191-201, but no subsequent entries. Full `/dsm-go` step 7 (line 69) has explicit activation; `/dsm-light-go` line 55 has passive note only. See `methodology.md` Entry 30.

### Add portfolio path to CLAUDE.md project template
- **DSM Section:** DSM_0.2 (Custom Instructions), CLAUDE.md Environment section
- **Problem:** DSM spoke projects list the project path and DSM Central repository path in CLAUDE.md but not the portfolio path. Without it, agents cannot send progress notifications to the portfolio, breaking the three-target notification loop (DSM Central, portfolio, local feedback). In dsm-graph-explorer, Session 19 reported "Portfolio unavailable" and Session 20 required manual user intervention to provide the path.
- **Proposed Solution:** Add a `Portfolio` field to the CLAUDE.md Environment section template:
  ```
  ## Environment
  - **Platform**: Linux (WSL2)
  - **Project path**: `~/project-name/`
  - **DSM repository**: `~/dsm-agentic-ai-data-science-methodology/`
  - **Portfolio**: `~/dsm-data-science-portfolio-working-folder/`
  ```
  This should be part of the standard CLAUDE.md scaffolding that `/dsm-align` or project setup generates. If no portfolio exists, the field can be omitted or set to "N/A".
- **Evidence:** dsm-graph-explorer Sessions 19-20 (2026-03-02 to 2026-03-03). Session 19 logged "Portfolio unavailable" during ecosystem path validation. Session 20 required the user to manually provide the portfolio path. See `methodology.md` Entry 31.

### Proposal #27: Research Gate Before Planning at All Scales
- **DSM Section:** DSM 2.0 (Project Management), DSM 1.0 Section 2.2 (Research & Context Building), DSM 4.0 Section 3 (Development Protocol)
- **Problem:** DSM prescribes research as part of the data science workflow (Section 2.2) but does not mandate it as a prerequisite for planning at every scale. In practice, the most successful plans in dsm-graph-explorer followed a four-step sequence: preliminary plan (idea) -> research -> plan -> action. This pattern was validated across:
  - **Epoch level:** Epoch 2 research session (2026-02-04) grounded all 5 sprints with no mid-course design changes
  - **Sprint level:** EXP-003 threshold tuning grounded Sprint 6's TF-IDF implementation
  - **Feature level:** EXP-004 performance benchmarks grounded Sprint 7's NetworkX approach
  - **Epoch 3 pre-planning:** Neo4j landscape research (2026-03-09) revealed that Neo4j has no embedded Python mode, Kuzu was archived, and FalkorDBLite is a viable alternative, fundamentally changing the planned architecture
  When research was skipped, plans contained assumptions that required mid-course correction.
- **Proposed Solution:** Add a "Research Gate" to the DSM planning protocol:
  1. When the agent receives a planning request (epoch plan, sprint plan, feature design), it first assesses whether there is unresolved technical uncertainty
  2. If uncertainty exists, the agent suggests a research phase before drafting the plan, explaining what questions need answering
  3. The research output is a document in `dsm-docs/research/` that the plan document explicitly references
  4. The depth of research scales with uncertainty: a simple sprint might need 10 minutes of web search; an epoch-level technology choice might need a full research session
  5. The workflow at every scale becomes: **Idea -> Research (if uncertainty) -> Plan -> Action**
  This should be added to DSM 2.0 (planning protocols) and referenced from DSM 4.0 Section 3 (development protocol). The agent should proactively suggest research rather than waiting for the user to request it.
- **Evidence:** dsm-graph-explorer Epochs 2-3 (2026-02-04 to 2026-03-09). Epoch 2 retrospective explicitly noted research-first planning as a top success factor. Epoch 3 pre-planning research changed the technology direction before any code was written. See `methodology.md` Entry 32.

### Proposal #28: Tiered Research (Amend #27 with Broad -> Deep-Dive Pattern)
- **DSM Section:** DSM 2.0 (Project Management), DSM 1.0 Section 2.2 (Research & Context Building)
- **Problem:** Proposal #27 established the Research Gate (Idea -> Research -> Plan -> Action). In practice, technology selection decisions naturally produce two tiers of uncertainty: (1) "which option?" (landscape-level) and (2) "how does the selected option work in our context?" (implementation-level). A single research pass resolves the first but often leaves the second unaddressed, producing sprint plans based on assumptions about the selected technology's capabilities.
- **Proposed Solution:** Amend the Research Gate protocol to include tiered research:
  1. **Broad research** (landscape): Evaluate options, compare trade-offs, produce a selection decision (e.g., DEC-006)
  2. **Assessment gate:** After the decision, the agent assesses whether the selected option has unresolved implementation-level unknowns (API specifics, feature coverage, persistence model, testing patterns, compatibility with project data model)
  3. **Deep-dive research** (if uncertainty exists): Focused investigation of the selected option targeting the specific unknowns identified in the assessment gate
  4. **Plan:** Sprint/epoch plan grounded in both research tiers
  This is not two mandatory research phases; it is one gate with optional depth refinement. Simple decisions (well-known technology, clear documentation) skip the deep-dive. Complex decisions (new/unfamiliar technology, unclear feature coverage) benefit from it.
- **Evidence:** dsm-graph-explorer Epoch 3 pre-planning (2026-03-09). Broad research evaluated 7 graph databases, produced DEC-006 (FalkorDBLite). Post-decision, 7 significant unknowns remained: Cypher subset, persistence model, multi-graph support, Python API, data model compatibility, testing patterns, known limitations. Sprint planning without resolving these would produce speculative task breakdowns. See `methodology.md` Entry 33.

### Proposal #29: Standard Experiment Documentation Template (Seven Elements)
- **DSM Section:** DSM 4.0 Section 4 (Tests vs Capability Experiments), DSM 1.0 Section 2.2 (Research & Context Building)
- **Problem:** DSM 4.0 Section 4 distinguishes tests from capability experiments but does not prescribe the internal documentation structure of an experiment. In practice (five experiments across this project), experiments were written with varying levels of rigor: some had justification but no success criteria; some had results but no explicit decision; none documented their execution environment. An online research session validated the proposed four-element structure (Justification, Expected Results, Validation, References) against six frameworks and identified three gaps present in every framework surveyed: no Success Criteria element, no Environment/Setup element, and no named Decision/Conclusion element. See `dsm-docs/research/experiment-documentation-standards.md` and `methodology.md` Entry 34.
- **Proposed Solution:** Define a seven-element experiment documentation template for DSM 4.0 Section 4:

  | # | Element | When | Description |
  |---|---------|------|-------------|
  | 1 | **Justification** | Pre-run | Why this experiment is needed; name the specific decision or gate it unlocks (ADR number, sprint phase) |
  | 2 | **Hypothesis** | Pre-run | The testable claim: "If [X], then [Y], because [Z]." Include the expected failure mode |
  | 3 | **Success Criteria** | Pre-run | What is measured, how it is measured, and the explicit pass/fail threshold per criterion |
  | 4 | **Environment** | Pre-run | Python version, key library versions, OS/hardware, random seeds, configuration flags |
  | 5 | **Results** | Post-run | Raw outcomes per criterion (actual values, not yet interpreted) |
  | 6 | **Decision** | Post-run | Pass / Fail / Inconclusive; explicit "expected X, observed Y, conclusion Z" per criterion; gate outcome (GO / NO-GO) |
  | 7 | **References** | Both | Backward: ADRs, plan sections, inbox entries, prior experiments. Forward: which decision this fed (added post-decision) |

  **Minimal variant** for lighter experiments: keep the four-element structure but add mandatory sub-elements: (a) pass/fail threshold as a required sub-element of "Expected Results," (b) gate outcome (GO/NO-GO) as a required sub-element of "Validation."

- **Evidence:** EXP-003 through EXP-005 in dsm-graph-explorer (2026-02-23 to 2026-03-10). Validated against: scientific method, Wohlin et al. "Experimentation in Software Engineering" (Springer 2024), GQM (Basili, UMD), FAIR principles (Nature 2016), NeurIPS reproducibility checklist, arXiv 2406.14325 (2024 ML reproducibility survey), Hypothesis-Driven Development (Cowan, IBM Garage, IEEE 2019). Full research: `dsm-docs/research/experiment-documentation-standards.md`. See `methodology.md` Entry 34.

### Proposal #30: "Challenge Myself to Reason" — Composition Challenge for Multi-Item Artifacts
- **DSM Section:** DSM_0.2 (Custom Instructions / Pre-Generation Brief Protocol), DSM 4.0 Section 3 (Development Protocol)
- **Problem:** The Pre-Generation Brief Protocol asks for What/Why/Key Decisions/Structure before generating artifacts. For single-item artifacts, this is sufficient. For multi-item artifacts (test suites, module files with multiple functions, multi-section documents), the protocol does not prompt either party to challenge the *composition*: why these N items, not more or fewer? In practice, the agent lists items and describes each one, but the collection as a whole goes unquestioned unless the human intervenes with ad-hoc challenges. This creates two problems: (1) the agent may include redundant items or miss important ones without detecting it; (2) the human must invent their own challenge questions rather than reviewing against a structured format.
- **Proposed Solution:** Add a "Composition Challenge" step to the Pre-Generation Brief, triggered when the artifact contains multiple items. The step uses an operational adaptation of Sinek's Golden Circle model (Why/What/How), extended with a "When" dimension for sequencing:

  | Dimension | Question | Value |
  |-----------|----------|-------|
  | **Why** | What requirement or goal does this collection serve? | Establishes purpose; prevents misaligned items |
  | **What** | Index of all items (high-level, no explanations) | Enables quick completeness review |
  | **Why not more or less** | Trace each item to a requirement; identify excluded candidates and reason for exclusion | Catches redundancy and gaps |
  | **How** | Key decisions, structure, execution approach | Supports standardization and error-proofing |
  | **When** | Is this the right next step in the sequence? | Catches ordering errors |

  The principle is named **"Challenge Myself to Reason"** and applies collaboratively: the agent uses it to proactively self-challenge before presenting, and the structured format gives the human a clear review framework to validate and approve against. Both parties reason through the same dimensions, replacing ad-hoc questioning with systematic review.

  **Trigger:** Multi-item artifacts only (3+ items). Single-item artifacts retain the existing single-sentence brief.

  **Not a replacement:** This enhances the existing What/Why/Key Decisions/Structure format by adding composition-level reasoning. The existing brief handles artifact-level context; the Composition Challenge handles item-level completeness.

- **Evidence:** dsm-graph-explorer Session 25 (2026-03-11), Sprint 9 Phase 9.3. Agent proposed 6 tests for `--graph-db` CLI integration. Presented per-test descriptions but did not justify the collection. User challenged: "why these 6?" then "why not more or less?" Agent's post-challenge reasoning was sound (traced to 5 checkpoint requirements + 1 real-data concern, identified 5 excluded candidates with reasons). The gap: this reasoning happened reactively after two user prompts, not proactively as part of the brief. See `methodology.md` Entry 35.

### Proposal #31: Edit Explanation Stop Protocol — Intra-File Approval Gates
- **DSM Section:** DSM_0.2 (Custom Instructions / Collaboration Protocol), DSM 4.0 Section 3 (Development Protocol)
- **Problem:** The file-by-file collaboration protocol (Proposal #15) and the Three-Gate Model (Proposal #24) define approval gates at the artifact level (before creating a file) and the phase level (concept → implementation → run). Neither addresses the intra-file edit level. When an implementation involves multiple distinct edits, the agent explains all edits and executes them in a single turn. The human sees explanation and diff simultaneously, with no opportunity to ask questions or redirect between edits. This is especially problematic for large edits or edits that involve non-trivial design choices embedded in the code.
- **Proposed Solution:** Add an **Edit Explanation Stop Protocol** to the collaboration workflow. For each distinct edit during implementation:

  1. **Explain:** Agent describes the edit in plain words: what it does, where it goes (file + location), and why (connection to current task). The explanation should be readable by someone who has not seen the code, not just "Added N lines."
  2. **Stop:** Agent stops and waits for human response.
  3. **Approve:** Human reads the explanation, asks questions if needed, approves.
  4. **Execute:** Agent performs the edit. Human reviews the resulting diff.

  **Grouping rule:** Trivial edits (fixing a typo, adding a single import, updating a version number) may be grouped and explained together. Distinct edits (different logical changes, different locations in the file, different design decisions) get separate cycles.

  **Relationship to existing protocols:**
  - Extends Proposal #24 (Three-Gate Model) to a finer granularity within the implementation gate
  - Complements Proposal #30 ("Challenge Myself to Reason"): the explanation pause is the moment where both parties reason about correctness
  - Replaces the implicit "approve the whole batch" pattern with explicit per-edit approval

- **Evidence:** dsm-graph-explorer Session 25 (2026-03-11), Sprint 9 Phase 9.3. Agent explained a multi-part edit to `cli.py` (expanding a guard condition, adding a dependency check, adding a persistence block) and attempted to execute all three in a single turn. User rejected the edit, noting that the explanation should have been a stopping point: "Stop after each explanation → I read, understand, ask questions, approve → continue → Edit." The agent had to re-approach the implementation one edit at a time. See `methodology.md` Entry 36.

### Proposal #32: Sprint Boundary Gate in /dsm-go Session Start
- **DSM Section:** DSM_0.2 (Custom Instructions / /dsm-go skill), DSM 2.0 Template 8 (Sprint Boundary Checklist)
- **Problem:** `/dsm-go` loads context from MEMORY.md and checkpoints, then suggests next work items (Step 9). No step verifies whether the previous sprint's boundary checklist was actually completed. MEMORY.md records "Sprint N complete" when code is committed, but the boundary checklist (checkpoint, journal, feedback, README) may not have been run. The agent conflates "code-complete" with "boundary-complete" and suggests starting the next sprint, leaving the boundary to the user's memory. This was caught in Session 28: Sprint 10 code was committed in Session 27, but the boundary checklist was never executed. The agent suggested Sprint 11 without noticing.
- **Proposed Solution:** Add a "Sprint Boundary Gate" step to `/dsm-go` between Step 3.5 (Checkpoint check) and Step 4 (Bandwidth report):

  ```
  Step 3.6 — Sprint Boundary Gate:
  1. Read the latest sprint number from MEMORY.md (e.g., "Sprint 10 complete")
  2. Check for boundary artifacts:
     a. Checkpoint: does dsm-docs/checkpoints/done/ contain a file matching the sprint?
     b. Journal: does the current epoch's blog journal have an entry for the sprint?
     c. README: does the Project Status section show the sprint as checked off?
  3. If all exist: report "Sprint N boundary verified" and continue
  4. If any are missing: report the missing artifacts as blockers:
     "Sprint N boundary incomplete. Missing: [list]. Complete the boundary
     checklist before starting new work."
  ```

  This is a verification gate, not a context-loading step. It blocks new work suggestions until the prior sprint is properly closed.

- **Evidence:** dsm-graph-explorer Session 28 (2026-03-12). Sprint 10 code committed in Session 27 (c8839e7). Session 28 `/dsm-go` loaded MEMORY.md ("Sprint 10 complete"), found no pending checkpoints (all moved to `done/` in Session 27), and suggested Sprint 11. User caught the missing boundary. Investigation confirmed: no Sprint 10 checkpoint, no journal entry, no README update, no feedback update. See `methodology.md` Entry 37.

### Proposal #33: Epoch Plan Update in Sprint Boundary Checklist
- **DSM Section:** DSM 2.0 Template 8 (Sprint Boundary Checklist), CLAUDE.md (project-level checklist)
- **Problem:** The Sprint Boundary Checklist lists 5 items (checkpoint, feedback, decisions, journal, README) but does not include "update epoch plan." The epoch plan document (`dsm-docs/plans/epoch-N-plan.md`) is the roadmap for the epoch; it contains per-sprint task lists with checkboxes. Since the checklist drives wrap-up behavior, the plan is systematically skipped at every sprint boundary. In dsm-graph-explorer, `epoch-3-plan.md` was created at Session 24 (Sprint 9 start) and never updated through Sprint 9 and Sprint 10 completion, leaving all tasks as `[ ]` despite both sprints being fully delivered.
- **Proposed Solution:** Add a sixth item to the Sprint Boundary Checklist:

  ```
  - [ ] Epoch plan updated (completed tasks checked off, sprint status updated)
  ```

  At sprint wrap-up, the agent marks the current sprint's tasks as `[x]` in the epoch plan and updates the sprint status from `PLANNED` to `COMPLETE`. This takes one edit per sprint and keeps the plan accurate as a progress tracker.

- **Evidence:** dsm-graph-explorer Session 29 (2026-03-12). `epoch-3-plan.md` created at Session 24. Sprints 9 and 10 fully complete (402 tests, all phases delivered, boundary checklists done for both). All 40+ task checkboxes in Sprints 9 and 10 still show `[ ]`. The plan lost its value as a progress instrument. Root cause: not in the checklist. See `methodology.md` Entry 38.

### Proposal #34: Alignment Review at Sprint Transitions
- **DSM Section:** DSM 2.0 Template 8 (Sprint Boundary Checklist), DSM_0.2 (Custom Instructions / session protocol)
- **Problem:** Even with Proposal #33's plan update step, the epoch plan is treated as a documentation artifact updated mechanically. But it is also a collaboration artifact reflecting shared understanding of scope and progress. Without a review step, the user must independently verify every checkbox and catch drift between plan and reality. In Session 29, after updating epoch-3-plan.md, the user explicitly requested: "confirm we are aligned and highlight any changes." The agent had no protocol step prompting this review.
- **Proposed Solution:** Add an "Alignment Review" step to the sprint transition protocol, after the plan update (Proposal #33) and before starting new sprint work:

  ```
  Sprint Transition — Alignment Review:
  After updating the epoch plan, present a summary to the user:
  1. What was completed (tasks checked off)
  2. Deviations from the original plan (scope changes, reordering)
  3. Additions not in the plan (new modules, extra tests, unplanned work)
  4. Current epoch progress (N of M MUSTs, N of M SHOULDs)
  5. Next sprint scope for confirmation
  Wait for user confirmation before starting the next sprint.
  ```

  This is a collaboration checkpoint, not a documentation step. It ensures the user and agent share the same understanding of where the project stands and where it's going.

- **Evidence:** dsm-graph-explorer Session 29 (2026-03-12). Agent updated epoch-3-plan.md (Sprint 9+10 checkboxes). User requested explicit alignment review and confirmation. Several deviations from original plan existed (find_repo_root() not planned, content-based parser variants not planned, CLI version bump). Without the review, these would have gone unnoticed. See `methodology.md` Entry 39.

### Proposal #35: Hub/Portfolio Notification in Sprint Boundary Checklist
- **DSM Section:** DSM 2.0 Template 8 (Sprint Boundary Checklist), DSM_0.2 (Custom Instructions / CLAUDE.md)
- **Problem:** The Sprint Boundary Checklist (6 items after Proposal #33) is entirely project-local. No item notifies hub projects (DSM Central, portfolio) that a spoke sprint completed. Hub projects only learn about spoke progress through indirect channels: feedback entries (methodology observations, not status signals) or manual README inspection. The `_inbox/` mechanism exists in both DSM Central and the portfolio for exactly this kind of cross-repo notification, but the boundary checklist does not invoke it. As a result, the portfolio's project status and DSM Central's ecosystem awareness are always stale.
- **Proposed Solution:** Add a 7th item to the Sprint Boundary Checklist:

  ```
  - [ ] Hub/portfolio notified of sprint completion (`_inbox/` in DSM Central and portfolio)
  ```

  At sprint wrap-up, the agent writes a brief notification file to each target's `_inbox/`:

  ```markdown
  # Sprint Completion: [Project Name] Sprint N
  **Date:** YYYY-MM-DD
  **Project:** [project name]
  **Sprint:** N — [sprint title]
  **Key deliverables:** [1-3 bullet points]
  **Tests:** N passed, N% coverage
  **Status:** [what's next]
  ```

  This is a push notification, not a pull mechanism. The hub processes its `_inbox/` at session start (per DSM_0.2 inbox protocol) and updates its awareness without polling spoke repositories.

  **Notification targets:**
  - DSM Central `_inbox/`: methodology ecosystem awareness
  - Portfolio `_inbox/`: project status tracking

- **Evidence:** dsm-graph-explorer Session 30 (2026-03-12). User asked "when do we inform central DSM and ds-portfolio about the sprint's boundary checklist completion?" during Sprint 11 boundary. Investigation confirmed no existing checklist item triggers hub/portfolio notification. See `methodology.md` Entry 40.

### Proposal #36: Ecosystem Alignment Gate at Epoch Boundaries
- **DSM Section:** DSM 2.0 (Project Management / Epoch Transition Protocol), DSM_0.2 (Custom Instructions / Planning Protocol)
- **Problem:** The Research Gate (Proposal #27) prescribes Idea -> Research -> Plan -> Action, addressing technical uncertainty within the project. It does not address ecosystem-level changes that accumulate over long development timeframes. Projects spanning multiple epochs (weeks to months) experience DSM ecosystem evolution: new DSM versions, adopted proposals, new spoke projects, portfolio priority shifts. Without checking ecosystem state before epoch planning, the project drafts plans against stale assumptions. The planning sequence should be: Idea -> Ecosystem Alignment -> Research (if uncertainty) -> Plan -> Action.
- **Proposed Solution:** Add an "Ecosystem Alignment Gate" to the epoch transition protocol, between the epoch retrospective and the Research Gate:

  ```
  Epoch Transition — Ecosystem Alignment Gate:
  Before drafting an epoch plan, the project consults the DSM hub:

  1. Send an alignment request to DSM Central _inbox/ containing:
     a. Current project state (epoch completed, metrics, capabilities)
     b. Candidate items for next epoch (carry-forward, deferred, new ideas)
     c. Questions: DSM version changes, proposal adoption status,
        new spoke projects, portfolio priorities

  2. Wait for hub response before drafting the epoch plan

  3. Incorporate hub feedback into scope and priority decisions
  ```

  This gate is triggered at epoch boundaries only, not at sprint boundaries. Sprint-level changes are too granular for ecosystem alignment; epoch-level changes are where strategic drift accumulates.

  **Relationship to existing protocols:**
  - Extends the Research Gate (Proposal #27) with an ecosystem dimension
  - Complements Hub/Portfolio Notification (Proposal #35): that sends status out; this requests context in
  - Does not replace the Research Gate: ecosystem alignment addresses "has the environment changed?"; research addresses "how should we build the next feature?"

- **Evidence:** dsm-graph-explorer Session 32 (2026-03-13). Project completed Epoch 3 (12 sprints, 6+ weeks, 35 proposals submitted). At epoch transition, the user identified that no protocol step checks whether the DSM ecosystem has evolved since Epoch 3 started. The project's CLAUDE.md implements several proposals locally (#15, #24, #30, #31) without knowing their adoption status. Epoch 4 planning would proceed on assumptions from 2026-03-10 (Epoch 3 start) without this gate. See `methodology.md` Entry 41.

### Proposal #37: Open Source Contribution Pipeline (Issue → Blog → PR)
- **DSM Section:** DSM 4.0 Section 4 (Tests vs Capability Experiments), DSM 2.0 (Strategic Visibility / Blog Process)
- **Problem:** DSM 4.0 capability experiments routinely discover gaps in external libraries (undocumented APIs, missing testing guidance, incomplete examples, version requirements). These findings are documented internally (research files, experiment scripts, blog journal) but never converted into upstream contributions. Each undocumented gap is simultaneously: (a) an impediment for other users of the library, (b) a natural contribution opportunity, and (c) a public visibility artifact for take-ai-bite and DSM. The current workflow stops at internal documentation, leaving strategic value unrealized.
- **Proposed Solution:** Add an "Open Source Contribution Pipeline" assessment step after capability experiments that validate external libraries:

  ```
  Post-Experiment Assessment — Contribution Pipeline:
  After completing a capability experiment (EXP-xxx) that validates an external library:

  1. Assess: Did the experiment discover documentation or usability gaps?
     Decision criteria:
     a. Would other users likely hit the same gap?
     b. Do we have enough evidence to document it clearly?
     c. Does the contribution showcase DSM methodology?
     If all three: suggest the pipeline. If not: skip.

  2. Step 1 — Issue: Open a GitHub issue on the upstream repo documenting
     the gaps. Include a link to the take-ai-bite project that discovered them.
     Gauge maintainer responsiveness before investing in a PR.

  3. Step 2 — Blog post: Write a blog post narrating the discovery process.
     Focus on how structured capability experiments (DSM 4.0 Section 4)
     systematically surface gaps that ad-hoc usage misses. This is the
     methodology showcase.

  4. Step 3 — PR: If maintainers are responsive, contribute the fix
     (documentation, examples, tests). The PR establishes take-ai-bite
     as a contributor in the library's ecosystem.
  ```

  **Scaling:** This pattern applies across all spoke projects. Any experiment that validates an external library is a potential pipeline trigger. Over time, contributions across multiple libraries compound into a visible open-source presence.

  **Relationship to existing protocols:**
  - Extends the experiment documentation template (Proposal #29) with a post-experiment assessment
  - Feeds the blog process (DSM 1.0 Section 2.5.6-2.5.8) with a specific narrative type: "experiment becomes contribution"
  - Complements the Ecosystem Alignment Gate (Proposal #36): contributions create bidirectional relationships with library ecosystems, not just dependency relationships

- **Evidence:** dsm-graph-explorer Session 33-34 (2026-03-13). EXP-005 (FalkorDBLite validation, 16/16 checks) and deep-dive research discovered 5 documentation gaps: import path confusion, no testing guidance, no complete working example, editable install failure, Python 3.12+ requirement. Session 34 opened FalkorDB/falkordblite#85 with project link. Blog journal already contained the narrative thread "when your experiment becomes upstream documentation." See `methodology.md` Entry 42.

### Proposal #38: Plan Notification to Hub/Portfolio After Drafting
- **DSM Section:** DSM 2.0 (Project Management / Planning Protocol), DSM_0.2 (Custom Instructions / Ecosystem Notifications)
- **Problem:** The DSM ecosystem has two notification mechanisms for spoke-to-hub communication: the Ecosystem Alignment Gate (Proposal #36, inbound: spoke asks hub before planning) and the Sprint Boundary Notification (Proposal #35, outbound: spoke tells hub after completing a sprint). Between these two points, the drafted plan is never communicated. The hub and portfolio learn what a spoke *did* but not what it *intends to do*. In a multi-spoke ecosystem, this creates a coordination gap: the hub could start work that conflicts with a spoke's planned direction, and other spokes could duplicate effort. The gap widens as more spoke projects join the ecosystem.
- **Proposed Solution:** Add a "Plan Notification" step to the DSM planning protocol (DSM 2.0), applicable to all spoke projects:

  ```
  Plan Notification (all DSM spoke projects):
  After drafting any plan (epoch plan for larger projects, sprint plan
  for smaller projects):

  1. Send a structured notification to hub and portfolio _inbox/ folders:
     - Plan summary (scope table with MoSCoW priorities)
     - Relevance to recipient's current work (how the plan intersects
       with hub-level items, other spokes, or portfolio goals)
     - Pointer to the full plan document
     - Requested action: review and flag conflicts before execution starts

  2. The notification is informational with an alignment request,
     not a blocking gate. The spoke can begin execution immediately
     but should incorporate feedback if the hub responds before the
     first sprint completes.
  ```

  **Scaling:** The trigger scales with project size:
  - **Larger projects (multi-sprint epochs):** Notify at epoch plan draft
  - **Smaller projects (single-sprint scope):** Notify at sprint plan draft
  - **Micro-projects (no sprints):** Skip; the overhead exceeds the value

  **Notification loop (complete):**
  ```
  Alignment request (inbound, Proposal #36)
    → Plan draft
      → Plan notification (outbound, this proposal)
        → Execution (sprints)
          → Sprint completion notification (outbound, Proposal #35)
  ```

  **Relationship to existing protocols:**
  - Complements Proposal #36 (Ecosystem Alignment Gate): that is inbound (spoke asks hub); this is outbound (spoke informs hub)
  - Complements Proposal #35 (Sprint Boundary Notification): that reports completed work; this reports planned work
  - Together, Proposals #35, #36, and #38 form a complete bidirectional communication loop between spokes and hub

- **Evidence:** dsm-graph-explorer Session 34 (2026-03-13). After drafting the Epoch 4 plan using DSM Central's alignment response, the user requested notifications to both DSM Central and portfolio, stating: "This pattern should be triggered every time a plan is drafted." The notification was sent manually; no protocol step triggered it. See `methodology.md` Entry 43.

### Proposal #39: Inbox Anti-Pattern Guard — No Full File Copies in _inbox/
- **DSM Section:** DSM_0.2 (Custom Instructions / Inbox Protocol), DSM_3 Section 6.4 (Bidirectional Project Inbox)
- **Problem:** An agent interpreted "push feedback to DSM Central inbox" as copying the full `methodology.md` (76KB) and `backlogs.md` (61KB) files into `_inbox/`. The `_inbox/README.md` defines the inbox as a transit point for brief structured entries, but does not explicitly prohibit file copies. The error compounded across multiple sessions, with each push overwriting the previous copy with a larger file. The root cause was a compressed memory entry ("Three-file atomic feedback: methodology.md + backlogs.md + DSM Central inbox") that was ambiguous about whether "DSM Central inbox" was a destination for the files or a third action (push a notification).
- **Proposed Solution:** Two changes:

  1. **Add anti-pattern guard to `_inbox/README.md`:**
     ```markdown
     ## Anti-Patterns
     - **Never copy full feedback files** (methodology.md, backlogs.md) into _inbox/.
       Inbox entries are notifications with pointers, not file mirrors.
       Reference the spoke's files by path (e.g., "See ~/project/dsm-docs/feedback-to-dsm/
       methodology.md Entry 42").
     - **Maximum entry size:** Each entry should be a brief summary (5-15 lines),
       not a reproduction of the source material.
     ```

  2. **Clarify the three-file atomic feedback pattern in DSM_0.2:**
     ```
     Three-file atomic feedback:
     1. Update methodology.md in the spoke project (dsm-docs/feedback-to-dsm/)
     2. Update backlogs.md in the spoke project (dsm-docs/feedback-to-dsm/)
     3. Push a brief structured notification to DSM Central _inbox/{project-name}.md
        summarizing the new entry and pointing to the spoke's files
     The third file is a notification, not a copy.
     ```

  **Scope:** All DSM spoke projects. Any agent reading compressed memory or ambiguous instructions could make the same mistake.

- **Evidence:** dsm-graph-explorer Session 34 (2026-03-13). Agent copied full methodology.md (76KB) and backlogs.md (61KB) into DSM Central `_inbox/`. The `_inbox/README.md` template shows entries of 5-10 lines; the copied files were 470+ and 550+ lines respectively. Error persisted across multiple sessions. See `methodology.md` Entry 44.

### Proposal #40: Inbox Filename Convention — Dated and Content-Identified
- **DSM Section:** DSM_0.2 (Custom Instructions / Inbox Protocol), DSM_3 Section 6.4 (Bidirectional Project Inbox)
- **Problem:** The `_inbox/README.md` prescribes filenames as `{project-name}.md` (e.g., `dsm-graph-explorer.md`). This convention lacks temporal context (when was it pushed?) and content identification (what does it contain?). The hub must open every file to understand and prioritize its contents. In a multi-spoke ecosystem with frequent notifications, this creates unnecessary overhead. The filesystem's modification timestamp is the only temporal signal, and it is fragile (copies, moves, edits all change it).
- **Proposed Solution:** Update the `_inbox/README.md` filename convention:

  **General pattern:** `{date}_{project-name}_{content-description}.md`

  **Specific patterns by notification type:**
  | Type | Pattern | Example |
  |------|---------|---------|
  | Feedback entries | `{date}_{project}_feedback-entries-{from}-{to}.md` | `2026-03-13_dsm-graph-explorer_feedback-entries-42-44.md` |
  | Plan notification | `{date}_{project}_{plan-type}-drafted.md` | `2026-03-13_dsm-graph-explorer_epoch-4-plan-drafted.md` |
  | Sprint completion | `{date}_{project}_sprint-{N}-complete.md` | `2026-03-13_dsm-graph-explorer_sprint-12-complete.md` |
  | Alignment request | `{date}_{project}_alignment-request.md` | `2026-03-13_dsm-graph-explorer_epoch-4-alignment-request.md` |

  **Benefits:**
  - Self-documenting: hub can triage by scanning filenames
  - Temporally ordered: `ls` sorts by date prefix
  - Content-identified: no need to open files to prioritize
  - Applies to all DSM spoke projects and all notification types

- **Evidence:** dsm-graph-explorer Session 34 (2026-03-13). Agent created `dsm-graph-explorer.md` (no date) in `_inbox/`. User corrected to `2026-03-13_dsm-graph-explorer_feedback-entries-42-44.md`. The `_inbox/README.md` file convention only prescribes `{project-name}.md`. See `methodology.md` Entry 45.

### Proposal #41: DSM_0.2 Modular Split Section Numbering Consistency
- **DSM Section:** DSM_0.2 (Custom Instructions / Module Dispatch Table), DSM_3 (Cross-Project Communication)
- **Problem:** The BL-090 modularization split DSM_0.2 from a single file (2,625 lines) into a slim core plus four modules (A-D). The pre-split document used numbered section references throughout (e.g., "Section 6.6", "Section 6.4.3", "Section 7"). After the split, the referenced content moved to module files, but the section references were not updated to indicate which module contains the target. Inline prose still says "Section 6.6" without specifying that it now lives in Module A or Module D. Any consumer following these references (agents, tools, humans) cannot locate the target without reading all module files.
- **Proposed Solution:** Two options (not mutually exclusive):

  1. **Update references to include module context:** Replace bare section references with module-qualified references. For example: "Section 6.6 (Module A)" or "see the Lightweight Session Lifecycle protocol in Module A." This is the minimal fix.

  2. **Add a section number mapping:** Include a mapping table in the core file or as an appendix that maps legacy section numbers to their module locations:
     ```
     | Legacy Section | Module | Current Heading |
     |---------------|--------|-----------------|
     | 6.4.3 | A | Session-End Inbox Push |
     | 6.6 | D | External Contribution |
     | 6.8 | Core | Private Project |
     ```

  Option 1 is lower effort and more sustainable (references are self-contained). Option 2 is a temporary migration aid that becomes stale as modules evolve.

- **Evidence:** dsm-graph-explorer Session 35 (2026-03-16). EXP-007 compared pre-split (v1.3.59) against post-split (v1.3.69) DSM_0.2 using GE's cross-reference validator. Both versions produce only warnings (0 errors), but the warnings reveal unresolvable section references pointing to content that moved to modules. See `methodology.md` Entry 46.

### Proposal #42: Heading-Based Section Detection in GE Parser
- **DSM Section:** DSM 4.0 (Software Engineering / Parser Design), DSM_0.2 (Custom Instructions / Tool Resilience)
- **Problem:** GE's `markdown_parser.py` only recognizes numbered section headings (pattern: `### 2.1 Title`). Documents that use plain markdown headings (`## Title`) produce zero section nodes in the graph. DSM_0.2 itself uses the heading-level format exclusively, meaning GE cannot build a meaningful section graph of the very methodology it validates. This limitation was surfaced by EXP-007 (0 sections detected in a 2,625-line document) and affects any markdown document that uses standard heading conventions.
- **Proposed Solution:** Add heading-based section detection alongside the existing numbered-section detection:

  1. **Detection:** Every markdown heading (`#` through `######`) becomes a candidate SECTION node. The heading level (count of `#` characters) provides hierarchy depth. The heading text provides the section identity.

  2. **Graph structure:** Each heading creates a SECTION node with attributes: `level` (1-6), `title` (heading text), `file`, `line`. Parent-child relationships derive from heading levels (an `##` is a child of the preceding `#`).

  3. **Cross-reference resolution:** For heading-based sections, resolve references by title matching:
     - Exact match first (e.g., "Pre-Generation Brief Protocol" matches `## Pre-Generation Brief Protocol`)
     - Fuzzy match via existing TF-IDF infrastructure (Sprint 6) for partial or paraphrased references

  4. **Activation:** Either default behavior (auto-detect which style the document uses) or a CLI flag (`--heading-sections`). Auto-detection is preferred: if numbered sections are found, use numbered mode; if not, fall back to heading-based mode.

  **Scope:** This is a GE enhancement, not a DSM methodology change. It makes GE useful for any markdown document, not just those with numbered sections.

- **Evidence:** dsm-graph-explorer Session 35 (2026-03-16). EXP-007 found 0 sections in DSM_0.2 (both pre-split and post-split) because the parser only recognizes numbered sections. The user noted: "The important part of the section is the level (#, ##, ###) not the number, and of course the section title that is handled with NLP or other approach." See `methodology.md` Entry 47.

---

## Low Priority

_No low-priority items identified yet._

---

**Last Updated:** 2026-03-16
**Total Proposals:** 42
**Pushed:** 2026-03-16 (Proposals #41-42 pushed simultaneously with creation)
