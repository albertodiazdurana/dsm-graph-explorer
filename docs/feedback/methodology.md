# DSM Feedback: Project Methodology

**Project:** DSM Graph Explorer
**Author:** Alberto Diaz Durana
**DSM Version Used:** DSM 4.0 v1.0, DSM 1.0 v1.1
**Date:** 2026-01-31 (started)
**Duration:** Sprint 1-10 complete

---

## 1. Project Overview

| Item | Planned | Actual |
|------|---------|--------|
| **Objective** | Repository integrity validator for DSM cross-references | Complete — CLI tool validates 125 files with config-based severity |
| **Language** | Python 3.12+ | Active — pytest, Click, Rich, Pydantic, PyYAML |
| **Timeline** | 8 sprints (Parser → Validation → CLI → Config → CI → Semantic → Graph → Linting) | Sprint 7 complete |
| **Deliverables** | CLI tool + integrity reports + blog | CLI with exclusions, config, severity, semantic drift detection, graph prototype |

---

## 2. Technical Pipeline (What Was Actually Built)

### Phase 0: Environment Setup
- Repository created at `D:\data-science\dsm-graph-explorer\`
- Project structure: `src/`, `tests/`, `docs/`, `outputs/`
- pyproject.toml with pytest, Click, Rich dependencies
- CLAUDE.md configured for Claude Code collaboration

### Sprint 1: Parser MVP
- `src/parser/markdown_parser.py` — extracts sections from headings
- `src/parser/cross_ref_extractor.py` — extracts cross-references from body text
- 52 unit tests, 98% coverage
- DEC-001: Pure regex over markdown libraries

### Sprint 2: Validation Engine
- `src/validator/cross_ref_validator.py` — validates refs against section index
- `src/validator/version_validator.py` — checks version consistency
- `src/reporter/report_generator.py` — markdown + Rich console output
- 74 new tests (126 total), 99% coverage

### Sprint 3: CLI & Real-World Run
- `src/cli.py` — Click-based CLI wiring full pipeline
- 19 tests (145 total), 98% coverage
- First real-world run: 122 files, 448 errors, 0 warnings (after fix)
- DEC-002: CLI design choices documented

### Sprint 4: Exclusion & Severity (Epoch 2)
- `src/config/config_loader.py` — Pydantic config models, YAML loading, config discovery
- `src/filter/file_filter.py` — fnmatch-based exclusion patterns
- `src/validator/cross_ref_validator.py` — INFO severity, `assign_severity()`, `apply_severity_overrides()`
- `src/reporter/report_generator.py` — INFO sections in markdown and Rich output
- `src/cli.py` — `--exclude`, `--config`, severity wiring, info count in summary
- 73 new tests (218 total), 95% coverage
- EXP-001 (Exclusion Patterns) and EXP-002 (Severity Classification) validated
- Real-world run: 125 files, 10 errors (Section 2.6), 0 warnings, 0 info

---

## 3. Libraries & Tools

| Library | Version | Purpose |
|---------|---------|---------|
| click | 8.1+ | CLI framework |
| rich | 13.0+ | Console output formatting |
| pydantic | 2.0+ | Config validation (Sprint 4) |
| pyyaml | 6.0+ | YAML config parsing (Sprint 4) |
| pytest | 7.4+ | Testing framework |
| pytest-cov | 4.1+ | Coverage reporting |

---

## 4. DSM Section Scoring

### Sections Used

| DSM Section | Sprint | Times Used | Avg Score | Top Issue |
|-------------|--------|------------|-----------|-----------|
| DSM 4.0 Section 2 (Project Structure) | Phase 0, S1, S3 | 4 | 3.3 | docs/ folder structure unclear for agents |
| DSM 4.0 Section 3 (Development Protocol) | S1, S2, S3, S4 | 5 | 3.7 | Missing pre-generation brief, explicit approval |
| Section 2.5.6 (Blog Process) | Phase 0, S1, S4 | 3 | 4.5 | Date prefix and metadata missing |
| Section 6.4 (Checkpoint Protocol) | S1, S2, S3, S4 | 4 | 4.5 | Missing sprint boundary checklist |
| Section 6.5 (Gateway Reviews) | S2 | 1 | 5.0 | None |
| Custom Instructions Template | S2, S3 | 2 | 3.5 | Explicit approval wording needed |
| Cross-Project Alignment (new) | S3 | 1 | 5.0 | Should be formalized in DSM |
| Research-First Planning (new) | S4 | 1 | 4.5 | Effective; should be standard |

### Entry 1: DSM 4.0 Section 2 (Project Structure Patterns)
- **Date:** 2026-01-31 | **Sprint:** Phase 0 | **Type:** Success
- **Context:** Setting up project repository structure following DSM 4.0 pattern
- **Finding:** Clear distinction between DSM 1.0 vs DSM 4.0 patterns; easy to follow. In-repo `docs/` structure worked well.
- **Scores:** Clarity 5, Applicability 5, Completeness 4, Efficiency 5 (Avg: 4.75)
- **Recommendation:** None — this section worked well.

### Entry 2: Section 2.5.6 (Blog/Communication Process)
- **Date:** 2026-01-31 | **Sprint:** Phase 0 | **Type:** Success
- **Context:** Preparing blog materials before implementation
- **Finding:** Materials template provided structure upfront; prevented technical debt. Journal capture during sprints produced rich material.
- **Scores:** Clarity 5, Applicability 5, Completeness 5, Efficiency 5 (Avg: 5.0)
- **Recommendation:** None — this section worked excellently.

### Entry 3: DSM 4.0 Section 3 (Development Protocol) — Pre-generation Brief Gap
- **Date:** 2026-02-01 | **Sprint:** S1 | **Type:** Gap
- **Context:** Starting TDD implementation. Agent generated test fixture + full test suite without explanation.
- **Finding:** The TDD workflow says "write tests first" but doesn't address the collaboration pattern where the human needs to understand and approve what will be created before the AI generates it.
- **Scores:** Clarity 3, Applicability 4, Completeness 2, Efficiency 3 (Avg: 3.0)
- **Recommendation:** Add "Pre-generation brief" step: explain what, why, contents before generating. See `backlogs.md`.

### Entry 4: DSM 4.0 Section 2 — Feedback File Location Inconsistency
- **Date:** 2026-02-01 | **Sprint:** S1 | **Type:** Pain Point
- **Context:** Feedback files initially created at `docs/dsm-feedback-*.md` per handoff instructions
- **Finding:** DSM specifies loose files but all other document types use subfolders (`docs/handoffs/`, `docs/decisions/`, etc.). Had to manually move files to `docs/feedback/` mid-project.
- **Scores:** Clarity 3, Applicability 4, Completeness 3, Efficiency 2 (Avg: 3.0)
- **Recommendation:** Standardize on `docs/feedback/` subfolder. See `backlogs.md`.

### Entry 5: Section 6.4 (Checkpoint and Feedback Protocol)
- **Date:** 2026-02-01 | **Sprint:** S1 | **Type:** Success
- **Context:** Creating milestone checkpoints at sprint boundaries
- **Finding:** Three-file feedback system worked well; checkpoint template captured all state needed for session continuity.
- **Scores:** Clarity 5, Applicability 5, Completeness 4, Efficiency 5 (Avg: 4.75)
- **Recommendation:** Add sprint boundary checklist to ensure nothing is missed. See `backlogs.md`.

### Entry 6: Section 6.5 (Gateway Reviews)
- **Date:** 2026-02-01 | **Sprint:** S2 | **Type:** Success
- **Context:** Gateway 2 alignment review after Sprint 1
- **Finding:** Caught missing `@` reference in Custom Instructions template; systematic quality gates work.
- **Scores:** Clarity 5, Applicability 5, Completeness 5, Efficiency 5 (Avg: 5.0)
- **Recommendation:** None — first use, format effective.

### Entry 7: Custom Instructions Template — Pre-generation Brief Wording
- **Date:** 2026-02-02 | **Sprint:** S3 | **Type:** Gap (Recurrence)
- **Context:** CLI implementation. Agent provided pre-generation brief, user said "ready" (sprint start), agent generated files without per-file approval.
- **Finding:** Same class of error as Entry 3. Protocol says "explain before generating" but doesn't specify agent must receive **explicit approval**. A simple "ready" in different context was misinterpreted.
- **Scores:** Clarity 2, Applicability 3, Completeness 2, Efficiency 2 (Avg: 2.25)
- **Reasoning:** Recurrence of Entry 3 error proves wording is insufficient.
- **Recommendation:** Strengthen to: "(1) Explain, (2) Wait for explicit approval, (3) Generate." See `backlogs.md`.

### Entry 8: Cross-Project Alignment Document (TRANSFER-4)
- **Date:** 2026-02-03 | **Sprint:** S3 | **Type:** Success
- **Context:** Applied sprint boundary checklist from sql-query-agent alignment document
- **Finding:** Four transfer items (feedback protocol, blog workflow, development protocol, sprint checklist) all applicable and useful. Checklist ensured all documentation completed.
- **Scores:** Clarity 5, Applicability 5, Completeness 5, Efficiency 5 (Avg: 5.0)
- **Recommendation:** Formalize cross-project alignment document as standard DSM artifact. See `backlogs.md`.

### Entry 9: Real-World Validation Run
- **Date:** 2026-02-03 | **Sprint:** S3 | **Type:** Success + Gap
- **Context:** Ran CLI against real DSM repository (122 files)
- **Finding:** Tool validated its purpose: 448 broken refs found. However, `KNOWN_DSM_IDS` was incomplete (5 entries); 152 warnings revealed short forms (DSM 1 vs DSM 1.0) and additional docs (DSM 0.1, 2.1, 3). Expanded to 11 entries → 0 warnings.
- **Scores:** Clarity 4, Applicability 5, Completeness 3, Efficiency 4 (Avg: 4.0)
- **Reasoning:** Design decisions need validation against real data. Initial assumptions were incomplete.
- **Recommendation:** Real-world testing essential before declaring MVP complete.

### Entry 10: docs/ Folder Structure Confusion — Agent Required Multiple Corrections
- **Date:** 2026-02-03 | **Sprint:** S3 | **Type:** Gap (Significant)
- **Context:** Sprint 3 closure required organizing documentation files. Agent needed to understand where feedback files go, where blog files go, what each docs/ subfolder contains, and the expected format of each file type.
- **Finding:** The agent demonstrated significant confusion about the docs/ folder structure despite DSM 4.0 Section 2 documentation. Specific errors requiring user correction:
  1. Attempted to create DSM backlog items directly in DSM repository instead of in project's `docs/feedback/backlogs.md`
  2. Confused about whether `blog.md` belongs in `docs/feedback/` or `docs/blog/`
  3. Did not understand the purpose distinction between `docs/backlog/` (alignment reports) vs `docs/feedback/` (DSM feedback)
  4. Required user to provide sql-agent `docs-folder-reference-sql-agent.md` as explicit reference
  5. Required user to point to sql-agent `docs/feedback/backlogs.md` and `docs/feedback/methodology.md` as format examples
  6. Multiple iterations needed to get file formats correct (rejected first attempts that didn't follow TRANSFER-1 entry format)
- **Scores:** Clarity 1, Applicability 3, Completeness 1, Efficiency 1 (Avg: 1.5)
- **Reasoning:** DSM 4.0 Section 2 lists folder names but does not adequately explain: (a) the **purpose** of each subfolder, (b) what **files** belong in each, (c) the **format** expected for each file type, (d) the **relationship** between folders (e.g., feedback/ is for DSM methodology feedback, backlog/ is for cross-project alignment). The agent needed an external reference project (sql-agent) to understand the structure — this should be self-contained in DSM.
- **Recommendation:** Create a standardized "docs/ Folder Structure Reference" document in DSM 4.0. For each subfolder, specify: (1) Purpose, (2) Files it contains, (3) Format/template for each file, (4) When files are created/updated. Include a complete reference implementation or link to one. See `backlogs.md`.

### Entry 11: Trailing Period Bug — Fixture vs Production Data Mismatch
- **Date:** 2026-02-04 | **Sprint:** Post-S3 | **Type:** Gap
- **Context:** Parser bug discovered during DSM remediation attempt. 448 errors were mostly false positives because parser couldn't find sections with trailing periods in their numbers (DSM uses `### 2.3.7. Title`, fixture used `### 2.3.7 Title`).
- **Finding:** Test fixture was created from assumption, not observation. Never verified fixture format against actual DSM files before writing tests. The same pattern occurred three times: (1) KNOWN_DSM_IDS incomplete, (2) DSM short forms missed, (3) trailing period format missed. All three would have been caught by a single real-data capability experiment in Sprint 1.
- **Scores:** Clarity 3, Applicability 4, Completeness 2, Efficiency 2 (Avg: 2.75)
- **Reasoning:** DSM 4.0 Section 4.4 distinguishes tests from capability experiments but doesn't emphasize validating synthetic fixtures against real data early. TDD works with fixtures, but fixtures encode assumptions. Those assumptions need validation against production data before building an entire test suite on them.
- **Recommendation:** Add to DSM 4.0 Section 3 or 4.4: "Before writing tests against synthetic fixtures, verify the fixture format matches actual production data. Run at least one capability experiment on real data in Sprint 1 to validate assumptions." See `backlogs.md`.

---

## 5. Methodology Observations for DSM

1. **Pre-generation brief is critical** — The "explain before generating" principle needs explicit approval step (violated twice: S1 and S3).
2. **Short sprint cadence works better** — 4 short sprints produced more feedback than one large sprint would have.
3. **Research-first grounding validates approach** — Phase 0.5 research confirmed regex approach fills a real gap.
4. **Cross-project learning compounds** — Patterns from sql-agent (TRANSFER-1 to TRANSFER-4) applied directly here.
5. **Real data validates design decisions** — KNOWN_DSM_IDS seemed complete until real-world run revealed gaps.
6. **Dog-fooding surfaces gaps faster** — Two concurrent projects found the same Validation Tracker/Feedback overlap issue.
7. **docs/ folder structure needs explicit documentation** — AI agents cannot infer folder purposes from names alone. The agent required 6 corrections and external references (sql-agent) to understand where files belong. Folder names are not self-documenting; purpose, contents, format, and relationships must be explicit.
8. **Validate fixtures against real data early** — Synthetic test fixtures encode assumptions. The trailing period bug (448 false positives) would have been caught by opening one real DSM file before writing the fixture. Capability experiments on real data should happen in Sprint 1, not Sprint 3.

---

## 6. Plan vs Reality

| Aspect | Planned | Actual | Delta |
|--------|---------|--------|-------|
| Sprints | 7 (Epoch 2 plan) | 4 complete | On track |
| Parser tests | 80%+ coverage | 98% coverage | Exceeded |
| Validation tests | 80%+ coverage | 99% coverage | Exceeded |
| CLI tests | 80%+ coverage | 98% coverage | Exceeded |
| Config/Filter tests | 80%+ coverage | 95% coverage | Exceeded |
| DSM errors found | Unknown | 448 → 6 → 10 (after severity) | Validated tool purpose |
| Blog posts | 1 per epoch | 2 published (Epoch 1 + WSL) | Ahead |

### Entry 12: Epoch 2 Planning Session — Research-First Approach
- **Date:** 2026-02-04 | **Sprint:** Epoch 2 Planning | **Type:** Success
- **Context:** Starting Epoch 2 with research phase before implementation planning.
- **Finding:** Conducting technical research on all key areas (Click multiple options, Pydantic config, fnmatch exclusions, TF-IDF, NetworkX) before detailed sprint planning produced a comprehensive, grounded plan. The research document serves as a reference during implementation.
- **Scores:** Clarity 5, Applicability 5, Completeness 5, Efficiency 5 (Avg: 5.0)
- **Recommendation:** Research-first planning should be standard for new epochs/phases.

### Entry 13: Backlog Organization — done/ Folder Pattern
- **Date:** 2026-02-04 | **Sprint:** Epoch 2 Planning | **Type:** Success
- **Context:** Organizing backlog items as done vs active.
- **Finding:** Creating a `done/` subfolder within `docs/backlog/` for resolved items keeps the backlog actionable. Active items are immediately visible; completed items are preserved for reference.
- **Scores:** Clarity 5, Applicability 5, Completeness 5, Efficiency 5 (Avg: 5.0)
- **Recommendation:** Add `done/` subfolder pattern to DSM docs folder structure guidance.

### Entry 14: Blog Post Dating — Missing Standard
- **Date:** 2026-02-05 | **Sprint:** Epoch 2 (Pre-Sprint 4) | **Type:** Gap
- **Context:** Writing blog post about WSL migration. Initial draft had informal date format.
- **Finding:** Section 2.5.6-2.5.8 (Blog/Communication Deliverable Process) specifies the overall process but does not include a standard format for blog post metadata. Posts should have consistent fields: Date, Author, Status (Draft/Published), Target Platform.
- **Scores:** Clarity 3, Applicability 4, Completeness 2, Efficiency 3 (Avg: 3.0)
- **Reasoning:** Blog posts are deliverables that persist. Without standard metadata, posts lack context for readers and future reference.
- **Recommendation:** Add blog post metadata template to Section 2.5.6: `**Date:** YYYY-MM-DD`, `**Author:**`, `**Status:** Draft|Review|Published`, `**Platform:** LinkedIn|Blog|etc`. See `backlogs.md`.

### Entry 15: Mermaid Diagrams for Blog Posts — Effective Workflow
- **Date:** 2026-02-05 | **Sprint:** Epoch 2 (Pre-Sprint 4) | **Type:** Success
- **Context:** Creating architecture diagram for Epoch 1 LinkedIn blog post. Needed a visual showing the compiler-inspired pipeline (Parser → Symbol Table → Resolver → Validator).
- **Finding:** Mermaid syntax + mermaid.live provides an efficient diagram workflow for blog posts. The AI assistant generates Mermaid code, user iterates on layout in text, then renders once at mermaid.live for PNG export. Text-based source is version-controllable. Vertical layouts (`flowchart TB`) with horizontal subgraphs work well for LinkedIn's feed format.
- **Scores:** Clarity 5, Applicability 5, Completeness 5, Efficiency 5 (Avg: 5.0)
- **Reasoning:** Mermaid is already supported in GitHub markdown, making source files self-documenting. The workflow (generate → iterate → export) is faster than visual diagramming tools.
- **Recommendation:** Add Mermaid diagram recommendation to Section 2.5.6. See `backlogs.md`.

### Entry 16: Blog File Naming — Date Prefix Convention
- **Date:** 2026-02-06 | **Sprint:** Epoch 2 (Pre-Sprint 4) | **Type:** Gap
- **Context:** Multiple blog posts accumulating in `docs/blog/<epoch>/` folders. Files named generically (`blog-draft.md`, `linkedin-post.md`) don't sort chronologically.
- **Finding:** Section 2.5.6 does not specify a file naming convention for blog posts. Adding a date prefix (`YYYY-MM-DD-title.md`) enables chronological ordering in file listings and makes publication date visible without opening the file.
- **Scores:** Clarity 3, Applicability 5, Completeness 2, Efficiency 4 (Avg: 3.5)
- **Reasoning:** Standard in static site generators (Jekyll, Hugo). Simple to adopt, immediately useful as post count grows.
- **Recommendation:** Add to Section 2.5.6: "Name blog files with date prefix: `YYYY-MM-DD-title.md`". See `backlogs.md`.

### Entry 17: Sprint 4 — Post-Validation Severity Override Pattern
- **Date:** 2026-02-06 | **Sprint:** Sprint 4 | **Type:** Success
- **Context:** Implementing Phase 4.3 (Severity Levels). Needed to wire config-based severity mappings (`DSM_*.md: ERROR`, `plan/*: INFO`) into the validation pipeline without complicating the core validator.
- **Finding:** Post-validation override pattern worked well: the validator assigns base severity (ERROR for broken refs, WARNING for unknown DSM), then `apply_severity_overrides()` remaps using config patterns. This keeps the validator logic clean and the override explicit. TDD with EXP-002 test matrix drove the implementation; all 7 EXP-002 tests passed on first run. The research phase (Entry 12) grounded the fnmatch and Pydantic choices, so implementation was straightforward.
- **Scores:** Clarity 5, Applicability 5, Completeness 4, Efficiency 4 (Avg: 4.5)
- **Reasoning:** Clean separation of concerns. Research-first planning (Entry 12) paid off; no surprises during implementation. 73 new tests brought total to 218. Real-world validation confirmed correct behavior: 10 errors (all Section 2.6), 0 warnings, 0 info.
- **Recommendation:** None; this sprint went smoothly. The research-first approach and phased implementation (4.1→4.2→4.3) kept complexity manageable.

### Entry 18: Blog File Roles — journal.md vs materials.md Overlap
- **Date:** 2026-02-06 | **Sprint:** Sprint 4 (boundary) | **Type:** Gap
- **Context:** Reviewing `docs/blog/<epoch>/` folder contents during sprint boundary checklist. Two files exist per epoch: `journal.md` (capture) and `materials.md` (preparation/scoping). The intended distinction: journal is chronological session notes, materials is a structured blog post blueprint.
- **Finding:** Section 2.5.6 specifies "Materials" and "Journal" as separate deliverables, but their roles overlap in practice. Three issues: (1) journal.md contains "Blog Material" subsections that duplicate materials.md's purpose, (2) materials.md is per-epoch but blog posts are per-topic; when an epoch has multiple posts (e.g., Epoch 2 has WSL migration + Sprint 4-5 productionization), one materials.md is insufficient, (3) neither file name indicates its role clearly to an AI agent encountering the structure for the first time.
- **Scores:** Clarity 2, Applicability 3, Completeness 2, Efficiency 2 (Avg: 2.25)
- **Reasoning:** The two-file pattern adds overhead without clear value separation. In practice, journal entries accumulate "Blog Material" subsections that are the real preparation, while materials.md becomes a one-time pre-draft that isn't maintained. A single file per blog post (with both observations and draft structure) would be simpler.
- **Recommendation:** Clarify in Section 2.5.6 whether journal and materials are distinct deliverables or can be merged. If distinct, specify: (a) journal = session-scoped observations only, no draft content, (b) materials = one per blog post, not per epoch. If merged, use a single `YYYY-MM-DD-title-materials.md` per post with both capture and draft sections. See `backlogs.md`.

### Entry 19: AI Collaboration Loop — File-by-File Approval Rhythm
- **Date:** 2026-02-09 | **Sprint:** Sprint 5 | **Type:** Gap
- **Context:** Sprint 5 implementation (CI + docs). Agent generated 4 files (workflow, config, hook, remediation guide) in sequence without stopping between each for review. Then used AskUserQuestion modal for approval, which darkened the background and blocked the space needed to read the explanation.
- **Finding:** The Pre-Generation Brief Protocol (added after Sprint 1 and reinforced in Sprint 3) says "explain before generating, wait for approval," but does not define the **mechanical loop** for multi-file tasks. Without a prescribed rhythm, the agent defaults to batch generation. Additionally, modal approval dialogs obstruct the IDE content the user needs to review. The approval mechanism must not block the reading space.
- **Scores:** Clarity 2, Applicability 3, Completeness 1, Efficiency 2 (Avg: 2.0)
- **Reasoning:** Third iteration of the same class of problem (Sprint 1: batch test generation, Sprint 3: batch CLI generation, Sprint 5: batch docs generation). The protocol wording improves each time but the behavior recurs because the loop mechanics are not specified step-by-step.
- **Recommendation:** Define a numbered file-by-file loop in DSM 4.0 Section 3: (1) show progress list with current item marked, (2) show description of next file, STOP, (3) wait for short Y/N approval, STOP, (4) if Y, create file and wait for diff review, STOP, (5) show progress list with completed item crossed out and next item marked, (6) repeat from step 2. Approval should use plain text, not modal dialogs. See `backlogs.md` Proposal #15.

### Entry 20: User-Facing Documentation — No Prescribed Location in docs/
- **Date:** 2026-02-10 | **Sprint:** Sprint 5 | **Type:** Gap
- **Context:** Sprint 5 produced a remediation guide (`docs/guides/remediation-guide.md`) and a configuration reference is planned next. Neither artifact fits any existing `docs/` subfolder.
- **Finding:** DSM 4.0 Section 2 defines `docs/` subfolders exclusively for project-management artifacts: `checkpoints/`, `decisions/`, `handoffs/`, `feedback/`, `blog/`, `backlog/`, `plan/`. User-facing documentation (installation guides, configuration references, how-tos) has no prescribed location. During Sprint 5, we created `docs/guides/` ad-hoc to separate user-facing content from PM artifacts. The separation proved immediately useful: the remediation guide is for tool users, not for tracking project progress, and placing it alongside checkpoints or decisions would be confusing.
- **Scores:** Clarity 3, Applicability 4, Completeness 2, Efficiency 4 (Avg: 3.25)
- **Reasoning:** Every existing subfolder has a clear PM purpose. Adding user-facing docs to any of them would blur that purpose. A dedicated `docs/guides/` subfolder maintains the clean separation DSM already establishes for other artifact types.
- **Recommendation:** Add `docs/guides/` as a standard subfolder in DSM 4.0 Section 2 for user-facing documentation. See `backlogs.md`.

### Entry 21: Folder Naming Ambiguity — feedback/ vs backlog/
- **Date:** 2026-02-10 | **Sprint:** Sprint 5 | **Type:** Gap
- **Context:** Reviewing `docs/` folder structure after adding Entry 20. Two subfolders use overlapping terminology: `docs/feedback/` contains `backlogs.md` (DSM improvement proposals) and `methodology.md` (DSM methodology observations), while `docs/backlog/` contains cross-project alignment reports.
- **Finding:** The name `feedback/` does not convey directionality. Its contents are specifically feedback *to DSM* (proposals for improving the methodology), but the folder name reads as generic project feedback. Meanwhile, the word "backlog" appears in both contexts with different meanings: `docs/backlog/` holds alignment reports, `docs/feedback/backlogs.md` holds DSM improvement proposals. A new contributor or AI agent encountering both folders would struggle to determine which is which without opening files.
- **Scores:** Clarity 2, Applicability 4, Completeness 3, Efficiency 3 (Avg: 3.0)
- **Reasoning:** DSM's three-file feedback system (methodology.md, backlogs.md, validation tracker) is specifically for feeding observations back to the methodology itself. Renaming `feedback/` to `feedback-to-dsm/` would make this directionality explicit and eliminate the naming collision with `backlog/`.
- **Recommendation:** Rename `docs/feedback/` to `docs/feedback-to-dsm/` in DSM 4.0 Section 2. See `backlogs.md`.

### Entry 22: Session Wrap-Up Missing Next-Steps Description
- **Date:** 2026-02-10 | **Sprint:** Sprint 5 (boundary) | **Type:** Gap
- **Context:** Starting a new session after Sprint 5 wrap-up. The wrap-up produced a checkpoint document and journal entry but did not include a short description of what comes next according to the epoch plan. The next session had to re-read the epoch plan to orient.
- **Finding:** The Sprint Boundary Checklist (DSM 2.0 Template 8, reinforced in CLAUDE.md) includes checkpoint, feedback, decisions, journal, and README updates, but does not include a "next steps" item. Without it, the wrap-up captures where the project *is* but not where it's *going*. This forces the next session to re-derive context from the plan document, adding orientation overhead that a single paragraph could eliminate.
- **Scores:** Clarity 3, Applicability 4, Completeness 2, Efficiency 3 (Avg: 3.0)
- **Reasoning:** Every other wrap-up artifact is backward-looking (what was done, what was decided, what was observed). A forward-looking summary is the natural complement, connecting the completed sprint to the upcoming one. The information already exists in the epoch plan; the wrap-up just needs to surface it.
- **Recommendation:** Add "Next steps summary" to the Sprint Boundary Checklist: a brief paragraph describing the next sprint's goal and key deliverables, referencing the relevant plan section. See `backlogs.md` Proposal #19.

### Entry 23: Visible Reasoning Blocks Do Not Replace Pre-Generation Briefs
- **Date:** 2026-02-10 | **Sprint:** Post-Sprint 5 | **Type:** Gap (Recurrence)
- **Context:** User asked to send feedback to DSM Central. Agent wrote implementation plan inside a Visible Reasoning block ("I should write an inbox entry to DSM Central"), then immediately started tool calls (Glob, Read) without explaining the plan to the user. User had to reject a tool call and ask why no explanation was given.
- **Finding:** The Visible Reasoning Protocol and the Pre-Generation Brief Protocol serve different purposes. Visible Reasoning shows *decision process* (why this approach over alternatives). Pre-Generation Brief shows *intent to the user* (what will be created, why, and waits for approval). Writing "I should write to the inbox" inside thinking delimiters is reasoning-to-self, not a brief-to-user. The agent treated the thinking block as a substitute for the brief, skipping the explain-wait-approve cycle.
- **Scores:** Clarity 3, Applicability 4, Completeness 2, Efficiency 2 (Avg: 2.75)
- **Reasoning:** Fourth iteration of the brief-skipping pattern (S1, S3, S5, now post-S5). Each recurrence has a different surface cause but the same root: the agent finds a reason to skip the explicit explain-wait-approve step. This time the reasoning block created a false sense of having communicated.
- **Recommendation:** Add clarification to DSM_0.2: "Visible Reasoning blocks supplement but do not replace the Pre-Generation Brief. Thinking blocks show decision reasoning; briefs show intent and require explicit approval before acting."

### Entry 24: Simultaneous Local + Hub Feedback Push
- **Date:** 2026-02-10 | **Sprint:** Post-Sprint 5 | **Type:** Methodology Observation
- **Context:** After logging Entry 23 locally, the question arose of when to push it to DSM Central's inbox. DSM_0.2 says "at session end or sprint boundaries, review docs/feedback/ for ripe entries." User determined this introduces unnecessary delay.
- **Finding:** Waiting for session end to push ripe feedback creates two problems: (1) the entry may be forgotten if the session ends abruptly, (2) it adds a redundant "review for ripeness" step when the entry was already judged ripe at creation time. Pushing to both destinations simultaneously (local feedback file + DSM Central inbox) eliminates both issues. The entry is already structured and actionable at the moment it's written; delaying the push adds no value.
- **Scores:** Clarity 4, Applicability 5, Completeness 4, Efficiency 5 (Avg: 4.5)
- **Reasoning:** The original session-end push was designed for entries that accumulate incrementally and need review before sending. But methodology entries and backlog proposals are written in final form. They're ripe on creation. The simultaneous push pattern respects this.
- **Recommendation:** Update DSM_0.2 Session-End Inbox Push: when a methodology or feedback entry is written in final form (structured, actionable), push to both local feedback file and DSM Central inbox simultaneously. Reserve session-end review for entries that were captured as rough notes during the session.

### Entry 25: Session Transcript Is Append-Only, Never Retroactively Edited
- **Date:** 2026-02-11 | **Sprint:** Sprint 6 | **Type:** Gap
- **Context:** After creating `.claude/session-transcript.md` per the Session Transcript Protocol (DSM_0.2 v1.3.11), the agent attempted to backfill past turns and edit a previously written transcript block to add an output summary that was missed.
- **Finding:** The Session Transcript Protocol says "two appends per turn: thinking before work, output after work" but does not explicitly state that the transcript is append-only. The agent interpreted the two-append rule as allowing retroactive corrections, which defeats the purpose of a real-time reasoning log. Past entries reflect what was known at the time; editing them erases the historical record and misleads the user who monitors the file in real time.
- **Scores:** Clarity 3, Applicability 4, Completeness 2, Efficiency 3 (Avg: 3.0)
- **Reasoning:** The protocol describes *when* to append (before and after acting) but not *what not to do* (edit past entries). Without an explicit append-only rule, an agent that misses an entry will naturally try to fix the gap by editing, which corrupts the log's integrity.
- **Recommendation:** Add to Session Transcript Protocol: "The transcript is append-only. Never modify or backfill past entries. Each entry reflects reasoning at the moment it was written. If a past entry was missed, note the gap in the next entry rather than editing history." See `backlogs.md` Proposal #20.

### Entry 26: Three-File Feedback Protocol Not Documented as Atomic Operation
- **Date:** 2026-02-11 | **Sprint:** Sprint 6 | **Type:** Gap
- **Context:** When sending feedback about the session transcript issue, the agent wrote only to DSM Central's inbox, skipping the local feedback files (`docs/feedback/methodology.md` and `docs/feedback/backlogs.md`). The user caught the omission.
- **Finding:** The three-file feedback system (methodology entry + backlog proposal + DSM Central inbox) is documented across multiple DSM sections but never stated as an atomic operation. The simultaneous push pattern (Entry 24) specifies *when* to push but not *what constitutes a complete push*. An agent can satisfy one destination while forgetting the others.
- **Scores:** Clarity 2, Applicability 5, Completeness 2, Efficiency 3 (Avg: 3.0)
- **Reasoning:** Each feedback destination serves a different purpose: methodology.md captures the observation with scores, backlogs.md captures the actionable proposal, and DSM Central receives the cross-project notification. Skipping any one creates an incomplete record.
- **Recommendation:** Add to DSM_0.2: "Every feedback item must be written to all three destinations as a single operation: (1) `docs/feedback/methodology.md` numbered entry with scores, (2) `docs/feedback/backlogs.md` numbered proposal, (3) DSM Central `docs/inbox/{project}.md` inbox entry. Partial writes are incomplete." See `backlogs.md` Proposal #21.

### Entry 27: Spoke Structure Scaffolding Creates Duplicate Folders
- **Date:** 2026-02-11 | **Sprint:** Sprint 6 | **Type:** Gap
- **Context:** User noticed two similar folders in `docs/`: `plan/` (containing epoch-1-plan.md and epoch-2-plan.md) and `plans/` (containing only `.gitkeep`). Git history shows `plans/` was created by commit `87eff49` ("Add docs/plans/ to align with DSM spoke structure, BACKLOG-083") while `plan/` already existed with actual documents.
- **Finding:** The DSM spoke structure template prescribes `docs/plans/` as a standard subfolder, but this project had already established `docs/plan/` (singular) with real content. The scaffolding task created the template folder without checking for an existing equivalent, leaving a dead duplicate. The singular/plural naming inconsistency (`plan/` vs `plans/`) means an automated or AI-driven scaffolding step cannot detect the collision by exact name match.
- **Scores:** Clarity 3, Applicability 4, Completeness 2, Efficiency 3 (Avg: 3.0)
- **Reasoning:** Spoke structure scaffolding assumes a clean project or consistent naming. When a project already has a folder serving the same purpose under a slightly different name, the template creates a duplicate rather than adopting the existing folder. This is the same class of problem as Entry 21 (naming ambiguity across folders).
- **Recommendation:** Standardize on a single canonical name for each spoke folder in the DSM template (either `plan/` or `plans/`, not both). Add a scaffolding pre-check: before creating a template folder, verify no existing folder serves the same purpose. See `backlogs.md` Proposal #22.

### Entry 28: experiments/ Folder Not in DSM 4.0 Project Structure
- **Date:** 2026-02-11 | **Sprint:** Sprint 6 | **Type:** Gap
- **Context:** Running EXP-003b (real data validation of semantic drift threshold) against the DSM methodology repository. The experiment script lives in `experiments/exp003b_real_data_validation.py`. DSM 4.0 Section 4.4 distinguishes tests from capability experiments conceptually, but DSM 4.0 Section 2 (Project Structure) does not list `experiments/` as a standard subfolder.
- **Finding:** Capability experiments (EXP-xxx) are a first-class DSM concept per Section 4.4, yet they have no prescribed home in the project structure. This project naturally created `experiments/` to hold experiment scripts, but the folder was never formally standardized. New projects following DSM 4.0 would not know to create it.
- **Scores:** Clarity 4, Applicability 4, Completeness 2, Efficiency 3 (Avg: 3.25)
- **Reasoning:** Tests have `tests/`, source code has `src/`, decisions have `docs/decisions/`, but experiments, despite being a distinct artifact type with their own naming convention (EXP-xxx), lack a designated folder. This creates inconsistency in the project structure template.
- **Recommendation:** Add `experiments/` to DSM 4.0 Section 2 (Project Structure Patterns) as a standard subfolder for capability experiment scripts. See `backlogs.md` Proposal #23.

### Entry 29: Concept Approval ≠ Implementation Approval
- **Date:** 2026-02-25 | **Sprint:** Sprint 7 | **Type:** Gap (Recurrence)
- **Context:** Phase 7.0 (EXP-004 performance benchmark). Agent presented a Pre-Generation Brief for `exp004_graph_performance.py`, user approved the concept with "y". Agent then wrote the 270-line script AND executed it against the DSM repository without stopping for code review.
- **Finding:** The Pre-Generation Brief Protocol specifies "explain before generating, wait for approval," but the agent treated conceptual approval of the brief as blanket permission to write and run the code. The protocol requires a second gate: after writing the file, present it for review (diff visible in IDE) and wait for explicit approval before executing. Concept approval validates the *what and why*; implementation approval validates the *how*. Skipping the second gate means the user never reviewed 270 lines of code that imports project modules, builds graph structures, and runs against external data.
- **Scores:** Clarity 2, Applicability 3, Completeness 1, Efficiency 1 (Avg: 1.75)
- **Reasoning:** Fifth recurrence of the brief-skipping pattern (S1: batch test generation, S3: batch CLI generation, S5: batch docs generation, post-S5: reasoning block as substitute, S16: concept approval as blanket permission). Each instance has a different surface cause but the same root: the agent finds a justification to skip the explicit file review step. The pattern persists because the protocol describes a single "approval" gate rather than distinguishing the two gates (concept vs implementation).
- **Recommendation:** Split the Pre-Generation Brief Protocol into three explicit gates: (1) **Concept gate:** explain what, why, and key decisions, wait for approval. (2) **Implementation gate:** write the file, present for review (user reads diff in IDE), wait for approval. (3) **Run gate:** when the file needs to be executed (tests, scripts, benchmarks), explain what will be run and wait for approval before executing. All gates require explicit "y" from the user. See `backlogs.md` Proposal #24.
- **Pushed:** 2026-02-25

---

### Entry 30: Lightweight Session Start Missing Transcript Behavioral Activation
- **Date:** 2026-03-03 | **Sprint:** Sprint 8 | **Type:** Gap (Bug)
- **Context:** Session 20 was started via `/dsm-light-go`. The skill correctly appended a boundary marker to the session transcript (lines 191-201), but no thinking/output entries were appended during the entire work session (7 files created/edited, 47 new tests). The full `/dsm-go` skill has an explicit behavioral activation at step 7 that commands: "From this point forward, follow the Session Transcript Protocol..." `/dsm-light-go` only has a passive note in the Notes section: "Session Transcript Protocol remains active."
- **Finding:** The word "remains active" assumes behavioral context carries over from a prior session. But each `/dsm-light-go` invocation starts a fresh conversation thread with no prior activation to "remain." A note in the Notes section does not trigger as an action step. The result: an entire session of Sprint 8 work (checks.py, lint_reporter.py, test_linter.py, CLI integration, config, README) went unlogged in the transcript.
- **Scores:** Clarity 4, Applicability 4, Completeness 3, Efficiency 2 (Avg: 3.25)
- **Reasoning:** The full `/dsm-go` skill embeds behavioral activation as part of step 7, using imperative language ("From this point forward...") tied to the transcript file creation. `/dsm-light-go` defers this to a note, breaking the activation chain. This is a design oversight, not a recurrence of a prior pattern.
- **Recommendation:** Add an explicit behavioral activation step to `/dsm-light-go` (and `/dsm-light-wrap-up` if applicable), mirroring `/dsm-go` step 7's language. Position it as a numbered step after the report, not a note. See `backlogs.md` Proposal #25.
- **Pushed:** 2026-03-03

### Entry 31: CLAUDE.md Should Include Portfolio Path
- **Date:** 2026-03-03 | **Sprint:** Sprint 8 | **Type:** Gap
- **Context:** During Session 20, the agent needed to notify the portfolio project about Sprint 8 completion. The portfolio path (`~/dsm-data-science-portfolio-working-folder/`) was not in CLAUDE.md or MEMORY.md. Session 19 had also reported "Portfolio unavailable" at startup because it could not resolve the path.
- **Finding:** The DSM ecosystem has three notification targets: DSM Central, portfolio, and local feedback files. The CLAUDE.md Environment section listed the project path and DSM repository path but not the portfolio path. Without it, spoke projects cannot reliably send progress updates to the portfolio, breaking the hub-spoke notification loop.
- **Scores:** Clarity 5, Applicability 5, Completeness 4, Efficiency 4 (Avg: 4.50)
- **Reasoning:** Every DSM spoke project should be able to reach all three notification targets without manual discovery. The portfolio path is as fundamental as the DSM Central path. Adding it to the CLAUDE.md template ensures it is available from the first session.
- **Recommendation:** Add a `Portfolio` entry to the Environment section in the CLAUDE.md project template (DSM_0.2 or DSM 4.0). Format: `- **Portfolio**: ~/path-to-portfolio/`. See `backlogs.md` Proposal #26.
- **Pushed:** 2026-03-03

### Entry 32: Research-Before-Planning Should Be a Standard Protocol Step
- **Date:** 2026-03-09 | **Sprint:** Epoch 3 pre-planning | **Type:** Gap / Pattern
- **Context:** Before Epoch 3 planning, the user requested a formal research phase on Neo4j development practices. This mirrors the Epoch 2 research session (2026-02-04) that grounded all five sprints. In both cases, research-first planning produced grounded, actionable plans with no mid-course design changes. The Epoch 2 retrospective explicitly noted this as a success factor.
- **Finding:** DSM does not prescribe research as a mandatory step before planning at any scale. In practice, the most successful planning outcomes in this project followed a four-step sequence: preliminary plan (idea) -> research -> plan -> action. This pattern held across epochs (Epoch 2 research session grounded Sprints 4-8), sprints (EXP-003 grounded Sprint 6's TF-IDF implementation), and individual features (EXP-004 grounded Sprint 7's NetworkX approach). When research was skipped or implicit, the resulting plans contained assumptions that required mid-course correction.
- **Scores:** Clarity 5, Applicability 5, Completeness 4, Efficiency 5 (Avg: 4.75)
- **Reasoning:** The pattern is scale-invariant: it applies to projects, epochs, sprints, and even individual features with non-trivial technical choices. The agent should proactively suggest a research phase when it detects unresolved technical uncertainty in a planning request, rather than waiting for the user to ask. This is not about adding overhead; a research phase for a simple sprint might be a 10-minute web search, while an epoch-level research phase might be a full session. The depth scales with the uncertainty.
- **Recommendation:** Add a "Research Gate" to the planning protocol at all scales. Before any plan document is drafted, the agent should assess whether there is unresolved technical uncertainty and, if so, suggest a research phase. The workflow becomes: Idea -> Research (if uncertainty exists) -> Plan -> Action. The research output should be a document in `docs/research/` that the plan document references. See `backlogs.md` Proposal #27.
- **Pushed:** 2026-03-09

### Entry 33: Tiered Research Pattern (Broad Landscape -> Focused Deep-Dive)
- **Date:** 2026-03-09 | **Sprint:** Epoch 3 pre-planning | **Type:** Pattern
- **Context:** During Epoch 3 pre-planning, two research phases emerged naturally. First, a broad landscape survey evaluated the graph database ecosystem (Neo4j, FalkorDBLite, Kuzu, Memgraph, DuckPGQ). This produced DEC-006 (FalkorDBLite selected). Second, after the decision was made, significant unknowns remained about FalkorDBLite specifically: Cypher subset coverage, persistence model, multi-graph support, Python API specifics, testing patterns. The user correctly identified that a focused deep-dive was needed before sprint planning could be actionable.
- **Finding:** Research naturally tiers into two levels when the planning scope involves technology selection: (1) broad landscape research to inform the selection decision, and (2) focused deep-dive research on the selected option to inform implementation planning. The broad research answers "which option?" while the deep-dive answers "how does this option work in our context?" Skipping the deep-dive would produce sprint plans based on assumptions about the selected technology's capabilities, repeating the synthetic-vs-real gap pattern observed in EXP-003/003b.
- **Scores:** Clarity 5, Applicability 5, Completeness 5, Efficiency 5 (Avg: 5.00)
- **Reasoning:** This extends Proposal #27 (Research Gate) with a refinement: when the broad research produces a technology selection, the agent should proactively assess whether the selected option has unresolved implementation-level unknowns. If so, suggest a focused deep-dive before proceeding to sprint planning. The workflow becomes: Idea -> Broad Research (landscape) -> Decision -> Deep-Dive Research (selected option) -> Plan -> Action. This is not two mandatory research phases; it is one research gate with optional depth refinement when the first pass reveals implementation uncertainty in the chosen path.
- **Recommendation:** Amend Proposal #27 to include tiered research: after a selection decision, the agent should assess remaining unknowns about the selected option and suggest a focused deep-dive if implementation-level uncertainty exists. See `backlogs.md` Proposal #28.
- **Pushed:** 2026-03-09

### Entry 34: Experiment Documentation Has Four Elements Right But Three Critical Gaps
- **Date:** 2026-03-10 | **Sprint:** Sprint 9, Phase 9.1 | **Type:** Gap / Pattern (research-validated)
- **Context:** During Session 24, the user requested a review of the four-element experiment documentation structure (Justification, Expected Results, Validation, References) used in this project. An online research session validated this structure against six independent frameworks: scientific method, ML tracking tools (MLflow, W&B, Neptune, DVC), Wohlin et al. "Experimentation in Software Engineering," GQM, reproducibility standards (FAIR, NeurIPS checklist, arXiv 2406.14325), and Hypothesis-Driven Development (Cowan, IBM Garage, IEEE 2019). Full research at `docs/research/experiment-documentation-standards.md`.
- **Finding:** The four-element structure is well-grounded: all major frameworks require justification, hypothesis, validation, and references. Its main contribution relative to mainstream ML tooling (MLflow, W&B, Neptune, DVC) is capturing justification and expected results, elements those tools entirely omit. However, three gaps were identified consistently across all six frameworks: (1) no explicit Success Criteria element — every framework distinguishes "what I predict" from "what threshold constitutes pass/fail and how I will measure it"; (2) no Environment/Setup documentation — identified by the 2024 reproducibility survey as the most commonly missing element in ML experiments; (3) Decision/Conclusion is not a named element — HDD and Wohlin both require separating the gate decision from the raw comparison, enabling experiment lists to be audited at a glance. A fourth lower-severity gap: no Learning/Insight capture (what was discovered beyond pass/fail), which HDD and the scientific method both identify as distinct from the comparison step.
- **Scores:** Clarity 5, Applicability 5, Completeness 5, Efficiency 5 (Avg: 5.00)
- **Reasoning:** The gaps are consistent across frameworks with different purposes (academic, industrial, reproducibility, DevOps). This convergence confirms they are genuine structural needs. The Success Criteria gap is highest impact: without explicit pass/fail thresholds documented before running, experiments are vulnerable to post-hoc rationalization. The Environment gap is most common in practice. The Decision gap is most impactful for auditability: a gate experiment without a named Decision element requires reading the full narrative to determine whether the gate passed. A seven-element revised structure is proposed: Justification, Hypothesis, Success Criteria, Environment, Results, Decision, References. As a minimal alternative, the existing four elements are kept but strengthened with mandatory sub-elements: pass/fail threshold in "Expected Results," gate outcome (GO/NO-GO) in "Validation."
- **Recommendation:** Adopt the seven-element structure for EXP-006 onwards. Do not backfill EXP-003/004 (decisions already made; retroactive documentation adds little value relative to effort). See `backlogs.md` Proposal #29 and `docs/research/experiment-documentation-standards.md`.
- **Pushed:** 2026-03-10

### Entry 35: "Challenge Myself to Reason" — Composition Challenge for Multi-Item Artifacts
- **Date:** 2026-03-11 | **Sprint:** Sprint 9, Phase 9.3 | **Type:** Gap / Philosophy
- **Context:** During Session 25, the agent proposed a test file with 6 tests for the `--graph-db` CLI feature. The agent presented the list with a brief per test but did not proactively justify the composition: why 6 tests, not 5 or 8? The user challenged with "why these 6 tests?" and then "why not more or less?" Only after these questions did the agent trace each test back to a checkpoint requirement, reason through what was excluded and why, and confirm the collection was complete. The reasoning was sound, but it happened reactively, not proactively. The Pre-Generation Brief Protocol (CLAUDE.md) asks for What/Why/Key Decisions/Structure, but none of these elements explicitly prompt the agent to challenge the *composition* of items within a multi-item artifact.
- **Finding:** When generating artifacts that contain multiple items (test suites, module files with multiple functions, documents with multiple sections), the current Pre-Generation Brief does not prompt either party to challenge the composition. The agent lists items and describes each, but the *collection as a whole* goes unquestioned unless the human intervenes. This creates an asymmetry: the human must generate their own challenge questions to validate the design, while the agent presents without self-critique. Adapting Sinek's Golden Circle model (Why/What/How) to an operational context, plus adding a "When" dimension for sequencing, produces a structured composition challenge that benefits both parties. The agent uses it to proactively challenge its own reasoning before presenting. The human uses it as a review framework: the structured format (Why/What/How/When) makes it clear what to validate and approve, replacing ad-hoc questioning with systematic review. This is where the collaboration makes both parties think and reason together through the same dimensions.
- **Scores:** Clarity 5, Applicability 5, Completeness 5, Efficiency 5 (Avg: 5.00)
- **Reasoning:** The principle is named "Challenge Myself to Reason" and applies to both the agent and the human collaboratively. On the agent side, it means proactively questioning artifact composition before presenting: tracing each item to a requirement, identifying what was excluded and why, and confirming the collection is complete. On the human side, the structured format (Why/What/How/When) provides a clear framework for review, replacing the need to invent challenge questions from scratch. The operational value aligns with established process design principles: Why establishes purpose and alignment (prevents wasted effort on misaligned items), What defines scope as an index (enables quick review of completeness), How details execution and key decisions (supports standardization and error-proofing), and When validates sequencing (catches ordering errors). This is triggered only for multi-item artifacts; single-item artifacts (a config file, a `.gitkeep`) need only the existing single-sentence brief.
- **Recommendation:** Amend the Pre-Generation Brief Protocol to include a "Composition Challenge" step for multi-item artifacts. When the artifact contains multiple items, the brief should include: (1) **Why** — purpose and alignment: why this collection exists, what requirement or goal it serves; (2) **What** — index of items at a high level without explanations: an enumeration of all items the artifact will contain; (3) **Why not more or less** — composition justification: trace each item to a requirement, identify excluded candidates and the reason for exclusion, confirm completeness; (4) **How** — key decisions and structure: design choices, organization, execution approach; (5) **When** — sequencing: is this the right next step in the sequence of actions? This enhances the existing What/Why/Key Decisions/Structure format rather than replacing it. See `backlogs.md` Proposal #30.
- **Pushed:** 2026-03-11

### Entry 36: Edit Explanation Stop Protocol — Explain, Stop, Approve, Execute
- **Date:** 2026-03-11 | **Sprint:** Sprint 9, Phase 9.3 | **Type:** Gap / Collaboration Protocol
- **Context:** During Session 25, the agent explained an upcoming multi-part edit to `cli.py` (Edit 3b of 3) and then immediately executed the edit in the same turn. The user had no opportunity to ask questions about the explanation before the code was modified. The agent bundled "here is what I will do" and "here is the diff" in a single response, collapsing the explain-wait-approve cycle into a single step. This extends Entry 29 (Three-Gate Model: Concept → Implementation → Run) to a finer granularity: within the implementation gate, each individual edit should also follow an explain-stop-approve-execute cycle.
- **Finding:** The file-by-file collaboration protocol (Entry 19, Proposal #15) and the Three-Gate Model (Entry 29, Proposal #24) address artifact-level and phase-level approval gates. Neither addresses the intra-file edit level. When an implementation involves multiple edits to the same file, the agent explains all edits and then executes them in sequence, giving the human a single combined approval point at best. This is especially problematic for large or conceptually distinct edits: the human sees the explanation of edit 3 while still processing edit 1, and the diff is already applied before questions can be raised. The correct flow is: (1) Agent explains the edit in plain words → **STOP**, (2) Human reads, understands, asks questions, approves → continue, (3) Agent executes the edit → human reviews the diff. This creates a shared understanding at each step and prevents wasted effort from executing edits that the human would have modified after reading the explanation.
- **Scores:** Clarity 5, Applicability 5, Completeness 4, Efficiency 4 (Avg: 4.50)
- **Reasoning:** This is a natural extension of the Three-Gate Model (Entry 29) to the edit level. The Three-Gate Model distinguishes concept approval from implementation approval from run approval. This entry adds that *within* the implementation gate, each distinct edit should have its own explain-stop-approve cycle. The cost is minimal (one extra turn per edit), and the value is high: the human can redirect the implementation before code is modified rather than after. This also supports the "Challenge Myself to Reason" principle (Entry 35): the explanation pause gives both parties a moment to reason about whether the edit is correct before it becomes a diff to review.
- **Recommendation:** Amend the collaboration protocol to include an Edit Explanation Stop Protocol: when implementing changes that involve multiple distinct edits (to the same or different files), explain each edit in plain words and stop for approval before executing. The explanation should include: what the edit does (in plain language, not just "Added N lines"), where it goes (file and approximate location), and why (how it connects to the current task). Trivial edits (fixing a typo, adding an import) may be grouped. See `backlogs.md` Proposal #31.
- **Pushed:** 2026-03-11

### Entry 37: Sprint Boundary Gate Missing from /dsm-go Session Start
- **Date:** 2026-03-12 | **Sprint:** Sprint 10 (boundary) | **Type:** Gap / Process
- **Context:** Session 28 started with `/dsm-go`. The agent loaded MEMORY.md ("Sprint 10 complete"), found no pending checkpoints, and suggested starting Sprint 11. The user asked "did we do the sprint boundary?" The agent checked and confirmed that no Sprint 10 boundary artifacts existed: no checkpoint, no journal entry, no feedback update, no README update. The agent had suggested starting a new sprint without verifying that the prior sprint was properly closed.
- **Finding:** `/dsm-go` Step 9 (Report) suggests next work items from MEMORY.md and checkpoints, but no step verifies whether the previous sprint's boundary checklist was completed. The word "complete" in MEMORY.md means code-complete (all phases done, tests passing, code committed), not boundary-complete (checkpoint, feedback, journal, README all updated). The agent conflated the two meanings. Step 3.5 (Checkpoint check) reads checkpoints for context and moves them to `done/`, but this is a context-loading step, not a verification gate. There is no step that asks: "Do boundary artifacts exist for the most recent sprint?" Without this gate, the agent will always skip straight to suggesting new work, leaving the boundary checklist to the user's memory.
- **Scores:** Clarity 5, Applicability 5, Completeness 4, Efficiency 5 (Avg: 4.75)
- **Reasoning:** The sprint boundary checklist (DSM 2.0 Template 8) is a quality gate, not optional documentation. It captures the sprint's outcomes, feeds the feedback loop, and updates the project's public-facing state. Skipping it means: (1) no checkpoint for future session context, (2) no journal entry for blog material, (3) no feedback review for methodology improvement, (4) README shows stale metrics and status. The fix is structural: add a verification step to `/dsm-go` that checks for boundary artifacts matching the latest sprint in MEMORY.md, and flag missing artifacts as a blocker before suggesting new work.
- **Recommendation:** Add a "Sprint Boundary Gate" step to `/dsm-go` between Step 3.5 (Checkpoint check) and Step 4 (Bandwidth). The gate reads the latest sprint number from MEMORY.md, then verifies boundary artifacts exist: (1) checkpoint in `docs/checkpoints/done/` matching the sprint, (2) journal entry in the current epoch's blog journal, (3) README status updated for the sprint. If any are missing, report them as blockers and suggest completing the boundary before new work. See `backlogs.md` Proposal #32.
- **Pushed:** 2026-03-12

### Entry 38: Epoch Plan Not Updated at Sprint Boundaries
- **Date:** 2026-03-12 | **Sprint:** Sprint 11 (start) | **Type:** Gap / Process
- **Context:** Session 29 began Sprint 11 planning. The user noticed that `epoch-3-plan.md` still shows all Sprint 9 and Sprint 10 tasks as unchecked (`[ ]`), despite both sprints being fully complete (402 tests, all phases delivered, boundary checklists done). The plan document was created at the start of Epoch 3 (Session 24) and never updated since.
- **Finding:** The Sprint Boundary Checklist in CLAUDE.md lists 5 items: checkpoint, feedback, decisions, journal, README. "Update epoch plan with completed tasks" is not one of them. Since the checklist is what drives sprint wrap-up behavior (the agent follows it literally), the plan document is systematically skipped at every sprint boundary. This is the same structural pattern as Entry 37 (missing sprint boundary gate) and Entry 20 (missing "next steps"): if a process step is not in the checklist, it does not happen. The epoch plan is the project's roadmap; when it shows all tasks as pending despite half the epoch being complete, it loses its value as a planning instrument and confuses anyone reading the repository.
- **Scores:** Clarity 5, Applicability 5, Completeness 4, Efficiency 4 (Avg: 4.50)
- **Reasoning:** The epoch plan serves two audiences: (1) the agent, which reads it at epoch/sprint boundaries for scope, and (2) the user, who reads it in the IDE to track progress. When the plan never gets updated, the user has to cross-reference MEMORY.md, checkpoints, and git history to reconstruct what's actually done. The fix is simple: add "Epoch plan updated" to the Sprint Boundary Checklist. The cost is one `sed` or edit per sprint. The value is a single source of truth for epoch progress.
- **Recommendation:** Add "Epoch plan updated (completed tasks checked off)" to the Sprint Boundary Checklist in CLAUDE.md and in DSM 2.0 Template 8. See `backlogs.md` Proposal #33.
- **Pushed:** 2026-03-12

### Entry 39: Alignment Review Missing at Sprint Transitions
- **Date:** 2026-03-12 | **Sprint:** Sprint 11 (start) | **Type:** Gap / Collaboration
- **Context:** After updating epoch-3-plan.md with Sprint 9+10 completions (Entry 38 fix), the user requested: "confirm we are aligned and highlight any changes. This should be part of the protocol between sprints." The user wants a collaborative review step, not just a mechanical checkbox update. The agent had been updating the plan silently; the user needs to see the changes, confirm accuracy, and verify scope for the next sprint before proceeding.
- **Finding:** The Sprint Boundary Checklist (even with Proposal #33's "update epoch plan" addition) treats the plan as a documentation artifact: update it and move on. But the plan is also a *collaboration artifact*: it reflects shared understanding of scope, progress, and priorities. Updating it without review means the user has to independently verify every checkbox, cross-reference with actual commits, and catch any drift between plan and reality. This is the planning equivalent of committing without code review. The gap is: there is no "alignment review" step where the agent presents the updated plan, highlights what changed (completions, deviations from plan, scope additions), and gets explicit confirmation before starting the next sprint.
- **Scores:** Clarity 5, Applicability 5, Completeness 4, Efficiency 4 (Avg: 4.50)
- **Reasoning:** Sprint transitions are natural alignment checkpoints. The agent has all the context (what was planned vs what was delivered, what deviated, what was added). Presenting a summary takes 30 seconds. Catching a misalignment before starting the next sprint saves an entire session of misdirected work. The cost-benefit is strongly in favor of the review step.
- **Recommendation:** Add an "Alignment Review" step to the sprint transition protocol, after the plan update and before starting new sprint work. The agent presents: (1) what was completed, (2) deviations from the original plan, (3) scope additions not in the plan, (4) current state of epoch progress, (5) next sprint scope for confirmation. User confirms before proceeding. See `backlogs.md` Proposal #34.
- **Pushed:** 2026-03-12

### Entry 40: Sprint Boundary Checklist Missing Hub/Portfolio Notification
- **Date:** 2026-03-12 | **Sprint:** Sprint 11 (boundary) | **Type:** Gap / Process
- **Context:** During Session 30, while running the Sprint 11 boundary checklist, the user asked: "when do we inform central DSM and ds-portfolio about the sprint's boundary checklist completion?" The checklist had 6 items (checkpoint, feedback, decisions, journal, README, epoch plan), all project-local. No item triggers a notification to hub projects (DSM Central) or the portfolio. Individual feedback entries are pushed atomically as they are created during the sprint, but these are methodology observations, not sprint completion signals. The hub and portfolio have `_inbox/` folders specifically designed for cross-repo notifications, yet no checklist item uses them for sprint status.
- **Finding:** The Sprint Boundary Checklist treats sprint completion as a project-internal event. Hub projects (DSM Central, portfolio) only learn about spoke sprint completions through two indirect channels: (1) feedback entries pushed during the sprint (methodology observations, not status), and (2) manual inspection of the spoke's README. Neither channel provides a structured "Sprint N complete" signal. This means the portfolio's project status page and DSM Central's ecosystem awareness are always stale unless manually updated. The `_inbox/` mechanism was designed precisely for this kind of cross-repo notification, but the boundary checklist does not invoke it.
- **Scores:** Clarity 5, Applicability 5, Completeness 4, Efficiency 4 (Avg: 4.50)
- **Reasoning:** The DSM ecosystem has three notification targets (DSM Central, portfolio, local feedback). The boundary checklist updates local feedback but does not notify the other two targets about the sprint's completion. This is the same structural pattern as Entries 37-38: if a step is not in the checklist, it does not happen. The cost is one brief notification file per target per sprint. The value is that hub projects can track spoke progress without polling.
- **Recommendation:** Add a 7th item to the Sprint Boundary Checklist: "Hub/portfolio notified of sprint completion (`_inbox/` in DSM Central and portfolio)." The notification should be a brief structured file (project name, sprint number, key deliverables, test count) dropped into each target's `_inbox/`. See `backlogs.md` Proposal #35.
- **Pushed:** 2026-03-12

---

**Last Updated:** 2026-03-12
**Entries So Far:** 40
**Average Score:** 3.75
**Pushed:** 2026-03-12 (Entry 40 pushed simultaneously with creation)
