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
- **Proposed Solution:** Add a mandatory step between Phase 0 (Setup) and Phase 1 (Development): "**Phase 0.5: Research & Grounding** — Before implementation, conduct a brief state-of-the-art review: (1) identify related tools and approaches, (2) assess gaps your project fills, (3) validate your technical approach against published best practices, (4) document findings in `docs/research/`."
- **Evidence:** A research review (coreference resolution literature, existing markdown link checkers, code static analysis patterns) confirmed our regex approach fills a real gap and follows the well-established parsing → resolution → validation pipeline. Without it, we would have proceeded on assumption rather than evidence.

### Create comprehensive docs/ folder structure reference document
- **DSM Section:** DSM 4.0 Section 2 (Project Structure Patterns)
- **Problem:** DSM 4.0 Section 2 lists folder names (`docs/handoffs/`, `docs/decisions/`, etc.) but does not adequately explain the **purpose** of each subfolder, what **files** belong in each, the **format** expected for each file type, or the **relationship** between folders. AI agents (and humans new to DSM) cannot understand the structure without external references.
- **Proposed Solution:** Create a "docs/ Folder Structure Reference" section in DSM 4.0 Section 2. For each subfolder, document:
  1. **Purpose** — What this folder is for (e.g., "feedback/ contains observations about DSM methodology effectiveness")
  2. **Files** — List of expected files with descriptions (e.g., "backlogs.md — proposed improvements to DSM")
  3. **Format** — Template or format specification for each file type
  4. **Timing** — When files are created/updated (e.g., "at sprint boundaries")
  5. **Relationship** — How this folder relates to others (e.g., "feedback/ is for DSM methodology feedback; backlog/ is for cross-project alignment reports")
  Include a link to a reference implementation project (e.g., sql-query-agent) as a concrete example.
- **Evidence:** During Sprint 3 closure, the AI agent required **6 explicit corrections** from the user:
  1. Tried to create backlog items in DSM repository instead of project's `docs/feedback/backlogs.md`
  2. Confused `docs/feedback/` vs `docs/blog/` for blog-related files
  3. Did not understand `docs/backlog/` (alignment) vs `docs/feedback/` (DSM feedback) distinction
  4. User had to provide `docs-folder-reference-sql-agent.md` as explicit reference
  5. User had to point to sql-agent files as format examples
  6. Multiple iterations needed to get file formats correct
  This level of confusion — requiring an external reference project — indicates the documentation is insufficient for self-contained understanding.

---

## Medium Priority

### Standardize feedback file location in DSM 4.0 project structure template
- **DSM Section:** DSM 4.0 Section 2 (Project Structure Patterns)
- **Problem:** DSM specifies feedback files as loose files in the `docs/` directory (e.g., `docs/dsm-feedback-backlogs.md`), inconsistent with the subfolder pattern used for all other document types (`docs/handoffs/`, `docs/decisions/`, `docs/checkpoints/`, `docs/blog/`).
- **Proposed Solution:** Update DSM 4.0 Section 2 project structure template to use `docs/feedback/` as a subfolder (containing `backlogs.md`, `methodology.md`) instead of loose `docs/dsm-feedback-*.md` files.
- **Evidence:** Feedback files were initially created at `docs/dsm-feedback-*.md` following the Phase 0 handoff instructions, then had to be manually moved to `docs/feedback/` mid-project. References in CLAUDE.md, README.md, and SPRINT_PLAN.md all needed updating.

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
- **Proposed Solution:** Formalize "Cross-Project Alignment Report" as a standard DSM artifact. Template: Transfer Items (what pattern, source, status), Observations, Action Items. Location: `docs/backlog/dsm-alignment-*.md`.
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
  - Store source in docs/blog/<epoch>/images/ as .mmd files
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

### Add docs/guides/ subfolder for user-facing documentation
- **DSM Section:** DSM 4.0 Section 2 (Project Structure Patterns)
- **Problem:** All existing `docs/` subfolders serve project-management purposes: `checkpoints/`, `decisions/`, `handoffs/`, `feedback/`, `blog/`, `backlog/`, `plan/`. User-facing documentation (installation guides, configuration references, how-tos) has no prescribed location. Projects either place guides in an ad-hoc subfolder or mix them with PM artifacts, blurring the folder structure's intent.
- **Proposed Solution:** Add `docs/guides/` to the DSM 4.0 Section 2 project structure template as a standard subfolder for user-facing documentation. Contents would include installation guides, configuration references, API documentation, and how-to guides. This keeps the existing PM subfolders focused on their original purpose while giving user-facing content a clear home.
- **Evidence:** In dsm-graph-explorer Sprint 5, a remediation guide and a configuration reference needed a location. No existing subfolder fit, so `docs/guides/` was created ad-hoc. The separation immediately clarified the folder structure: PM artifacts in their respective subfolders, user-facing docs in `guides/`. See `methodology.md` Entry 20.

### Rename docs/feedback/ to docs/feedback-to-dsm/ for explicit directionality
- **DSM Section:** DSM 4.0 Section 2 (Project Structure Patterns)
- **Problem:** The folder name `docs/feedback/` does not convey that its contents are feedback *to DSM* (methodology observations and improvement proposals). The generic name is easily confused with `docs/backlog/` (cross-project alignment reports), especially since `feedback/` contains a file called `backlogs.md`, making the word "backlog" appear in both contexts with different meanings. A new contributor or AI agent cannot distinguish the two folders by name alone.
- **Proposed Solution:** Rename `docs/feedback/` to `docs/feedback-to-dsm/` in the DSM 4.0 Section 2 project structure template. The directional name makes the folder's purpose self-documenting: it contains observations and proposals flowing from the project back to the DSM methodology. No change to file contents or the three-file feedback system itself.
- **Evidence:** In dsm-graph-explorer, the AI agent confused `docs/feedback/` with `docs/backlog/` on multiple occasions (see also Entry 5 in methodology.md). The naming collision between the folder `docs/backlog/` and the file `docs/feedback/backlogs.md` compounds the ambiguity. See `methodology.md` Entry 21.

### Add next-steps summary to Sprint Boundary Checklist
- **DSM Section:** Section 6.4 (Checkpoint and Feedback Protocol) + DSM 2.0 Template 8
- **Problem:** The Sprint Boundary Checklist is entirely backward-looking: checkpoint, feedback, decisions, journal, README. It captures what was done but not what comes next. The next session starts without immediate orientation and must re-read the epoch plan to determine the upcoming sprint's goal and deliverables.
- **Proposed Solution:** Add a "Next steps summary" item to the Sprint Boundary Checklist: a brief paragraph (3-5 sentences) describing the next sprint's goal, key deliverables, and relevant plan reference. Example: "Sprint 6 implements semantic validation: TF-IDF keyword similarity and drift detection (EXP-003). Key deliverables: `src/validator/semantic_validator.py`, capability experiment results. See epoch-2-plan.md Phase 6." This item should be written into the checkpoint document and/or MEMORY.md so the next session can orient immediately.
- **Evidence:** Sprint 5 wrap-up in dsm-graph-explorer completed all checklist items (checkpoint, journal, feedback, README) but omitted any forward-looking summary. The next session had to re-read the epoch plan to understand what Sprint 6 involves. A single paragraph at wrap-up would have saved that orientation step. See `methodology.md` Entry 22.

---

## Low Priority

_No low-priority items identified yet._

---

**Last Updated:** 2026-02-10
**Total Proposals:** 19
