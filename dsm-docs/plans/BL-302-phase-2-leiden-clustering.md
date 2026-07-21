# BL-302 Phase 2: Leiden Clustering for Knowledge-Summary Output

**Status:** OPEN
**Priority:** High
**Date Created:** 2026-07-21
**Origin:** DEC-010 (this project) + DSM Central BL-367 (format research) + GE S47 Q3, continues the BL-302 line (Phase 1 shipped Sprint 16, Phase 1.5 CLOSED Sprint 17)
**Author:** Alberto Diaz Durana
**Target:** Sprint 18 (Epoch 5)
**Related:** [BL-302 Phase 1.5](BL-302-phase-1.5-toon-migration.md), [DEC-009](../decisions/DEC-009-no-local-llm-dependencies.md), [DEC-010](../decisions/DEC-010-toon-migration-format.md), [epoch-5-plan.md](epoch-5-plan.md)

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
- An early validation gate on cluster quality

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

Gate: do the clusters correspond to recognizable project areas on a repository whose
structure is known independently? A cluster set that cuts across obvious boundaries, or
collapses to one giant cluster, fails the gate regardless of modularity score.

## Acceptance Criteria

1. `--knowledge-summary` on this repository emits **zero** `.venv/`, `site-packages/`,
   or `.pytest_cache/` directories
2. Default exclusions are overridable by an explicit opt-out
3. Leiden clustering runs on the cleaned graph and emits a bounded cluster section
4. Cluster output is markdown, no format flag involvement
5. P4 validation gate passes on a known-structure repository, with the result recorded
   before any fixture freeze
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
