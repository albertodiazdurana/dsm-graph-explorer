**Consumed at:** Session 47 start (2026-04-13)

# Sprint 15 Checkpoint — Session 45

**Date:** 2026-04-02
**Session:** 45
**Sprint:** 15 (Protocol Usage Analysis)
**Branch:** session-45/2026-04-02
**Status:** Sprint 15 COMPLETE

---

## Sprint 15 Deliverables

### Implementation (Sessions 42-43)

Six new analysis modules implementing a four-layer protocol usage methodology:

| Module | Purpose | Tests |
|--------|---------|-------|
| `section_index.py` | DSM_0.2 section inventory + designed classification | 11 |
| `declared_refs.py` | Layer 1: CLAUDE.md reference extraction | 10 |
| `prescribed_refs.py` | Layer 2: Skill definition scanning | 12 |
| `observed_refs.py` | Layer 3: Session transcript analysis | 11 |
| `usage_report.py` | Four-layer aggregation + ground truth validation | 13 |
| `usage_diff.py` | Cross-spoke usage comparison | 10 |

CLI: `--protocol-usage`, `--usage-compare`, Rich table output.
Total: 664 tests, 91% coverage.

### EXP-009: Protocol Usage Validation (Session 45)

**Result: CONDITIONAL PASS**

Stage A (all 4 layers, real data):
- 177 sections indexed, 42 dispatch entries (DSM_0.2 v1.4.1)
- 225 total references (6 declared, 82 prescribed, 137 observed)
- 18 high-usage, 159 low-usage, 65 designed-vs-observed gaps
- Ground truth: 4/7 pass (57%), below 60% threshold
- Bug found and fixed: GT ID matching used exact match, needed suffix match

Stage B (transcript validation of 3 failing GT sections):
- Read-Only Access: true negative (implicit constraint, never named)
- Inclusive Language: true negative (passive standard, compliance = absence of violations)
- Active Suggestion Protocol: behavioral false negative (behavior present, label absent)
- Pattern: procedural protocols (4/4 pass) vs behavioral protocols (0/3 pass)
- Recommendation: split ground truth into procedural and behavioral sets

### Inbox Processing (Session 45)

Two DSM Central items received and processed:
1. **EXP-002 Knowledge Graph Feasibility** (BACKLOG-302): `--knowledge-summary` feature
   deferred to Sprint 16 backlog. GraphML None-value bug noted.
2. **EXP-001 Reachability** (BACKLOG-230): Informational, acknowledged.
   Validation dataset opportunity noted.

Research documents created in `dsm-docs/research/`.

### Epoch Plan Updated

Sprint 15 tasks checked off, Sprint 16 candidates updated with BACKLOG-302
and GraphML bug fix, COULD list expanded with 3 new items from inbox.

## Key Metrics

| Metric | Start (Sprint 14) | End (Sprint 15) |
|--------|-------------------|-----------------|
| Tests | 547 | 664 |
| Coverage | 95% | 91% |
| Source files | 18 | 24 (+6) |
| Test files | 19 | 25 (+6) |
| Experiments | 8 | 9 (EXP-009) |

## What Remains (Epoch 4)

- [ ] Sprint 15 boundary: feedback push, blog journal, README, hub/portfolio notification
- [ ] Sprint 16 decision gate: `--knowledge-summary` (BACKLOG-302) vs epoch close-out
- [ ] GraphML None-value bug fix (small, any sprint)
- [ ] Open Source Contribution Pipeline (FalkorDBLite issue #85)
- [ ] dsm-docs/ → dsm-dsm-docs/ migration (long-standing)