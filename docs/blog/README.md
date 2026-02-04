# docs/blog/

Blog content from raw materials to published posts, organized by epoch.

## Structure

```
docs/blog/
├── epoch-1/           # Epoch 1: Parser MVP & Validator (Sprints 1-3)
│   ├── blog-draft.md
│   ├── blog-materials-sprints.md
│   ├── journal.md
│   ├── linkedin-post.md
│   ├── materials.md
│   └── broken-refs-example.png
└── epoch-2/           # Epoch 2: CLI & Exclusions (Sprint 4+)
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
