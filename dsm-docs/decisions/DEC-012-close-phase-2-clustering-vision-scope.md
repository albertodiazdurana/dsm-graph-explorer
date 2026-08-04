# DEC-012: Close BL-302 Phase 2 (clustering), vision scope governs the Intrinsic-ToC

**Status:** Accepted
**Date:** 2026-07-31
**Session:** S57
**Author:** Alberto Diaz Durana
**Related:** BL-302 Phase 2 (Leiden clustering), BL-GE-002 (graph source expansion, to be created), DEC-009 (no local LLM dependencies), DEC-011 (Semantic Concept Layer), research `2026-07-21_cluster-quality-graph-density.md`, Intrinsic-ToC Vision §2 / §4 / §9

---

## Context

Sprint 18 was scoped as BL-302 Phase 2: Leiden community detection over the reference
graph, emitting concept clusters into `--knowledge-summary`. The phase reached P1
(graph scope exclusions, shipped S55) and then halted.

Session 56 halted P2 on a premise failure. A degree-preserving null model showed the
Leiden partition exceeds a randomised graph with the same degree sequence by only
**2.8%** (z = 2.68, 0/50 null replicates reached the real modularity), and the quality
metric used through most of that session, NMI against directory labels, scored the
**same or higher on the null** (0.1881 null vs 0.1812 real) and was therefore invalid.
The underlying cause is coverage: only about **25% of files** carry any cross-reference,
and roughly 99% of sections are orphans.

Session 57 resolved the P4 validation gate (an ambiguity that blocked any experiment
design) to a null-controlled degeneracy floor, then re-derived the project's aim from
the Intrinsic-ToC vision rather than continuing to compare candidate designs against
each other. That re-derivation is what this decision rests on.

## Decision

**Close BL-302 Phase 2 without adopting clustering.** The Intrinsic-ToC's Layer 1
component set is the four the vision specifies, and all four ship today. Clustering is
not among them.

**Replace Sprint 18 with a new Sprint 19** that answers Intrinsic-ToC Vision §9
Open Question 4 (graph source expansion), formalised as **BL-GE-002** and scoped to
config/YAML files and cross-file link extraction. Python AST work is explicitly out of
scope for that sprint.

The phase closes the way BL-302 Phase 1.5 closed: by reaching a recorded resolution.
A gate that correctly rejects its candidate is a successful gate.

### Sprint renumbering

| Was | Becomes |
|---|---|
| Sprint 18, BL-302 Phase 2 (Leiden clustering) | Closed, not delivered |
| , | Sprint 19, BL-GE-002 graph source expansion |
| Sprint 19, hop distance + EXP-001 validation | Sprint 20 |
| Sprint 20, ecosystem graph foundations | Sprint 21 |

Sprints 19 and 20 existed only as epoch-plan sections with no plan files, so the
renumbering costs nothing beyond the epoch-plan edit.

## Justification (strongest first)

Provenance is marked on every item, because the analysis behind this decision produced
several claims that measurement later overturned, and the record should make the
difference visible rather than flatten it.

1. **Clustering is absent from the vision. [QUOTED]** Vision §4 states what Layer 1
   maps: project structure, hub documents, cross-reference hotspots, orphan files. §2
   defines the connectivity dimension as "which files are hubs (most referenced), which
   are orphans (disconnected), which sections are load-bearing (hotspots)". Clustering
   appears in neither, nor in the §4 condensation budget table. It entered the roadmap
   through S49's GraphRAG fit study, not through the vision.

2. **Layer 1 as specified is already complete. [VERIFIED IN CODE]**
   `generate_knowledge_summary` (`src/analysis/knowledge_summary.py`) calls
   `generate_hierarchy`, `generate_hub_documents`, `generate_hotspots` and
   `generate_orphans`. All four specified components have shipped since Sprint 16.
   Phase 2 would have added an unspecified fifth.

3. **The substrate does not support clustering. [MEASURED, NULL-CONTROLLED, S56]**
   2.8% modularity excess over a degree-preserving null, on a graph where ~25% of files
   have any cross-reference. Cluster count and size distribution are not visibly
   distinguishable from the null. This is the strongest empirical leg and it does not
   depend on any Session 57 analysis.

4. **The premise that introduced clustering is refuted. [MEASURED + SOURCED, S56]**
   S49 adopted GraphRAG's Leiden while rejecting its LLM entity extraction as
   DEC-009-incompatible. The extraction is what produces a clusterable substrate:
   GraphRAG does not cluster document cross-references at all, it derives an entity
   graph and clusters that. The algorithm was carried forward and the thing that fed it
   was left behind.

5. **The vision already asked the density question, and it gates a later layer.
   [QUOTED]** §9 Open Question 4: "The current graph indexes markdown only. When (and
   how) should it expand to include Python source, YAML configs, and other file types?
   This gates Layer 4." Unanswered since 2026-04. The 25% coverage is a consequence of
   that open scoping question, not a newly discovered defect.

6. **The aim already has a success criterion, and it is not a Layer 1 component
   property. [QUOTED + PRIOR EXPERIMENT]** Vision §4: "The quality of Layer 2 depends
   entirely on how well Layer 1 is structured." Success is agent navigation
   performance, which EXP-011 (S53) already measured: ToC arms used ~6x fewer tool calls
   and answered more accurately than the no-ToC arm. Sprint 18 spent two sessions
   arguing a component-level gate while the aim-level metric sat unused.

## Counter-evidence considered (per DSM_0.2 §8.2.1)

1. **Option A (centrality) is a real upgrade, and this decision does not take it.
   [MEASURED S57, refuted the agent's own claim]** The recommendation that led here
   originally argued that PageRank would collapse to the shipped degree ranking on a
   graph this sparse, making a centrality upgrade cosmetic. A pre-registered check
   (threshold fixed before running: 3+ positions changed or any new entrant) **refuted
   that claim on both corpora**: GE 9/10 positions changed, DSM Central 5/10 with 2 new
   entrants, against a global Pearson r of 0.92 between degree and PageRank. PageRank
   produces a materially different hub ordering. Option A therefore remains available
   as a genuine, cheap Layer 1 quality improvement, and closing Phase 2 neither
   delivers nor forecloses it.

   > **Annotation S58 (2026-08-04), reproduction.** The S57 check was run inline and no
   > script survived, so these figures could not be regenerated. They now can:
   > `scripts/check_pagerank_vs_degree.py`. The re-run **confirms the verdict** (material
   > reordering on both corpora) and reproduces DSM Central's Pearson r (0.9204) and its
   > 2 new entrants. It **diverges on the positions-changed counts**, reporting GE 7/10
   > and Central 8/10 against the 9/10 and 5/10 recorded above. Both corpora moved in the
   > interval (Central released v1.19.0), and S57's exact projection cannot be inspected,
   > so the causes are not separable. The conclusion is unaffected, because it rests on
   > the pre-registered threshold being cleared rather than on the specific count, and the
   > threshold is cleared by a wider margin in the re-run than in the original. The text
   > above is left as the S57 record; this annotation is the correction.
   >
   > The re-run also fixes a defect in the S57 script that the original session disclosed:
   > degree counts were looked up in a top-10-only dictionary, so entrants from outside
   > the top 10 printed as "0 refs". This script ranks the full file set. Its degree
   > output was validated position-for-position against the shipped
   > `--knowledge-summary` hub table.

2. **Option C (ship the connected core with disclosure) is defensible.** Partial
   coverage with explicit disclosure is the documented shipping norm for comparable
   systems. Choosing closure over C trades a shippable-but-weak feature for scope
   honesty, and a reasonable reader could take the other side.

3. **Option D (three-arm agent A/B) would have produced direct evidence.** It is the
   only option that addresses the decisive evidence gap rather than arguing around it.
   It is not taken because DSM_0.2 §8.9.2 (added v1.19.0, after the option set was
   written) gates fan-out actions of exactly this shape, and re-fires per fan-out
   rather than carrying a standing acceptance, and because the strength of the cluster
   arm is uncertain on a 2.8%-over-null partition. Note this reasoning is weakened by
   counter-evidence 1: the centrality arm is more substantive than the agent argued.

4. **The epoch loses a delivered success criterion.** Epoch 5 listed "BL-302 Phase 2
   delivered" as a criterion. It is reframed rather than met, following the precedent
   set two bullets above it in the same plan when the DEC-010 C3 gate failed.

5. **Agent reliability on this decision line. [SELF-REPORTED, MATERIAL]** Three
   recommendations were made across S56 and S57 on the Sprint 18 question. All three
   had a key supporting claim overturned by cheap measurement, twice after the
   recommendation had already been approved. The pattern is consistent: the
   *measurements* in this chain have held up, the *inferences layered on them* have
   not. Justifications 1, 2, 3, 4 and 5 above are quoted or measured. Justification 6's
   reading of the vision is interpretive. Weight accordingly.

## Conditions on acceptance

1. **This does not refute clustering as a technique.** It finds clustering
   out-of-vision-scope on the current substrate. The claim is scoped to this graph, at
   this coverage, for this artifact.

2. **Revisit trigger.** If BL-GE-002 (graph source expansion) or BL-GE-001 (semantic
   concept layer) raises cross-reference coverage materially above the measured ~25%,
   clustering may be re-proposed. Any such proposal must clear the null-controlled
   degeneracy floor recorded in BL-302 Phase 2 §P4 (resolved S57), not an absolute
   modularity threshold.

3. **BL-GE-002 must state its boundary against BL-GE-001.** BL-GE-001 adds concept
   *edges* between existing nodes; BL-GE-002 adds *nodes* from new file types. Both
   raise density by different mechanisms and the boundary is cheaper to state at
   authoring time than to untangle later.

4. **Option A remains unresolved, not rejected.** If a centrality upgrade is wanted, it
   is a separate small item against Layer 1 quality, not a revival of Phase 2.

## Consequences

### Positive

- Scope honesty: the Intrinsic-ToC's component set matches the vision that defines it.
- Removes an inherited item whose premise was refuted, closing the second instance in
  this project of a forward-looking claim outliving its context.
- Redirects effort to a question the vision itself raised and that gates Layer 4.
- The resolved P4 degeneracy floor survives as reusable validation machinery for any
  future partition-based feature.

### Negative

- Epoch 5 does not deliver a clustering feature, and one success criterion is reframed
  rather than met.
- Two planned sprints renumber.
- P1's shipped work (`DEFAULT_EXCLUDES`) was scoped as a clustering prerequisite. It
  retains independent value (it removed 16 dependency directories from the summary) but
  its original justification no longer applies.
- Sprint 18 consumed parts of three sessions and ships no user-facing feature. Its
  deliverables are the research file, the resolved P4 gate, and this decision.

### Neutral

- The `cluster` optional extra (`leidenalg` + `igraph`, added S56) can remain installed
  or be removed; nothing depends on it either way.
- Clustering stays available for a later epoch under the revisit trigger above.

## References

- `dsm-docs/plans/BL-302-phase-2-leiden-clustering.md`, the phase being closed, including
  the S57 P4 resolution
- `dsm-docs/research/2026-07-21_cluster-quality-graph-density.md`, null-model results,
  eliminated designs, and the option space (§7)
- `dsm-docs/research/2026-04-13_intrinsic-toc-vision.md`, §2 connectivity vocabulary,
  §4 Layer 1 component spec and Layer 2 success statement, §9 Q4 graph expansion
- `dsm-docs/plans/BL-302-phase-1.5-toon-migration.md`, the closure precedent
- `dsm-docs/plans/epoch-5-plan.md`, success criteria and sprint sequence
- `src/analysis/knowledge_summary.py`, the shipped Layer 1 emitters
- DSM_0.2 §8.9.2, High-Token-Cost Action Gate (bears on option D)
