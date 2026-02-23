# DSM Graph Explorer - Epoch 1 Plan

**Project Type:** Software Engineering (DSM 4.0 Track)
**Start Date:** 2026-01-30
**End Date:** 2026-02-03
**Status:** COMPLETE
**Project Lead:** Alberto Diaz Durana (with AI assistance)

---

## Project Overview

### Purpose

Build a repository integrity validator and graph database explorer for the DSM methodology framework, applying DSM 4.0 software engineering methodology to build tooling (dog-fooding).

### Scope

**MUST (MVP):**
- Python parser to extract cross-references from DSM markdown files
- Cross-reference validator (Section X.Y.Z, Appendix X.Y, DSM_X)
- Version consistency checker (DSM_0, README, CHANGELOG)
- Integrity report generator (markdown format)
- Test suite (TDD approach with pytest)
- CLI interface for running validation
- Basic README with setup instructions

**SHOULD (Enhancements):**
- Pre-commit hook integration
- CI/CD workflow (GitHub Actions)
- Backlog status validation (done/ items have Status: Implemented)
- DSM_0 alignment checker (sections match descriptions)
- Semantic cross-reference validation: TF-IDF keyword similarity between reference context and target section title (lightweight, scikit-learn). Detects meaning drift when sections are rewritten but keep their numbers.

**COULD (Future project):**
- Neo4j graph database with DSM structure (prototype with NetworkX first)
- Cypher query library for navigation
- Web visualization (Neo4j Browser)
- Relationship mapping (REFERENCES, CONTAINS, PARENT_OF)
- spaCy NER for advanced reference extraction
- Sentence transformer embeddings for deep semantic cross-reference alignment (upgrade from TF-IDF). Reference: [tfidf-to-transformers-with-disaster-tweets](https://github.com/albertodiazdurana/tfidf-to-transformers-with-disaster-tweets) — prior work demonstrating TF-IDF → embeddings → transformers progression for context-sensitive text classification

### Success Criteria

**Technical:**
- [ ] Parser successfully extracts all cross-references from DSM files
- [ ] Validator detects broken cross-references (if any exist)
- [ ] Version numbers match across DSM_0, README, CHANGELOG
- [ ] All tests pass (target: 80%+ coverage for MVP)
- [ ] CLI runs successfully on DSM repository
- [ ] Integrity report is readable and actionable

**Process:**
- [ ] TDD approach followed (tests before implementation)
- [ ] Blog journal updated at each sprint completion
- [ ] DSM feedback files updated at each sprint boundary
- [ ] Checkpoint created at each sprint completion

**Deliverable:**
- [ ] Working integrity validator tool
- [ ] Example integrity report for DSM repository
- [ ] README with installation and usage instructions
- [ ] Blog draft with project results

---

## Sprint Structure

Each sprint is a self-contained deliverable. Every sprint boundary produces:
1. **DSM feedback update** — methodology observations from that sprint
2. **Blog journal entry** — material for the blog narrative
3. **Checkpoint document** — state capture for handoff continuity

### Phase 0: Environment Setup [COMPLETE]

**Date completed:** 2026-01-31

**Deliverables:**
- [x] Repository created: `D:\data-science\dsm-graph-explorer\`
- [x] Git initialized with `.gitignore`
- [x] Virtual environment created (Python 3.12+)
- [x] `pyproject.toml` with dependencies (pytest, etc.)
- [x] Project structure created (src/, tests/, docs/, outputs/)
- [x] `.claude/CLAUDE.md` pointing to central DSM
- [x] Blog materials moved to `docs/blog/materials.md`
- [x] Initial README stub

### Phase 0.5: Research & Grounding [COMPLETE]

**Date completed:** 2026-02-01

**Purpose:** Validate the technical approach against published best practices before implementation.

**Deliverables:**
- [x] Research document: `docs/research/handoff_graph_explorer_research.md`
- [x] Gap analysis: confirmed no existing tool handles prose cross-references
- [x] Approach validation: regex for structured patterns aligns with code static analysis pipeline
- [x] Future direction identified: NetworkX before Neo4j, spaCy NER as upgrade path

**Key finding:** The approach follows the well-established parsing → symbol resolution → dependency analysis → validation pipeline from code static analysis, applied to documentation. The gap (prose reference validation) is real and unserved by existing markdown tools.

### Sprint 1: Parser MVP [COMPLETE]

**Date completed:** 2026-02-01

**Objective:** Build a markdown parser to extract sections and cross-references from DSM documentation.

**Deliverables:**
- [x] `src/parser/markdown_parser.py` — Read markdown files, extract sections with hierarchical numbering
- [x] `src/parser/cross_ref_extractor.py` — Extract cross-reference patterns (Section, Appendix, DSM)
- [x] `tests/fixtures/sample_dsm.md` — Test fixture with DSM patterns and edge cases
- [x] `tests/test_parser.py` — Unit tests for both parser modules (TDD)
- [x] `docs/decisions/DEC-001_parser_library_choice.md` — Decision document

**Decisions made:**
- Parser library: **Pure regex** (simple, no dependencies, handles structured patterns well)
- Line numbers: **Yes**, tracked for precise error reporting
- Code blocks: **Skipped** using fenced code block state tracking (toggle on ``` lines)

**Sprint boundary deliverables:**
- [x] DSM feedback update
- [x] Blog journal entry
- [x] Checkpoint document

### Sprint 2: Validation Engine [COMPLETE]

**Date completed:** 2026-02-01

**Objective:** Implement validation logic and integrity report generation.

**Deliverables:**
- [x] `src/validator/cross_ref_validator.py` — Validate references exist as actual sections
- [x] `src/validator/version_validator.py` — Check version consistency across DSM_0, README, CHANGELOG
- [x] `src/reporter/report_generator.py` — Generate markdown integrity reports + Rich console output
- [x] `tests/test_validator.py` — 51 unit tests for validators
- [x] `tests/test_reporter.py` — 23 tests for reporter (including 4 integration tests)

**Decisions made:**
- Validation strictness: **Severity levels** (ERROR for broken refs, WARNING for unknown DSM docs)
- Report format: **Both** markdown files and Rich console output
- DSM references: **Known identifier list** (`KNOWN_DSM_IDS`)
- Cross-file API: **`build_section_index()`** aggregates across multiple `ParsedDocument` objects

**Sprint boundary deliverables:**
- [x] DSM feedback update
- [x] Blog journal entry
- [x] Checkpoint document

### Sprint 3: CLI & Real-World Run [COMPLETE]

**Date completed:** 2026-02-03

**Objective:** Build CLI interface, run validator against the real DSM repository, evaluate results.

**Deliverables:**
- [x] `src/cli.py` — Command-line interface (Click)
- [x] Integration tests — Full validator run on fixture data
- [x] First real DSM integrity report in `outputs/reports/`
- [x] Metrics captured: 122 files, 1,847 refs, 448 errors, 0 warnings

**Decisions made:**
- CLI design: DEC-002 documented
- Error remediation: DEC-003 documented

**Sprint boundary deliverables:**
- [x] DSM feedback update
- [x] Blog journal entry (with real metrics and findings)
- [x] Checkpoint document

### Sprint 4: Documentation & Publication

**Objective:** Complete documentation, optional CI/CD, draft blog post.

**Deliverables:**
- [ ] README finalized with installation, usage, examples
- [ ] `pyproject.toml` finalized
- [ ] `.github/workflows/dsm-validate.yml` — CI/CD workflow (SHOULD item, if time allows)
- [ ] Blog draft from materials + journal entries
- [ ] Final DSM feedback synthesis
- [ ] Final checkpoint document

---

## Technical Stack

### Core Dependencies

```toml
[project]
name = "dsm-graph-explorer"
version = "0.1.0"
description = "Repository integrity validator and graph explorer for DSM methodology"
requires-python = ">=3.12"

dependencies = [
    "click>=8.1.0",      # CLI framework
    "rich>=13.7.0",      # Terminal formatting
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
```

### Future Dependencies (COULD scope)

- NetworkX (graph analysis prototype)
- Neo4j Community Edition (graph database)
- py2neo or neo4j-driver (Python interface)
- spaCy (NER-based reference extraction)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Regex pattern complexity** | Medium | Medium | Start with simple patterns, iterate; upgrade to spaCy if needed |
| **DSM-specific edge cases** | High | Low | Test against actual DSM files early; handle gracefully |
| **Performance on large files** | Low | Medium | Profile if issues arise; optimize only if needed |
| **Scope creep (COULD features)** | Medium | Medium | Strict MUST/SHOULD/COULD discipline; defer explicitly |
| **Blog completion time** | Medium | Low | Materials prepared; draft incrementally via sprint journal entries |

---

## Blog Integration Plan

Following Section 2.5.6 (Blog/Communication Deliverable Process):

### Step 1: Preparation [COMPLETE]
- Materials document created with title options, hook, story arc
- Technical details prepared
- Figures to capture identified

### Step 2: Scoping [COMPLETE]
- Platform: LinkedIn Article + GitHub README
- Audience: Technical writers, documentation engineers
- Tone: Narrative + tutorial
- Length: 2,500-3,000 words

### Step 3: Capture (During each sprint)
- Update `docs/blog/journal.md` at each sprint boundary
- Capture metrics at each sprint completion
- Screenshot key findings (integrity reports, terminal output)
- Document "aha moments" and design decisions

### Step 4: Drafting (Sprint 4)
- Generate first draft from materials + journal
- Include actual metrics and code examples

### Step 5: Review (Post Sprint 4)
- Citation completeness check
- Jargon accessibility review
- Decision justification verification

### Step 6: Publication
- Format for LinkedIn Article
- Create short post (150-300 words) for engagement
- Publish article, then link via comment

---

## DSM Feedback Plan

Following Section 6.4.5 (Project Feedback Deliverables):

### Three-File System

1. **`docs/feedback/backlogs.md`** — DSM gaps and improvement opportunities
2. **`docs/feedback/methodology.md`** — DSM section effectiveness scoring (1-5)
3. **`docs/feedback/blog.md`** — Blog process effectiveness

**Updated at every sprint boundary**, not just at project end.

---

## Project Structure

Following DSM 4.0 Section 2.2 (Project Structure Patterns):

```
dsm-graph-explorer/
├── .claude/
│   └── CLAUDE.md              # Points to central DSM
├── src/
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── markdown_parser.py
│   │   └── cross_ref_extractor.py
│   ├── validator/
│   │   ├── __init__.py
│   │   ├── cross_ref_validator.py
│   │   └── version_validator.py
│   ├── reporter/
│   │   ├── __init__.py
│   │   └── report_generator.py
│   └── cli.py
├── tests/
│   ├── test_parser.py
│   ├── test_validator.py
│   ├── test_reporter.py
│   └── fixtures/
│       └── sample_dsm.md
├── docs/
│   ├── plan/
│   │   └── SPRINT_PLAN.md     # This file
│   ├── research/
│   │   └── handoff_graph_explorer_research.md
│   ├── handoffs/
│   ├── decisions/
│   ├── checkpoints/
│   ├── blog/
│   │   ├── materials.md
│   │   └── journal.md
│   └── feedback/
│       ├── backlogs.md
│       ├── methodology.md
│       └── blog.md
├── outputs/
│   └── reports/
│       └── dsm-integrity-report.md
├── .gitignore
├── README.md
├── pyproject.toml
└── .github/
    └── workflows/
        └── dsm-validate.yml   # SHOULD item
```

---

## Resolved Questions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Parser library? | Pure regex | Simple, no dependencies, handles structured DSM patterns. Upgrade to spaCy if edge cases demand it. |
| CLI framework? | Click | Already in dependencies, well-documented, standard choice. |
| Line numbers? | Yes | Enables precise error reporting ("Broken ref at line 842"). |
| Skip code blocks? | Yes | Toggle state on fenced ``` lines to avoid false positives. |
| Testing approach? | Unit tests + integration tests | Unit tests per sprint, integration tests in Sprint 3. |
| Report format? | Markdown (primary) | Console output via Rich for CLI; markdown for saved reports. |
| Validation strictness? | Severity levels | ERROR for broken refs, WARNING for unknown DSM docs. |
| DSM document refs? | Known identifier list | `KNOWN_DSM_IDS` list; unknown IDs produce warnings. |
| Cross-file API? | Section index aggregation | `build_section_index()` merges multiple ParsedDocument objects. |

---

**Plan Status:** Epoch 1 Complete (Sprints 1-3)
**Last Updated:** 2026-02-04
**Next:** See [epoch-2-plan.md](epoch-2-plan.md) for future work
