# BL-GE-002: Graph Source Expansion (config/YAML + cross-file links)

**Status:** Planned (Sprint 19, Epoch 5)
**Priority:** High
**Date Created:** 2026-08-04
**Origin:** Intrinsic-ToC Vision §9 Open Question 4 (raised 2026-04-13, unanswered until now); promoted to a work item by [DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md) (S57)
**Author:** Alberto Diaz Durana
**Target:** Sprint 19 (Epoch 5), see [epoch-5-sprint-19-plan.md](epoch-5-sprint-19-plan.md)
**Related:** [DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md), [BL-GE-001](BL-GE-001_semantic-concept-layer.md), [DEC-009](../decisions/DEC-009-no-local-llm-dependencies.md), [BL-302 Phase 2](BL-302-phase-2-leiden-clustering.md), [Intrinsic-ToC Vision](../research/2026-04-13_intrinsic-toc-vision.md) §4 / §9, research `2026-07-21_cluster-quality-graph-density.md`

---

## Context

The Intrinsic-ToC Vision has carried this open question since 2026-04-13, §9 Q4:

> **Graph expansion:** The current graph indexes markdown only. When (and how) should it
> expand to include Python source, YAML configs, and other file types? This gates Layer 4.

It sat unanswered for four months. Sprint 18 then ran into its consequence from the other
direction: S56 measured that only about **25% of files carry any cross-reference**, and
roughly 99% of sections are orphans. That sparsity is what made Leiden clustering
indistinguishable from a degree-preserving null (2.8% modularity excess), and it is why
[DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md) closed BL-302
Phase 2 and redirected the sprint here. The coverage number is not a newly discovered
defect, it is the measured cost of an unanswered scoping question.

### What the graph actually indexes today (verified in code, 2026-08-04)

This BL is written against the implementation, not against the phrase "markdown only".
The distinction changes what the work is:

| Stage | Location | Current behaviour |
|---|---|---|
| Discovery | `collect_markdown_files`, `src/cli.py:36` | Glob over each input path; default `**/*.md`, already user-overridable via `--glob` |
| Parsing | `parse_markdown_file`, `src/parser/markdown_parser.py:56` | Markdown-specific: numbered headings, appendix headings, `#` headings, into `Section` objects |
| Reference extraction | `extract_cross_references`, `src/parser/cross_ref_extractor.py:37` | Regex over prose for `Section N`, `Appendix X`, `DSM_N`, plus heading references |
| Graph assembly | `build_reference_graph`, `src/graph/graph_builder.py:62` | File nodes and section nodes, section IDs of the form `path:number` or `path:h:slug` |

The constraint is therefore **not** at the discovery layer. `--glob` will happily hand a
`.yaml` file to the pipeline today; what is missing is a parser that produces meaningful
nodes from it and an extractor that recognises the references such a file contains.
Framing the work as "widen the glob" would be wrong and would produce empty nodes.

## Motivation

Three distinct payoffs, listed strongest first:

1. **It closes the vision's own open question, and that question gates Layer 4.** Layer 4
   (Code Ontologies) cannot begin while the graph has no concept of a non-markdown node.
   This BL does not build Layer 4, it removes the blocker in front of it.

2. **Configuration is where this ecosystem's real cross-file structure lives, and the
   graph currently cannot see any of it.** `.claude/settings.json` hooks point at
   `.claude/hooks/*.sh`; `.mcp.json` names servers and environment variables;
   `pyproject.toml` declares the package layout and optional extras; CI workflow YAML
   references scripts and test paths. Every one of those is a genuine dependency edge
   that exists in the repository and is absent from the graph.

3. **It raises cross-reference coverage by adding real edges rather than by loosening a
   threshold.** This matters because DEC-012 §Conditions 2 makes coverage the revisit
   trigger for clustering. Any coverage improvement claimed here must be measured the
   same way S56 measured the deficit, so the two numbers are comparable.

## Scope

### In scope

1. **Config/YAML file indexing.** A parser producing graph nodes from structured config
   files. Target formats, in priority order: YAML (`.yml`/`.yaml`, including CI
   workflows), TOML (`pyproject.toml`), JSON (`.claude/settings.json`, `.mcp.json`).
2. **Cross-file link extraction.** Recognising and materialising path-valued references
   inside those files as edges to existing file nodes, e.g. a hook `command` naming a
   script, a workflow `uses`/`run` naming a path, a `pyproject.toml` `py-modules` entry.
3. **Graph model extension** sufficient to hold the above without restructuring the
   existing file/section node types.
4. **Integration into `--knowledge-summary`** so the new nodes appear in Layer 1 output
   under the existing condensation budget, or an explicit decision that they do not.
5. **A coverage measurement** taken before and after, using S56's methodology, so the
   effect on the ~25% figure is a number and not an impression.

### Out of scope

- **Python AST parsing, and this exclusion is deliberate rather than an omission.**
  Reasons: (a) it is Layer 4 proper, and this BL exists to unblock Layer 4, not to
  deliver it; (b) it is a materially larger build (Tree-sitter or `ast`, call graphs,
  inheritance edges) that would not fit beside the config work in one sprint; (c) the
  sprint it replaces was lost to exactly this failure mode, where an unstated scope
  extension crept in and was never challenged, so the exclusion is written down here
  rather than left to be inferred. Python source expansion, if wanted, is a separate BL.
- Local LLM or NLP inference of any kind, per
  [DEC-009](../decisions/DEC-009-no-local-llm-dependencies.md). Extraction is structural:
  a YAML key path is read, not interpreted.
- Semantic concept nodes, that is [BL-GE-001](BL-GE-001_semantic-concept-layer.md), see
  the boundary below.
- Re-opening clustering. DEC-012 §Conditions 2 defines the revisit trigger and the gate
  it must clear; nothing in this BL revives BL-302 Phase 2.
- Cross-repo / ecosystem expansion, that is Sprint 21 (Layer 3).

### Boundary against BL-GE-001 (required by DEC-012 §Conditions 3)

Both BLs raise graph density, by different mechanisms, and the boundary is stated here at
authoring time because it is far cheaper than untangling the two later:

| | BL-GE-001 (Semantic Concept Layer) | BL-GE-002 (this BL) |
|---|---|---|
| **Adds** | *Edges* between nodes that already exist | *Nodes* sourced from file types not previously indexed |
| **New node type** | `concept`, an abstract object independent of any file | None; new files become file/section-shaped nodes in the existing model |
| **Mechanism** | Author-declared concept registration | Structural parsing of config syntax |
| **Layer** | 4.5 | Prerequisite to 4 |
| **Epoch** | 6 (DEC-011 accepted, plan pending) | 5, Sprint 19 |

The overlap risk to watch: a config key such as `dsm-version` is both a config value this
BL would index and a *concept* BL-GE-001 would track for drift. The rule is that
BL-GE-002 records **where the value is written**, and BL-GE-001 records **what the value
means and whether its occurrences agree**. If BL-GE-002 finds itself comparing two values
for consistency, it has crossed into BL-GE-001.

## Dependencies

- **DEC-009** (constraint): bounds extraction to structural parsing.
- **DEC-012** (origin): authorises this as Sprint 19 and fixes its scope.
- **P1 of BL-302 Phase 2** (`DEFAULT_EXCLUDES`, shipped S55): load-bearing here. Widening
  the indexed file set past markdown will pull in dependency directories again unless the
  exclusions hold. The exclusion list was written for `.md` files and must be re-checked
  against the new formats, since `.venv` and `.pytest_cache` contain large numbers of
  YAML/TOML/JSON files that markdown-only globbing never reached.

## Phases

Phase detail lives here. `epoch-5-sprint-19-plan.md` is the sprint-level wrapper and does
not restate this list.

### P1: Baseline and exclusion re-verification

Small, well-bounded, and deliberately first because P4 cannot be interpreted without it.

- Measure current cross-reference coverage using the S56 methodology, so the post-change
  number is comparable rather than merely reported.
- Widen the indexed file set experimentally (via `--glob`) and count how many dependency
  directories reappear in `--knowledge-summary`. `DEFAULT_EXCLUDES` was authored against
  `.md` files; `.venv` and `.pytest_cache` hold far more YAML/TOML/JSON than markdown, so
  the exclusion list is expected to need extension.
- **Success:** a recorded baseline coverage figure, and zero dependency directories in the
  summary at the widened file set.

### P2: Structured-config parser

- New parser producing graph nodes from YAML, TOML and JSON, in that priority order.
- Node granularity per Open Question 1.
- Must not disturb the existing markdown path; the two coexist behind the same discovery
  stage.
- **Success:** a config file yields nodes that carry its identity and internal structure,
  test-first, with the existing suite green.

### P3: Cross-file link extraction

- Extract path-valued references from the parsed config (hook `command`, workflow
  `run`/`uses`, `pyproject.toml` module declarations, `.mcp.json` server paths) and
  materialise them as edges to existing file nodes.
- Unresolvable and out-of-repo paths handled per Open Question 2.
- **Success:** a known dependency that exists in the repository and was previously absent
  from the graph (for example `.claude/settings.json` to `.claude/hooks/*.sh`) appears as
  an edge.

### P4: EXP-013 coverage gate

The sprint's capability experiment. Run after P3, against the P1 baseline, with the
threshold pre-registered **before** the measurement.

- **What it gates, stated precisely, because this is easy to get wrong:** the outcome does
  **not** decide whether Sprint 19 ships. Config nodes and their edges are real repository
  dependencies and retain their value at any coverage number. What the outcome decides is
  whether [DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md)
  §Conditions 2's clustering revisit trigger fires. A "fail" here is a finding about
  clustering, not a failed sprint.
- Pre-registered threshold: see Open Question 5, unresolved at authoring time and to be
  fixed before P4 runs, never after.
- **Success:** the coverage delta is measured and recorded whichever way it goes, and the
  revisit-trigger question is answered rather than left open.

### P5: Layer 1 integration

- Surface config nodes in `--knowledge-summary`, or record the decision that they stay
  graph-only, per Open Question 3.
- Docs pass: CLI `--help`, README, and the `DEFAULT_EXCLUDES` documentation that
  Sprint 18 left open (its plan marks the default-exclusions half of its docs deliverable
  as carrying forward to this sprint).
- **Success:** Layer 1 output reflects the widened graph within its condensation budget,
  or the exclusion is recorded with a reason.

## Open questions (to resolve during sprint planning, not here)

1. **Node granularity for a config file.** Is a YAML document one node, or does each
   top-level key become a section-shaped node the way markdown headings do?
2. **Does an unresolvable path reference become an edge to nothing, or no edge?** The
   markdown path already has an orphan concept; config paths that point outside the repo
   (`~/dsm-agentic-ai-data-science-methodology/`) need a stated rule.
3. **Condensation budget.** Vision §4 gives Layer 1 a ~200-line budget with a
   per-component table. Adding a source class needs either a budget line or a decision
   that config nodes are graph-only and never surface in the ToC.
4. **Whether `--glob` remains the control surface** or the new file classes are selected
   by a separate flag. Reusing `--glob` is simplest but makes "markdown plus config" hard
   to express as a single pattern.
5. **The P4 pre-registered threshold, and it needs a human decision.** What coverage delta
   would count as "materially above the measured ~25%" for the purposes of DEC-012
   §Conditions 2? This is deliberately left unset here rather than guessed, because a
   threshold chosen after the parser exists is a threshold chosen by whoever knows which
   way the number went. Fix it at sprint kickoff, before P2 begins.

## Acceptance criteria

- [ ] Config/YAML parser implemented, test-first, producing graph nodes
- [ ] Cross-file path references extracted as edges, test-first
- [ ] `DEFAULT_EXCLUDES` re-verified against the widened file set, with the dependency-
      directory count in the summary output recorded before and after
- [ ] Cross-reference coverage measured pre- and post-change using S56's methodology,
      result recorded whichever way it goes
- [ ] `--knowledge-summary` integration shipped, or a recorded decision that config nodes
      stay graph-only
- [ ] Vision §9 Q4 annotated with the answer this BL reaches
- [ ] Python AST expansion confirmed still out of scope at sprint close, or split into
      its own BL

## References

- [Intrinsic-ToC Vision](../research/2026-04-13_intrinsic-toc-vision.md) §4 (Layer 1
  components and condensation budget), §9 Q4 (the question this answers)
- [DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md), origin,
  scope fix, and the boundary requirement in §Conditions 3
- [BL-GE-001](BL-GE-001_semantic-concept-layer.md), the sister density mechanism
- `dsm-docs/research/2026-07-21_cluster-quality-graph-density.md`, the ~25% coverage
  measurement and the null-model methodology to reuse
- `src/cli.py` (`collect_markdown_files`), `src/parser/markdown_parser.py`,
  `src/parser/cross_ref_extractor.py`, `src/graph/graph_builder.py`, the four stages any
  new source class must pass through
