# Reference: docs/ Folder Structure from sql-query-agent-ollama

**Source Project:** SQL Query Agent with Ollama
**Purpose:** Document how each docs/ subfolder was used in practice
**Date:** 2026-02-03

---

## Overview

The sql-agent project used the following docs/ structure across 2 sprints:

```
docs/
├── plans/           # Development roadmaps
├── decisions/       # Architecture Decision Records (ADRs)
├── checkpoints/     # Milestone snapshots
├── research/        # State-of-art research, experiment design
├── backlog/         # DSM alignment reports
├── feedback/        # DSM methodology feedback (3-file system)
├── blog/            # Blog posts, LinkedIn posts, images
└── _references/     # External reference materials
```

---

## docs/plans/

**Purpose:** Development roadmaps and sprint planning documents.

**Files created:**
| File | Description |
|------|-------------|
| `PLAN.md` | Master plan with architecture, evaluation metrics, model candidates, code snippets |
| `sprint-1-plan.md` | Sprint 1 phases, success criteria, deliverables (notebook prototype) |
| `sprint-2-plan.md` | Sprint 2 phases, success criteria, deliverables (Streamlit app) |

**Usage pattern:** Created at project start, referenced throughout, updated when scope changed.

---

## docs/decisions/

**Purpose:** Architecture Decision Records — document significant technical choices with rationale.

**Files created:**
| File | Decision |
|------|----------|
| `DEC-001_chinook-database.md` | Chose Chinook SQLite database for development |
| `DEC-002_feedback-folder-consolidation.md` | Consolidated feedback files into single folder |
| `DEC-003_model-aware-prompts.md` | Different prompt formats for sqlcoder vs llama3.1 |
| `DEC-004_sql-postprocessing.md` | Programmatic SQL fixes for SQLite compatibility |
| `DEC-005_model-selection-llama3-1-8b.md` | Selected llama3.1:8b as production model |

**Naming convention:** `DEC-NNN_short-description.md`

**Content structure:**
- Context: What problem we faced
- Decision: What we chose
- Rationale: Why this option
- Alternatives considered: What else we evaluated
- Consequences: Trade-offs accepted

---

## docs/checkpoints/

**Purpose:** Milestone snapshots capturing progress, metrics, and open questions.

**Files created:**
| File | Milestone |
|------|-----------|
| `s01_setup_checkpoint.md` | Sprint 1 setup complete |
| `s01_phase1_phase2_checkpoint.md` | Sprint 1 core agent built |
| `s01_completion_checkpoint.md` | Sprint 1 complete with evaluation |
| `s02_phase1_blog_checkpoint.md` | Sprint 2 blog posts drafted |
| `s02_phase2_pre_checkpoint.md` | Sprint 2 app structure ready |
| `s02_phase2_checkpoint.md` | Sprint 2 app functional |
| `s02_final_checkpoint.md` | Sprint 2 complete, project wrapped |

**Naming convention:** `s0X_description_checkpoint.md` (sprint number prefix)

**Content structure:**
- Date and sprint context
- Deliverables completed
- Metrics (test counts, accuracy, etc.)
- Open questions for next phase
- Blockers (if any)

---

## docs/research/

**Purpose:** Literature review, state-of-art research, experiment design documents.

**Files created:**
| File | Description |
|------|-------------|
| `text_to_sql_state_of_art.md` | Survey of text-to-SQL approaches, benchmarks, best practices |
| `ablation-study-design.md` | Design for EXP-002 (6 configs × 14 queries) |

**Usage pattern:** Created in Phase 0.5 (research phase) before implementation. Referenced when making architecture decisions. Ablation study design created before running experiments.

---

## docs/backlog/

**Purpose:** DSM alignment reports — gateway reviews and cross-project learnings.

**Files created:**
| File | Description |
|------|-------------|
| `dsm-alignment-gateway1-setup.md` | Gateway 1 review after project setup |

**Usage pattern:** Created at DSM gateway checkpoints. Contains checklist results, findings, required actions.

---

## docs/feedback/

**Purpose:** Three-file system for tracking DSM methodology effectiveness.

**Files created:**
| File | Description | Entries |
|------|-------------|---------|
| `methodology.md` | Score DSM per interaction (1-5 scale), gaps, recommendations | 22 entries |
| `backlogs.md` | Structured proposals for DSM improvements | 8 proposals |

**Note:** `blog.md` was not used separately — blog feedback was captured in `methodology.md` entries.

**Usage pattern:** Updated throughout project whenever a DSM interaction occurred (positive or negative). Running summary metrics maintained at top of methodology.md.

---

## docs/blog/

**Purpose:** Blog content from raw materials to published posts.

**Files created:**
| File | Description |
|------|-------------|
| `blog-materials-s01.md` | Raw observations from Sprint 1 |
| `blog-materials-s02.md` | Raw observations from Sprint 2 |
| `blog-s01.md` | Blog Part 1: "Two Experiments in Parallel" |
| `blog-s02-collaboration-value.md` | Blog Part 2: "The Case for Human-Agent Collaboration" |
| `blog-s02-ablation.md` | Blog Part 3: "What 84 Experiments Taught Me About Prompt Engineering" |
| `linkedin-post-s01.md` | LinkedIn version of Part 1 (with published URL) |
| `linkedin-post-s02.md` | LinkedIn version of Part 2 (with published URL) |
| `linkedin-post-s02-ablation.md` | LinkedIn version of Part 3 (with published URL) |
| `images/ablation-bar-chart.svg` | Bar chart visualization for Part 3 |
| `images/expected-vs-measured.svg` | Comparison visualization for Part 3 |

**Also present (user-added):**
- `ablation-results.png`
- `counter-intuitive-lesson.png`
- `execution-accuracy-by-prompt-configuration.png`
- `my-machine-is-having-a-hard-time.png`
- `Can-you-see-the-error.png`

**Naming convention:**
- Materials: `blog-materials-s0X.md`
- Full posts: `blog-s0X.md` or `blog-s0X-[topic].md`
- LinkedIn: `linkedin-post-s0X.md` or `linkedin-post-s0X-[topic].md`

---

## docs/_references/

**Purpose:** External reference materials not created by the project.

**Files:**
| File | Description |
|------|-------------|
| `handoff_jetbrains_alignment.md` | Reference from another project |
| `job-description.md` | External job description for context |

**Usage pattern:** Read-only reference materials. Prefixed with `_` to indicate external/reference status.

---

## Summary Statistics

| Folder | File Count | Primary Use |
|--------|------------|-------------|
| plans/ | 3 | Roadmaps |
| decisions/ | 5 | ADRs |
| checkpoints/ | 7 | Milestones |
| research/ | 2 | Literature + experiment design |
| backlog/ | 1 | DSM alignment |
| feedback/ | 2 | DSM feedback |
| blog/ | 8 posts + 7 images | Content |
| _references/ | 2 | External docs |

**Total:** 30 markdown files + 7 images across 2 sprints.

---

**Document created for:** dsm-graph-explorer project reference
