# DSM Graph Explorer, Plans & Backlog

Epoch roadmaps and active backlog items. Completed items move to `done/`.

## Backlog ID Convention

Two tracks, to avoid collision with DSM Central's BL registry:

- **`BL-{NNN}`** — Central-imported items. Keep the ID assigned by DSM Central
  (e.g., `BL-302`). Never renumbered locally.
- **`BL-GE-{NNN}`** — local-origin items (Graph Explorer). The `GE` prefix
  disambiguates from Central's registry. Numbered from `001`.

**Required fields:** Status, Priority (High/Medium/Low), Date Created, Origin, Author.

## Active Backlog

| BL | Title | Track | Priority | Status |
|----|-------|-------|----------|--------|
| BL-GE-002 | Graph Source Expansion (config/YAML + cross-file links) | Local-origin | High | Planned (Sprint 19) |
| BL-GE-001 | Semantic Concept Layer (Layer 4.5) | Local-origin | Medium | Proposed (DEC-011 accepted, Epoch 6 plan pending) |
| BL-302 Phase 1.5 | TOON Migration for `--knowledge-summary` | Central-imported | High | Closed S53, TOON not adopted (DEC-010 Amendment 2) |
| BL-302 Phase 2 | Leiden Clustering | Central-imported | High | Closed S57 without delivery ([DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md)) |

## Epoch Roadmaps

| File | Epoch | Status |
|------|-------|--------|
| `epoch-1-plan.md` | Epoch 1 | Complete |
| `epoch-2-plan.md` | Epoch 2 | Complete |
| `epoch-3-plan.md` | Epoch 3 | Complete |
| `epoch-4-plan.md` | Epoch 4 | Complete |
| `epoch-5-plan.md` | Epoch 5 | In progress (current), Sprints 17-18 closed, Sprint 19 in planning |

## Lifecycle

Active backlog items and epoch roadmaps live here. Completed backlog items move
to `done/`. Epoch plans remain in place after completion (status marked Complete)
as the historical roadmap record.
