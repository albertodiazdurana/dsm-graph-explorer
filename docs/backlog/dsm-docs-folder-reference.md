# DSM Docs Folder Structure Reference

**Source Project:** SQL Query Agent with Ollama
**Purpose:** Document how the `docs/` folder was organized in sql-agent as reference for dsm-graph-explorer
**Date:** 2026-02-04

---

## Overview

The sql-agent project used a structured `docs/` folder following DSM 4.0 patterns. Each subfolder has a distinct purpose and lifecycle.

---

## Folder Structure

```
docs/
├── plans/                 # Roadmaps and sprint plans
├── research/              # State-of-art research, literature review
├── decisions/             # Architecture Decision Records (ADRs)
├── checkpoints/           # Milestone snapshots
├── backlog/               # DSM alignment reports (DSM → project)
├── feedback/              # DSM feedback files (project → DSM)
├── blog/                  # Blog materials, posts, images
└── _references/           # External references (job descriptions, etc.)
```

---

## Folder Details

### `docs/plans/`

**Purpose:** Development roadmaps and sprint-level planning.

**Files in sql-agent:**
| File | Content |
|------|---------|
| `PLAN.md` | Master development plan (architecture, evaluation metrics, code snippets) |
| `sprint-1-plan.md` | Sprint 1 phases, deliverables, success criteria |
| `sprint-2-plan.md` | Sprint 2 phases, deliverables, success criteria |

**When to update:** At project start, at sprint boundaries, when scope changes.

---

### `docs/research/`

**Purpose:** Literature review, state-of-art surveys, experiment design documentation.

**Files in sql-agent:**
| File | Content |
|------|---------|
| `text_to_sql_state_of_art.md` | Benchmarks, approaches, model comparisons, best practices from papers |
| `ablation-study-design.md` | Experiment design for EXP-002 (6 configs × 14 queries) |

**When to update:** Phase 0.5 (research phase), before major experiments.

---

### `docs/decisions/`

**Purpose:** Architecture Decision Records (ADRs) — document significant technical choices with rationale.

**Files in sql-agent:**
| File | Decision |
|------|----------|
| `DEC-001_chinook-database.md` | Selected Chinook as test database |
| `DEC-002_feedback-folder-consolidation.md` | Consolidated feedback files into single folder |
| `DEC-003_model-aware-prompts.md` | Different prompt formats per model |
| `DEC-004_sql-postprocessing.md` | Programmatic SQL fixes vs prompt-only approach |
| `DEC-005_model-selection-llama3-1-8b.md` | Selected llama3.1:8b over sqlcoder:7b |

**Naming convention:** `DEC-NNN_short-description.md`

**When to update:** When making a significant technical choice with alternatives considered.

---

### `docs/checkpoints/`

**Purpose:** Milestone snapshots documenting state at key points.

**Files in sql-agent:**
| File | Milestone |
|------|-----------|
| `s01_setup_checkpoint.md` | Sprint 1 setup complete |
| `s01_phase1_phase2_checkpoint.md` | Sprint 1 phases 1-2 complete |
| `s01_completion_checkpoint.md` | Sprint 1 final |
| `s02_phase1_blog_checkpoint.md` | Sprint 2 blog phase complete |
| `s02_phase2_pre_checkpoint.md` | Sprint 2 pre-ablation |
| `s02_phase2_checkpoint.md` | Sprint 2 ablation complete |
| `s02_final_checkpoint.md` | Sprint 2 final |

**Naming convention:** `s0X_description_checkpoint.md`

**When to update:** At phase boundaries, sprint boundaries, significant milestones.

---

### `docs/backlog/`

**Purpose:** DSM alignment reports — how well the project follows DSM, action items.

**Direction:** DSM → Project (methodology guiding the project)

**Files in sql-agent:**
| File | Content |
|------|---------|
| `dsm-alignment-gateway1-setup.md` | Gateway 1 review at project setup |

**When to update:** At gateway reviews (sprint boundaries).

---

### `docs/feedback/`

**Purpose:** Three-file feedback system — track DSM effectiveness, propose improvements.

**Direction:** Project → DSM (project informing methodology improvements)

**Files in sql-agent:**
| File | Content |
|------|---------|
| `methodology.md` | 22 entries scoring DSM effectiveness (avg 4.3/5), gaps identified |
| `backlogs.md` | 12 structured proposals for DSM improvements |

**When to update:** Throughout sprint (methodology.md), when gaps identified (backlogs.md).

---

### `docs/blog/`

**Purpose:** Blog materials from raw observations to published posts.

**Files in sql-agent:**
| File | Content |
|------|---------|
| `blog-materials-s01.md` | Raw observations from Sprint 1 |
| `blog-materials-s02.md` | Raw observations from Sprint 2 |
| `blog-s01.md` | Full blog post: "Two Experiments in Parallel" |
| `blog-s02-collaboration-value.md` | Full blog post: "The Case for Human-Agent Collaboration" |
| `blog-s02-ablation.md` | Full blog post: "What 84 Experiments Taught Me About Prompt Engineering" |
| `linkedin-post-s01.md` | LinkedIn version of blog 1 (with published URL) |
| `linkedin-post-s02.md` | LinkedIn version of blog 2 (with published URL) |
| `linkedin-post-s02-ablation.md` | LinkedIn version of blog 3 (with published URL) |
| `images/` | SVG/PNG visuals for posts |

**Naming convention:**
- Materials: `blog-materials-s0X.md`
- Full post: `blog-s0X.md` or `blog-s0X-[topic].md`
- LinkedIn: `linkedin-post-s0X.md` or `linkedin-post-s0X-[topic].md`

**When to update:** Throughout sprint (materials), at sprint boundaries (posts).

---

### `docs/_references/`

**Purpose:** External reference materials not part of DSM workflow.

**Files in sql-agent:**
| File | Content |
|------|---------|
| `job-description.md` | JetBrains ML Engineer role for interview alignment |
| `handoff_jetbrains_alignment.md` | Session handoff notes |

**When to update:** As needed for external context.

---

## Summary

| Folder | Direction | Frequency |
|--------|-----------|-----------|
| `plans/` | — | Sprint boundaries |
| `research/` | — | Phase 0.5, before experiments |
| `decisions/` | — | When significant choices made |
| `checkpoints/` | — | Phase/sprint boundaries |
| `backlog/` | DSM → Project | Gateway reviews |
| `feedback/` | Project → DSM | Throughout, sprint boundaries |
| `blog/` | — | Throughout, sprint boundaries |
| `_references/` | — | As needed |
