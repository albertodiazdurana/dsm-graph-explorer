# BL-302 Phase 2: Leiden Clustering for Knowledge-Summary Output

**Status:** CLOSED, clustering **not adopted** (S57, 2026-07-31, per [DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md)). P1 shipped; P2/P3 cancelled; P4 survives as reusable validation machinery. See "Resolution" below.
**Priority:** High
**Date Created:** 2026-07-21
**Origin:** DEC-010 (this project) + DSM Central BL-367 (format research) + GE S47 Q3, continues the BL-302 line (Phase 1 shipped Sprint 16, Phase 1.5 CLOSED Sprint 17)
**Author:** Alberto Diaz Durana
**Target:** Sprint 18 (Epoch 5), closed without delivery; replaced by Sprint 19 (BL-GE-002)
**Related:** [BL-302 Phase 1.5](BL-302-phase-1.5-toon-migration.md), [DEC-009](../decisions/DEC-009-no-local-llm-dependencies.md), [DEC-010](../decisions/DEC-010-toon-migration-format.md), [DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md), [epoch-5-plan.md](epoch-5-plan.md)

---

## Sprint 18 Closure (2026-07-31, Session 57)

### Resolution (2026-07-31, Session 57): closed as out-of-vision-scope

Session 56 halted this phase on a premise failure. Session 57 resolved the P4 gate
ambiguity, then re-derived the aim from the Intrinsic-ToC vision instead of continuing to
compare candidate designs. The decisive finding is that **clustering is absent from the
vision**: §4 lists what Layer 1 maps (project structure, hub documents, cross-reference
hotspots, orphan files) and §2 defines connectivity as hubs, orphans and hotspots.
Clustering is in neither, nor in the §4 condensation budget. It entered through S49's
GraphRAG fit study, whose separation of Leiden from the entity extraction that feeds it
was already refuted in S56.

`generate_knowledge_summary` was verified to emit all four specified components, so
**Layer 1 as specified has been complete since Sprint 16**, and this phase would have
added an unspecified fifth to a substrate measured at 2.8% modularity excess over a
degree-preserving null with ~25% file coverage.

Rationale, counter-evidence, revisit trigger and consequences are recorded in
[DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md) and are not
restated here.

**Phase disposition:**

| Phase | Disposition |
|---|---|
| P1, graph scope exclusion | **Shipped** (S55, in master). Retains independent value: removed 16 dependency directories from the summary. Its original framing as a clustering prerequisite no longer applies. |
| P2, Leiden clustering | **Cancelled.** The `cluster` extra (`leidenalg` + `igraph`) may remain installed or be removed; nothing depends on it. |
| P3, cluster emission | **Cancelled.** |
| P4, validation gate | **Retained as machinery, not run.** The null-controlled degeneracy floor resolved below is the standing validation form for any future partition-based feature, per DEC-012's revisit trigger. |

**This does not refute clustering as a technique.** It is out-of-vision-scope on this
substrate, at this coverage, for this artifact. DEC-012 records the conditions under
which it may be re-proposed.

---

## Context

BL-302 Phase 1 (Sprint 16) shipped `--knowledge-summary`, a bounded, agent-consumable
summary of a repository's reference graph: document hierarchy, hub documents, hotspots,
and orphans. Phase 1.5 (Sprint 17) attempted to migrate that output to TOON and was
CLOSED without adoption, the format stays markdown.

Phase 2 adds the remaining Epoch 4 deferred item on the Intrinsic-ToC line: concept
clusters derived from the reference graph, so a consuming agent can see which parts of
a repository belong together rather than only which documents are large or central.

## Motivation

The current summary answers "what is big" and "what is central". It does not answer
"what belongs with what". Clustering closes that gap using structure the graph already
carries, with no new knowledge source.

## Correction to the inherited premise (S55, 2026-07-21)

The epoch-5 plan and [BL-302 Phase 1.5 line 77](BL-302-phase-1.5-toon-migration.md)
scoped this phase as depending on TOON:

> Phase 2 (Leiden clusters) requires native nesting; TOON handles this, incumbent does not.

**That claim is refuted.** Both emitters were run against this repository in S55
(227 files, 2,585 sections, 133 cross-references):

- The markdown path (`generate_hierarchy`, `src/analysis/knowledge_summary.py:161-181`)
  already emits two-level nesting: a bold directory header followed by indented
  per-file bullets and an `... and N more` truncation line.
- The TOON path (`_generate_toon_summary`) flattens the same data into
  `directories[56]{path,files,sections,shown,more}` plus a second table that repeats
  the path column.

Markdown is more nested than the implemented TOON, not less. Measured: markdown
230 lines / 17,734 bytes, TOON 206 lines / 18,032 bytes (fewer lines, more bytes,
consistent with the S52 C3 token-gate failure).

**Consequence:** Phase 2 has no format prerequisite. It emits markdown, using the
nesting `generate_hierarchy` already demonstrates. The claim was written to justify a
migration that was subsequently abandoned and never survived contact with the code.
Phase 1.5 carries a matching amendment.

## Scope

### In scope

- Default graph-scope exclusions so clustering runs on project content, not dependencies
- Leiden community detection over the existing reference graph (structural only)
- A cluster section in `--knowledge-summary` markdown output
- Tests alongside each phase, per the project's TDD protocol
- An early validation gate: a degeneracy floor against a degree-preserving null

### Out of scope

- Embeddings, NER, or any local LLM/NLP model. **DEC-009 decision: "Drop all three
  items. GE will not add local LLM or NLP model dependencies."** Clustering here is
  purely structural, derived from graph edges.
- Author-declared or extracted semantic concepts, that is BL-GE-001 (Layer 4.5)
- Re-opening the output format question, markdown is settled (DEC-010 Amendment 2)
- Cross-repo / ecosystem clustering, that is Sprint 20

## Phases

Phase detail lives here. `epoch-5-sprint-18-plan.md` is the sprint-level wrapper and
does not restate this list.

### P1: Graph scope exclusion

The exclusion mechanism already exists and is wired: `src/cli.py:842` calls
`filter_files(md_files, config.exclude, base_path)`, fed from the YAML config. What is
missing is sensible defaults. `_resolve_paths` (`src/cli.py:56`) is a bare
`path.glob("**/*.md")`, and this repo's config excludes only `dsm-docs/_references`,
`htmlcov`, and `outputs`, so everything under `.venv/` is included.

Observed on this repository: 57 directories emitted, **16 of them under `.venv/` or
`.pytest_cache/`**, including numpy, scipy, sklearn, black, and idna license files.
`.claude/transcripts/` (27 files of agent session data) is also included. Verified
against the repository's real `.dsm-graph-explorer.yml`, not a test config.

Add a `DEFAULT_EXCLUDES` constant merged with `config.exclude`:
`.venv`, `site-packages`, `node_modules`, `.git`, `.pytest_cache`, `build`, `dist`.
Provide an opt-out for callers that genuinely want dependency content.

Treated as a **product defect**, not per-repo config responsibility: a tool whose
output is an agent-consumable table of contents should not ship dependency license
files as project knowledge in any consuming repository.

### P2: Leiden clustering

Run Leiden community detection over the cleaned graph. Library choice
(`leidenalg` vs `networkx.community`) is decided in-phase, weighing the optional-dependency
cost, GE already treats graph libraries as optional extras.

**Open design question, deliberately not pinned here:** flat partition vs
multi-resolution hierarchy. A flat partition is sufficient for a table of contents and
is materially cheaper; the hierarchy is what "nesting" originally referred to. Resolve
in-sprint against real output rather than committing in advance.

### P3: Cluster emission

Emit a cluster section into the `--knowledge-summary` markdown, using the same nesting
idiom as `generate_hierarchy`. Bounded output: cap clusters shown and members per
cluster, with an `... and N more` line, matching the existing truncation convention.

### P4: Validation gate

Run early, before any fixture freeze. This is the direct lesson of Sprint 17, where the
DEC-010 C3 gate was sequenced after a golden-fixture freeze and, when finally run,
failed, having nearly enshrined a schema that could not ship.

**Gate (resolved S57):** a **degeneracy floor**, not a quality bar. It asks whether the
partition is non-degenerate and therefore worth shipping at all, and it is answered
against a **degree-preserving null model**, never an absolute threshold. Two failure
modes:

1. **Null-indistinguishable.** The partition's modularity must exceed a
   degree-preserving rewire of the same graph by a margin pre-registered before the run.
2. **Collapse.** A partition resolving to one giant cluster, or to near-singletons,
   fails regardless of modularity score.

Whether the clusters are *good* is deliberately out of scope. That is what the direction
decision, and under option D the agent A/B, exists to answer.

**Operationalization is direction-conditional** and is not pinned here, because the
direction decision ([research §7](../research/2026-07-21_cluster-quality-graph-density.md))
is open:

| Direction | P4 becomes |
|---|---|
| A, centrality pivot | Retired, no clusters to gate |
| B, grow the graph | Survives in shape; the *new* graph needs its own null (thresholded similarity graphs inflate clustering coefficients, research §4) |
| C, connected core | Live gate as above, plus coverage disclosure |
| D, agent A/B | Superseded by cross-arm task performance; the degeneracy floor drops to a pre-condition on the cluster arm |

**Amendment (S57): the "cuts across obvious boundaries" clause is struck.** It read:

> Gate: do the clusters correspond to recognizable project areas on a repository whose
> structure is known independently? A cluster set that cuts across obvious boundaries, or
> collapses to one giant cluster, fails the gate regardless of modularity score.

Struck because all three available readings fail, and not because of the ambiguity. Read
as **folder boundaries**, the gate is self-defeating, the folder tree already answers it
and `generate_hierarchy` already emits it, and its instrument (NMI-vs-directories) was
eliminated as invalid. Read as **topical coherence**, it has no null control and is the
metric class the null-model test invalidated. Read as a **degeneracy screen** (the reading
the "or collapses to one giant cluster" conjunction supports, and the one adopted above),
it is valid but was written before the evidence that answers it: real modularity beats the
null in 0/50 replicates (z = 2.68) while cluster count and size distribution are
indistinguishable from it. The clause was authored 2026-07-21 before that evidence
existed; disambiguating it would have produced a gate that still could not do its job.

## Acceptance Criteria

> **Superseded S57 (see Resolution above).** Criteria 1, 2, 6 and 7 were met by P1 and
> stand. Criteria 3, 4 and 5 are **unmet and unreachable** under DEC-012, since they
> require the cancelled clustering phases. They are kept as a record of what the phase
> intended, not as outstanding work. Per the S55 lesson, a criterion that has become
> unsatisfiable is annotated rather than silently left open.

1. `--knowledge-summary` on this repository emits **zero** `.venv/`, `site-packages/`,
   or `.pytest_cache/` directories
2. Default exclusions are overridable by an explicit opt-out
3. Leiden clustering runs on the cleaned graph and emits a bounded cluster section
4. Cluster output is markdown, no format flag involvement
5. P4 degeneracy floor is run against a degree-preserving null with the margin
   pre-registered, and the result recorded before any fixture freeze, including a FAIL,
   which is a successful gate
6. Tests alongside each phase; existing suite stays green
7. No new required dependencies, graph libraries remain optional extras (DEC-009)

## Dependencies

- BL-302 Phase 1 (Sprint 16, shipped), provides `--knowledge-summary`
- BL-302 Phase 1.5 (Sprint 17, CLOSED), settles markdown as the format
- DEC-009, constrains this to structural analysis
- No dependency on TOON, see the correction above

## Risks

- **Cluster quality is subjective.** Mitigated by P4's independent-structure check and
  by running the gate early.
- **Leiden is non-deterministic across seeds.** Fix a seed for reproducible output;
  unstable clusters across runs would make the ToC untrustworthy.
- **Default exclusions could hide content a consumer wants.** Mitigated by the opt-out
  and by reporting the excluded count, which the CLI already does (`src/cli.py:1049`).
- **Scope creep toward semantic clustering.** DEC-009 and the BL-GE-001 boundary are
  the guard, structural only.

## References

- `src/analysis/knowledge_summary.py`, current emitters
- `src/cli.py:56`, `:842`, `:1049`, path resolution, exclusion filter, excluded-count report
- [DEC-009](../decisions/DEC-009-no-local-llm-dependencies.md), no local LLM/NLP dependencies
- [BL-302 Phase 1.5](BL-302-phase-1.5-toon-migration.md), format resolution + Amendment 3
- [epoch-5-plan.md](epoch-5-plan.md), Sprint 18 scope
