# Sprint 19: BL-GE-002 (Graph Source Expansion)

**Status:** PLANNED (S58, 2026-08-04). Replaces the closed Sprint 18 per [DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md).
**Duration:** 1.5-2 sessions (6-12 hours; five phases, P1 small and diagnostic, P2/P3 carrying the build, P4 the capability gate)
**Goal:** Extend the reference graph beyond markdown to structured config files (YAML, TOML, JSON) and materialise the path-valued references inside them as edges, answering Intrinsic-ToC Vision §9 Open Question 4 and unblocking Layer 4.
**Prerequisites:** Sprint 18 closed ([DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md), clustering out-of-vision-scope); BL-302 P1 `DEFAULT_EXCLUDES` shipped (S55) and load-bearing here.

**Work item (all phase detail lives there, this plan is the sprint-level wrapper):**
[BL-GE-002, Graph Source Expansion](BL-GE-002_graph-source-expansion.md). See also
[epoch-5-plan.md](epoch-5-plan.md) §Sprint 19.

---

## Research Assessment

**No Phase 0.5 deep-dive required.** The scope was fixed by DEC-012 and the current
implementation was read at BL authoring time rather than assumed, which already corrected
the framing once: the graph is not markdown-only because discovery is locked to markdown.
`collect_markdown_files` (`src/cli.py:36`) takes a `--glob` that already defaults to
`**/*.md` and is user-overridable. The constraint sits in the parser and the reference
extractor, not the file walk. A sprint scoped as "widen the glob" would have produced
empty nodes and looked like progress.

What remains genuinely unknown is node granularity for a config document (Open Design
Question 1), and that resolves better against real parsed output at P2 than against
speculation now. This mirrors Sprint 18's judgement on flat-vs-hierarchical partitions,
which was the right call there even though the sprint closed for unrelated reasons.

One inherited item to re-check rather than assume, per the lesson that cost Sprint 18 its
premise: `DEFAULT_EXCLUDES` was authored and tested against `.md` files. Dependency
directories hold far more YAML/TOML/JSON than markdown. P1 verifies the exclusions still
hold at the widened file set instead of trusting that they carry over.

## Experiment Gate

**Experiment REQUIRED: EXP-013 (coverage delta from source expansion).**

Per DSM 4.0 Section 4, tests establish correctness while capability experiments establish
whether the capability is real. Unit tests can prove that a given YAML file yields given
nodes. They cannot answer whether the resulting edges are genuine repository structure or
parsing noise, which is the capability claim this sprint makes.

**What the gate does and does not decide, stated explicitly because the coupling is easy
to invert:** EXP-013 does **not** gate whether Sprint 19 ships. Config nodes and their
path edges are real dependencies that exist in the repository regardless of what the
coverage number turns out to be. What EXP-013 decides is whether
[DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md) §Conditions 2's
clustering revisit trigger fires, that is, whether cross-reference coverage rises
materially above the ~25% S56 measured. A result below threshold is a finding about
clustering, not a failed sprint. Sprint 18 spent two sessions arguing a component-level
gate while the aim-level question went unmeasured; the distinction is written into the
plan this time.

**Sequencing:** P1 takes the baseline before any parser exists, P4 measures against it.
The threshold is pre-registered at kickoff (Open Design Question 4), before P2 begins and
therefore before anyone knows which way the number moves. Sprint 17 sequenced its C3 gate
after a fixture freeze and nearly enshrined a schema that could not ship; that ordering is
not repeated.

## Branch Strategy

Level 3 branch `sprint-19/graph-source-expansion` off the session branch. Merges back to
the session branch when all MUST deliverables are checked off. Per DSM_0.2 Three-Level
Branching, and per the S55 reminder that merging a Level 3 branch is a **phase** boundary,
not a sprint boundary: fire the Phase Boundary Checklist on merge and keep the sprint open
in MEMORY until the Sprint Boundary Checklist below actually runs.

---

## Deliverables

### MUST (sprint fails without these)

- [ ] Baseline cross-reference coverage measured and recorded using the S56 methodology, before any parser work (BL-GE-002 §P1)
- [ ] `DEFAULT_EXCLUDES` verified against the widened file set; zero dependency directories in `--knowledge-summary` output at the new glob, with before/after counts recorded (BL-GE-002 §P1)
- [ ] Structured-config parser for YAML, TOML and JSON producing graph nodes, test-first (BL-GE-002 §P2)
- [ ] Path-valued cross-file references materialised as edges to existing file nodes, test-first (BL-GE-002 §P3)
- [ ] EXP-013 run and recorded in `data/experiments/`, with the threshold pre-registered before P2 (BL-GE-002 §P4)
- [ ] Existing suite stays green (baseline **722 passed, 1 skipped, 91% coverage**, measured 2026-08-04 on this branch)
- [ ] Docs: CLI `--help` and README cover the new source classes, **and** the `DEFAULT_EXCLUDES` documentation Sprint 18 left open and explicitly carried forward to this sprint

### SHOULD (expected, defer if blocked)

- [ ] Coverage ≥ 91% (current baseline; no regression)
- [ ] `--knowledge-summary` surfaces config nodes within the Layer 1 condensation budget, or a recorded decision that they stay graph-only (BL-GE-002 §P5)
- [ ] `dsm-docs/guides/config-reference.md` documents `DEFAULT_EXCLUDES` and its opt-out (carried from Sprint 18 SHOULD, never delivered)
- [ ] Intrinsic-ToC Vision §9 Q4 annotated with the answer this sprint reaches

### COULD (stretch)

- [ ] Additional config formats beyond the three named (`.ini`, `.cfg`), only if P2 generalises cleanly
- [ ] A `--sources` flag separating source-class selection from `--glob` (Open Design Question 3), only if the single-pattern approach proves awkward in practice

---

## Phases

All phase detail (sub-tasks, design notes, success criteria) lives in
[BL-GE-002 §Phases](BL-GE-002_graph-source-expansion.md#phases). Summary map:

| Phase | Focus | Execution mode | Success criterion |
|---|---|---|---|
| P1: Baseline + exclusions | Coverage baseline; `DEFAULT_EXCLUDES` re-verified at the widened file set | measurement | Baseline recorded; zero dependency directories in output |
| P2: Config parser | YAML/TOML/JSON to graph nodes | code | Config file yields nodes carrying its identity and structure; suite green |
| P3: Link extraction | Path-valued references to edges | code | A known previously-invisible dependency appears as an edge |
| P4: EXP-013 | Coverage delta vs the P1 baseline, threshold pre-registered | experiment | Delta measured and recorded; DEC-012 revisit-trigger question answered either way |
| P5: Layer 1 integration | Summary surfacing + docs pass | code | Config nodes within budget, or exclusion recorded with a reason |

---

## Phase Boundary Checklist (intra-sprint)
- [ ] Update methodology.md with phase observations and scores
- [ ] Create checkpoint if significant milestone reached
- [ ] Log decisions made during phase (dsm-docs/decisions/)
- [ ] Update blog materials if insights worth sharing

---

## Open Design Questions

1. **Node granularity for a config document.** One node per file, or one per top-level key the way markdown headings become sections? Resolve at P2 against real parsed output (BL-GE-002 §Open questions 1).
2. **Unresolvable and out-of-repo path references.** Config files routinely point outside the repo (`~/dsm-agentic-ai-data-science-methodology/`). Edge to nothing, orphan-style node, or no edge? Needs a stated rule before P3 (BL-GE-002 §Open questions 2).
3. **Control surface.** Reuse `--glob`, or add a separate source-class flag? Reusing `--glob` is simplest but makes "markdown plus config" awkward as a single pattern (BL-GE-002 §Open questions 4).
4. **The EXP-013 pre-registered threshold, and it needs a human decision at kickoff.** What coverage delta counts as "materially above ~25%" for DEC-012 §Conditions 2? Deliberately unset at authoring time: a threshold fixed after the parser exists is a threshold fixed by someone who knows which way the number went (BL-GE-002 §Open questions 5).

---

## How to Resume
1. Read this sprint plan.
2. Read [BL-GE-002](BL-GE-002_graph-source-expansion.md) for phase detail, the scope boundary against BL-GE-001, and the out-of-scope reasoning on Python AST.
3. Read [DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md), especially §Conditions, which sets the revisit trigger EXP-013 tests.
4. Read the four pipeline stages any new source class must pass through: `src/cli.py:36` (`collect_markdown_files`), `src/parser/markdown_parser.py:56` (`parse_markdown_file`), `src/parser/cross_ref_extractor.py:37` (`extract_cross_references`), `src/graph/graph_builder.py:62` (`build_reference_graph`).
5. Read `dsm-docs/research/2026-07-21_cluster-quality-graph-density.md` for the ~25% coverage measurement and the methodology P1/P4 must reuse.

---

## Sprint Boundary Checklist
- [ ] Checkpoint document created (dsm-docs/checkpoints/)
- [ ] Feedback files updated (backlogs, methodology)
- [ ] Decision log updated with sprint decisions
- [ ] Tests passing (DSM 4.0 projects)
- [ ] dsm-docs/guides/smoke-tests.md current (or N/A if no smoke tests recorded this sprint)
- [ ] Blog journal entry written
- [ ] Blog publication tracker updated (`dsm-docs/blog/README.md`)
- [ ] Repository README updated (status, results, structure)
- [ ] Next steps summary (3-5 sentences: next sprint goal, key deliverables, relevant plan reference)
- [ ] **Local:** Epoch plan updated (completed tasks checked off, sprint status updated)
- [ ] **Local:** Hub/portfolio notified of sprint completion (`_inbox/` in DSM Central and portfolio)

> **Reconciled S57.** Items 1-9 are DSM_2.0.C §1 Template 8 verbatim; 10-11 are local
> additions carried over from `.claude/CLAUDE.md`, which previously held a divergent
> 7-item list. Neither list was a subset of the other. Both now carry the same 11.
