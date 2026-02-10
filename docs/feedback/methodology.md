# DSM Feedback: Project Methodology

**Project:** DSM Graph Explorer
**Author:** Alberto Diaz Durana
**DSM Version Used:** DSM 4.0 v1.0, DSM 1.0 v1.1
**Date:** 2026-01-31 (started)
**Duration:** Sprint 1-4 complete

---

## 1. Project Overview

| Item | Planned | Actual |
|------|---------|--------|
| **Objective** | Repository integrity validator for DSM cross-references | Complete — CLI tool validates 125 files with config-based severity |
| **Language** | Python 3.12+ | Active — pytest, Click, Rich, Pydantic, PyYAML |
| **Timeline** | 7 sprints (Parser → Validation → CLI → Config → CI → Semantic → Graph) | Sprint 4 complete |
| **Deliverables** | CLI tool + integrity reports + blog | CLI with exclusions, config, severity levels |

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

---

**Last Updated:** 2026-02-10
**Entries So Far:** 21
**Average Score:** 3.67
