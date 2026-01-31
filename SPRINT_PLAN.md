# DSM Graph Explorer - Sprint 1 Project Plan

**Project Type:** Software Engineering (DSM 4.0 Track)
**Sprint Duration:** Phase 1 MVP (5-7 days estimated)
**Start Date:** 2026-01-30
**Project Lead:** Alberto Diaz Durana (with AI assistance)

---

## Project Overview

### Purpose
Build a repository integrity validator and graph database explorer for the DSM methodology framework, applying DSM 4.0 software engineering methodology to build tooling (dog-fooding).

### Scope

**MUST (Phase 1 MVP - Sprint 1):**
- Python parser to extract cross-references from DSM markdown files
- Cross-reference validator (Section X.Y.Z, Appendix X.Y, DSM_X)
- Version consistency checker (DSM_0, README, CHANGELOG)
- Integrity report generator (markdown format)
- Test suite (TDD approach with pytest)
- CLI interface for running validation
- Basic README with setup instructions

**SHOULD (Phase 1 enhancements):**
- Pre-commit hook integration
- CI/CD workflow (GitHub Actions)
- Backlog status validation (done/ items have Status: Implemented)
- DSM_0 alignment checker (sections match descriptions)

**COULD (Phase 2 - Future Sprint):**
- Neo4j graph database with DSM structure
- Cypher query library for navigation
- Web visualization (Neo4j Browser)
- Relationship mapping (REFERENCES, CONTAINS, PARENT_OF)

### Success Criteria

**Technical:**
- [ ] Parser successfully extracts all cross-references from DSM files
- [ ] Validator detects broken cross-references (if any exist)
- [ ]Version numbers match across DSM_0, README, CHANGELOG
- [ ] All tests pass (target: 80%+ coverage for MVP)
- [ ] CLI runs successfully on DSM repository
- [ ] Integrity report is readable and actionable

**Process:**
- [ ] TDD approach followed (tests before implementation)
- [ ] Blog journal updated at each phase completion
- [ ] DSM feedback files created (backlogs, methodology, blog)
- [ ] Checkpoint created at Phase 1 completion

**Deliverable:**
- [ ] Working integrity validator tool
- [ ] Example integrity report for DSM repository
- [ ] README with installation and usage instructions
- [ ] Blog draft with Phase 1 results

---

## Sprint Structure (DSM 4.0 Adapted Phases)

### Phase 0: Environment Setup (Day 1 - 4 hours)

**Objectives:**
- Initialize project repository
- Set up Python development environment
- Create project structure following DSM 4.0 pattern

**Deliverables:**
- [ ] Repository created: `D:\data-science\dsm-graph-explorer\`
- [ ] Git initialized with `.gitignore`
- [ ] Virtual environment created (Python 3.12+)
- [ ] `pyproject.toml` with dependencies (pytest, etc.)
- [ ] Project structure created (src/, tests/, docs/, outputs/)
- [ ] `.claude/CLAUDE.md` pointing to central DSM
- [ ] Blog materials moved to `docs/blog/materials.md`
- [ ] Initial README stub

### Phase 1: Data Pipeline (Day 1-2 - 8 hours)

**Objectives:**
- Build markdown parser to extract sections and cross-references
- Handle DSM-specific patterns (hierarchical numbering, appendices)

**Deliverables:**
- [ ] `src/parser/markdown_parser.py` - Read markdown files, extract sections
- [ ] `src/parser/cross_ref_extractor.py` - Extract cross-reference patterns
- [ ] Test fixtures - Sample markdown for testing
- [ ] `tests/test_parser.py` - Unit tests for parser
- [ ] Blog journal: Document parser design decisions

**Key Decisions:**
- Parser library choice (regex vs markdown library like `mistune`)
- Section number extraction pattern
- Handling of hierarchical sections (2.1, 2.1.1, etc.)

### Phase 2: Core Modules (Day 3-4 - 10 hours)

**Objectives:**
- Implement validation logic
- Build integrity report generator

**Deliverables:**
- [ ] `src/validator/cross_ref_validator.py` - Validate references exist
- [ ] `src/validator/version_validator.py` - Check version consistency
- [ ] `src/reporter/report_generator.py` - Generate markdown reports
- [ ] `tests/test_validator.py` - Unit tests for validators
- [ ] `tests/test_reporter.py` - Unit tests for reporter
- [ ] Blog journal: Document validation approach

**Key Decisions:**
- Validation strictness (warning vs error)
- Report format (console vs markdown vs both)
- Error message clarity

### Phase 3: Integration & Evaluation (Day 5 - 6 hours)

**Objectives:**
- Build CLI interface
- Run validator against DSM repository
- Evaluate results

**Deliverables:**
- [ ] `src/cli.py` - Command-line interface
- [ ] Integration tests - Full validator run
- [ ] Example integrity report from DSM repository
- [ ] Blog journal: Document findings and metrics

**Key Metrics to Capture:**
- Number of cross-references found
- Number of broken references (if any)
- Number of version consistency issues (if any)
- Execution time
- Files analyzed

### Phase 4: Application & Documentation (Day 6-7 - 8 hours)

**Objectives:**
- Complete documentation
- Set up CI/CD (SHOULD item)
- Draft blog post

**Deliverables:**
- [ ] README with installation, usage, examples
- [ ] `pyproject.toml` finalized with all dependencies
- [ ] `.github/workflows/dsm-validate.yml` - CI/CD workflow (if time allows)
- [ ] Blog draft from materials + journal
- [ ] DSM feedback files created
- [ ] Checkpoint document

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

### Phase 2 Future Dependencies
- Neo4j Community Edition (graph database)
- py2neo or neo4j-driver (Python interface)

---

## Timeline Estimate

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 0: Environment Setup | 4 hours | Day 1 |
| Phase 1: Data Pipeline | 8 hours | Day 1-2 |
| Phase 2: Core Modules | 10 hours | Day 3-4 |
| Phase 3: Integration | 6 hours | Day 5 |
| Phase 4: Documentation | 8 hours | Day 6-7 |
| **Total** | **36 hours** | **5-7 days** |

**Buffer:** 20% for unexpected issues, refactoring

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Regex pattern complexity** | Medium | Medium | Start with simple patterns, iterate; use tested markdown library if needed |
| **DSM-specific edge cases** | High | Low | Test against actual DSM files early; handle gracefully |
| **Performance on large files** | Low | Medium | Profile if issues arise; optimize only if needed |
| **Scope creep (Phase 2 features)** | Medium | Medium | Strict MUST/SHOULD/COULD discipline; defer Phase 2 explicitly |
| **Blog completion time** | Medium | Low | Materials prepared; draft incrementally during implementation |

---

## Blog Integration Plan

Following Section 2.5.6 (Blog/Communication Deliverable Process):

### Step 1: Preparation (Complete)
- ✓ Materials document created with title options, hook, story arc
- ✓ Technical details prepared
- ✓ Figures to capture identified

### Step 2: Scoping (Complete)
- ✓ Platform: LinkedIn Article + GitHub README
- ✓ Audience: Technical writers, documentation engineers
- ✓ Tone: Narrative + tutorial
- ✓ Length: 2,500-3,000 words

### Step 3: Capture (During Implementation)
- Create `docs/blog/journal.md` for daily observations
- Capture metrics at each phase completion
- Screenshot key findings (integrity reports, terminal output)
- Document "aha moments" and design decisions

### Step 4: Drafting (Phase 4)
- Generate first draft from materials + journal
- Include actual metrics and code examples

### Step 5: Review (Post-Phase 1)
- Citation completeness check
- Jargon accessibility review
- Decision justification verification

### Step 6: Publication (After Phase 1 complete)
- Format for LinkedIn Article
- Create short post (150-300 words) for engagement
- Publish article, then link via comment

---

## DSM Feedback Plan

Following Section 6.4.5 (Project Feedback Deliverables):

### Three-File System

1. **`docs/dsm-feedback-backlogs.md`**
   - Daily observations of DSM gaps or improvement opportunities
   - Action items for DSM enhancement

2. **`docs/dsm-feedback-methodology.md`**
   - Record of what DSM guidance was used
   - Effectiveness scoring (1-5)
   - Observations on methodology application to software engineering

3. **`docs/dsm-feedback-blog.md`**
   - Blog writing process observations
   - Section 2.5.6-2.5.8 effectiveness
   - Publication strategy insights

---

## Project Structure (Confirmed)

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
├── docs/                      # In-repo (DSM 4.0 pattern)
│   ├── handoffs/
│   ├── decisions/
│   ├── checkpoints/
│   ├── blog/
│   │   ├── materials.md       # Prepared materials
│   │   └── journal.md         # Daily observations
│   ├── dsm-feedback-backlogs.md
│   ├── dsm-feedback-methodology.md
│   └── dsm-feedback-blog.md
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

## Next Steps

1. **Phase 0 execution begins:** Create project structure
2. **Daily rhythm:** Work in 2-4 hour sessions, update blog journal
3. **Checkpoint at Phase 1 complete:** Document milestone
4. **Sprint 1 complete:** Phase 1 MVP delivered, blog drafted
5. **Sprint 2 planning:** Evaluate Phase 2 scope based on Phase 1 learnings

---

## Open Questions (To Resolve During Phase 0)

1. **Parser library:** Use regex or markdown library (mistune, markdown-it-py)?
2. **CLI framework:** Click (recommended) or argparse?
3. **Testing approach:** Unit tests only or include integration tests?
4. **Report format:** Markdown only or support multiple formats?

These will be answered with research and prototyping in early phases.

---

**Plan Status:** Ready for execution
**Approval:** Proceed to Phase 0 - Environment Setup
