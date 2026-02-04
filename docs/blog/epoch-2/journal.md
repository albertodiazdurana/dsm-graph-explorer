# Epoch 2 Blog Journal

**Project:** DSM Graph Explorer
**Epoch:** 2 (Exclusion, Semantic Validation, Graph Prototype)
**Started:** 2026-02-04

---

## Session: 2026-02-04 — Epoch 2 Planning

### What Happened

1. **Backlog cleanup** — Organized `docs/backlog/` with a `done/` subfolder. Moved 4 resolved items:
   - Gateway 2 review (ACTION-1 completed)
   - Cross-project patterns from sql-agent
   - Docs folder reference
   - Parser trailing period fix

2. **Blog reorganization** — Moved Epoch 1 blog files to `epoch-1/` folder, created `epoch-2/` for new content.

3. **Research phase** — Conducted technical research for all Epoch 2 areas:
   - Click `multiple=True` for repeatable `--exclude` options
   - Pydantic + PyYAML for config validation
   - `fnmatch` for glob pattern exclusions
   - scikit-learn TF-IDF for semantic similarity
   - NetworkX for graph construction
   - GitHub Actions workflow patterns

4. **Detailed sprint plan** — Created comprehensive plan with:
   - 4 sprints (Exclusion → CI → Semantic → Graph)
   - 4 experiments defined (EXP-001 through EXP-004)
   - Pydantic added to core dependencies
   - Phase-by-phase task breakdowns

### Aha Moments

1. **Pydantic for config validation** — User asked if Pydantic would be useful. Answer: Yes! Type-safe config models with automatic YAML validation and clear error messages. Much better than raw PyYAML parsing.

2. **Research-first planning** — Conducting technical research before detailed planning produces grounded, actionable plans. The research document becomes a reference during implementation.

3. **done/ folder pattern** — Simple but effective: move resolved backlog items to a subfolder instead of deleting them. Keeps backlog actionable while preserving history.

### Metrics

| Metric | Value |
|--------|-------|
| Backlog items resolved | 4 |
| Backlog items active | 1 (Epoch 2 inputs) |
| Research topics covered | 6 |
| Experiments defined | 4 |
| Sprints planned | 4 |

### Blog Material

**Title options for Epoch 2 blog:**
1. "From Prototype to Production: Adding CI to a Documentation Validator"
2. "The 448→6→0 Journey: Making Error Reports Actionable"
3. "Dog-Fooding Your Methodology: What Happens When Tools Validate Their Creators"

**Key narrative threads:**
- The trailing period bug: 145 tests passed but real data revealed the flaw
- Lesson: Validate fixtures against production data early
- Research-first planning for new epochs

---

## Planned: Sprint 4 — Exclusion & Severity

**Objective:** Implement `--exclude` flag and config file support.

**Key deliverables:**
- Pydantic config models
- `--exclude` CLI option (repeatable)
- `.dsm-graph-explorer.yml` support
- Severity levels (ERROR/WARNING/INFO)

**Experiments:**
- EXP-001: Exclusion pattern validation
- EXP-002: Severity classification

---

**Last Updated:** 2026-02-04
