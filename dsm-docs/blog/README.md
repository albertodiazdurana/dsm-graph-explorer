# dsm-docs/blog/

Blog content from raw materials to published posts, organized by epoch.

## Publication tracker

The Sprint Boundary Checklist item "Blog publication tracker updated" points at this
file. Until S58 there was no tracker in it to update, only a structure diagram, so the
item was unsatisfiable as written. This table is that tracker.

| Post | Epoch | Status | Where |
|------|-------|--------|-------|
| [Validating 7,400 Lines of Documentation with Compiler Architecture](epoch-1/2026-02-05-blog-draft.md) | 1 | **Published** 2026-02-05 | [LinkedIn](https://www.linkedin.com/posts/albertodiazdurana_technicalwriting-docsascode-documentation-activity-7425203346304835585-9fZJ) (also [LinkedIn short form](epoch-1/2026-02-05-linkedin-post.md)) |
| [WSL migration](epoch-2/2026-02-06-wsl-migration-post.md) | 2 | Draft v1, unpublished since 2026-02-06 | , |
| [How a Fleet of Agents Red-Carded My Own Decision](epoch-5/2026-07-06-multi-agent-red-card.md) | 5 | Drafted 2026-07-06, **no status line in the file**, publication state unrecorded | , |

Epochs 3 and 4 produced a journal but no post. Sprint 18's journal entry is outstanding,
see the Workflow note below.

## Structure

```
dsm-docs/blog/
├── journal.md         # Top-level append-only capture (pre-epoch-split)
├── epoch-1/           # Epoch 1: Parser MVP & Validator (Sprints 1-3)
│   ├── 2026-02-05-blog-draft.md
│   ├── 2026-02-05-linkedin-post.md
│   ├── blog-materials-sprints.md
│   ├── journal.md
│   ├── materials.md
│   └── *.png
├── epoch-2/           # Epoch 2: CLI & Exclusions (Sprint 4+)
│   ├── 2026-02-06-wsl-migration-post.md
│   ├── README.md
│   ├── journal.md
│   └── materials.md
├── epoch-3/           # Epoch 3: journal only
│   └── journal.md
├── epoch-4/           # Epoch 4: journal + materials, no post
│   ├── journal.md
│   └── materials.md
└── epoch-5/           # Epoch 5: Intrinsic-ToC evolution
    ├── 2026-07-06-multi-agent-red-card.md
    ├── journal.md
    └── materials.md
```

## File Naming Convention

| File | Purpose |
|------|---------|
| `materials.md` | Prepared blog structure: titles, hooks, story arc, technical details |
| `journal.md` | Sprint-by-sprint observations, design decisions, metrics, aha moments |
| `blog-draft.md` | Full blog post draft |
| `linkedin-post.md` | LinkedIn version (with published URL after posting) |
| `images/` | SVG or PNG visuals for posts |

## Workflow

- **During sprint:** Capture observations in `journal.md`
- **At sprint boundary:** Update journal with metrics and aha moments
- **Phase 4:** Draft full blog from `materials.md` + `journal.md`

**Reference:** Section 2.5.6-2.5.8 (Blog/Communication Deliverable Process)
