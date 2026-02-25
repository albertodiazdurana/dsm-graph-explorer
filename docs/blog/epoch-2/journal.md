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

## Session: 2026-02-09/10 — Sprint 5: CI & Documentation

### What Happened

1. **Phase 5.1: CI Workflow & Config** — Created `.github/workflows/dsm-validate.yml` (GitHub Actions, triggered on push/PR to markdown or config changes) and `.dsm-graph-explorer.yml` (self-validation config demonstrating the spoke-repo pattern).

2. **Phase 5.2: Pre-commit Hook** — Created `scripts/pre-commit-hook.sh`. Validates staged `.md` files, gracefully skips if `dsm-validate` is not installed. Supports both manual installation and pre-commit framework integration.

3. **Phase 5.3: User Guides** — Two new documents in `docs/guides/`:
   - `remediation-guide.md` — How to read output, fix each error type, manage cross-repo references, CI integration patterns.
   - `config-reference.md` — Complete field reference for `.dsm-graph-explorer.yml` with pattern matching rules, CLI interaction, hub vs spoke examples.

4. **DSM Feedback** — Three new methodology entries and four backlog proposals:
   - Entry 19 / Proposal #15: File-by-file approval loop mechanics (collaboration protocol)
   - Entry 20 / Proposal #17: `docs/guides/` subfolder for user-facing documentation
   - Entry 21 / Proposal #18: `feedback/` → `feedback-to-dsm/` rename for explicit directionality
   - Proposal #16: Convention linting mode (from DSM central audit)

5. **Test fix** — `test_errors_with_strict_exits_one` was affected by config auto-discovery: the repo's `.dsm-graph-explorer.yml` downgraded severity, changing the expected exit code. Fixed by passing an empty config file to isolate the test.

6. **README update** — Added Sprint 5 features, updated project structure (`.github/`, `scripts/`, `docs/guides/`, `docs/backlog/`), updated status line and footer.

### Aha Moments

1. **Spoke-repo config pattern** — When a project references DSM sections defined in another repository, those references will always appear as broken. The solution is a config pattern: set `docs/**/*.md` to INFO severity. The findings stay visible (useful for reference) but don't block CI. This is the first reusable configuration pattern to emerge from the project.

2. **docs/guides/ as a category** — DSM's `docs/` subfolders are all project-management artifacts (checkpoints, decisions, feedback). User-facing documentation (guides, references, how-tos) didn't have a home. Creating `docs/guides/` immediately clarified the structure. This became Entry 20, a concrete gap in DSM 4.0 Section 2.

3. **Config auto-discovery affects tests** — Adding `.dsm-graph-explorer.yml` to the repo root meant the config loader finds it during test runs, not just during manual validation. Tests that depend on default severity behavior need to explicitly pass an empty config. A subtle interaction between production config and test isolation.

4. **Collaboration loop, third iteration** — The Pre-Generation Brief Protocol has been strengthened three times (Sprint 1, Sprint 3, Sprint 5). Each iteration made the mechanics more explicit: from "explain first" to "STOP and wait" to a numbered file-by-file loop with plain text approvals. The pattern suggests that protocol refinement converges through practice, not through specification alone.

### Metrics

| Metric | Value |
|--------|-------|
| New files created | 5 (workflow, config, hook, 2 guides) |
| Files modified | 5 (README, backlogs, methodology, epoch-2-plan, test_cli) |
| DSM methodology entries added | 3 (Entries 19-21) |
| DSM backlog proposals added | 4 (Proposals 15-18) |
| Tests added | 0 (no new application code) |
| Tests fixed | 1 (config auto-discovery isolation) |
| Total tests | 218 |
| Coverage | 95% |

### Blog Material

**Sprint 5 narrative threads:**
- From tool to pipeline: adding CI, pre-commit, and docs turns a CLI tool into a deployable validation system
- The spoke-repo problem: what happens when your tool validates references to documents it can't see
- Documentation as product: user guides vs project-management docs, and why they need different homes
- Collaboration protocol convergence: three iterations of the same problem, each making the mechanics more explicit

---

## Sessions: 2026-02-10 through 2026-02-23 — Sprint 6: Semantic Validation

### What Happened

1. **Phase 6.0: EXP-003 Threshold Tuning** — Designed and ran a capability experiment with 25 synthetic test cases (10 match, 10 drift, 5 ambiguous with generic titles). Evaluated title-only vs title+excerpt modes across thresholds 0.05-0.30. Key finding: title-only cannot disambiguate generic titles like "Expected Outcomes" or "Deliverables" (gap = -0.033), while title+excerpt creates a 0.264 separation gap. Documented as [DEC-005](../../decisions/DEC-005-semantic-validation-approach.md): threshold 0.10, min 3 tokens, corpus-scoped IDF, section number stripping.

2. **Phase 6.1: Parser Context Extraction** — Extended the parser models with `Section.context_excerpt` (~50 words of prose after each heading) and `CrossReference.context_before`/`context_after` (3 lines surrounding each reference). These fields feed the TF-IDF comparison. 12 new tests (8 excerpt, 4 context window).

3. **Phase 6.2: TF-IDF Similarity Module** — Built `src/semantic/similarity.py` with corpus-scoped TF-IDF vectorization, stopword removal, section number stripping, and a minimum token gate. The module is self-contained with scikit-learn as an optional dependency. 14 new tests.

4. **Phase 6.3: CLI Integration** — Wired semantic validation into the CLI with a `--semantic` flag. Added `semantic_threshold` and `semantic_min_tokens` to the config loader. Built `build_section_lookup()` in the cross-ref validator for efficient section resolution. Extended the report generator with drift warning (yellow) and insufficient context (dim) tables in both Rich and markdown output. Graceful fallback when scikit-learn is absent (clear error, exit code 2). 6 new CLI integration tests.

5. **EXP-003b: Real Data Validation** — The pivotal experiment. Generated 1,191 cross-reference rows from the actual DSM methodology repository. Used agent-assisted labeling on 128 near-threshold rows (scores 0.08-0.12): the agent proposed labels based on context fields, the user validated in batches. Results: Precision=1.000, Recall=0.496, F1=0.663 at threshold 0.10. All 63 disagreements were false negatives (auto=drift, manual=match), with scores between 0.08 and 0.10. Root causes: empty target excerpts, vocabulary mismatch in backlog proposals, short generic section titles. DEC-005 amended to lower threshold from 0.10 to 0.08.

6. **Session 15 Housekeeping** — Migrated `docs/inbox/` → `_inbox/` (DSM v1.3.52 compliance), `experiments/` → `data/experiments/` (Proposal #23 accepted), retroactively stamped all 50 feedback entries as Pushed, analyzed a research paper on contrastive decoding (informational, pushed to DSM Central).

### Aha Moments

1. **Synthetic vs real data gap** — EXP-003 (synthetic) achieved F1=0.889 with recall=0.800. EXP-003b (real) dropped to F1=0.663 with recall=0.496 at the same threshold. The synthetic test cases were too clean: they had rich excerpts and distinct vocabulary. Real-world DSM content has empty excerpts, short titles, and vocabulary overlap between backlog proposals and section content. This validated the EXP-003 limitations section, which explicitly called out the synthetic data risk.

2. **Agent-assisted labeling** — Labeling 128 rows manually would take hours. The agent read context fields, proposed labels with reasoning, and presented them in grouped batches for human validation. The user validated ~130 rows in ~15 minutes. This is a reusable pattern: agent proposes, human validates, both contribute complementary strengths. Captured as methodology Entry 23 / Proposal #20.

3. **Perfect precision, imperfect recall** — The tool never says "match" when it shouldn't (0 false positives), but it misses half the actual matches (63 false negatives). This is the right failure mode for a validation tool: conservative is better than permissive. Users can lower the threshold to recover more matches, accepting the trade-off explicitly.

4. **Empty excerpts as recall killer** — ~50% of false negatives had `(none)` as the target excerpt, leaving TF-IDF with only 3-5 tokens from the section title. This is not a bug in the algorithm; it is a content gap in the documentation. The finding creates a feedback loop: improving section content (adding introductory sentences) would directly improve semantic validation accuracy.

5. **Experiments as first-class artifacts** — Sprint 6 produced two experiment scripts (`exp003_tfidf_threshold.py`, `exp003b_real_data_validation.py`) that are as important as the source code. They are the evidence base for DEC-005. Moving them to `data/experiments/` (Proposal #23) gave them proper status in the project structure.

### Metrics

| Metric | Value |
|--------|-------|
| New source files | 1 (`src/semantic/similarity.py`) |
| Modified source files | 4 (parser, config_loader, cross_ref_validator, report_generator) |
| New test files | 1 (`test_cli_semantic.py`) |
| Tests added | 32 (12 parser + 14 semantic + 6 CLI) |
| Total tests | 250 |
| Coverage | 95% |
| Experiments run | 2 (EXP-003, EXP-003b) |
| Decisions created | 1 (DEC-005, later amended) |
| Methodology entries added | 7 (Entries 22-28) |
| Backlog proposals added | 5 (Proposals 19-23) |
| Sessions | 5 (Sessions 11-15) |

### Blog Material

**Sprint 6 narrative threads:**
- When synthetic tests lie: how 25 hand-crafted cases produced F1=0.889 but real data revealed F1=0.663
- The precision-recall trade-off in documentation tools: why conservative is correct
- Agent-assisted labeling: a human-AI collaboration pattern for ground truth creation
- Empty excerpts as a content quality signal: when your tool's weakness reveals your documentation's weakness
- From experiment to amendment: how EXP-003b changed a decision that EXP-003 established

**Title options for Sprint 6 blog:**
1. "When Your Synthetic Tests Are Too Optimistic: Validating NLP Thresholds Against Real Data"
2. "Perfect Precision, Imperfect Recall: The Right Failure Mode for Documentation Tools"
3. "1,191 Cross-References Later: What Real-World Data Teaches You About TF-IDF Thresholds"

---

**Last Updated:** 2026-02-25
