# Epoch 2 Blog Journal

**Date:** 2026-02-04 (started)
**Project:** DSM Graph Explorer
**Epoch:** 2 (Exclusion, Semantic Validation, Graph Prototype)

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

## Session: 2026-02-05 — WSL Migration Verification

### What Happened

1. **Environment migration** — Completed migration from Windows to WSL2 following DEC-004:
   - DSM Central: `D:\data-science\agentic-ai-data-science-methodology` → `~/dsm-agentic-ai-data-science-methodology`
   - Graph Explorer: `D:\data-science\dsm-graph-explorer` → `~/dsm-graph-explorer`

2. **Path updates** — Updated documentation across both repositories:
   - Graph Explorer CLAUDE.md (environment section, @ reference)
   - WSL migration guide (v1.1, new path structure)
   - DSM Central checkpoint (path mappings, diagram)

3. **Environment verification** — Confirmed all systems operational:
   - pytest: 202 tests passed (94% coverage, 1.05s)
   - dsm-validate: Scanned 125 files in 0.08s, found 8 Section 2.6 errors

4. **Stale venv fix** — Discovered copied venv had hardcoded Windows paths in shebangs. Resolution: delete and recreate.

### Aha Moments

1. **Venv portability trap** — Copying a Python venv across environments doesn't work; the shebang paths are hardcoded at creation time. Always recreate, never copy.

2. **Documentation as infrastructure** — Migrating development environments requires updating multiple documentation files. A checklist helps ensure nothing is missed (CLAUDE.md, guides, checkpoints).

3. **Hub-and-spoke in practice** — Updating DSM Central and Graph Explorer together demonstrated how the hub-and-spoke model handles cross-project changes. Changes propagate through file references, not copied content.

4. **Folder naming matters** — Renaming `agentic-ai-data-science-methodology` to `dsm-agentic-ai-data-science-methodology` (adding prefix) makes `ls ~/dsm-*` show all related projects together.

### Metrics

| Metric | Value |
|--------|-------|
| Files updated | 3 (CLAUDE.md, migration guide, DSM checkpoint) |
| Tests verified | 202 passed |
| Validation run | 125 files, 0.08s |
| Venv recreated | Yes (stale path issue) |

### Blog Material

**Title options for WSL migration post:**
1. "From Windows to WSL: Migrating a Documentation Validation Ecosystem"
2. "Environment Standardization: Why We Moved Our AI-Assisted Projects to Linux"
3. "The Venv Portability Trap and Other Migration Lessons"

**Key narrative threads:**
- Decision-driven migration (DEC-004 as structured approach)
- Environment parity: dev matches CI/CD
- Practical pitfalls: venv shebangs, path updates
- Hub-and-spoke coordination across projects

---

## Session: 2026-02-06 — Sprint 4: Exclusion & Severity

### What Happened

1. **Phase 4.1: Config Infrastructure** (previous session) — Built Pydantic config models (`Config`, `SeverityMapping`), YAML loading, config file discovery, CLI merge logic. 36 tests.

2. **Phase 4.2: Exclusion Logic** (previous session) — Implemented `file_filter.py` with fnmatch-based patterns, `--exclude` and `--config` CLI options. EXP-001 validated. 18 tests.

3. **Phase 4.3: Severity Levels** — Added INFO to Severity enum, created `assign_severity()` and `apply_severity_overrides()` functions. Post-validation override pattern: validator assigns base severity, then config patterns remap it. Wired through CLI and updated reporter for three-level output. EXP-002 validated. 19 new tests.

4. **Real-world validation** — Ran against DSM repo: 125 files, 10 errors (Section 2.6), 0 warnings, 0 info. Added `"0.2"` to KNOWN_DSM_IDS (was causing 44 warnings).

5. **Sprint boundary documentation** — Updated methodology.md (Entry 17), checkpoint document, epoch-2-plan.md (all Sprint 4 tasks marked complete), CLAUDE.md (full Sprint Boundary Checklist from DSM 2.0 Template 8), README.

### Aha Moments

1. **Post-validation override is clean** — Instead of embedding severity logic in the validator, applying overrides after validation keeps the core logic simple. `dataclasses.replace()` creates new results without mutation.

2. **Research-first planning pays off** — The research phase (Session 2026-02-04) grounded the fnmatch and Pydantic choices. Sprint 4 implementation had no surprises; every design decision was pre-validated.

3. **EXP-002 test matrix as specification** — Writing the test matrix in the plan document, then implementing it as tests, made the specification executable. The tests ARE the specification.

4. **Three-phase sprint structure works** — Splitting Sprint 4 into Config → Exclusion → Severity kept each phase focused and testable. Natural dependency order.

### Metrics

| Metric | Value |
|--------|-------|
| Tests added | 73 |
| Total tests | 218 |
| Coverage | 95% |
| New source files | 2 (`config_loader.py`, `file_filter.py`) |
| Modified source files | 3 (`cli.py`, `cross_ref_validator.py`, `report_generator.py`) |
| EXP-001 cases | 4/4 passed |
| EXP-002 cases | 7/7 passed |

### Blog Material

**Sprint 4 narrative thread:**
- From 448 errors to 10: the journey of making error reports actionable
- Config files as documentation: `.dsm-graph-explorer.yml` tells you what to exclude and why
- Severity levels let teams triage: ERROR for core docs, INFO for drafts, WARNING as default
- Post-validation override: a clean pattern for separating "what's wrong" from "how bad is it"

---

**Last Updated:** 2026-02-06
